(function () {
  "use strict";

  const icons = {
    "issue-opened":
      "M8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z M8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0Zm0 1.5a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13Z",
    "issue-closed":
      "M11.28 6.78a.75.75 0 0 0-1.06-1.06L7.25 8.69 5.78 7.22a.75.75 0 0 0-1.06 1.06l2 2a.75.75 0 0 0 1.06 0l3.5-3.5Z M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0Z",
    "git-pull-request":
      "M1.5 3.25a2.25 2.25 0 1 1 3 2.122v5.256a2.25 2.25 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 1.5 3.25Zm9.5-.75h1.25A2.75 2.75 0 0 1 15 5.25v5.378a2.25 2.25 0 1 1-1.5 0V5.25c0-.69-.56-1.25-1.25-1.25H11v1.75a.25.25 0 0 1-.427.177L7.823 3.177a.25.25 0 0 1 0-.354l2.75-2.75A.25.25 0 0 1 11 .25V2.5Z",
    "git-pull-request-closed":
      "M3.25 1A2.25 2.25 0 0 1 4 5.372v5.256a2.251 2.251 0 1 1-1.5 0V5.372A2.251 2.251 0 0 1 3.25 1Zm9.5 5.5a.75.75 0 0 1 .75.75v3.378a2.251 2.251 0 1 1-1.5 0V7.25a.75.75 0 0 1 .75-.75Zm-2.03-5.273a.75.75 0 0 1 1.06 0l.97.97.97-.97a.748.748 0 0 1 1.265.332.75.75 0 0 1-.205.729l-.97.97.97.97a.751.751 0 0 1-.018 1.042.751.751 0 0 1-1.042.018l-.97-.97-.97.97a.749.749 0 0 1-1.275-.326.749.749 0 0 1 .215-.734l.97-.97-.97-.97a.75.75 0 0 1 0-1.06ZM2.5 3.25a.75.75 0 1 0 1.5 0 .75.75 0 0 0-1.5 0ZM3.25 12a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm9.5 0a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Z",
    "git-merge":
      "M5.45 5.154A4.25 4.25 0 0 0 9.25 7.5h1.378a2.251 2.251 0 1 1 0 1.5H9.25A5.734 5.734 0 0 1 5 7.123v3.505a2.25 2.25 0 1 1-1.5 0V5.372a2.25 2.25 0 1 1 1.95-.218ZM4.25 13.5a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm8.5-4.5a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM5 3.25a.75.75 0 1 0 0 .005V3.25Z",
    comment:
      "M1.75 2.5h12.5a.25.25 0 0 1 .25.25v8.5a.25.25 0 0 1-.25.25H6.5a.75.75 0 0 0-.53.22L3.5 14.19v-1.94a.75.75 0 0 0-.75-.75h-1a.25.25 0 0 1-.25-.25v-8.5a.25.25 0 0 1 .25-.25ZM14.25 1H1.75A1.75 1.75 0 0 0 0 2.75v8.5C0 12.216.784 13 1.75 13H2v2.543a.457.457 0 0 0 .78.323L6.646 13h7.604A1.75 1.75 0 0 0 16 11.25v-8.5A1.75 1.75 0 0 0 14.25 1Z",
    "file-diff":
      "M1 2.75C1 1.784 1.784 1 2.75 1h7.586c.464 0 .909.184 1.237.513l2.914 2.914c.329.328.513.773.513 1.237v7.586A1.75 1.75 0 0 1 13.25 15H2.75A1.75 1.75 0 0 1 1 13.25Zm1.75-.25a.25.25 0 0 0-.25.25v10.5c0 .138.112.25.25.25h10.5a.25.25 0 0 0 .25-.25V6h-2.75A1.75 1.75 0 0 1 9 4.25V2.5Zm7.75.062V4.25c0 .138.112.25.25.25h1.688ZM5.72 6.72a.75.75 0 0 1 1.06 0L8 7.94l1.22-1.22a.75.75 0 1 1 1.06 1.06L9.06 9l1.22 1.22a.75.75 0 1 1-1.06 1.06L8 10.06l-1.22 1.22a.75.75 0 0 1-1.06-1.06L6.94 9 5.72 7.78a.75.75 0 0 1 0-1.06Z",
  };

  const copyIcon =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#9198a1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>';
  const copiedIcon =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#1a7f37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>';
  const copyRightOffset = 8;
  let config = null;

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
  if (!shell) {
    enhanceStaticMarkdown(document);
    return;
  }

  config = JSON.parse(shell.dataset.localGithubApp);
  window.LocalGithubData.root = config.dataRoot;
  const state = { page: 1, filter: "open", assignee: "", assigneeUsers: [], query: "", manifest: null, basic: null, items: [] };
  const listView = shell.querySelector("[data-route-view='list']");
  const detailView = shell.querySelector("[data-route-view='detail']");
  const list = shell.querySelector("[data-list]");
  const detail = shell.querySelector("[data-detail]");
  const pager = shell.querySelector("[data-pager]");
  const searchInput = shell.querySelector("[data-search-input]");
  const assigneeFilter = shell.querySelector("[data-assignee-filter]");
  const assigneeTrigger = shell.querySelector("[data-assignee-trigger]");
  const assigneeMenu = shell.querySelector("[data-assignee-menu]");
  const assigneeSearch = shell.querySelector("[data-assignee-search]");
  const assigneeOptions = shell.querySelector("[data-assignee-options]");
  const assigneeLabel = shell.querySelector("[data-assignee-label]");

  init().catch((error) => {
    list.innerHTML = `<div class="empty-state">${escapeHtml(error.message)}</div>`;
  });

  async function init() {
    state.manifest = await window.LocalGithubData.load("web_manifest");
    updateCounts();
    bindFilters();
    bindAssigneeFilter();
    bindSearch();
    window.addEventListener("hashchange", route);
    await route();
  }

  async function route() {
    const selected = itemFromHash();
    if (selected) {
      showDetailView();
      await loadDetail(selected.kind, selected.number, selected.commentId);
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

  function bindSearch() {
    if (!searchInput) return;
    searchInput.addEventListener("input", async () => {
      state.query = searchInput.value.trim().toLowerCase();
      await loadPage(1);
    });
  }

  function bindAssigneeFilter() {
    if (!assigneeFilter || !assigneeTrigger || !assigneeMenu || !assigneeSearch) return;
    assigneeTrigger.addEventListener("click", () => {
      const open = assigneeMenu.hidden;
      assigneeMenu.hidden = !open;
      assigneeTrigger.setAttribute("aria-expanded", String(open));
      if (open) {
        assigneeSearch.focus();
        assigneeSearch.select();
      }
    });
    assigneeSearch.addEventListener("input", () => {
      renderAssigneeOptions(assigneeSearch.value);
    });
    assigneeSearch.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeAssigneeMenu();
      if (event.key === "Enter" && assigneeOptions) {
        const firstMatch = Array.from(assigneeOptions.querySelectorAll("[data-assignee-value]"))
          .find((option) => option.dataset.assigneeValue);
        if (firstMatch) {
          event.preventDefault();
          firstMatch.click();
        }
      }
    });
    document.addEventListener("click", (event) => {
      if (!assigneeFilter.contains(event.target)) closeAssigneeMenu();
    });
  }

  function populateAssigneeFilter() {
    const users = new Map();
    state.basic.forEach((item) => {
      (item.assignees || []).forEach((user) => {
        const login = user.login || "";
        if (login) users.set(login.toLowerCase(), user);
      });
    });
    state.assigneeUsers = Array.from(users.values())
      .sort((left, right) => left.login.localeCompare(right.login, undefined, { sensitivity: "base" }));
    renderAssigneeOptions("");
  }

  function renderAssigneeOptions(query) {
    if (!assigneeOptions) return;
    const normalizedQuery = query.trim().toLowerCase();
    assigneeOptions.replaceChildren();
    assigneeOptions.appendChild(createAssigneeOption("", "All assignees", null));
    const matches = state.assigneeUsers.filter((user) =>
      (user.login || "").toLowerCase().includes(normalizedQuery));
    matches.forEach((user) => {
      assigneeOptions.appendChild(createAssigneeOption(
        (user.login || "").toLowerCase(),
        `@${user.login}`,
        user,
      ));
    });
    if (!matches.length && normalizedQuery) {
      const empty = document.createElement("div");
      empty.className = "assignee-filter-empty";
      empty.textContent = "No matching assignees";
      assigneeOptions.appendChild(empty);
    }
  }

  function createAssigneeOption(value, text, user) {
    const button = document.createElement("button");
    button.className = "assignee-filter-option";
    button.type = "button";
    button.dataset.assigneeValue = value;
    if (value === state.assignee) button.classList.add("selected");
    if (user && user.avatar_url) {
      const avatar = document.createElement("img");
      avatar.src = user.avatar_url;
      avatar.alt = "";
      button.appendChild(avatar);
    }
    const label = document.createElement("span");
    label.textContent = text;
    button.appendChild(label);
    button.addEventListener("click", async () => {
      state.assignee = value;
      if (assigneeLabel) assigneeLabel.textContent = value ? text : "All";
      if (assigneeSearch) assigneeSearch.value = "";
      closeAssigneeMenu();
      renderAssigneeOptions("");
      await loadPage(1);
    });
    return button;
  }

  function closeAssigneeMenu() {
    if (!assigneeMenu || !assigneeTrigger) return;
    assigneeMenu.hidden = true;
    assigneeTrigger.setAttribute("aria-expanded", "false");
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
      populateAssigneeFilter();
    }
    const stateFiltered = state.filter === "all"
      ? state.basic
      : state.basic.filter((item) => item.state === state.filter);
    const assigneeFiltered = state.assignee
      ? stateFiltered.filter((item) =>
          (item.assignees || []).some((user) => (user.login || "").toLowerCase() === state.assignee))
      : stateFiltered;
    const filtered = state.query
      ? assigneeFiltered.filter((item) => matchesSearch(item, state.query))
      : assigneeFiltered;
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

  function matchesSearch(item, query) {
    const labels = (item.labels || []).map((label) => label.name || "").join(" ");
    const user = item.user || {};
    const participants = (item.participant_logins || []).join(" ");
    const haystack = [
      item.title || "",
      item.number ? `#${item.number}` : "",
      item.number || "",
      item.state || "",
      item.kind || "",
      user.login || "",
      participants,
      labels,
    ]
      .join(" ")
      .toLowerCase();
    return haystack.includes(query);
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
    const assignees = (item.assignees || []).map(renderListAssignee).join("");
    return `
      <article class="issue-row">
        <div class="issue-icon ${status.className}">${octicon(status.icon)}</div>
        <div class="issue-main">
          <div class="issue-title-line">
            <a class="issue-title" href="#/${item.kind}/${item.number}" data-load-detail data-number="${item.number}">${escapeHtml(item.title || "")}</a>
            ${item.is_new ? '<span class="new-badge">New</span>' : ""}
            ${labels}
          </div>
          <div class="issue-meta">
            #${item.number} ${escapeHtml(status.label.toLowerCase())} by ${userLink(item.user)}
            · updated ${formatTime(item.updated_at)}
          </div>
        </div>
        <div class="issue-row-aside">
          ${assignees ? `<div class="issue-row-assignees" aria-label="Assignees">${assignees}</div>` : ""}
          <div class="comment-count">${octicon("comment")} ${item.comments || 0}</div>
        </div>
      </article>
    `;
  }

  function renderListAssignee(user) {
    const login = user.login || "ghost";
    return `
      <a class="list-assignee" href="${escapeAttr(userProfileUrl(user))}" target="_blank" rel="noreferrer" title="Assigned to ${escapeAttr(login)}" aria-label="Assigned to ${escapeAttr(login)}">
        <img src="${escapeAttr(user.avatar_url || "")}" alt="">
      </a>
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

  async function loadDetail(kind, number, commentId = null) {
    shell.classList.remove("files-mode");
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
    bindPrDetailTabs(detail);
    bindPrDiffLoader(detail, item, kind);
    document.title = `${state.manifest.repository.full_name} #${number}`;
    scrollToComment(commentId);
  }

  function scrollToComment(commentId) {
    if (!commentId) {
      window.scrollTo({ top: 0 });
      return;
    }
    const target = document.getElementById(`comment-${commentId}`);
    if (!target) {
      window.scrollTo({ top: 0 });
      return;
    }
    target.scrollIntoView({ block: "start" });
    target.classList.add("timeline-item-target");
    setTimeout(() => target.classList.remove("timeline-item-target"), 1600);
  }

  function renderDetail(shard, kind) {
    const item = shard.item || {};
    const status = statusFor({ ...item, kind });
    const comments = shard.comments || [];
    const reviews = shard.review_comments || [];
    const files = shard.files || [];
    const diffLoaded = Boolean(shard.diff_loaded);
    const labels = item.labels || [];
    const assignees = item.assignees || [];
    const milestone = item.milestone;
    const metaLine =
      kind === "pull"
        ? `${userLink(item.user)} opened ${formatTime(item.created_at)}`
        : `${userLink(item.user)} opened ${formatTime(item.created_at)} · ${comments.length} comments`;
    const conversationItems = comments
      .map((comment) => ({ createdAt: comment.created_at || "", html: renderTimelineItem(comment, "commented") }))
      .concat(buildReviewThreads(reviews).map((thread) => ({
        createdAt: thread.root.created_at || "",
        html: renderReviewThread(thread),
      })))
      .sort((left, right) => left.createdAt.localeCompare(right.createdAt));
    const timeline = [renderTimelineItem(item, "opened this")]
      .concat(conversationItems.map((entry) => entry.html))
      .join("");
    const sourceUrl = item.html_url || "";

    const conversationPanel = `
      <div class="issue-info-head">
        <h1 class="issue-info-title">${escapeHtml(item.title || "")} <span class="muted">#${item.number || ""}</span></h1>
        <div class="issue-info-meta">
          <span class="state-badge ${status.className}">${octicon(status.icon)} ${status.label}</span>
          <span>${metaLine}</span>
          ${sourceUrl ? `<a class="issue-source-link" href="${escapeAttr(sourceUrl)}" target="_blank" rel="noreferrer" aria-label="Open on GitHub">${externalLinkIcon()}</a>` : ""}
        </div>
      </div>
      ${kind === "pull" ? renderPrDetailTabs(files, diffLoaded) : ""}
      <div class="issue-info-layout" data-pr-panel="conversation">
        <section class="timeline">
          ${timeline}
        </section>
        <aside class="issue-sidebar">
          ${sidebarSection("Assignees", assignees.length ? assignees.map(renderSidebarUser).join("") : '<span class="muted">No one assigned</span>')}
          ${sidebarSection("Labels", labels.length ? labels.map(renderSidebarLabel).join("") : '<span class="muted">None yet</span>')}
          ${sidebarSection("Milestone", milestone ? escapeHtml(milestone.title || "") : '<span class="muted">No milestone</span>')}
          ${sidebarSection("Development", '<span class="muted">No branches or pull requests</span>')}
        </aside>
      </div>
    `;
    return kind === "pull" && diffLoaded ? `${conversationPanel}${renderChangedFiles(files)}` : conversationPanel;
  }

  function renderPrDetailTabs(files, diffLoaded) {
    const fileCount = files.length;
    return `
      <nav class="pr-detail-tabs" aria-label="Pull request sections">
        <button class="pr-detail-tab active" type="button" data-pr-tab="conversation">${octicon("comment")} Conversation</button>
        ${diffLoaded
          ? `<button class="pr-detail-tab" type="button" data-pr-tab="files">${octicon("file-diff")} Files changed <span class="Counter">${fileCount}</span></button>`
          : `<button class="pr-detail-tab" type="button" data-load-pr-diff>${octicon("file-diff")} Load diff</button>`}
        <span class="pr-diff-error" data-pr-diff-error role="alert"></span>
      </nav>
    `;
  }

  function bindPrDetailTabs(root, activeTab = "conversation") {
    const tabs = Array.from(root.querySelectorAll("[data-pr-tab]"));
    if (!tabs.length) return;
    const panels = Array.from(root.querySelectorAll("[data-pr-panel]"));
    const appShell = root.closest(".app-shell");
    const activate = (name) => {
      tabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.prTab === name));
      panels.forEach((panel) => {
        panel.hidden = panel.dataset.prPanel !== name;
      });
      if (appShell) {
        appShell.classList.toggle("files-mode", name === "files");
      }
    };
    tabs.forEach((tab) => {
      tab.addEventListener("click", () => activate(tab.dataset.prTab));
    });
    root.querySelectorAll("[data-file-target]").forEach((button) => {
      button.addEventListener("click", () => {
        const target = document.getElementById(button.dataset.fileTarget || "");
        if (target) target.scrollIntoView({ block: "start" });
      });
    });
    activate(activeTab);
  }

  function bindPrDiffLoader(root, shard, kind) {
    const button = root.querySelector("[data-load-pr-diff]");
    if (!button || kind !== "pull") return;
    const errorTarget = root.querySelector("[data-pr-diff-error]");
    button.addEventListener("click", async () => {
      const [owner, repo] = String(state.manifest.repository.full_name || "").split("/");
      button.disabled = true;
      button.textContent = "Loading diff...";
      if (errorTarget) errorTarget.textContent = "";
      try {
        const url = `/api/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/pulls/${Number(shard.item.number)}/files`;
        const response = await fetch(url, { headers: { Accept: "application/json" } });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) {
          throw new Error(payload.error || `Unable to load diff (${response.status}).`);
        }
        shard.files = payload.files || [];
        shard.diff_loaded = true;
        detail.innerHTML = renderDetail(shard, kind);
        enhanceMarkdown(detail);
        bindPrDetailTabs(detail, "files");
        bindPrDiffLoader(detail, shard, kind);
      } catch (error) {
        button.disabled = false;
        button.textContent = "Load diff";
        if (errorTarget) errorTarget.textContent = error.message;
      }
    });
  }

  function renderChangedFiles(files) {
    const totalAdditions = files.reduce((sum, file) => sum + Number(file.additions || 0), 0);
    const totalDeletions = files.reduce((sum, file) => sum + Number(file.deletions || 0), 0);
    return `
      <section class="changed-files" data-pr-panel="files" hidden>
        <div class="changed-files-header">
          <strong>Files changed</strong>
          <span class="muted">${files.length} ${files.length === 1 ? "file" : "files"}</span>
          <span class="diffstat additions">+${totalAdditions}</span>
          <span class="diffstat deletions">-${totalDeletions}</span>
        </div>
        ${files.length ? `
          <div class="pr-files-layout">
            <aside class="pr-file-list" aria-label="Changed files">
              ${files.map(renderChangedFileLink).join("")}
            </aside>
            <div class="pr-file-diffs">
              ${files.map(renderChangedFile).join("")}
            </div>
          </div>
        ` : '<div class="empty-state">No changed files saved locally.</div>'}
      </section>
    `;
  }

  function renderChangedFileLink(file, index) {
    return `
      <button class="pr-file-link" type="button" data-file-target="file-${index + 1}">
        <span class="pr-file-link-name">${escapeHtml(file.filename || "unknown file")}</span>
        <span class="pr-file-link-stat">
          <span class="diffstat additions">+${Number(file.additions || 0)}</span>
          <span class="diffstat deletions">-${Number(file.deletions || 0)}</span>
        </span>
      </button>
    `;
  }

  function renderChangedFile(file, index) {
    const patch = file.patch || "";
    const rows = patch ? renderSplitDiffRows(patch) : '<tr><td class="diff-line-empty" colspan="4">Patch not available from GitHub API.</td></tr>';
    return `
      <article class="changed-file" id="file-${index + 1}">
        <div class="changed-file-header">
          <span class="changed-file-name">${escapeHtml(file.filename || "unknown file")}</span>
          <span class="changed-file-meta">
            ${escapeHtml(file.status || "modified")}
            <span class="diffstat additions">+${Number(file.additions || 0)}</span>
            <span class="diffstat deletions">-${Number(file.deletions || 0)}</span>
          </span>
        </div>
        <div class="diff-table-wrap">
          <table class="split-diff-table">
            <colgroup>
              <col class="diff-num-col">
              <col class="diff-code-col">
              <col class="diff-num-col">
              <col class="diff-code-col">
            </colgroup>
            <tbody>${rows}</tbody>
          </table>
        </div>
      </article>
    `;
  }

  function renderSplitDiffRows(patch) {
    const lines = patch.split("\n");
    let oldLine = 0;
    let newLine = 0;
    const rows = [];

    for (let index = 0; index < lines.length; index += 1) {
      const line = lines[index];
      const hunk = line.match(/^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@/);
      if (hunk) {
        oldLine = Number(hunk[1]);
        newLine = Number(hunk[2]);
        rows.push(`
          <tr class="diff-hunk">
            <td class="diff-num diff-context"></td>
            <td class="diff-hunk-cell" colspan="3"><code>${escapeHtml(line)}</code></td>
          </tr>
        `);
        continue;
      }

      if (line.startsWith("-")) {
        const deletions = [];
        const additions = [];
        while (index < lines.length && lines[index].startsWith("-")) {
          deletions.push({ text: lines[index].slice(1), number: oldLine });
          oldLine += 1;
          index += 1;
        }
        while (index < lines.length && lines[index].startsWith("+")) {
          additions.push({ text: lines[index].slice(1), number: newLine });
          newLine += 1;
          index += 1;
        }
        index -= 1;
        const length = Math.max(deletions.length, additions.length);
        for (let row = 0; row < length; row += 1) {
          rows.push(renderSplitDiffRow(deletions[row], additions[row], "changed"));
        }
        continue;
      }

      if (line.startsWith("+")) {
        rows.push(renderSplitDiffRow(null, { text: line.slice(1), number: newLine }, "added"));
        newLine += 1;
        continue;
      }

      const text = line.startsWith(" ") ? line.slice(1) : line;
      rows.push(renderSplitDiffRow({ text, number: oldLine }, { text, number: newLine }, "context"));
      oldLine += 1;
      newLine += 1;
    }

    return rows.join("");
  }

  function renderSplitDiffRow(oldSide, newSide, kind) {
    const oldClass = oldSide ? (kind === "context" ? "diff-context" : "diff-deletion") : "diff-empty";
    const newClass = newSide ? (kind === "context" ? "diff-context" : "diff-addition") : "diff-empty";
    const oldText = oldSide ? renderDiffCodeText(oldSide.text, oldSide, newSide, "deletion") : "";
    const newText = newSide ? renderDiffCodeText(newSide.text, oldSide, newSide, "addition") : "";
    return `
      <tr>
        <td class="diff-num ${oldClass}">${oldSide ? oldSide.number : ""}</td>
        <td class="diff-code ${oldClass}"><code>${oldText}</code></td>
        <td class="diff-num ${newClass}">${newSide ? newSide.number : ""}</td>
        <td class="diff-code ${newClass}"><code>${newText}</code></td>
      </tr>
    `;
  }

  function renderDiffCodeText(text, oldSide, newSide, type) {
    if (!oldSide || !newSide || oldSide.text === newSide.text) {
      return escapeHtml(text);
    }
    const parts = changedTextBounds(oldSide.text, newSide.text);
    const bounds = type === "deletion" ? parts.old : parts.new;
    if (bounds.start >= bounds.end) return escapeHtml(text);
    const className = type === "deletion" ? "diff-word-deletion" : "diff-word-addition";
    return `${escapeHtml(text.slice(0, bounds.start))}<span class="${className}">${escapeHtml(text.slice(bounds.start, bounds.end))}</span>${escapeHtml(text.slice(bounds.end))}`;
  }

  function changedTextBounds(oldText, newText) {
    let prefix = 0;
    const minLength = Math.min(oldText.length, newText.length);
    while (prefix < minLength && oldText[prefix] === newText[prefix]) {
      prefix += 1;
    }

    let suffix = 0;
    while (
      suffix < oldText.length - prefix &&
      suffix < newText.length - prefix &&
      oldText[oldText.length - 1 - suffix] === newText[newText.length - 1 - suffix]
    ) {
      suffix += 1;
    }

    return {
      old: expandChangedTextBounds(oldText, prefix, oldText.length - suffix),
      new: expandChangedTextBounds(newText, prefix, newText.length - suffix),
    };
  }

  function expandChangedTextBounds(text, start, end) {
    let expandedStart = start;
    let expandedEnd = end;

    while (expandedStart > 0 && isDiffWordChar(text[expandedStart - 1])) {
      expandedStart -= 1;
    }
    while (expandedEnd < text.length && isDiffWordChar(text[expandedEnd])) {
      expandedEnd += 1;
    }

    return { start: expandedStart, end: expandedEnd };
  }

  function isDiffWordChar(char) {
    return /[A-Za-z0-9_$]/.test(char || "");
  }

  function externalLinkIcon() {
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path fill="none" d="M15 3h6v6m-11 5L21 3m-3 10v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>';
  }

  function enhanceStaticMarkdown(root) {
    root.querySelectorAll(".markdown-body").forEach((body) => {
      body.innerHTML = markdown(body.textContent || "");
    });
    enhanceMarkdown(root);
  }

  function renderTimelineItem(item, action) {
    const user = item.user || {};
    const commentId = item.id ? ` id="comment-${escapeAttr(item.id)}"` : "";
    const profileUrl = userProfileUrl(user);
    const login = escapeHtml(user.login || "ghost");
    return `
      <article class="timeline-item"${commentId}>
        <a class="avatar-link" href="${escapeAttr(profileUrl)}" target="_blank" rel="noreferrer" aria-label="${login}">
          <img class="avatar" src="${escapeAttr(user.avatar_url || "")}" alt="">
        </a>
        <div class="comment">
          <div class="comment-header">
            <strong><a class="comment-author" href="${escapeAttr(profileUrl)}" target="_blank" rel="noreferrer">${login}</a></strong>
            <span>${escapeHtml(action)} ${formatTime(item.created_at)}</span>
          </div>
          <div class="markdown-body">${markdown(item.body || "") || '<p class="muted">No description provided.</p>'}</div>
        </div>
      </article>
    `;
  }

  function buildReviewThreads(reviews) {
    const byId = new Map(reviews.map((comment) => [String(comment.id), { root: comment, replies: [] }]));
    const roots = [];
    reviews.forEach((comment) => {
      const parent = comment.in_reply_to_id ? byId.get(String(comment.in_reply_to_id)) : null;
      if (parent) {
        parent.replies.push(comment);
      } else {
        roots.push(byId.get(String(comment.id)));
      }
    });
    roots.forEach((thread) => thread.replies.sort((left, right) => String(left.created_at || "").localeCompare(String(right.created_at || ""))));
    return roots.sort((left, right) => String(left.root.created_at || "").localeCompare(String(right.root.created_at || "")));
  }

  function renderReviewThread(thread) {
    const comment = thread.root;
    const user = comment.user || {};
    const profileUrl = userProfileUrl(user);
    const login = escapeHtml(user.login || "ghost");
    const line = comment.line || comment.original_line;
    const location = line ? `L${line}` : "outdated";
    const commentId = comment.id ? ` id="comment-${escapeAttr(comment.id)}"` : "";
    return `
      <article class="timeline-item review-timeline-item"${commentId}>
        <a class="avatar-link" href="${escapeAttr(profileUrl)}" target="_blank" rel="noreferrer" aria-label="${login}">
          <img class="avatar" src="${escapeAttr(user.avatar_url || "")}" alt="">
        </a>
        <div class="review-thread">
          <div class="review-file-header">
            ${octicon("file-diff")}
            <a href="${escapeAttr(comment.html_url || "#")}" target="_blank" rel="noreferrer">${escapeHtml(comment.path || "unknown file")}</a>
            <span class="review-location">${escapeHtml(location)}</span>
          </div>
          ${renderReviewDiff(comment)}
          ${renderReviewComment(comment, "reviewed")}
          ${thread.replies.map((reply) => renderReviewComment(reply, "replied")).join("")}
        </div>
      </article>
    `;
  }

  function renderReviewComment(comment, action) {
    const user = comment.user || {};
    const profileUrl = userProfileUrl(user);
    const login = escapeHtml(user.login || "ghost");
    const commentId = action === "replied" && comment.id ? ` id="comment-${escapeAttr(comment.id)}"` : "";
    return `
      <div class="review-comment"${commentId}>
        <div class="comment-header">
          <img class="review-comment-avatar" src="${escapeAttr(user.avatar_url || "")}" alt="">
          <strong><a class="comment-author" href="${escapeAttr(profileUrl)}" target="_blank" rel="noreferrer">${login}</a></strong>
          <span>${escapeHtml(action)} ${formatTime(comment.created_at)}</span>
          ${comment.html_url ? `<a class="comment-jump-link" href="${escapeAttr(comment.html_url)}" target="_blank" rel="noreferrer" aria-label="Open review comment on GitHub">${externalLinkIcon()}</a>` : ""}
        </div>
        <div class="markdown-body">${markdown(comment.body || "") || '<p class="muted">No comment provided.</p>'}</div>
      </div>
    `;
  }

  function renderReviewDiff(comment) {
    const diff = String(comment.diff_hunk || "");
    if (!diff.trim()) {
      return '<div class="review-diff-unavailable">Code context is no longer available.</div>';
    }
    const lines = diff.split("\n");
    let oldLine = 0;
    let newLine = 0;
    const hasOriginalLocation = Boolean(comment.original_start_line || comment.original_line);
    const targetEnd = Number(hasOriginalLocation ? comment.original_line : comment.line || 0);
    const targetStart = Number(
      hasOriginalLocation
        ? comment.original_start_line || comment.original_line
        : comment.start_line || comment.line || 0
    );
    const targetSide = String(comment.start_side || comment.side || "RIGHT").toUpperCase();
    let hunkHeader = "";
    const parsedRows = [];
    lines.forEach((value) => {
      const hunk = value.match(/^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@/);
      if (hunk) {
        oldLine = Number(hunk[1]);
        newLine = Number(hunk[2]);
        hunkHeader = value;
        return;
      }
      const type = value.startsWith("+") ? "addition" : value.startsWith("-") ? "deletion" : "context";
      const oldNumber = type === "addition" ? "" : oldLine;
      const newNumber = type === "deletion" ? "" : newLine;
      const currentLine = targetSide === "LEFT" ? oldNumber : newNumber;
      const selected = targetStart && Number(currentLine) >= targetStart && Number(currentLine) <= targetEnd;
      parsedRows.push({ value, type, oldNumber, newNumber, selected });
      if (type !== "addition") oldLine += 1;
      if (type !== "deletion") newLine += 1;
    });
    const selectedIndexes = parsedRows
      .map((row, index) => row.selected ? index : -1)
      .filter((index) => index >= 0);
    let first = selectedIndexes.length ? Math.max(0, selectedIndexes[0] - 3) : 0;
    let last = selectedIndexes.length ? Math.min(parsedRows.length - 1, selectedIndexes[selectedIndexes.length - 1] + 3) : Math.min(parsedRows.length - 1, 6);
    const rows = [];
    if (hunkHeader) {
      rows.push(`<tr class="review-diff-hunk"><td colspan="3"><code>${escapeHtml(hunkHeader)}</code></td></tr>`);
    }
    if (first > 0) rows.push(renderReviewDiffEllipsis(first));
    parsedRows.slice(first, last + 1).forEach((row) => {
      const selected = row.selected ? " review-diff-selected" : "";
      rows.push(`<tr class="review-diff-${row.type}${selected}"><td class="review-diff-num">${row.oldNumber}</td><td class="review-diff-num">${row.newNumber}</td><td class="review-diff-code"><code>${escapeHtml(row.value)}</code></td></tr>`);
    });
    if (last < parsedRows.length - 1) rows.push(renderReviewDiffEllipsis(parsedRows.length - last - 1));
    return `<div class="review-diff"><table><tbody>${rows.join("")}</tbody></table></div>`;
  }

  function renderReviewDiffEllipsis(hiddenLines) {
    return `<tr class="review-diff-ellipsis"><td colspan="3">${hiddenLines} ${hiddenLines === 1 ? "line" : "lines"} hidden</td></tr>`;
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
    if (item.state === "closed") return { className: "closed", icon: item.kind === "pull" ? "git-pull-request-closed" : "issue-closed", label: "Closed" };
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
    if (!config) return `#${number}`;
    const currentKind = config.itemKind;
    const otherKind = currentKind === "pull" ? "issue" : "pull";
    const targetKind = numberExists(currentKind, number)
      ? currentKind
      : numberExists(otherKind, number)
        ? otherKind
        : currentKind;
    const targetPage = targetKind === "pull" ? "pulls.html" : "issues.html";
    const hash = `#/${targetKind}/${number}`;
    return targetKind === currentKind ? hash : `${targetPage}${hash}`;
  }

  function numberExists(kind, number) {
    return Boolean(state.manifest?.detail_pages?.[kind]?.[String(number)]);
  }

  function userLink(user) {
    if (!user) return "ghost";
    return `<a class="user-link" href="${escapeAttr(userProfileUrl(user))}" target="_blank" rel="noreferrer">${escapeHtml(user.login || "ghost")}</a>`;
  }

  function userProfileUrl(user) {
    if (user && user.html_url) return user.html_url;
    if (user && user.login && user.login !== "ghost") return `https://github.com/${user.login}`;
    return "https://github.com";
  }

  function pageFromHash() {
    const match = location.hash.match(/^#page-(\d+)$/);
    return match ? Number(match[1]) : 1;
  }

  function itemFromHash() {
    const match = location.hash.match(/^#\/(issue|pull)\/(\d+)(?:\/comment-(\d+))?$/);
    return match ? { kind: match[1], number: Number(match[2]), commentId: match[3] || null } : null;
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
