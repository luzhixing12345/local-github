# local-github

本地快速浏览 Github issue/pr，查看新增 comment/issue/pr

这个项目的起因是在网页端浏览 Github repo 的 issue/pr 之间切换比较慢，因为每次都要重新发起请求。而且作为一个非 member 也不想时时刻刻 watch 新增 issue/pr/comment 收到一堆邮件，但又想知道有哪些内容更新了，谁新增了回复，谁提交了新的 issue/pr，哪些 issue/pr 的 状态更改了，所以诞生了这个项目

基本思路是通过 Github API 获取开源仓库的所有issue/pr信息保存到本地 json，然后本地生成静态页面浏览。考虑到绝大部分项目的 update 没有那么频繁，所以这种把数据拉到本地查看的方案也还好。这个项目的页面完全仿照 Github 的页面，几乎可以说 1:1 复刻，然后去掉了一些不重要的组件。

## Quick start

```bash
pip install local_github
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
