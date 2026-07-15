from __future__ import annotations

import argparse
import functools
import http.server
import json
import re
import socket
import sys
import urllib.parse
from pathlib import Path
from socketserver import ThreadingMixIn
from typing import Any, Dict, Iterable, List, Optional

from .generator import build_site, copy_assets
from .github_api import GitHubClient, GitHubError, Repository, require_token
from .storage import discover_repositories, load_bundle, repo_data_dir, save_stage


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_args(argv)
    if args.command == "sync" and not args.repositories:
        print_sync_suggestions()
        return 0
    if args.command == "server":
        serve_docs(args.host, args.port)
        return 0

    repos = [Repository.parse(value) for value in args.repositories]

    if args.command == "sync":
        sync_repositories(repos)
        build_site(discover_repositories())
        print(f"Generated {Path('docs/index.html').resolve()}")
        serve_docs(args.host, args.port)
        return 0

    if args.command == "all":
        sync_repositories(repos)

    if args.command in ("build", "all"):
        build_repos = repos or discover_repositories()
        if not build_repos:
            raise SystemExit("No local repository data found. Run sync first.")
        build_site(build_repos)
        print(f"Generated {Path('docs/index.html').resolve()}")

    return 0


def parse_args(argv: Optional[Iterable[str]]) -> argparse.Namespace:
    raw_args = list(argv) if argv is not None else sys.argv[1:]
    commands = {"sync", "build", "all", "server", "-h", "--help"}
    if raw_args and raw_args[0] not in commands:
        raw_args = ["all"] + raw_args

    parser = argparse.ArgumentParser(
        description="Fetch GitHub issues/PRs and generate static HTML.",
        epilog=(
            "Examples:\n"
            "  local-github sync https://github.com/TencentCloud/CubeSandbox\n"
            "  local-github build\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")

    sync_parser = subparsers.add_parser("sync", help="Fetch data, build docs/, and start the local server.")
    sync_parser.add_argument("repositories", nargs="*", help="Repository names such as owner/repo.")
    sync_parser.add_argument("--host", default="0.0.0.0", help="Server host. Default: 0.0.0.0.")
    sync_parser.add_argument("--port", type=int, default=8000, help="Server port. Default: 8000.")

    build_parser = subparsers.add_parser("build", help="Generate docs/ from local data.")
    build_parser.add_argument("repositories", nargs="*", help="Optional repository names to build.")

    all_parser = subparsers.add_parser("all", help="Fetch data and generate docs/.")
    all_parser.add_argument("repositories", nargs="+", help="Repository names such as owner/repo.")

    server_parser = subparsers.add_parser("server", help="Serve the generated docs/ with a local HTTP server.")
    server_parser.add_argument("--host", default="0.0.0.0", help="Host to bind. Default: 0.0.0.0.")
    server_parser.add_argument("--port", type=int, default=8000, help="Port to bind. Default: 8000.")

    parsed = parser.parse_args(raw_args)
    if parsed.command is None:
        parser.print_help()
        raise SystemExit(2)
    elif not hasattr(parsed, "repositories"):
        parsed.repositories = []
    return parsed


def print_sync_suggestions(docs_repos_root: Path = Path("docs/repos")) -> None:
    repos = discover_docs_repositories(docs_repos_root)
    if not repos:
        print("No repositories found under docs/repos.")
        print("Usage: local-github sync owner/repo")
        return

    print("No repository specified for sync.")
    print("Available repositories from docs/repos:")
    for repo in repos:
        print(f"  local-github sync {repo.full_name}")


def discover_docs_repositories(docs_repos_root: Path = Path("docs/repos")) -> List[Repository]:
    repos: List[Repository] = []
    if not docs_repos_root.exists():
        return repos
    for owner_dir in sorted(path for path in docs_repos_root.iterdir() if path.is_dir()):
        for repo_dir in sorted(path for path in owner_dir.iterdir() if path.is_dir()):
            repos.append(Repository(owner_dir.name, repo_dir.name))
    return repos


class ReusableThreadingHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class LocalGitHubRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        if not urllib.parse.urlsplit(self.path).path.startswith("/api/"):
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_GET(self) -> None:
        path = urllib.parse.urlsplit(self.path).path
        if path.startswith("/api/"):
            self.handle_api_request(path)
            return
        super().do_GET()

    def handle_api_request(self, path: str) -> None:
        parts = [urllib.parse.unquote(part) for part in path.strip("/").split("/")]
        if (
            len(parts) != 7
            or parts[:2] != ["api", "repos"]
            or parts[4] != "pulls"
            or parts[6] != "files"
            or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}", parts[2]) is None
            or re.fullmatch(r"[A-Za-z0-9._-]+", parts[3]) is None
            or not parts[5].isdigit()
            or int(parts[5]) < 1
        ):
            self.send_json(404, {"error": "API endpoint not found."})
            return

        repo = Repository(parts[2], parts[3])
        if not (repo_data_dir(repo) / "repo.json").is_file():
            self.send_json(404, {"error": f"Repository {repo.full_name} has not been synced locally."})
            return

        try:
            token = require_token()
        except GitHubError as exc:
            self.send_json(503, {"error": str(exc)})
            return

        try:
            files = GitHubClient(token).fetch_pull_files_for_pull(repo, int(parts[5]))
        except GitHubError as exc:
            self.send_json(502, {"error": str(exc)})
            return

        self.send_json(200, {"files": files})

    def send_json(self, status: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def serve_docs(host: str = "0.0.0.0", port: int = 8000) -> None:
    docs_root = Path("docs")
    docs_root.mkdir(parents=True, exist_ok=True)
    copy_assets(docs_root)
    handler = functools.partial(LocalGitHubRequestHandler, directory=str(Path.cwd()))
    server = ReusableThreadingHTTPServer((host, port), handler)
    actual_port = int(server.server_address[1])
    local_url = f"http://127.0.0.1:{actual_port}/docs/index.html"
    remote_url = f"http://{local_ip_address()}:{actual_port}/docs/index.html"

    print("")
    print(f"    ➜  Local:   {local_url}")
    print(f"    ➜  Remote:  {remote_url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped local-github server.")
    finally:
        server.server_close()


def local_ip_address() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return str(sock.getsockname()[0])
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def sync_repositories(repos: List[Repository]) -> None:
    try:
        token = require_token()
    except GitHubError as exc:
        raise SystemExit(str(exc)) from exc
    client = GitHubClient(token)
    for repo in repos:
        previous = load_previous_bundle(repo)
        previous_synced_at = previous.get("meta", {}).get("synced_at") if previous else None
        incremental = bool(previous_synced_at)
        print(f"Syncing {repo.full_name} ...")
        if incremental:
            print(f"  Incremental sync since {previous_synced_at}")
        else:
            print("  No previous local data found. Running full sync.")

        print("  [1/7] Fetching repository metadata ...")
        repository = client.fetch_repository(repo)
        repo_path = save_stage(repo, "repo.json", repository)
        print(f"        Saved repo.json -> {repo_path}")

        print("  [2/7] Fetching issues ...")
        fetched_issues = client.fetch_issue_events(repo, since=previous_synced_at, include_pulls=False) if incremental else client.fetch_issues(repo)
        issues = merge_items(previous.get("issues", []) if previous else [], fetched_issues)
        issues_path = save_stage(repo, "issues.json", issues)
        print(f"        Saved issues.json ({len(issues)} total, {len(fetched_issues)} fetched) -> {issues_path}")

        print("  [3/7] Fetching pull requests ...")
        if incremental:
            updated_pull_refs = client.fetch_issue_events(repo, since=previous_synced_at, include_pulls=True)
            fetched_pulls = [client.fetch_pull(repo, int(item["number"])) for item in updated_pull_refs]
        else:
            fetched_pulls = client.fetch_pulls(repo)
        pulls = merge_items(previous.get("pulls", []) if previous else [], fetched_pulls)
        pulls_path = save_stage(repo, "pulls.json", pulls)
        print(f"        Saved pulls.json ({len(pulls)} total, {len(fetched_pulls)} fetched) -> {pulls_path}")

        print("  [4/7] Fetching issue comments ...")
        issue_comments = dict(previous.get("issue_comments", {}) if previous else {})
        issue_comments.update(
            client.fetch_issue_comments(repo, fetched_issues, progress=item_progress("issues", "comments"))
        )
        issue_comments_path = save_stage(repo, "issue_comments.json", issue_comments)
        print(
            f"        Saved issue_comments.json ({sum(len(value) for value in issue_comments.values())} comments)"
            f" -> {issue_comments_path}"
        )

        print("  [5/7] Fetching pull request conversation comments ...")
        pull_comments = dict(previous.get("pull_comments", {}) if previous else {})
        pull_comments.update(
            client.fetch_issue_comments(repo, fetched_pulls, progress=item_progress("pull requests", "comments"))
        )
        pull_comments_path = save_stage(repo, "pull_comments.json", pull_comments)
        print(
            f"        Saved pull_comments.json ({sum(len(value) for value in pull_comments.values())} comments)"
            f" -> {pull_comments_path}"
        )

        print("  [6/7] Fetching pull request review comments ...")
        if incremental:
            review_comments = merge_review_comments(
                previous.get("review_comments", []),
                [
                    comment
                    for pull in fetched_pulls
                    for comment in client.fetch_pull_review_comments(repo, int(pull["number"]))
                ],
            )
        else:
            review_comments = client.fetch_review_comments(repo)
        review_comments_path = save_stage(repo, "review_comments.json", review_comments)
        print(f"        Saved review_comments.json ({len(review_comments)} comments) -> {review_comments_path}")

        print("  [7/7] Writing sync metadata ...")
        news = build_news(previous, issues, pulls, issue_comments, pull_comments, review_comments, previous_synced_at)
        news_path = save_stage(repo, "news.json", news)
        print(f"        Saved news.json ({news['total']} updates) -> {news_path}")
        meta_path = save_stage(repo, "meta.json", {"synced_at": current_utc_timestamp()})
        print(f"        Saved meta.json -> {meta_path}")
        print(f"Fetch Data Done {repo.full_name}: {len(issues)} issues, {len(pulls)} pull requests -> {repo_path.parent}")
        
        print("-" * 80)

def load_previous_bundle(repo: Repository) -> Dict[str, Any]:
    if not (repo_data_dir(repo) / "repo.json").exists():
        return {}
    try:
        return load_bundle(repo)
    except FileNotFoundError:
        return {}


def merge_items(existing: List[Dict[str, Any]], updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged = {int(item["number"]): item for item in existing}
    for item in updates:
        merged[int(item["number"])] = item
    return sorted(merged.values(), key=lambda item: item.get("number", 0), reverse=True)


def merge_review_comments(existing: List[Dict[str, Any]], updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged = {str(comment.get("id")): comment for comment in existing if comment.get("id") is not None}
    for comment in updates:
        if comment.get("id") is not None:
            merged[str(comment["id"])] = comment
    return sorted(merged.values(), key=lambda comment: comment.get("created_at", ""), reverse=True)


def build_news(
    previous: Dict[str, Any],
    issues: List[Dict[str, Any]],
    pulls: List[Dict[str, Any]],
    issue_comments: Dict[str, List[Any]],
    pull_comments: Dict[str, List[Any]],
    review_comments: List[Dict[str, Any]],
    since: Optional[str],
) -> Dict[str, Any]:
    previous = previous or {}
    old_issues = by_number(previous.get("issues", []))
    old_pulls = by_number(previous.get("pulls", []))
    new_issue_numbers = [item["number"] for item in issues if int(item["number"]) not in old_issues]
    new_pull_numbers = [item["number"] for item in pulls if int(item["number"]) not in old_pulls]
    if not previous:
        issue_status_changes: List[Dict[str, Any]] = []
        pull_status_changes: List[Dict[str, Any]] = []
        new_issue_comments: List[Dict[str, Any]] = []
        new_pull_comments: List[Dict[str, Any]] = []
        new_reviews: List[Dict[str, Any]] = []
    else:
        issue_status_changes = status_changes(old_issues, issues, "issue")
        pull_status_changes = status_changes(old_pulls, pulls, "pull")
        new_issue_comments = [
            item
            for item in new_comments(previous.get("issue_comments", {}), issue_comments, "issue")
            if item["number"] not in new_issue_numbers
        ]
        new_pull_comments = [
            item
            for item in new_comments(previous.get("pull_comments", {}), pull_comments, "pull")
            if item["number"] not in new_pull_numbers
        ]
        new_reviews = [
            item
            for item in new_review_comments(previous.get("review_comments", []), review_comments)
            if item["number"] not in new_pull_numbers
        ]
    total = (
        len(new_issue_numbers)
        + len(new_pull_numbers)
        + len(issue_status_changes)
        + len(pull_status_changes)
        + len(new_issue_comments)
        + len(new_pull_comments)
        + len(new_reviews)
    )
    return {
        "since": since,
        "new_issue_numbers": new_issue_numbers,
        "new_pull_numbers": new_pull_numbers,
        "issue_status_changes": issue_status_changes,
        "pull_status_changes": pull_status_changes,
        "new_issue_comments": new_issue_comments,
        "new_pull_comments": new_pull_comments,
        "new_review_comments": new_reviews,
        "total": total,
    }


def by_number(items: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    return {int(item["number"]): item for item in items}


def status_changes(old_items: Dict[int, Dict[str, Any]], new_items: List[Dict[str, Any]], kind: str) -> List[Dict[str, Any]]:
    changes = []
    for item in new_items:
        number = int(item["number"])
        old = old_items.get(number)
        if not old:
            continue
        if old.get("state") != item.get("state") or old.get("merged_at") != item.get("merged_at"):
            changes.append(
                {
                    "kind": kind,
                    "number": number,
                    "title": item.get("title"),
                    "from": "merged" if old.get("merged_at") else old.get("state"),
                    "to": "merged" if item.get("merged_at") else item.get("state"),
                    "updated_at": item.get("updated_at"),
                }
            )
    return changes


def new_comments(old_comments: Dict[str, List[Any]], current_comments: Dict[str, List[Any]], kind: str) -> List[Dict[str, Any]]:
    changes = []
    for number, comments in current_comments.items():
        old_ids = {comment.get("id") for comment in old_comments.get(str(number), [])}
        for comment in comments:
            if comment.get("id") not in old_ids:
                changes.append(
                    {
                        "kind": kind,
                        "number": int(number),
                        "comment_id": comment.get("id"),
                        "user": comment.get("user"),
                        "body": comment.get("body"),
                        "created_at": comment.get("created_at"),
                    }
                )
    return sorted(changes, key=lambda item: item.get("created_at") or "", reverse=True)


def new_review_comments(old_comments: List[Dict[str, Any]], current_comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    old_ids = {comment.get("id") for comment in old_comments}
    changes = []
    for comment in current_comments:
        if comment.get("id") in old_ids:
            continue
        pull_url = comment.get("pull_request_url", "")
        changes.append(
            {
                "kind": "pull",
                "number": int(pull_url.rstrip("/").split("/")[-1]) if pull_url else 0,
                "comment_id": comment.get("id"),
                "user": comment.get("user"),
                "body": comment.get("body"),
                "path": comment.get("path"),
                "created_at": comment.get("created_at"),
            }
        )
    return sorted(changes, key=lambda item: item.get("created_at") or "", reverse=True)


def current_utc_timestamp() -> str:
    from time import gmtime, strftime

    return strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())


def item_progress(label: str, unit: str):
    def report(index: int, total: int, count: int) -> None:
        if total == 0:
            return
        if index == 1 or index == total or index % 10 == 0:
            print(f"        {label}: {index}/{total} items processed, latest item has {count} {unit}")

    return report


if __name__ == "__main__":
    sys.exit(main())
