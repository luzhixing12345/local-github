# local-github
本地快速浏览 Github issue/pr，查看新增 comment/issue/pr/response

## Quick start

```bash
python -m local_github.main luzhixing12345/zood
```

命令会读取项目根目录 `.github-token`，从 GitHub API 同步仓库 Issue / PR 数据到 `data/github/`，然后生成 `docs/` 静态页面。

生成结果采用少量 HTML 页面加数据分片：

- `docs/index.html`：仓库入口。
- `docs/repos/<owner>/<repo>/issues.html`：Issue 列表和详情页面壳。
- `docs/repos/<owner>/<repo>/pulls.html`：PR 列表和详情页面壳。
- `docs/repos/<owner>/<repo>/data/*.json`：原始数据分片。
- `docs/repos/<owner>/<repo>/data/*.js`：用于直接 `file://` 打开的按需加载数据分片。

Issue / PR 详情通过单页路由显示，不额外生成详情 HTML。例如：

```text
docs/repos/luzhixing12345/zood/issues.html#/issue/22
docs/repos/luzhixing12345/zood/pulls.html#/pull/1
```

生成后直接打开：

```text
docs/index.html
```

也可以分步执行：

```bash
python -m local_github.main sync luzhixing12345/zood
python -m local_github.main build
```

## Shell completion

`pip install local_github` 会安装 bash / zsh 补全脚本到当前 Python prefix 的标准目录：

- `share/bash-completion/completions/local-github`
- `share/zsh/site-functions/_local-github`

补全脚本会从当前目录向上查找 `docs/repos/<owner>/<repo>`，输入下面命令后按 `Tab` 可以补全本地已有仓库：

```bash
local-github sync <Tab>
```

如果 `docs/` 不在当前项目目录下，可以指定：

```bash
export LOCAL_GITHUB_DOCS_REPOS=/path/to/docs/repos
```
