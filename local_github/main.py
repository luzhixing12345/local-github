from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List, Optional

from .generator import build_site
from .github_api import GitHubClient, Repository, read_token
from .storage import discover_repositories, save_stage


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
        print(f"Syncing {repo.full_name} ...")
        print("  [1/7] Fetching repository metadata ...")
        repository = client.fetch_repository(repo)
        repo_path = save_stage(repo, "repo.json", repository)
        print(f"        Saved repo.json -> {repo_path}")

        print("  [2/7] Fetching issues ...")
        issues = client.fetch_issues(repo)
        issues_path = save_stage(repo, "issues.json", issues)
        print(f"        Saved issues.json ({len(issues)} issues) -> {issues_path}")

        print("  [3/7] Fetching pull requests ...")
        pulls = client.fetch_pulls(repo)
        pulls_path = save_stage(repo, "pulls.json", pulls)
        print(f"        Saved pulls.json ({len(pulls)} pull requests) -> {pulls_path}")

        print("  [4/7] Fetching issue comments ...")
        issue_comments = client.fetch_issue_comments(repo, issues, progress=comment_progress("issues"))
        issue_comments_path = save_stage(repo, "issue_comments.json", issue_comments)
        print(
            f"        Saved issue_comments.json ({sum(len(value) for value in issue_comments.values())} comments)"
            f" -> {issue_comments_path}"
        )

        print("  [5/7] Fetching pull request conversation comments ...")
        pull_comments = client.fetch_issue_comments(repo, pulls, progress=comment_progress("pull requests"))
        pull_comments_path = save_stage(repo, "pull_comments.json", pull_comments)
        print(
            f"        Saved pull_comments.json ({sum(len(value) for value in pull_comments.values())} comments)"
            f" -> {pull_comments_path}"
        )

        print("  [6/7] Fetching pull request review comments ...")
        review_comments = client.fetch_review_comments(repo)
        review_comments_path = save_stage(repo, "review_comments.json", review_comments)
        print(f"        Saved review_comments.json ({len(review_comments)} comments) -> {review_comments_path}")

        print("  [7/7] Writing sync metadata ...")
        meta_path = save_stage(repo, "meta.json", {"synced_at": current_utc_timestamp()})
        print(f"        Saved meta.json -> {meta_path}")
        print(f"Fetch Data Done {repo.full_name}: {len(issues)} issues, {len(pulls)} pull requests -> {repo_path.parent}")
        
        print("-" * 80)
        print("Run `local-github build` to generate static HTML from the fetched data.")
        


def current_utc_timestamp() -> str:
    from time import gmtime, strftime

    return strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())


def comment_progress(label: str):
    def report(index: int, total: int, count: int) -> None:
        if total == 0:
            return
        if index == 1 or index == total or index % 10 == 0:
            print(f"        Comments for {label}: {index}/{total} items processed")

    return report


if __name__ == "__main__":
    sys.exit(main())
