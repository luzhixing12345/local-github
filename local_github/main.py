from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .generator import build_site
from .github_api import GitHubClient, Repository, read_token
from .storage import discover_repositories, load_bundle, repo_data_dir, save_stage


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_args(argv)
    repos = [Repository.parse(value) for value in args.repositories]

    if args.command in ("sync", "all"):
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
    commands = {"sync", "build", "all", "-h", "--help"}
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

    sync_parser = subparsers.add_parser("sync", help="Fetch repository data into data/github.")
    sync_parser.add_argument("repositories", nargs="+", help="Repository names such as owner/repo.")

    build_parser = subparsers.add_parser("build", help="Generate docs/ from local data.")
    build_parser.add_argument("repositories", nargs="*", help="Optional repository names to build.")

    all_parser = subparsers.add_parser("all", help="Fetch data and generate docs/.")
    all_parser.add_argument("repositories", nargs="+", help="Repository names such as owner/repo.")

    parsed = parser.parse_args(raw_args)
    if parsed.command is None:
        parser.print_help()
        raise SystemExit(2)
    elif not hasattr(parsed, "repositories"):
        parsed.repositories = []
    return parsed


def sync_repositories(repos: List[Repository]) -> None:
    token = read_token()
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

        print("  [1/8] Fetching repository metadata ...")
        repository = client.fetch_repository(repo)
        repo_path = save_stage(repo, "repo.json", repository)
        print(f"        Saved repo.json -> {repo_path}")

        print("  [2/8] Fetching issues ...")
        fetched_issues = client.fetch_issue_events(repo, since=previous_synced_at, include_pulls=False) if incremental else client.fetch_issues(repo)
        issues = merge_items(previous.get("issues", []) if previous else [], fetched_issues)
        issues_path = save_stage(repo, "issues.json", issues)
        print(f"        Saved issues.json ({len(issues)} total, {len(fetched_issues)} fetched) -> {issues_path}")

        print("  [3/8] Fetching pull requests ...")
        if incremental:
            updated_pull_refs = client.fetch_issue_events(repo, since=previous_synced_at, include_pulls=True)
            fetched_pulls = [client.fetch_pull(repo, int(item["number"])) for item in updated_pull_refs]
        else:
            fetched_pulls = client.fetch_pulls(repo)
        pulls = merge_items(previous.get("pulls", []) if previous else [], fetched_pulls)
        pulls_path = save_stage(repo, "pulls.json", pulls)
        print(f"        Saved pulls.json ({len(pulls)} total, {len(fetched_pulls)} fetched) -> {pulls_path}")

        print("  [4/8] Fetching issue comments ...")
        issue_comments = dict(previous.get("issue_comments", {}) if previous else {})
        issue_comments.update(
            client.fetch_issue_comments(repo, fetched_issues, progress=item_progress("issues", "comments"))
        )
        issue_comments_path = save_stage(repo, "issue_comments.json", issue_comments)
        print(
            f"        Saved issue_comments.json ({sum(len(value) for value in issue_comments.values())} comments)"
            f" -> {issue_comments_path}"
        )

        print("  [5/8] Fetching pull request conversation comments ...")
        pull_comments = dict(previous.get("pull_comments", {}) if previous else {})
        pull_comments.update(
            client.fetch_issue_comments(repo, fetched_pulls, progress=item_progress("pull requests", "comments"))
        )
        pull_comments_path = save_stage(repo, "pull_comments.json", pull_comments)
        print(
            f"        Saved pull_comments.json ({sum(len(value) for value in pull_comments.values())} comments)"
            f" -> {pull_comments_path}"
        )

        print("  [6/8] Fetching pull request review comments ...")
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

        print("  [7/8] Fetching pull request changed files ...")
        pull_files = dict(previous.get("pull_files", {}) if previous else {})
        file_targets = unique_items_by_number(
            list(fetched_pulls) + pulls_missing_files(pulls, pull_files)
        )
        if len(file_targets) != len(fetched_pulls):
            print(
                f"        {len(file_targets) - len(fetched_pulls)} historical pull requests are missing files; "
                "fetching them now."
            )
        pull_files.update(client.fetch_pull_files(repo, file_targets, progress=item_progress("pull requests", "files")))
        pull_files_path = save_stage(repo, "pull_files.json", pull_files)
        print(f"        Saved pull_files.json ({sum(len(value) for value in pull_files.values())} files) -> {pull_files_path}")

        print("  [8/8] Writing sync metadata ...")
        news = build_news(previous, issues, pulls, issue_comments, pull_comments, review_comments, previous_synced_at)
        news_path = save_stage(repo, "news.json", news)
        print(f"        Saved news.json ({news['total']} updates) -> {news_path}")
        meta_path = save_stage(repo, "meta.json", {"synced_at": current_utc_timestamp()})
        print(f"        Saved meta.json -> {meta_path}")
        print(f"Fetch Data Done {repo.full_name}: {len(issues)} issues, {len(pulls)} pull requests -> {repo_path.parent}")
        
        print("-" * 80)
        print("Run `local-github build` to generate static HTML from the fetched data.")
        

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


def pulls_missing_files(pulls: List[Dict[str, Any]], pull_files: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
    return [pull for pull in pulls if str(pull.get("number")) not in pull_files]


def unique_items_by_number(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    unique: Dict[int, Dict[str, Any]] = {}
    for item in items:
        unique[int(item["number"])] = item
    return sorted(unique.values(), key=lambda item: item.get("number", 0), reverse=True)


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
