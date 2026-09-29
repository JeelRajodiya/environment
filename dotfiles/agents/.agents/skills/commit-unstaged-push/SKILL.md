---
name: commit-unstaged-push
description: Group related unstaged Git changes into atomic commits named with Conventional Commits, then push them. Use when asked to commit unstaged work and push it, or to make atomic commits and push.
---

# Commit Unstaged Changes and Push

Inspect `git status` and the complete unstaged diff, including untracked files, before staging anything. Commit only files and hunks that are clearly part of the requested code or documentation change. Leave generated logs, research notes, plan files, scratch Markdown, and other incidental or ambiguous files untracked/unstaged unless the user explicitly asks to include them. Preserve unrelated changes, and do not amend, reset, stash, or rewrite history unless the user explicitly requests it.

Group files and hunks by the smallest independently useful change. Use `git add -p` when a file contains changes for more than one commit. If a safe atomic grouping is ambiguous, ask the user rather than guessing.

Before each commit, inspect its staged diff and check it for credential-like values. Stop and report the affected path if one is found; do not commit or push it.

Create each commit with a Conventional Commits subject:

```text
<type>(optional-scope): concise imperative summary
```

Use the change to select the type (`feat`, `fix`, `docs`, `refactor`, `test`, `build`, `ci`, `chore`, and so on). Follow stricter repository conventions when present. Keep commits focused and avoid empty commits.

After committing, push the current branch with a plain `git push` (use `git push -u origin <branch>` if no upstream is set). Never force-push. If the push is rejected, report the error instead of pulling, rebasing, or forcing.

Finish by showing the created commit hashes, the push result, and any remaining unstaged or untracked files.
