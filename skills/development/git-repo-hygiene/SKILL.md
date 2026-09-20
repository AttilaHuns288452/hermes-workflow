---
name: git-repo-hygiene
description: Use when committing or pushing changes to any repo.
version: 1.0.0
author: Hermes Agent (Nous Research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, hygiene, line-endings, staging, secrets, github]
    category: development
---

# Git Repo Hygiene

Standing rules for committing and pushing changes to any repo — especially Windows-origin repos (CRLF on disk, no `.gitattributes`) and public remotes. Load before any commit-and-push flow. Deploy/hosting is `web-development/publish-site`; repo operations are `github/github-repo-management` (both user-owned — do not duplicate them here).

## Always-On Rules

1. **Diagnose line-ending churn before trusting a big diff.** If `git diff --stat` shows thousands of modified files, run `git diff --ignore-cr-at-eol --stat` — that number is the real change. Windows-origin repos look fully rewritten when they aren't; committing or reviewing on top of the noise buries the actual edit.
2. **Normalize EOL once, in its own commit, before content edits.** `git config core.autocrlf false`, write `.gitattributes` with `* text=auto eol=lf`, then `git add --renormalize .`. Commit normalization separately from content — it's unreviewable by design. After the normalize commit, content edits stay single-file diffs.
3. **`git add --renormalize` stages deletions for any tracked file missing from disk.** A phantom index entry (needs `git rm -r --cached <dir>` first) or a file vanished outside your task gets deleted from the repo. Audit `git diff --cached --name-status` before committing; restore strays with `git checkout HEAD -- <path>`.
4. **Never blind-stage with `git add -A` on repos containing build outputs, caches, or tooling state.** It sweeps in untracked junk (`__pycache__/`, agent-internal dirs, stale `dist/`) alongside the real change. Stage explicit paths, or audit the staged name-status list and unstage anything you didn't touch.
5. **Secret-scan the staged diff before every push to a public repo** — docs, READMEs, config templates included:
   ```bash
   git diff --cached | grep -inE "sk-[a-zA-Z0-9]{16,}|api[_-]?key['\" ]*[:=]['\" ]*[a-zA-Z0-9]{20}"
   ```
   Masked placeholder prefixes (`sk-xxx...`, `sk_live_...`) and env-var NAMES (`key_env: FOO_API_KEY`) are fine; key values are not. Config templates reference keys by env var name only.

## Verification

Before reporting a push done:

- `git status -sb` clean against origin (nothing staged, nothing unexpectedly deleted).
- `git log origin/<branch> --oneline -3` lists the pushed commits.
- For a hygiene commit: `git diff HEAD~1 --stat | tail -1` confirms expected file count — normalize commit = whole tree; content commit = only the files edited.
