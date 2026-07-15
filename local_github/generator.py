"""Generate static HTML shells and data shards from local GitHub JSON data."""

from __future__ import annotations

import hashlib
import html
import json
import shutil
import urllib.parse
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .github_api import Repository
from .storage import load_bundle, repo_data_dir


DOCS_ROOT = Path("docs")
ASSETS_ROOT = Path(__file__).resolve().parent / "assets"
PAGE_SIZE = 100
DETAIL_GROUP_SIZE = 50
GITHUB_MARK_PATH = "M12.026 2c-5.509 0-9.974 4.465-9.974 9.974 0 4.406 2.857 8.145 6.821 9.465.499.09.679-.217.679-.481 0-.237-.008-.865-.011-1.696-2.775.602-3.361-1.338-3.361-1.338-.452-1.152-1.107-1.459-1.107-1.459-.905-.619.069-.605.069-.605 1.002.07 1.527 1.028 1.527 1.028.89 1.524 2.336 1.084 2.902.829.091-.645.351-1.085.635-1.334-2.214-.251-4.542-1.107-4.542-4.93 0-1.087.389-1.979 1.024-2.675-.101-.253-.446-1.268.099-2.64 0 0 .837-.269 2.742 1.021a9.582 9.582 0 0 1 2.496-.336 9.554 9.554 0 0 1 2.496.336c1.906-1.291 2.742-1.021 2.742-1.021.545 1.372.203 2.387.099 2.64.64.696 1.024 1.587 1.024 2.675 0 3.833-2.33 4.675-4.552 4.922.355.308.675.916.675 1.846 0 1.334-.012 2.41-.012 2.737 0 .267.178.577.687.479C19.146 20.115 22 16.379 22 11.974 22 6.465 17.535 2 12.026 2z"
GITHUB_FAVICON = "data:image/svg+xml," + urllib.parse.quote(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="{GITHUB_MARK_PATH}"/></svg>',
    safe="",
)


def build_site(repos: Iterable[Repository], docs_root: Path = DOCS_ROOT) -> None:
    docs_root.mkdir(parents=True, exist_ok=True)
    copy_assets(docs_root)

    loaded = [(repo, load_bundle(repo)) for repo in repos]
    write_page(docs_root / "index.html", render_index(loaded))

    for repo, bundle in loaded:
        repo_root = docs_root / "repos" / repo.owner / repo.name
        if repo_root.exists():
            shutil.rmtree(repo_root)
        repo_root.mkdir(parents=True, exist_ok=True)
        write_repo_data(repo_data_dir(repo), bundle)
        write_page(repo_root / "issues.html", render_collection_shell(repo, bundle, "issues"))
        write_page(repo_root / "pulls.html", render_collection_shell(repo, bundle, "pulls"))
        write_page(repo_root / "news.html", render_news_shell(repo, bundle))


def copy_assets(docs_root: Path) -> None:
    for name in ("css", "js"):
        source = ASSETS_ROOT / name
        target = docs_root / name
        if target.exists():
            shutil.rmtree(target)
        if source.exists():
            shutil.copytree(source, target)


def write_repo_data(data_root: Path, bundle: Dict[str, Any]) -> None:
    data_root.mkdir(parents=True, exist_ok=True)
    cleanup_web_data(data_root)
    manifest = {
        "repository": compact_repository(bundle["repository"]),
        "issues": collection_manifest(sorted_by_number(bundle["issues"]), "issue"),
        "pulls": collection_manifest(sorted_by_number(bundle["pulls"]), "pull"),
        "news": {"total": bundle.get("news", {}).get("total", 0)},
        "detail_group_size": DETAIL_GROUP_SIZE,
        "detail_pages": {
            "issue": detail_page_index(sorted_by_number(bundle["issues"])),
            "pull": detail_page_index(sorted_by_number(bundle["pulls"])),
        },
        "meta": bundle.get("meta", {}),
    }
    write_json(data_root / "web_manifest.json", manifest)

    for kind, singular in (("issues", "issue"), ("pulls", "pull")):
        items = sorted_by_number(bundle[kind])
        summaries = [summary_item(item, singular, bundle) for item in items]
        write_json(data_root / f"{kind}_basic.json", {"items": summaries})

    for index, issues in enumerate(chunks(sorted_by_number(bundle["issues"]), DETAIL_GROUP_SIZE), start=1):
        write_json(
            data_root / f"issue_details_{index}.json",
            {"items": [detail_item(issue, bundle, "issue") for issue in issues]},
        )

    for index, pulls in enumerate(chunks(sorted_by_number(bundle["pulls"]), DETAIL_GROUP_SIZE), start=1):
        write_json(
            data_root / f"pull_details_{index}.json",
            {"items": [detail_item(pull, bundle, "pull") for pull in pulls]},
        )


def cleanup_web_data(data_root: Path) -> None:
    patterns = (
        "web_manifest.json",
        "issues_basic.json",
        "pulls_basic.json",
        "issue_details_*.json",
        "pull_details_*.json",
    )
    for pattern in patterns:
        for path in data_root.glob(pattern):
            path.unlink()


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def detail_page_index(items: List[Dict[str, Any]]) -> Dict[str, int]:
    return {
        str(item["number"]): index // DETAIL_GROUP_SIZE + 1
        for index, item in enumerate(items)
    }


def detail_item(item: Dict[str, Any], bundle: Dict[str, Any], kind: str) -> Dict[str, Any]:
    number = str(item["number"])
    comments_key = "pull_comments" if kind == "pull" else "issue_comments"
    review_comments: List[Dict[str, Any]] = []
    if kind == "pull":
        review_comments = [
            comment
            for comment in bundle.get("review_comments", [])
            if comment.get("pull_request_url", "").endswith(f"/{number}")
        ]
    return {
        "item": item,
        "comments": bundle.get(comments_key, {}).get(number, []),
        "review_comments": review_comments,
        "files": [],
    }


def collection_manifest(items: List[Dict[str, Any]], singular: str) -> Dict[str, Any]:
    open_count = sum(1 for item in items if item.get("state") == "open")
    merged_count = sum(1 for item in items if singular == "pull" and item.get("merged_at"))
    return {
        "total": len(items),
        "open": open_count,
        "closed": len(items) - open_count,
        "merged": merged_count,
        "page_size": PAGE_SIZE,
        "pages": {
            "all": page_count(len(items)),
            "open": page_count(open_count),
            "closed": page_count(len(items) - open_count),
        },
    }


def page_count(total: int) -> int:
    return max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)


def sorted_by_number(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(items, key=lambda item: item.get("number", 0), reverse=True)


def by_number(items: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    return {int(item["number"]): item for item in items}


def compact_repository(repository: Dict[str, Any]) -> Dict[str, Any]:
    keys = (
        "full_name",
        "description",
        "html_url",
        "visibility",
        "stargazers_count",
        "forks_count",
        "open_issues_count",
        "default_branch",
    )
    return {key: repository.get(key) for key in keys}


def summary_item(item: Dict[str, Any], kind: str, bundle: Dict[str, Any]) -> Dict[str, Any]:
    news = bundle.get("news", {})
    new_numbers_key = "new_pull_numbers" if kind == "pull" else "new_issue_numbers"
    return {
        "kind": kind,
        "number": item.get("number"),
        "title": item.get("title"),
        "state": item.get("state"),
        "merged_at": item.get("merged_at"),
        "draft": item.get("draft", False),
        "user": compact_user(item.get("user")),
        "assignees": [compact_user(user) for user in item.get("assignees", [])],
        "participant_logins": participant_logins(item, kind, bundle),
        "labels": [
            {"name": label.get("name"), "color": label.get("color")}
            for label in item.get("labels", [])
        ],
        "comments": comment_count(item, kind, bundle),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
        "is_new": item.get("number") in news.get(new_numbers_key, []),
    }


def comment_count(item: Dict[str, Any], kind: str, bundle: Dict[str, Any]) -> int:
    number = str(item.get("number"))
    issue_comment_total = len(bundle.get("pull_comments" if kind == "pull" else "issue_comments", {}).get(number, []))
    if kind != "pull":
        return issue_comment_total
    review_total = sum(
        1
        for comment in bundle.get("review_comments", [])
        if comment.get("pull_request_url", "").endswith(f"/{number}")
    )
    return issue_comment_total + review_total


def participant_logins(item: Dict[str, Any], kind: str, bundle: Dict[str, Any]) -> List[str]:
    number = str(item.get("number"))
    users = [item.get("user")] + list(item.get("assignees", []))
    users.extend(
        comment.get("user")
        for comment in bundle.get("pull_comments" if kind == "pull" else "issue_comments", {}).get(number, [])
    )
    if kind == "pull":
        users.extend(
            comment.get("user")
            for comment in bundle.get("review_comments", [])
            if comment.get("pull_request_url", "").endswith(f"/{number}")
        )
    return sorted(
        {
            str(user.get("login"))
            for user in users
            if user and user.get("login")
        },
        key=str.lower,
    )


def compact_user(user: Dict[str, Any]) -> Dict[str, Any]:
    user = user or {}
    return {
        "login": user.get("login", "ghost"),
        "html_url": user.get("html_url", "#"),
        "avatar_url": user.get("avatar_url", ""),
    }


def chunks(items: List[Any], size: int) -> Iterable[List[Any]]:
    if not items:
        return
    for start in range(0, len(items), size):
        yield items[start : start + size]


def write_page(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_index(items: List[Any]) -> str:
    rows = []
    for repo, bundle in items:
        repository = bundle["repository"]
        repo_path = f"repos/{repo.owner}/{repo.name}"
        rows.append(
            f"""
            <article class="repo-card">
              <div class="repo-card-header">
                {octicon("repo")}
                <a class="repo-name" href="{repo_path}/issues.html">{escape(repository.get("full_name", repo.full_name))}</a>
                <span class="visibility">{escape(repository.get("visibility", "public"))}</span>
              </div>
              <p class="repo-description">{escape(repository.get("description") or "No description provided.")}</p>
              <div class="repo-meta">
                <span>{octicon("star")} {repository.get("stargazers_count", 0)}</span>
                <span>{octicon("repo-forked")} {repository.get("forks_count", 0)}</span>
                <span>{octicon("issue-opened")} {len(bundle["issues"])} issues</span>
                <span>{octicon("git-pull-request")} {len(bundle["pulls"])} pull requests</span>
              </div>
              <div class="repo-actions">
                <a class="btn" href="{repo_path}/issues.html">Issues</a>
                <a class="btn" href="{repo_path}/pulls.html">Pull requests</a>
              </div>
            </article>
            """
        )
    body = f"""
      <main class="container">
        <div class="pagehead">
          <h1>local-github</h1>
          <p class="muted">Static GitHub issue and pull request browser.</p>
        </div>
        <section class="repo-grid">
          {''.join(rows) if rows else '<p class="muted">No repositories synced yet.</p>'}
        </section>
      </main>
    """
    return layout("Repositories", body, "")


def render_collection_shell(repo: Repository, bundle: Dict[str, Any], kind: str) -> str:
    repository = bundle["repository"]
    is_pull = kind == "pulls"
    title = "Pull requests" if is_pull else "Issues"
    active = "pulls" if is_pull else "issues"
    page_data = html.escape(
        json.dumps(
            {
                "kind": kind,
                "itemKind": "pull" if is_pull else "issue",
                "dataRoot": f"../../../../data/github/{repo.owner}/{repo.name}",
            }
        ),
        quote=True,
    )
    body = f"""
      {repo_header(repo, repository, active, bundle.get("news", {}).get("total", 0))}
      <main class="container app-shell" data-local-github-app="{page_data}">
        <section data-route-view="list">
          <div class="list-toolbar">
            <input class="filter-input" type="search" data-search-input aria-label="Search {'pull requests' if is_pull else 'issues'}">
            <a class="btn btn-primary" href="{escape(repository.get("html_url", "#"))}/{'pulls' if is_pull else 'issues'}" target="_blank" rel="noreferrer">New {'pull request' if is_pull else 'issue'}</a>
          </div>
          <section class="issue-box">
            <div class="issue-box-header">
              <button class="tab-button" type="button" data-state-filter="all">All <span data-count="total">0</span></button>
              <button class="tab-button active" type="button" data-state-filter="open">{octicon("issue-opened" if not is_pull else "git-pull-request")} Open <span data-count="open">0</span></button>
              <button class="tab-button" type="button" data-state-filter="closed">{octicon("check")} Closed <span data-count="closed">0</span></button>
              <div class="assignee-filter" data-assignee-filter>
                <button class="assignee-filter-trigger" type="button" data-assignee-trigger aria-haspopup="true" aria-expanded="false">
                  Assignee: <span data-assignee-label>All</span>
                </button>
                <div class="assignee-filter-menu" data-assignee-menu hidden>
                  <input class="assignee-filter-input" type="search" data-assignee-search placeholder="Search users" aria-label="Search assignees">
                  <div class="assignee-filter-options" data-assignee-options></div>
                </div>
              </div>
            </div>
            <div class="issue-list" data-list>
              <div class="empty-state">Loading...</div>
            </div>
            <div class="pager" data-pager></div>
          </section>
        </section>
        <section data-route-view="detail" hidden>
          <div data-detail>
            <div class="empty-state">Loading detail...</div>
          </div>
        </section>
      </main>
    """
    return layout(f"{repo.full_name} {title}", body, "../../../")


def render_news_shell(repo: Repository, bundle: Dict[str, Any]) -> str:
    news = bundle.get("news", {})
    repository = bundle["repository"]
    sections = [
        render_news_section("New issues", news_issue_rows(news.get("new_issue_numbers", []), bundle, "issue")),
        render_news_section("New pull requests", news_issue_rows(news.get("new_pull_numbers", []), bundle, "pull")),
        render_news_section("Status changes", status_change_rows(news.get("issue_status_changes", []) + news.get("pull_status_changes", []))),
        render_news_section("New comments", comment_news_rows(news.get("new_issue_comments", []) + news.get("new_pull_comments", []) + news.get("new_review_comments", []))),
    ]
    body_content = "".join(section for section in sections if section)
    body = f"""
      {repo_header(repo, repository, "news", news.get("total", 0))}
      <main class="container app-shell">
        <div class="news-head">
          <h1>News</h1>
          <p class="muted">Updates from the latest sync{news_since_text(news.get("since"))}.</p>
        </div>
        <section class="news-box">
          {body_content}
        </section>
      </main>
    """
    return layout(f"{repo.full_name} News", body, "../../../")


def render_news_section(title: str, rows: str) -> str:
    if not rows:
        return ""
    return f"""
      <section class="news-section">
        <h2>{escape(title)}</h2>
        <div class="news-list">{rows}</div>
      </section>
    """


def news_issue_rows(numbers: List[int], bundle: Dict[str, Any], kind: str) -> str:
    source = by_number(bundle["pulls" if kind == "pull" else "issues"])
    rows = []
    for number in numbers:
        item = source.get(int(number))
        if not item:
            continue
        page = "pulls.html" if kind == "pull" else "issues.html"
        status = static_status_for(item, kind)
        labels = "".join(
            f'<span class="label" style="background-color:#{escape(label.get("color", "d0d7de"))}">{escape(label.get("name", "label"))}</span>'
            for label in item.get("labels", [])
        )
        rows.append(
            f"""
            <article class="issue-row">
              <div class="issue-icon {status['class_name']}">{octicon(status['icon'])}</div>
              <div class="issue-main">
                <div class="issue-title-line">
                  <a class="issue-title" href="{page}#/{kind}/{number}">{escape(item.get("title", ""))}</a>
                  {labels}
                </div>
                <div class="issue-meta">#{number} {escape(status['label'].lower())} by {static_user_link(item.get("user"))} · updated {format_relative_time(item.get("updated_at"))}</div>
              </div>
              <div class="comment-count">{octicon("comment")} {comment_count(item, kind, bundle)}</div>
            </article>
            """
        )
    return "".join(rows)


def status_change_rows(changes: List[Dict[str, Any]]) -> str:
    rows = []
    for change in changes:
        page = "pulls.html" if change.get("kind") == "pull" else "issues.html"
        kind = escape(change.get("kind", "issue"))
        number = int(change.get("number", 0))
        rows.append(
            f"""
            <article class="news-row">
              <span class="news-kind">{kind}</span>
              <a class="issue-title" href="{page}#/{kind}/{number}">{escape(change.get("title", ""))}</a>
              <span class="muted">#{number} changed from {escape(change.get("from", ""))} to {escape(change.get("to", ""))}</span>
            </article>
            """
        )
    return "".join(rows)


def comment_news_rows(comments: List[Dict[str, Any]]) -> str:
    rows = []
    for comment in sorted(comments, key=lambda item: item.get("created_at") or "", reverse=True):
        kind = comment.get("kind", "issue")
        number = int(comment.get("number", 0))
        page = "pulls.html" if kind == "pull" else "issues.html"
        user = comment.get("user") or {}
        user_href = user_profile_url(user)
        user_login = escape(user.get("login", "ghost"))
        comment_id = comment.get("comment_id")
        comment_href = f"{page}#/{kind}/{number}/comment-{comment_id}" if comment_id else f"{page}#/{kind}/{number}"
        jump_icon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path fill="none" d="M15 3h6v6m-11 5L21 3m-3 10v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>'
        rows.append(
            f"""
            <article class="timeline-item news-comment-item">
              <a class="avatar-link" href="{escape(user_href)}" target="_blank" rel="noreferrer" aria-label="{user_login}">
                <img class="avatar" src="{escape(user.get("avatar_url", ""))}" alt="">
              </a>
              <div class="comment">
                <div class="comment-header">
                  <strong><a class="comment-author" href="{escape(user_href)}" target="_blank" rel="noreferrer">{user_login}</a></strong>
                  <span>commented on <a href="{page}#/{kind}/{number}">#{number}</a> {format_relative_time(comment.get("created_at"))}</span>
                  <a class="comment-jump-link" href="{comment_href}" aria-label="Open comment">{jump_icon}</a>
                </div>
                <div class="markdown-body">{escape(comment.get("body") or "")}</div>
              </div>
            </article>
            """
        )
    return "".join(rows)


def news_since_text(value: Any) -> str:
    if not value:
        return ""
    return f" since {format_datetime(value)}"


def format_date(value: Any) -> str:
    if not value:
        return "unknown"
    text = str(value)
    try:
        from datetime import datetime, timezone

        date = datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
        return f"on {date.strftime('%b')} {date.day}, {date.year}"
    except ValueError:
        return escape(text)


def format_datetime(value: Any) -> str:
    if not value:
        return "unknown"
    text = str(value)
    try:
        from datetime import datetime, timezone

        date = datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
        return f"on {date.strftime('%b')} {date.day}, {date.year} {date.strftime('%H:%M')} UTC"
    except ValueError:
        return escape(text)


def format_relative_time(value: Any) -> str:
    if not value:
        return "unknown"
    text = str(value)
    try:
        from datetime import datetime, timezone

        date = datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
        now = datetime.now(timezone.utc)
        diff_seconds = max(0, int((now - date).total_seconds()))
        minute = 60
        hour = 60 * minute
        day = 24 * hour

        if diff_seconds < minute:
            return "just now"
        if diff_seconds < hour:
            minutes = diff_seconds // minute
            return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
        if diff_seconds < day:
            hours = diff_seconds // hour
            return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
        if diff_seconds < 2 * day:
            return "yesterday"
        if diff_seconds < 7 * day:
            return f"{diff_seconds // day} days ago"
        if diff_seconds < 14 * day:
            return "last week"
        if diff_seconds < 30 * day:
            return f"{diff_seconds // day} days ago"
        return format_date(value)
    except ValueError:
        return escape(text)


def static_status_for(item: Dict[str, Any], kind: str) -> Dict[str, str]:
    if kind == "pull" and item.get("merged_at"):
        return {"class_name": "merged", "icon": "git-merge", "label": "Merged"}
    if item.get("state") == "closed":
        return {"class_name": "closed", "icon": "git-pull-request-closed" if kind == "pull" else "issue-closed", "label": "Closed"}
    return {"class_name": "open", "icon": "git-pull-request" if kind == "pull" else "issue-opened", "label": "Open"}


def static_user_link(user: Dict[str, Any]) -> str:
    user = user or {}
    return (
        f'<a class="user-link" href="{escape(user_profile_url(user))}" target="_blank" rel="noreferrer">'
        f'{escape(user.get("login", "ghost"))}</a>'
    )


def user_profile_url(user: Dict[str, Any]) -> str:
    if user.get("html_url"):
        return str(user["html_url"])
    if user.get("login") and user.get("login") != "ghost":
        return f"https://github.com/{user['login']}"
    return "https://github.com"


def repo_header(repo: Repository, repository: Dict[str, Any], active: str, news_total: int = 0) -> str:
    issues_active = "active" if active == "issues" else ""
    pulls_active = "active" if active == "pulls" else ""
    news_active = "active" if active == "news" else ""
    return f"""
      <header class="repo-header">
        <div class="container repo-title">
          <a class="github-home-link" href="../../../index.html" aria-label="local-github home">{octicon("repo")}</a>
          <span class="repo-full-name">
            <span class="repo-owner">{escape(repo.owner)}</span>
            <span class="repo-separator">/</span>
            <span class="repo-name-part">{escape(repo.name)}</span>
          </span>
          <span class="visibility">{escape(repository.get("visibility", "public"))}</span>
        </div>
        <nav class="container tabs">
          <a class="tab {issues_active}" href="issues.html">{octicon("issue-opened")} Issues</a>
          <a class="tab {pulls_active}" href="pulls.html">{octicon("git-pull-request")} Pull requests</a>
          <a class="tab {news_active}" href="news.html">{octicon("comment")} News <span class="tab-counter">{news_total}</span></a>
        </nav>
      </header>
    """


def layout(title: str, body: str, root_prefix: str) -> str:
    css = versioned_asset_url(root_prefix, "css/github.css")
    js = versioned_asset_url(root_prefix, "js/app.js")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <link rel="icon" type="image/svg+xml" href="{GITHUB_FAVICON}">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js/styles/github.min.css">
  <link rel="stylesheet" href="{css}">
</head>
<body>
  {body}
  <script src="https://cdn.jsdelivr.net/npm/dompurify/dist/purify.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/highlight.js/lib/common.min.js"></script>
  <script src="{js}"></script>
</body>
</html>
"""


def versioned_asset_url(root_prefix: str, relative_path: str) -> str:
    content = (ASSETS_ROOT / relative_path).read_bytes()
    version = hashlib.sha256(content).hexdigest()[:12]
    return f"{root_prefix}{relative_path}?v={version}"


def escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def octicon(name: str) -> str:
    if name == "repo":
        return (
            '<svg class="octicon octicon-mark-github" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">'
            f'<path d="{GITHUB_MARK_PATH}"></path>'
            "</svg>"
        )
    if name == "issue-closed":
        return (
            '<svg class="octicon octicon-issue-closed" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true">'
            '<circle cx="8" cy="8" r="6.75" fill="none" stroke="currentColor" stroke-width="1.5"></circle>'
            '<path fill="currentColor" d="M11.28 6.78a.75.75 0 0 0-1.06-1.06L7.25 8.69 5.78 7.22a.75.75 0 0 0-1.06 1.06l2 2a.75.75 0 0 0 1.06 0l3.5-3.5Z"></path>'
            "</svg>"
        )
    paths = {
        "star": "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.75.75 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z",
        "repo-forked": "M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z",
        "issue-opened": "M8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z M8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0Zm0 1.5a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13Z",
        "git-pull-request": "M1.5 3.25a2.25 2.25 0 1 1 3 2.122v5.256a2.25 2.25 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 1.5 3.25Zm9.5-.75h1.25A2.75 2.75 0 0 1 15 5.25v5.378a2.25 2.25 0 1 1-1.5 0V5.25c0-.69-.56-1.25-1.25-1.25H11v1.75a.25.25 0 0 1-.427.177L7.823 3.177a.25.25 0 0 1 0-.354l2.75-2.75A.25.25 0 0 1 11 .25V2.5Z",
        "git-pull-request-closed": "M3.25 1A2.25 2.25 0 0 1 4 5.372v5.256a2.251 2.251 0 1 1-1.5 0V5.372A2.251 2.251 0 0 1 3.25 1Zm9.5 5.5a.75.75 0 0 1 .75.75v3.378a2.251 2.251 0 1 1-1.5 0V7.25a.75.75 0 0 1 .75-.75Zm-2.03-5.273a.75.75 0 0 1 1.06 0l.97.97.97-.97a.748.748 0 0 1 1.265.332.75.75 0 0 1-.205.729l-.97.97.97.97a.751.751 0 0 1-.018 1.042.751.751 0 0 1-1.042.018l-.97-.97-.97.97a.749.749 0 0 1-1.275-.326.749.749 0 0 1 .215-.734l.97-.97-.97-.97a.75.75 0 0 1 0-1.06ZM2.5 3.25a.75.75 0 1 0 1.5 0 .75.75 0 0 0-1.5 0ZM3.25 12a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm9.5 0a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Z",
        "git-merge": "M5.45 5.154A4.25 4.25 0 0 0 9.25 7.5h1.378a2.251 2.251 0 1 1 0 1.5H9.25A5.734 5.734 0 0 1 5 7.123v3.505a2.25 2.25 0 1 1-1.5 0V5.372a2.25 2.25 0 1 1 1.95-.218ZM4.25 13.5a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm8.5-4.5a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM5 3.25a.75.75 0 1 0 0 .005V3.25Z",
        "check": "M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.75.75 0 1 1 1.06-1.06L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z",
        "comment": "M1.75 2.5h12.5a.25.25 0 0 1 .25.25v8.5a.25.25 0 0 1-.25.25H6.5a.75.75 0 0 0-.53.22L3.5 14.19v-1.94a.75.75 0 0 0-.75-.75h-1a.25.25 0 0 1-.25-.25v-8.5a.25.25 0 0 1 .25-.25ZM14.25 1H1.75A1.75 1.75 0 0 0 0 2.75v8.5C0 12.216.784 13 1.75 13H2v2.543a.457.457 0 0 0 .78.323L6.646 13h7.604A1.75 1.75 0 0 0 16 11.25v-8.5A1.75 1.75 0 0 0 14.25 1Z",
        "link": "M7.775 3.275a.75.75 0 0 0-1.06-1.06L3.19 5.74a3.75 3.75 0 0 0 0 5.303.75.75 0 0 0 1.06-1.061 2.25 2.25 0 0 1 0-3.182l3.525-3.525Zm.45 9.45a.75.75 0 0 0 1.06 1.06l3.525-3.525a3.75 3.75 0 0 0 0-5.303.75.75 0 1 0-1.06 1.061 2.25 2.25 0 0 1 0 3.182l-3.525 3.525Zm1.323-6.273a.75.75 0 0 0-1.06 0L5.95 8.99a.75.75 0 1 0 1.06 1.061l2.538-2.538a.75.75 0 0 0 0-1.06Z",
    }
    path = paths.get(name, paths["issue-opened"])
    return f'<svg class="octicon octicon-{name}" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="{path}"></path></svg>'
