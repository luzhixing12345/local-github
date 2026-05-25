"""Local JSON storage for fetched GitHub data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .github_api import Repository


DATA_ROOT = Path("data/github")


def repo_data_dir(repo: Repository, data_root: Path = DATA_ROOT) -> Path:
    return data_root / repo.owner / repo.name


def save_bundle(repo: Repository, bundle: Dict[str, Any], data_root: Path = DATA_ROOT) -> Path:
    target = repo_data_dir(repo, data_root)
    target.mkdir(parents=True, exist_ok=True)
    files = {
        "repo.json": bundle["repository"],
        "issues.json": bundle["issues"],
        "pulls.json": bundle["pulls"],
        "issue_comments.json": bundle["issue_comments"],
        "pull_comments.json": bundle["pull_comments"],
        "review_comments.json": bundle["review_comments"],
        "meta.json": {"synced_at": bundle["synced_at"]},
    }
    for name, payload in files.items():
        write_json(target / name, payload)
    return target


def save_stage(repo: Repository, filename: str, payload: Any, data_root: Path = DATA_ROOT) -> Path:
    target = repo_data_dir(repo, data_root)
    target.mkdir(parents=True, exist_ok=True)
    path = target / filename
    write_json(path, payload)
    return path


def load_bundle(repo: Repository, data_root: Path = DATA_ROOT) -> Dict[str, Any]:
    source = repo_data_dir(repo, data_root)
    return {
        "repository": read_json(source / "repo.json"),
        "issues": read_json(source / "issues.json"),
        "pulls": read_json(source / "pulls.json"),
        "issue_comments": read_json(source / "issue_comments.json"),
        "pull_comments": read_json(source / "pull_comments.json"),
        "review_comments": read_json(source / "review_comments.json"),
        "meta": read_json(source / "meta.json"),
    }


def discover_repositories(data_root: Path = DATA_ROOT) -> List[Repository]:
    repos: List[Repository] = []
    if not data_root.exists():
        return repos
    for owner_dir in sorted(path for path in data_root.iterdir() if path.is_dir()):
        for repo_dir in sorted(path for path in owner_dir.iterdir() if path.is_dir()):
            if (repo_dir / "repo.json").exists():
                repos.append(Repository(owner_dir.name, repo_dir.name))
    return repos


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))
