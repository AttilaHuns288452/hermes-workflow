---
name: public-repo-readiness
description: Audit AND enhance a GitHub repository for public-readiness — security exposure (secrets, local paths), .gitignore hygiene, documentation accuracy (README claims matching reality), README & website improvement, template/placeholder verification, and file consistency checks. Use when the user asks "is my repo safe to make public?", "clean up my repo before publishing", "audit my repo for secrets", "verify my repo is ready for public contributors", or "improve the README and website".
version: 1.0.0
author: Hermes Agent
user-invocable: true
triggers:
  - audit repo
  - public repo
  - repo security
  - repo readiness
  - repo safe to publish
  - improve repo
  - enhance repo
  - improve readme
  - repo website
metadata:
  decide:
    keywords: [audit, public, repo, security, readiness, gitignore, secret, publish, github, cleanup, improve, enhance, readme, website, github pages]
    domain: software-development
    confidence: high
---

# Public Repo Readiness Audit

Systematic audit of a GitHub repository before making it public or after significant updates. Covers four pillars: **security exposure**, **git hygiene**, **documentation accuracy**, and **template integrity**.

## When to Use

- User asks "Is my repo safe to make public?"
- User asks "Audit my repo for secrets / local paths"
- User asks "Clean up my repo before sharing"
- Before opening a private repo to public access
- After mirroring local configuration into a public repo (e.g., Hermes skills mirror, dotfiles repo, config templates)
- Periodic maintenance: "Check my repo is still clean"

## The Four-Pillar Audit

### Pillar 1 — Security Exposure Scan

Scan **every file in the repo** (not just git diffs) for patterns that should never appear in public:

```bash
# 1. Local filesystem paths — the most common leak
# (Windows paths are especially distinctive)
grep -rn 'C:\\Users\\' . --include='*.md' --include='*.yaml' --include='*.yml' --include='*.json' --include='*.toml' --include='*.cfg' --include='*.ini' 2>/dev/null

# 2. Unix home paths
grep -rn '$HOME' . --include='*.md' --include='*.yaml' --include='*.json' 2>/dev/null | grep -v '\.env\.example\|\.gitignore\|README\|SETUP\b'

# 3. API keys and tokens (provider-specific patterns)
grep -rnP '(sk-[a-zA-Z0-9]{20,}|[Aa]pi[_-][Kk]ey[=:]\s*["'\''][a-zA-Z0-9_\-]{16,}|bearer\s+[a-zA-Z0-9_\-]{20,})' . --include='*' 2>/dev/null | grep -v '\.env\.example\|\.gitignore\|node_modules\|\.git/'

# 4. Generic secret/token/password env var values
grep -rnP '(TOKEN|SECRET|PASSWORD|CREDENTIALS)\s*[=:]\s*["'\''][^"'\''\s]{8,}' . --include='*.yaml' --include='*.yml' --include='*.json' 2>/dev/null | grep -v '\.env\.example\|\.gitignore\|YOUR_\|PLACEHOLDER\|<your'

# 5. Local username references
grep -rnP '(C:\\Users\\|/home/|/Users/)' . --include='*' 2>/dev/null | grep -v '\.git/'
```

**One sweep command — personal paths only (most common leak):**
```bash
grep -rn --include='*.py' --include='*.md' --include='*.yaml' --include='*.yml' \
  --include='*.html' --include='*.sh' --include='*.ps1' --include='*.bat' \
  --include='*.json' --include='*.toml' --include='*.cfg' --include='*.ini' \
  -iE '(C:\.Users\\|/home/|/Users/)' . 2>/dev/null \
  | grep -v 'graphify-out/' | grep -v '\.git/' | grep -v 'node_modules/'
```

**One sweep command — API keys / tokens:**
```bash
grep -rn --include='*.py' --include='*.md' --include='*.yaml' --include='*.yml' \
  --include='*.json' --include='*.toml' --include='*.cfg' --include='*.ini' \
  -iE '(sk-[a-zA-Z0-9]{20,}|gh[porsu]_[a-zA-Z0-9]{36,}|AKIA[0-9A-Z]{16})' . 2>/dev/null \
  | grep -v 'graphify-out/' | grep -v '\.git/' | grep -v 'node_modules/' \
  | grep -v 'sk-xxx\|ghp_xxx\|YOUR_\|\.\.\.\|example\|template'
```

**One sweep command — named service remotes:**
```bash
# Check for rclone remote names, docker hub user names, AWS account IDs, etc.
grep -rn --include='*.py' --include='*.md' --include='*.yaml' --include='*.sh' \
  --include='*.ps1' --include='*.bat' \
  -iE '(remote_name\s*=|rclone remote|gdrive:)' . 2>/dev/null \
  | grep -v 'graphify-out/' | grep -v '\.git/' | grep -v 'node_modules/' \
  | grep -v 'my_gdrive\|YOUR_\|example\|placeholder'
```

**Note on file types:** On a Windows-hosted Git Bash, `--include='*.ps1'` and `--include='*.bat'` are critical — PowerShell scripts commonly contain hardcoded remote names and user-specific paths that plain Python/MD scans miss.

**Note on escaping:** When using `sed` to replace Windows paths (which contain backslashes), prefer the `patch` tool over `sed` to avoid escaping nightmares. The `sed` backslash escape chain for a path like `C:\Users\Attila\...` is error-prone:
```bash
# sed: pain (need quadruple escaping for backslashes and brackets)
sed -i 's|C:\\Users\\Attila|$HOME|g' file.md   # may fail on bracket chars

# patch: clean (use the tool directly, not sed via terminal)
patch path="file.md" old_string="C:\Users\Attila\..." new_string="$HOME/..."
```

## The Scan → Fix → Re-Scan Loop

After any bulk operation that modifies files in the repo (sync, merge, bulk find-replace), always close the loop:

```bash
# 1. Full sweep
echo "BEFORE:"
grep -rn --include='*.py' --include='*.md' --include='*.yaml' --include='*.ps1' \
  -iE '(C:\.Users\\|/home/|/Users/)' . 2>/dev/null \
  | grep -v 'graphify-out/' | grep -v '\.git/' | grep -v 'node_modules/'

# 2. Fix everything found (use patch tool per file)

# 3. Re-verify — zero expected
echo "AFTER: should be empty"
grep -rn --include='*.py' --include='*.md' --include='*.yaml' --include='*.ps1' \
  -iE '(C:\.Users\\|/home/|/Users/)' . 2>/dev/null \
  | grep -v 'graphify-out/' | grep -v '\.git/' | grep -v 'node_modules/'
echo "DONE"
```

If the "after" scan still shows hits, those are the files you missed — iterate until zero.

**Note on `.pyc` cache files:** Compiled Python bytecode in `__pycache__/` directories may contain embedded strings (including paths) from the source code. These binary files won't show up in text grep scans. If a `__pycache__/` directory is tracked in git, either:
- `git rm -r --cached __pycache__/ && echo '__pycache__/' >> .gitignore`
- Or use binary grep: `grep -rlaP '[^\x00-\x7F]' __pycache__/ 2>/dev/null` to check for unexpected binary content

**Pillar 1 full checklist:**
- [ ] Personal filesystem paths found and replaced
- [ ] API keys / tokens verified (doc-examples only)
- [ ] Named service remotes (rclone, docker, etc.) sanitized
- [ ] Template files use placeholders only
- [ ] Build artifacts excluded from git tracking
- [ ] `.pyc` / cached files un-tracked
- [ ] Re-verified after every sync/overwrite

**Check build artifacts:**
- Build output directories (`dist/`, `build/`, `.next/`, `graphify-out/`, etc.) often embed local paths
- AST caches, manifest files, JSON databases — all can contain absolute filesystem paths
- If tracked in git, remove them with `git rm -r --cached <dir>` and add to `.gitignore`

### Pillar 2 — Git Hygiene

```bash
# 1. Check .gitignore exists and covers common patterns
cat .gitignore 2>/dev/null || echo "MISSING: .gitignore"

# Essential entries for a config/skills mirror repo:
#   - Build artifacts (graphify-out/, dist/, build/, .next/)
#   - OS files (.DS_Store, Thumbs.db)
#   - Editor temp files (*.swp, *.swo, *~)
#   - Environment/secret files (.env, .env.* except .env.example)
#   - Python cache (__pycache__/, *.pyc)
#   - Node modules (node_modules/)

# 2. Check for tracked build artifacts
git ls-files --cached | grep -E '(graphify-out|dist/|build/|\.next/)' | head -5

# 3. Check for orphan skills (files on disk not in skills_list)
# See Pillar 3 for CRLF/LF consistency

# 4. Check git size
git count-objects -v | grep size-pack

# 5. Check .gitattributes line ending normalization
cat .gitattributes 2>/dev/null || echo "MISSING: .gitattributes (recommended for cross-platform repos)"
```

### Pillar 3 — Documentation Accuracy

Verify all human-facing claims match reality. This is critical because stale docs mislead contributors and create support burden.

**Checklist:**
- [ ] README.md skill count matches actual installed skills
- [ ] README.md project count matches actual projects in repo
- [ ] Website/landing page (index.html) numbers match README
- [ ] Dashboard or catalog pages use the same counts
- [ ] SETUP.md install commands actually work (test the exact command)
- [ ] Quick-start code blocks compile/run
- [ ] Every documented CLI command exists in `--help` output (see Verify Documented Commands below)
- [ ] Feature lists match what's actually in the repo
- [ ] Links to other docs are not broken (check for `file.md` that doesn't exist)

**Get the real count:**
```bash
# Count SKILL.md files
find . -name 'SKILL.md' -type f | wc -l

# Count skill categories (dirs with at least one SKILL.md)
find . -name 'SKILL.md' -type f | xargs -I{} dirname {} | xargs -I{} dirname {} | sort -u | wc -l

# Count sub-skills (nested skill dirs)
find . -name 'SKILL.md' -type f -printf '%h\n' | sed 's|/[^/]*$||' | sort -u | while read dir; do
  count=$(find "$dir" -name 'SKILL.md' -type f | wc -l)
  echo "$dir: $count SKILL.md files"
done
```

**Then diff against all documentation files:**
- README.md — hero description, feature list, dashboard section
- index.html (or website/index.html) — hero stats, feature grid, tab labels, JS data array
- dashboard.html — counts in JS data
- SETUP.md — install commands, step count, tool list
- Any SKILLS_CATALOG.md, INTEGRATION.md, or other overview docs
- Compiled bundles and `legacy/` pages — they embed copies of commands; grep them too (`grep -rn 'hermes run' . --include='*.html' --include='*.js'`)

### Verify Documented Commands Actually Run

Eyeballing commands is not verification — run them in a fresh `git clone --depth 1` against the real CLI:

1. **Subcommand must exist**: `hermes --help` (or `<tool> --help`) lists valid subcommands. Anything absent (e.g. `hermes run`) prints usage and exits non-zero. Docs must use `hermes -z "prompt"` for one-shot prompts.
2. **Non-interactive loops need `-y`**: `hermes skills install <dir>` WITHOUT `-y` prints `Fetching: <dir>` then exits 0 **without installing** — silent abort. Install-all loops must be `hermes skills install -y "$dir"`. Verify by installing one skill with and without `-y` first.
3. **Truncated placeholders break copy-paste**: docs that show `$FREEL..._KEY` (literal ellipsis) fail verification. Grep docs for `...` inside env-var names before shipping.
4. **Fix source, rebuild the site**: if the website embeds commands (e.g. `src/App.jsx`), patch the source then `npm run build` (outDir `docs/`) and commit the rebuilt bundle. Never hand-patch minified JS; `git checkout -- docs/` to discard noise from test builds.
5. **JS/JSX string escaping**: shell commands in single-quoted JS strings lose backslashes — `\;` renders as `;` (breaks `find -exec ... \;`). Source needs `\\;` so the UI shows `\;`.
6. **Package-name vs binary-name**: verify install commands resolve to the right binary — e.g. `uv tool install graphifyy` ships `graphify` + `graphify-mcp`; `npm i -g @colbymchenry/codegraph` ships `codegraph`. Check via `npm view <pkg> bin` / pip `entry_points` rather than assuming the binary name.

See `references/hermes-cli-verified-commands.md` for the tested command table.

**CRLF/LF consistency (for cross-platform repos):**
```bash
# Check if any files have mixed or non-standard line endings
git ls-files --eol | grep -v 'i/lf'
```
If the repo is meant to work on both Windows and Unix, add a `.gitattributes`:
```
* text=auto
*.md text
*.yaml text
*.yml text
*.json text
*.sh text eol=lf
*.ps1 text eol=crlf
```

### Pillar 4 — Template Integrity

For repos that provide template files (`config.yaml.template`, `.env.example`, etc.):

```bash
# Check every template file for real (non-placeholder) values
grep -n 'sk-\|ghp_\|gho_\|ghu_\' .env.example config.yaml.template 2>/dev/null

# Check for placeholder markers
grep -c 'YOUR_\|<your\|CHANGE_ME\|PLACEHOLDER' .env.example config.yaml.template 2>/dev/null
# If count is low (< 3 per file), there may be un-placeholded real values
```

**Fix pattern for any found real values:**
1. Replace the real value with `YOUR_UPPERCASE_DESCRIPTION` or `<lowercase-description>`
2. Add a comment explaining where to get the real value

## Special Cases

### Hermes Workflow Mirror Repos

When the repo is a mirror of a Hermes Agent skill installation:

1. **Graphify build artifacts** (`graphify-out/`) — these contain absolute local filesystem paths in AST cache JSON blobs. Add to `.gitignore` and `git rm --cached` if already tracked.

2. **Skill mirror integrity** — verify every SKILL.md from local `~/.hermes/skills/` is mirrored in the repo, and check reference files for merge-necessary divergence:
   ```bash
   # Check SKILL.md content differences (whitespace-only diffs are safe)
   find ~/AppData/Local/hermes/skills/ -name 'SKILL.md' | while read sk; do
     rel=$(echo "$sk" | sed 's|.*/skills/||')
     if [ -f "skills/$rel" ]; then
       if ! diff -w "skills/$rel" "$sk" >/dev/null 2>&1; then
         echo "CONTENT DIFF: skills/$rel"
       fi
     else
       echo "MISSING FROM REPO: skills/$rel"
     fi
   done

   # Check reference files for merge-necessary divergence
   # (both sides may have unique content that needs combining)
   for skill_dir in skills/*/*/; do
     skill_rel=$(echo "$skill_dir" | sed 's|^skills/||;s|/$||')
     for subdir in references scripts templates assets; do
       local_dir="$HOME/AppData/Local/hermes/skills/$skill_rel/$subdir"
       repo_dir="skills/$skill_rel/$subdir"
       if [ -d "$local_dir" ] && [ -d "$repo_dir" ]; then
         content_diffs=$(diff -rq "$local_dir" "$repo_dir" 2>/dev/null | grep 'differ$' || true)
         if [ -n "$content_diffs" ]; then
           echo "MERGE NEEDED: $skill_rel/$subdir — files differ in content"
         fi
       fi
     done
   done
   ```
   When reference files diverge (e.g., local has new security warnings, repo has redacted secrets):
   - Copy the local version to the repo first (preserves local content additions)
   - Then apply any security redactions that only exist in the repo version

3. **CRLF/LF differences** — the local Hermes install may use CRLF (Windows) while the repo uses LF. Content is identical; only whitespace differs. Verify with `diff -w`.

4. **Config templates** — `config.yaml.template` must use placeholders like `YOUR_USERNAME`, `YOUR_VAULT_PATH`, not real values. Same for `.env.example`.

### Dotfiles Repos

- Check `~/.gitconfig`, `~/.bashrc`, `~/.zshrc` for any token values
- Ensure SSH config uses placeholders for hostnames/IPs
- Check shell history files for inline credentials

## Pillar 5 — README & Website Enhancement

When the user asks to improve a GitHub repo's README or GitHub Pages website, follow this workflow:

### Discovery Phase

Scrape the live README, website source files, and key code files (App.jsx, index.css, package.json, vite.config.js) before changing anything. Get the full picture of current claims, structure, and build config.

### README Enhancement

Update README when new integrations or capabilities are added:

- **Hero section** — update count/summary lines
- **New sections** — add dedicated integration sections with what-it-does, key capabilities, model/routing assignments
- **Quick Start + Built With** — keep current

### Website Enhancement (React + Tailwind / Vite → docs/)

**Adding a new section:**
1. Create `src/data-<topic>.json` with structured content
2. Add a React component in `src/App.jsx` using existing patterns (Reveal, spotlight-card, premium-card, eyebrow badge, category colours)
3. Import the data file at top of App.jsx
4. Add `<Section />` to the main `<main>` render
5. Update OG meta tags in `index.html`

**Vite entry handling (CRITICAL):** If root `index.html` references built assets (`assets/index-*.js`) instead of source (`/src/main.jsx`), rewrite it to the proper Vite dev entry format keeping all OG meta tags and font preloads.

**Build & Deploy:**
```bash
npm install && npm run build    # outputs to docs/
cp docs/index.html index.html   # sync root for GH Pages
git add -A && git commit -m "<section>" && git push
```

### Design Patterns to Follow

- **Dark theme** — `#080b14` surface, `#e4eaf5` text, `#8895b8` secondary
- **Glass cards** — `spotlight-card` / `premium-card` classes with radial hover glow
- **Reveal** — `Reveal` component (IntersectionObserver fade-up)
- **Section structure** — `section-pad`, `eyebrow` badge, gradient heading
- **Icons** — inline SVG (Lucide-style), no extra deps
- **Category colours** — green `#3ddc84`, purple `#9b7cf7`, cyan `#6bc5e8`, gold `#f0d060`, rose `#e4686a`, blue `#4a8cf4`
- Use `patch` (not sed) for React source edits
- No motion libs unless asked — IntersectionObserver covers it
- OG description should mention new integrations
- Shallow clone with `--depth 1` for repos with 2000+ files

### Verification

```bash
npm run build   # check no errors
cp docs/index.html index.html
git push
# Wait ~30s then scrape live GH Pages URL to confirm
```

## ⚠️ Critical Pitfalls

### Pitfall 1: Sanitization Ordering — Sanitize After Sync, Not Before

When mirroring a local setup (skills, scripts, configs) into a public repo, the ordering of operations matters enormously:

**WRONG ORDER:**
1. Sanitize files (remove personal paths, secrets) ← Gets overwritten
2. Sync/overwrite from local source ← **Undoes all your fixes**
3. Commit → **Leaks personal data**

**CORRECT ORDER:**
1. Sync/overwrite from local source first
2. Re-run the full security scan (Pillar 1)
3. Sanitize any newly-introduced personal paths
4. Verify doc counts match new reality (Pillar 3)
5. Commit

This is especially dangerous with **`cp`-based syncs** where you copy entire skill directories. Every `cp` that overwrites a sanitized file re-introduces the leak. After syncing, always re-run the grep scans from Pillar 1 before committing.

**Concrete `cp` overwrite scenario:**
```bash
# You spent 30 minutes sanitizing skills/productivity/mcp-integrations/SKILL.md
# Then you do:
cp -r /c/Users/Attila/AppData/Local/hermes/skills/* repo/skills/
# ↑ This overwrites your sanitized SKILL.md with the original containing paths
# You must re-sanitize after every such copy
```

**The fix loop:**
```bash
# 1. Sync (copies everything, overwriting sanitized files)
cp -r "$SOURCE/skills/"* "$REPO/skills/"
cp -r "$SOURCE/scripts/"* "$REPO/scripts/"

# 2. Scan immediately
grep -rn --include='*.py' --include='*.md' --include='*.yaml' --include='*.html' --include='*.sh' --include='*.ps1' \
  -iE '(/Users/|/home/|C:\.Users\\)' . 2>/dev/null \
  | grep -v 'graphify-out/' | grep -v '\.git/' | grep -v 'node_modules/'

# 3. Sanitize all findings
# 4. Re-verify (zero findings expected)
# 5. Commit
```

### Pitfall 2: Graphify AST Cache False Positives

The `graphify-out/cache/ast/` directory contains JSON dumps of code ASTs. These embed **absolute filesystem paths** in node labels (e.g., `"id": "c_users_attila_documents_projects_..."`). When running grep-based scans for local paths:

```bash
# BAD — produces hundreds of false positives from AST cache
grep -rn 'C:\\Users\\\\' . --include='*.json'

# GOOD — exclude graphify-out from the scan
grep -rn 'C:\\Users\\\\' . --include='*.json' | grep -v 'graphify-out/'
```

The directory is already `.gitignore`-safe (build artifact), but grep scans against the checked-out repo will flag every AST node containing a username. Always exclude `graphify-out/` from path-based grep scans, or strip the directory with `git rm -r --cached graphify-out/` and re-scan.

### Pitfall 3: Post-Sync Static Count Drift

After syncing skills into a mirror repo, the skill count changes. Every static file that hardcodes a number will be wrong. Search and fix across ALL of these:

```bash
files_with_counts=(README.md SETUP.md index.html dashboard.html)
for f in "${files_with_counts[@]}"; do
  if [ -f "$f" ]; then
    old_count=$(grep -oP '(?<=\b)[0-9]{2,}(?=\s*(Skills|skills|SKILL))' "$f" 2>/dev/null || echo 0)
    echo "$f: claims $old_count"
  fi
done
actual=$(find skills/ -name 'SKILL.md' | wc -l)
echo "Actual: $actual"
```

The most common stale references are `<div class="num">SKILL_COUNT</div>` in HTML hero stats, and `(SKILL_COUNT total)` in SETUP.md step headers. The `sed` pattern above handles most cases but always verify after running it.

## Fix Workflow

For each issue found, apply fixes in this order:

1. **Secrets / paths** → Replace with placeholder, commit asap (treat as security incident)
2. **Gitignore gaps** → Add entry to `.gitignore`, `git rm --cached` if already tracked
3. **Doc inaccuracies** → Update all stale counts/claims across README, website, catalog
4. **Template gaps** → Replace real values with placeholders, add comments
5. **Line ending issues** → Add `.gitattributes` for normalization
6. **Commit message** — include which pillars were audited and what was fixed

## Output

After the audit, provide:

1. **Summary table** — Green/Yellow/Red per pillar with key findings
2. **Details** — specific file paths, line numbers, and fix actions taken
3. **Residual risk** — any issues that couldn't be fully fixed and why
4. **Next audit recommendation** — when to recheck

Example summary:

```
Pillar            Status  Key Finding
──────────────────────────────────────────────
Secret/Path Scan  ✅      No secrets found
Git Hygiene       ⚠️      3.8MB graphify-out/ tracked (FIXED)
Doc Accuracy      ⚠️      7 stale "90+" → "117" count refs (FIXED)
Template Integrity ✅      All placeholders correct
```

## Related Skills
- `security-review` — code-level vulnerability review of git diffs (complementary: use before merging PRs)
- `requesting-code-review` — pre-commit verification pipeline for individual changes
- `setup` — project/tool setup (for setting up repos after cloning)
- `github-repo-management` — repo lifecycle management
- `references/hermes-workflow-repo-audit.md` — session-specific audit results for a Hermes Workflow mirror repo
