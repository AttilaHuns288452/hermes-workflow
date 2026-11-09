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
6. **A path-limited `git add <dir>/` (or a glob like `git add frontend/*.mjs`) stages only files INSIDE that directory/pattern** — a root-level file sharing the stem (`server/` vs `server.js`, `api/` vs `api.js`, root `pay_smoke.mjs` vs `frontend/*.mjs`) is silently missed and the commit ships without it, so the new endpoint 404s in production while the code exists locally. Stage explicit paths for both the directory and its root-level namesake, and read the commit's own file list (`git show --stat`) against the files you edited before declaring anything shipped. When a bulk edit touched many files, diff the edited-file count you expect against `git diff --cached --name-status` before `git commit` — a glob that came up short is invisible until a post-push `git status` shows the leftovers (recovering needs `git commit --amend` + `--force-with-lease`).
7. **Keep multi-line commit messages out of the driver's own string literal.**
   When git runs from a script or a tool call, a message with paragraphs inside a
   quoted Python/JS/shell string breaks the *caller* (unterminated string) before
   git ever runs — and the error names a line of your script, not git, so it reads
   like a tool failure. Write the message to a file and use `git commit -F <file>`,
   or pass one `--message` per paragraph, then `git log -1 --format=%B` to confirm
   the paragraphs landed.
8. **Quiet history for cosmetic work (user preference).** When the user asks
   for cleanup commits to stay quiet (comment rewrites, formatting, renames
   they do not want narrated), use a bland message like `updated file` and do
   NOT enumerate what the cleanup touched — the diff is the record. Read the
   request as standing for that class of work in the repo until told otherwise.
9. **A repo-wide rename is verified by grep on tracked text, not by the diff.** Confirm the exact replacement string and scope once before touching dozens of files (app code only, or also QA fixtures, mock data, migrations, docs — when the user says "replace the X stuff" they usually mean everything), then require zero hits for the OLD token plus a sensible hit count for the NEW one before committing. Exclude `.git`, dependency dirs, build output, and regenerable index caches (`.codegraph/`) — stale tokens inside those are not rename failures. Leaving the old token in QA fixtures and mock data breaks the suites and re-surfaces in user-facing output; renaming in code is not renaming identity rows in the database (see `productivity/supabase`).
10. **Shared repos move while you work — rebase before pushing, then re-install dependencies.** Fetch and read the incoming range (`git log --oneline HEAD..<remote>/<branch>`, `--stat`) for overlap with your files before rebasing; after a rebase that moved `package.json`/lockfile, run the package manager's install again before building. Stale `node_modules` breaks the build with unresolved-import errors that NAME YOUR CODE, so the failure mimics a merge conflict in source while the diff is clean — reinstall first, then suspect the code.

## Verification

Before reporting a push done:

- `git status -sb` clean against origin (nothing staged, nothing unexpectedly deleted).
- `git log origin/<branch> --oneline -3` lists the pushed commits.
- For a hygiene commit: `git diff HEAD~1 --stat | tail -1` confirms expected file count — normalize commit = whole tree; content commit = only the files edited.
- `git show --stat` on the new commit lists EVERY file you edited. A missing file is a missed `git add`, and it ships broken to production. The commit MESSAGE must describe that diff — if a `&&`-chained `git add ... && git commit` aborted with "nothing to commit", an earlier command already committed; read `git log` before retrying or the retry commits leftovers under a stale message from a previous step.
- `git diff --check` passes before staging a bulk text edit. Trailing whitespace on a touched line — even in an archived doc — fails the gate and stalls the commit; strip it in the source rather than bypassing the check. A new blank line at end-of-file reports as `new blank line at EOF` and is the usual failure when a patch appends a comment to a small config file; delete the trailing blank line rather than relaxing the gate.
