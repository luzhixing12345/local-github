# bash completion for local-github

_local_github_find_docs_repos() {
  local dir="$PWD"
  while [[ "$dir" != "/" ]]; do
    if [[ -d "$dir/docs/repos" ]]; then
      printf '%s\n' "$dir/docs/repos"
      return
    fi
    dir="$(dirname "$dir")"
  done

  if [[ -n "${LOCAL_GITHUB_DOCS_REPOS:-}" && -d "$LOCAL_GITHUB_DOCS_REPOS" ]]; then
    printf '%s\n' "$LOCAL_GITHUB_DOCS_REPOS"
  elif [[ -n "${LOCAL_GITHUB_DOCS_ROOT:-}" && -d "$LOCAL_GITHUB_DOCS_ROOT/repos" ]]; then
    printf '%s\n' "$LOCAL_GITHUB_DOCS_ROOT/repos"
  elif [[ -d "$PWD/docs/repos" ]]; then
    printf '%s\n' "$PWD/docs/repos"
  fi
}

_local_github_repo_names() {
  local repos_root owner repo
  repos_root="$(_local_github_find_docs_repos)"
  [[ -n "$repos_root" && -d "$repos_root" ]] || return

  for owner in "$repos_root"/*; do
    [[ -d "$owner" ]] || continue
    for repo in "$owner"/*; do
      [[ -d "$repo" ]] || continue
      printf '%s/%s\n' "$(basename "$owner")" "$(basename "$repo")"
    done
  done
}

_local_github_complete() {
  local cur prev cmd
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  prev="${COMP_WORDS[COMP_CWORD - 1]}"

  if [[ "$COMP_CWORD" -eq 1 ]]; then
    COMPREPLY=($(compgen -W "sync build all server --help -h" -- "$cur"))
    return 0
  fi

  cmd="${COMP_WORDS[1]}"
  case "$cmd" in
    sync|build|all)
      COMPREPLY=($(compgen -W "$(_local_github_repo_names)" -- "$cur"))
      ;;
    *)
      COMPREPLY=()
      ;;
  esac
  return 0
}

complete -F _local_github_complete local-github
