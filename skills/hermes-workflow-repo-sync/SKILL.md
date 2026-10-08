---
name: hermes-workflow-repo-sync
description: "Use when syncing/checking the hermes-workflow GitHub repo."
---

# hermes-workflow repo sync

The public repo is the shareable mirror of the user's Hermes Agent setup — their stated intent for it. Coding/software-dev skills are the headline content; zero real secrets is a hard gate.

- Repo: `github.com/AttilaHuns288452/hermes-workflow`, branch **master** (not main — `origin/main` throws ambiguous-argument).
- Canonical working copy: `~/Documents/Projects/hermes-workflow`. Other copies (e.g. `~/Documents/SkillReferences/hermes-workflow`) are read-only mirrors — never write to them, update via git pull only.

## Sync procedure (live → repo)

1. Freshness: `git fetch origin && git status -sb` — no ahead/behind means up to date.
2. Find missing live skills: `comm -23 <(ls ~/.hermes/skills/ | sort) <(ls skills/ | sort)`. Sync is **one-way live→repo**: the ~200 extra repo dirs are vendored external ecosystems (ECC, superpowers, design kits) — leave them, and never copy them back into `~/.hermes`.
3. Copy each missing dir: `cp -r ~/.hermes/skills/<name> skills/`. Gate the push with `python3 scripts/audit_skills.py` — duplicate-name WARNs ("vendored upstream vs curated copy") are allowed; FIX-level errors block the push.
4. Secret scan before every push: grep the tree for key shapes (`sk-[A-Za-z0-9]{20,}`, `ghp_`/`gho_`, `xox`, `AKIA`, `am_sk_`, `AIza`, `glpat`), excluding noise like `example|<your|REDACTED`. Every hit must be a placeholder, a scanner regex, or doc prose — never a live key. (Live tokens once shipped in git history and needed filter-repo + rotation; scan prevents a repeat.)
5. Update the skill-count prose after ANY skill-count change. The counts are hand-maintained — no generator exists. Grep the OLD count across `README.md SETUP.md SKILLS_CATALOG.md index.html src/App.jsx src/data-skills.json` and replace; SKILL-file count ≠ top-level-dir count, update both everywhere they appear together (badge, hero, table, tree diagram, checklist). SKILLS_CATALOG's per-skill entries are curated prose — update counts only, never regenerate the file.
6. Rebuild the site: `npm run build` (Vite outputs to `docs/`). Verify the new count actually appears in the fresh `docs/assets/index-*.js`, commit all, push.
7. GitHub Pages CDN serves stale builds for ~2-3 min after push — cache-bust (`?cb=<timestamp>`) when QAing the live site, or it false-fails.

## Coverage checklist ("does the repo reflect my setup?")

- `comm -23` output empty (all live skills present), especially the dev cluster: software-development, development, debugging, tdd, code-review, language-pattern skills — plus flagship personal skills like ponytail.
- Layer-stack files exist: `skills/decide/`, `META_PROMPT.md`, `skills/workflow/token-saver/`, `skills/core-identity-guard/`, `skills/subagent-delegation/`, `skills/verification-before-completion/`.
- Counts in README/SETUP/site match real `find skills -name SKILL.md | wc -l` and `ls skills/ | wc -l`.

## Pitfalls

- CRLF→LF warnings on `git add` come from Windows-origin files and are harmless — do not chase them.
- When adding a new live skill, create it FLAT in `~/.hermes/skills/<name>/` (no category subdir) so the flat `ls` diff in step 2 keeps seeing it.
