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
