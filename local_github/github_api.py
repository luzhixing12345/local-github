"""Small GitHub REST API client used by the static exporter."""

from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional


API_ROOT = "https://api.github.com"
TOKEN_HELP = """未找到 GitHub API Token（当前目录下的 .github-token）。

请按以下步骤创建并保存 Token：
  1. 打开 https://github.com/settings/tokens/new
  2. 创建 Personal Access Token（公开仓库无需额外权限；
     私有仓库需要授予对应的仓库读取权限）。
  3. 仅将 Token 值写入文件：
       printf '%s\\n' 'YOUR_TOKEN' > .github-token
       chmod 600 .github-token

请勿将 .github-token 提交到版本控制。"""


@dataclass(frozen=True)
class Repository:
    owner: str
    name: str

    @classmethod
    def parse(cls, value: str) -> "Repository":
        normalized = value.strip()
        prefix = "https://github.com/"
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix) :]
        normalized = normalized.strip("/")
        parts = normalized.split("/")
        if len(parts) < 2 or not parts[0] or not parts[1]:
            raise ValueError(f"Invalid repository: {value!r}. Expected owner/repo.")
        return cls(parts[0], parts[1])

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.name}"


class GitHubError(RuntimeError):
    pass


class GitHubClient:
    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token
        self.ssl_context = self._ssl_context()

    def get_json(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = self._url(path, params)
        req = urllib.request.Request(url, headers=self._headers())
        try:
            with urllib.request.urlopen(req, timeout=30, context=self.ssl_context) as response:
                payload = response.read().decode("utf-8")
                return json.loads(payload) if payload else None
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GitHubError(f"GitHub API error {exc.code} for {path}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise GitHubError(f"GitHub API request failed for {path}: {exc.reason}") from exc

    def get_paginated(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        *,
        max_pages: Optional[int] = None,
    ) -> List[Any]:
        results: List[Any] = []
        page = 1
        while True:
            query = {"per_page": 100, "page": page}
            if params:
                query.update(params)
            chunk = self.get_json(path, query)
            if not chunk:
                break
            if not isinstance(chunk, list):
                raise GitHubError(f"Expected paginated list for {path}, got {type(chunk).__name__}")
            results.extend(chunk)
            if len(chunk) < 100:
                break
            page += 1
            if max_pages is not None and page > max_pages:
                break
            time.sleep(0.1)
        return results

    def fetch_repository_bundle(self, repo: Repository) -> Dict[str, Any]:
        repo_json = self.fetch_repository(repo)
        issues = self.fetch_issues(repo)
        pulls = self.fetch_pulls(repo)
        issue_comments = self.fetch_issue_comments(repo, issues)
        pull_comments = self.fetch_issue_comments(repo, pulls)
        review_comments = self.fetch_review_comments(repo)

        return {
            "repository": repo_json,
            "issues": issues,
            "pulls": pulls,
            "issue_comments": issue_comments,
            "pull_comments": pull_comments,
            "review_comments": review_comments,
            "pull_files": {},
            "synced_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    def fetch_repository(self, repo: Repository) -> Dict[str, Any]:
        return self.get_json(f"/repos/{repo.full_name}")

    def fetch_issues(self, repo: Repository) -> List[Dict[str, Any]]:
        return self.fetch_issue_events(repo, include_pulls=False)

    def fetch_issue_events(
        self,
        repo: Repository,
        *,
        since: Optional[str] = None,
        include_pulls: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        params = {"state": "all", "sort": "updated", "direction": "desc"}
        if since:
            params["since"] = since
        all_issues = self.get_paginated(
            f"/repos/{repo.full_name}/issues",
            params,
        )
        if include_pulls is True:
            return [item for item in all_issues if "pull_request" in item]
        if include_pulls is False:
            return [item for item in all_issues if "pull_request" not in item]
        return all_issues

    def fetch_pulls(self, repo: Repository) -> List[Dict[str, Any]]:
        return self.get_paginated(
            f"/repos/{repo.full_name}/pulls",
            {"state": "all", "sort": "updated", "direction": "desc"},
        )

    def fetch_pull(self, repo: Repository, number: int) -> Dict[str, Any]:
        return self.get_json(f"/repos/{repo.full_name}/pulls/{number}")

    def fetch_review_comments(self, repo: Repository) -> List[Dict[str, Any]]:
        return self.get_paginated(
            f"/repos/{repo.full_name}/pulls/comments",
            {"sort": "updated", "direction": "desc"},
        )

    def fetch_pull_review_comments(self, repo: Repository, number: int) -> List[Dict[str, Any]]:
        return self.get_paginated(f"/repos/{repo.full_name}/pulls/{number}/comments")

    def fetch_pull_files_for_pull(self, repo: Repository, number: int) -> List[Dict[str, Any]]:
        return self.get_paginated(f"/repos/{repo.full_name}/pulls/{number}/files")

    def fetch_pull_files(
        self,
        repo: Repository,
        pulls: Iterable[Dict[str, Any]],
        progress: Optional[Callable[[int, int, int], None]] = None,
    ) -> Dict[str, List[Any]]:
        pull_list = list(pulls)
        files: Dict[str, List[Any]] = {}
        total = len(pull_list)
        for index, pull in enumerate(pull_list, start=1):
            number = str(pull["number"])
            files[number] = self.fetch_pull_files_for_pull(repo, int(number))
            if progress:
                progress(index, total, len(files[number]))
        return files

    def fetch_issue_comments(
        self,
        repo: Repository,
        items: Iterable[Dict[str, Any]],
        progress: Optional[Callable[[int, int, int], None]] = None,
    ) -> Dict[str, List[Any]]:
        item_list = list(items)
        comments: Dict[str, List[Any]] = {}
        total = len(item_list)
        for index, item in enumerate(item_list, start=1):
            number = str(item["number"])
            comments[number] = self.get_paginated(f"/repos/{repo.full_name}/issues/{number}/comments")
            if progress:
                progress(index, total, len(comments[number]))
        return comments

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "local-github",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    @staticmethod
    def _url(path: str, params: Optional[Dict[str, Any]]) -> str:
        url = f"{API_ROOT}{path}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        return url

    @staticmethod
    def _ssl_context() -> ssl.SSLContext:
        try:
            import certifi  # type: ignore

            return ssl.create_default_context(cafile=certifi.where())
        except Exception:
            return ssl.create_default_context()


def read_token(path: str = ".github-token") -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            token = handle.read().strip()
            return token or None
    except FileNotFoundError:
        return None


def require_token(path: str = ".github-token") -> str:
    token = read_token(path)
    if token is None:
        raise GitHubError(TOKEN_HELP)
    return token
