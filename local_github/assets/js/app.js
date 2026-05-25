(function () {
  "use strict";

  const icons = {
    "issue-opened":
      "M8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z M8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0Zm0 1.5a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13Z",
    "issue-closed":
      "M11.28 6.78a.75.75 0 0 0-1.06-1.06L7.25 8.69 5.78 7.22a.75.75 0 0 0-1.06 1.06l2 2a.75.75 0 0 0 1.06 0l3.5-3.5Z M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0Z",
    "git-pull-request":
      "M1.5 3.25a2.25 2.25 0 1 1 3 2.122v5.256a2.25 2.25 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 1.5 3.25Zm9.5-.75h1.25A2.75 2.75 0 0 1 15 5.25v5.378a2.25 2.25 0 1 1-1.5 0V5.25c0-.69-.56-1.25-1.25-1.25H11v1.75a.25.25 0 0 1-.427.177L7.823 3.177a.25.25 0 0 1 0-.354l2.75-2.75A.25.25 0 0 1 11 .25V2.5Z",
    "git-merge":
      "M5 3.25a2.25 2.25 0 1 1-3 2.122v5.256a2.25 2.25 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 5 3.25Zm5.28 1.47a.75.75 0 0 0-1.06 1.06l1.97 1.97H9.75A4.75 4.75 0 0 0 5 12.5v.128a2.251 2.251 0 0 1 1.5 0V12.5a3.25 3.25 0 0 1 3.25-3.25h1.44l-1.97 1.97a.75.75 0 1 0 1.06 1.06l3.25-3.25a.75.75 0 0 0 0-1.06L10.28 4.72Z",
    comment:
      "M1.75 2.5h12.5a.25.25 0 0 1 .25.25v8.5a.25.25 0 0 1-.25.25H6.5a.75.75 0 0 0-.53.22L3.5 14.19v-1.94a.75.75 0 0 0-.75-.75h-1a.25.25 0 0 1-.25-.25v-8.5a.25.25 0 0 1 .25-.25ZM14.25 1H1.75A1.75 1.75 0 0 0 0 2.75v8.5C0 12.216.784 13 1.75 13H2v2.543a.457.457 0 0 0 .78.323L6.646 13h7.604A1.75 1.75 0 0 0 16 11.25v-8.5A1.75 1.75 0 0 0 14.25 1Z",
  };

  const copyIcon =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#9198a1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>';
  const copiedIcon =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#1a7f37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>';
  const copyRightOffset = 8;

  window.LocalGithubData = {
    shards: {},
    async load(name) {
      if (this.shards[name]) {
        return Promise.resolve(this.shards[name]);
      }
      const response = await fetch(`${window.LocalGithubData.root}/${name}.json`);
      if (!response.ok) {
        throw new Error(`Failed to load ${name}.json`);
      }
      const payload = await response.json();
      this.shards[name] = payload;
      return payload;
    },
    root: "",
  };

  document.documentElement.classList.add("js-enabled");

  const shell = document.querySelector("[data-local-github-app]");
  if (!shell) return;

  const config = JSON.parse(shell.dataset.localGithubApp);
  window.LocalGithubData.root = config.dataRoot;
  const state = { page: 1, filter: "open", manifest: null, basic: null, items: [] };
  const listView = shell.querySelector("[data-route-view='list']");
  const detailView = shell.querySelector("[data-route-view='detail']");
  const list = shell.querySelector("[data-list]");
  const detail = shell.querySelector("[data-detail]");
  const pager = shell.querySelector("[data-pager]");

  init().catch((error) => {
    list.innerHTML = `<div class="empty-state">${escapeHtml(error.message)}</div>`;
  });

  async function init() {
    state.manifest = await window.LocalGithubData.load("web_manifest");
    updateCounts();
    bindFilters();
    window.addEventListener("hashchange", route);
    await route();
  }

  async function route() {
    const selected = itemFromHash();
    if (selected) {
      showDetailView();
      await loadDetail(selected.kind, selected.number);
      return;
    }
    showListView();
    await loadPage(pageFromHash(), { updateHash: false });
  }

  function bindFilters() {
    shell.querySelectorAll("[data-state-filter]").forEach((button) => {
      button.addEventListener("click", async () => {
        shell.querySelectorAll("[data-state-filter]").forEach((item) => item.classList.remove("active"));
        button.classList.add("active");
        state.filter = button.dataset.stateFilter;
        await loadPage(1);
      });
    });
  }

  function updateCounts() {
    const counts = state.manifest[config.kind];
    shell.querySelector("[data-count='total']").textContent = counts.total;
    shell.querySelector("[data-count='open']").textContent = counts.open;
    shell.querySelector("[data-count='closed']").textContent = counts.closed;
  }

  async function loadPage(page, options = {}) {
    const info = state.manifest[config.kind];
    if (!state.basic) {
      const basic = await window.LocalGithubData.load(`${config.kind}_basic`);
      state.basic = basic.items || [];
    }
    const filtered = state.filter === "all"
      ? state.basic
      : state.basic.filter((item) => item.state === state.filter);
    const pages = Math.max(1, Math.ceil(filtered.length / info.page_size));
    state.page = Math.min(Math.max(page, 1), pages);
    list.innerHTML = '<div class="empty-state">Loading...</div>';
    const start = (state.page - 1) * info.page_size;
    state.items = filtered.slice(start, start + info.page_size);
    renderList();
    renderPager(pages);
    if (options.updateHash !== false) {
      history.replaceState(null, "", `#page-${state.page}`);
    }
  }

  function renderList() {
    const items = state.items;
    if (!items.length) {
      list.innerHTML = '<div class="empty-state">No items found.</div>';
      return;
    }
    list.innerHTML = items.map(renderRow).join("");
    list.querySelectorAll("[data-load-detail]").forEach((link) => {
      link.addEventListener("click", (event) => {
        event.preventDefault();
        const number = Number(link.dataset.number);
        location.hash = `#/${config.itemKind}/${number}`;
      });
    });
  }

  function renderRow(item) {
    const status = statusFor(item);
    const labels = (item.labels || [])
      .map((label) => `<span class="label" style="background-color:#${escapeAttr(label.color || "d0d7de")}">${escapeHtml(label.name || "label")}</span>`)
      .join("");
    return `
      <article class="issue-row">
        <div class="issue-icon ${status.className}">${octicon(status.icon)}</div>
        <div class="issue-main">
          <div class="issue-title-line">
            <a class="issue-title" href="#/${item.kind}/${item.number}" data-load-detail data-number="${item.number}">${escapeHtml(item.title || "")}</a>
            ${labels}
          </div>
          <div class="issue-meta">
            #${item.number} ${escapeHtml(status.label.toLowerCase())} by ${userLink(item.user)}
            · updated ${formatTime(item.updated_at)}
          </div>
        </div>
        <div class="comment-count">${octicon("comment")} ${item.comments || 0}</div>
      </article>
    `;
  }

  function renderPager(pages) {
    if (pages <= 1) {
      pager.innerHTML = "";
      pager.hidden = true;
      return;
    }
    pager.hidden = false;
    pager.innerHTML = `
      <button class="btn" type="button" data-page="${state.page - 1}" ${state.page <= 1 ? "disabled" : ""}>Previous</button>
      <span class="muted">Page ${state.page} of ${pages}</span>
      <button class="btn" type="button" data-page="${state.page + 1}" ${state.page >= pages ? "disabled" : ""}>Next</button>
    `;
    pager.querySelectorAll("[data-page]").forEach((button) => {
      button.addEventListener("click", () => loadPage(Number(button.dataset.page)));
    });
  }

  async function loadDetail(kind, number) {
    detail.innerHTML = '<div class="empty-state">Loading detail...</div>';
    const page = state.manifest.detail_pages[kind]?.[String(number)];
    if (!page) {
      detail.innerHTML = '<div class="empty-state">Detail data not found.</div>';
      return;
    }
    const shard = await window.LocalGithubData.load(`${kind}_details_${page}`);
    const item = (shard.items || []).find((entry) => entry.item && Number(entry.item.number) === Number(number));
    if (!item) {
      detail.innerHTML = '<div class="empty-state">Detail data not found.</div>';
      return;
    }
    detail.innerHTML = renderDetail(item, kind);
    enhanceMarkdown(detail);
    document.title = `${state.manifest.repository.full_name} #${number}`;
    window.scrollTo({ top: 0 });
  }

  function renderDetail(shard, kind) {
    const item = shard.item || {};
    const status = statusFor({ ...item, kind });
    const comments = shard.comments || [];
    const reviews = shard.review_comments || [];
    const labels = item.labels || [];
    const assignees = item.assignees || [];
    const milestone = item.milestone;
    const branchLine =
      kind === "pull"
        ? `<span class="branch-line"> wants to merge <strong>${escapeHtml(item.head?.ref || "")}</strong> into <strong>${escapeHtml(item.base?.ref || "")}</strong></span>`
        : "";
    const timeline = [renderTimelineItem(item, "opened this")]
      .concat(comments.map((comment) => renderTimelineItem(comment, "commented")))
      .join("");
    const reviewNote = reviews.length
      ? `<div class="timeline-note">${reviews.length} review comments saved locally. Full review rendering is planned for a later pass.</div>`
      : "";

    return `
      <div class="issue-info-head">
        <h1 class="issue-info-title">${escapeHtml(item.title || "")} <span class="muted">#${item.number || ""}</span></h1>
        <div class="issue-info-meta">
          <span class="state-badge ${status.className}">${octicon(status.icon)} ${status.label}</span>
          <span>${userLink(item.user)} opened ${formatTime(item.created_at)} · ${comments.length} comments${branchLine}</span>
        </div>
      </div>
      <div class="issue-info-layout">
        <section class="timeline">
          ${timeline}
          ${reviewNote}
        </section>
        <aside class="issue-sidebar">
          ${sidebarSection("Assignees", assignees.length ? assignees.map(renderSidebarUser).join("") : '<span class="muted">No one assigned</span>')}
          ${sidebarSection("Labels", labels.length ? labels.map(renderSidebarLabel).join("") : '<span class="muted">None yet</span>')}
          ${sidebarSection("Milestone", milestone ? escapeHtml(milestone.title || "") : '<span class="muted">No milestone</span>')}
          ${sidebarSection("Development", '<span class="muted">No branches or pull requests</span>')}
        </aside>
      </div>
    `;
  }

  function renderTimelineItem(item, action) {
    const user = item.user || {};
    return `
      <article class="timeline-item">
        <img class="avatar" src="${escapeAttr(user.avatar_url || "")}" alt="">
        <div class="comment">
          <div class="comment-header">
            <strong>${escapeHtml(user.login || "ghost")}</strong>
            <span>${escapeHtml(action)} ${formatTime(item.created_at)}</span>
          </div>
          <div class="markdown-body">${markdown(item.body || "") || '<p class="muted">No description provided.</p>'}</div>
        </div>
      </article>
    `;
  }

  function sidebarSection(title, body) {
    return `
      <section class="sidebar-section">
        <h2>${escapeHtml(title)}</h2>
        <div>${body}</div>
      </section>
    `;
  }

  function renderSidebarUser(user) {
    return `
      <a class="sidebar-user" href="${escapeAttr(user.html_url || "#")}" target="_blank" rel="noreferrer">
        <img class="sidebar-avatar" src="${escapeAttr(user.avatar_url || "")}" alt="">
        <span>${escapeHtml(user.login || "ghost")}</span>
      </a>
    `;
  }

  function renderSidebarLabel(label) {
    return `<span class="label sidebar-label" style="background-color:#${escapeAttr(label.color || "d0d7de")}">${escapeHtml(label.name || "label")}</span>`;
  }

  function statusFor(item) {
    if (item.kind === "pull" && item.merged_at) return { className: "merged", icon: "git-merge", label: "Merged" };
    if (item.state === "closed") return { className: "closed", icon: "issue-closed", label: "Closed" };
    return { className: "open", icon: item.kind === "pull" ? "git-pull-request" : "issue-opened", label: "Open" };
  }

  function markdown(text) {
    const value = String(text || "");
    if (!value.trim()) return "";

    if (window.marked && window.DOMPurify) {
      const raw = window.marked.parse(value, {
        breaks: false,
        gfm: true,
      });
      return enhanceReferences(
        window.DOMPurify.sanitize(raw, {
          ADD_ATTR: ["checked", "class", "disabled", "rel", "target"],
        })
      );
    }

    return enhanceReferences(
      escapeHtml(value)
        .split(/\n{2,}/)
        .map((block) => {
          const blockValue = block.trim();
          if (!blockValue) return "";
          if (blockValue.startsWith("## ")) return `<h2>${blockValue.slice(3)}</h2>`;
          if (blockValue.startsWith("# ")) return `<h1>${blockValue.slice(2)}</h1>`;
          return `<p>${linkify(blockValue).replace(/\n/g, "<br>")}</p>`;
        })
        .join("")
    );
  }

  function linkify(text) {
    return text.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noreferrer">$1</a>');
  }

  function enhanceMarkdown(root) {
    root.querySelectorAll(".markdown-body a[href]").forEach((anchor) => {
      const href = anchor.getAttribute("href") || "";
      if (/^https?:\/\//i.test(href)) {
        anchor.setAttribute("target", "_blank");
        anchor.setAttribute("rel", "noreferrer");
      }
    });
    if (window.hljs) {
      root.querySelectorAll(".markdown-body pre code").forEach((block) => {
        window.hljs.highlightElement(block);
      });
    }
    installCodeCopy(root);
    installImageLinks(root);
  }

  function installImageLinks(root) {
    root.querySelectorAll(".markdown-body img").forEach((image) => {
      if (image.dataset.imageLinkBound === "true") return;
      image.dataset.imageLinkBound = "true";
      image.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        openImageUrl(image.currentSrc || image.src);
      });
    });
    root.querySelectorAll(".markdown-body a").forEach((anchor) => {
      const image = anchor.querySelector("img");
      if (!image || anchor.dataset.imageLinkBound === "true") return;
      anchor.dataset.imageLinkBound = "true";
      anchor.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        openImageUrl(image.currentSrc || image.src || anchor.href);
      });
    });
  }

  function openImageUrl(src) {
    if (!src) return;
    window.open(src, "_blank", "noopener,noreferrer");
  }

  function installCodeCopy(root) {
    root.querySelectorAll(".markdown-body pre").forEach((block) => {
      if (block.dataset.copyBound === "true") return;
      block.dataset.copyBound = "true";
      block.addEventListener("mouseenter", () => addCodeCopyButton(block));
      block.addEventListener("mouseleave", () => removeCodeCopyButton(block));
      block.addEventListener("scroll", () => updateCodeCopyButtonPosition(block));
    });
  }

  function addCodeCopyButton(block) {
    if (block.querySelector(".code-copy-button")) return;
    const button = document.createElement("button");
    button.className = "code-copy-button";
    button.type = "button";
    button.setAttribute("aria-label", "Copy code");
    button.innerHTML = copyIcon;
    button.addEventListener("click", async (event) => {
      event.preventDefault();
      event.stopPropagation();
      await copyCodeBlock(block);
      button.innerHTML = copiedIcon;
      button.classList.add("copied");
      setTimeout(() => {
        if (document.body.contains(button)) {
          button.innerHTML = copyIcon;
          button.classList.remove("copied");
        }
      }, 1200);
    });
    block.appendChild(button);
    updateCodeCopyButtonPosition(block);
  }

  function removeCodeCopyButton(block) {
    const button = block.querySelector(".code-copy-button");
    if (button) button.remove();
  }

  function updateCodeCopyButtonPosition(block) {
    const button = block.querySelector(".code-copy-button");
    if (!button) return;
    button.style.right = `${copyRightOffset - block.scrollLeft}px`;
  }

  async function copyCodeBlock(block) {
    const code = block.querySelector("code");
    const text = code ? code.innerText : block.innerText;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return;
    }
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.top = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
  }

  function enhanceReferences(html) {
    if (!html || !window.DOMParser) return html;
    const doc = new DOMParser().parseFromString(`<div>${html}</div>`, "text/html");
    const root = doc.body.firstElementChild;
    if (!root) return html;
    const walker = doc.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (!shouldSkipReferenceNode(node)) nodes.push(node);
    }
    nodes.forEach(replaceReferencesInTextNode);
    return root.innerHTML;
  }

  function shouldSkipReferenceNode(node) {
    const parent = node.parentElement;
    return Boolean(parent && parent.closest("a, code, pre, script, style, textarea"));
  }

  function replaceReferencesInTextNode(node) {
    const text = node.nodeValue || "";
    const pattern = /(^|[^\w/])(@[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?|#\d+)/g;
    let match;
    let lastIndex = 0;
    const fragment = document.createDocumentFragment();

    while ((match = pattern.exec(text))) {
      const prefix = match[1];
      const token = match[2];
      const tokenStart = match.index + prefix.length;
      fragment.append(document.createTextNode(text.slice(lastIndex, tokenStart)));
      fragment.append(referenceAnchor(token));
      lastIndex = tokenStart + token.length;
    }

    if (lastIndex === 0) return;
    fragment.append(document.createTextNode(text.slice(lastIndex)));
    node.replaceWith(fragment);
  }

  function referenceAnchor(token) {
    const anchor = document.createElement("a");
    anchor.textContent = token;
    if (token.startsWith("@")) {
      anchor.href = `https://github.com/${token.slice(1)}`;
      anchor.target = "_blank";
      anchor.rel = "noreferrer";
      return anchor;
    }
    anchor.href = localNumberHref(Number(token.slice(1)));
    return anchor;
  }

  function localNumberHref(number) {
    return `#/${config.itemKind}/${number}`;
  }

  function userLink(user) {
    if (!user) return "ghost";
    return `<a class="user-link" href="${escapeAttr(user.html_url || "#")}" target="_blank" rel="noreferrer">${escapeHtml(user.login || "ghost")}</a>`;
  }

  function pageFromHash() {
    const match = location.hash.match(/^#page-(\d+)$/);
    return match ? Number(match[1]) : 1;
  }

  function itemFromHash() {
    const match = location.hash.match(/^#\/(issue|pull)\/(\d+)$/);
    return match ? { kind: match[1], number: Number(match[2]) } : null;
  }

  function showListView() {
    listView.hidden = false;
    detailView.hidden = true;
  }

  function showDetailView() {
    listView.hidden = true;
    detailView.hidden = false;
  }

  function formatTime(value) {
    if (!value) return "unknown";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "unknown";

    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const minute = 60 * 1000;
    const hour = 60 * minute;
    const day = 24 * hour;

    if (diffMs < minute) return "just now";
    if (diffMs < hour) {
      const minutes = Math.floor(diffMs / minute);
      return `${minutes} ${minutes === 1 ? "minute" : "minutes"} ago`;
    }
    if (diffMs < day) {
      const hours = Math.floor(diffMs / hour);
      return `${hours} ${hours === 1 ? "hour" : "hours"} ago`;
    }
    if (diffMs < 2 * day) return "yesterday";
    if (diffMs < 7 * day) {
      const days = Math.floor(diffMs / day);
      return `${days} days ago`;
    }
    if (diffMs < 14 * day) return "last week";
    if (diffMs < 30 * day) {
      const days = Math.floor(diffMs / day);
      return `${days} days ago`;
    }

    const formatted = new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    }).format(date);
    return `on ${formatted}`;
  }

  function octicon(name) {
    if (name === "issue-closed") {
      return '<svg class="octicon octicon-issue-closed" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><circle cx="8" cy="8" r="6.75" fill="none" stroke="currentColor" stroke-width="1.5"></circle><path fill="currentColor" d="M11.28 6.78a.75.75 0 0 0-1.06-1.06L7.25 8.69 5.78 7.22a.75.75 0 0 0-1.06 1.06l2 2a.75.75 0 0 0 1.06 0l3.5-3.5Z"></path></svg>';
    }
    return `<svg class="octicon octicon-${name}" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="${icons[name] || icons["issue-opened"]}"></path></svg>`;
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function escapeAttr(value) {
    return escapeHtml(value);
  }
})();
