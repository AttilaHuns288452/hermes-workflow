---
name: public-repo-readiness
description: Audit a GitHub repository for public-readiness — security exposure (secrets, local paths), .gitignore hygiene, documentation accuracy (README claims matching reality), template/placeholder verification, and file consistency checks. Use when the user asks "is my repo safe to make public?", "clean up my repo before publishing", "audit my repo for secrets", or "verify my repo is ready for public contributors".
version: 1.0.0
author: Hermes Agent
user-invocable: true
triggers:
  - audit repo
  - public repo
  - repo security
  - repo readiness
  - repo safe to publish
metadata:
  decide:
    keywords: [audit, public, repo, security, readiness, gitignore, secret, publish, github, cleanup]
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

**Check template files specifically:**
- `config.yaml.template` — ALL values should be placeholders (`YOUR_NAME`, `<your-key>`, `CHANGE_ME`)
- `.env.example` — ALL values should be placeholders
- Any `.env.*` files should use placeholder values only

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

2. **Skill mirror integrity** — verify every SKILL.md from local `~/.hermes/skills/` is mirrored in the repo:
   ```bash
   # Check for differences (whitespace-only diffs are safe)
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
   ```

3. **CRLF/LF differences** — the local Hermes install may use CRLF (Windows) while the repo uses LF. Content is identical; only whitespace differs. Verify with `diff -w`.

4. **Config templates** — `config.yaml.template` must use placeholders like `YOUR_USERNAME`, `YOUR_VAULT_PATH`, not real values. Same for `.env.example`.

### Dotfiles Repos

- Check `~/.gitconfig`, `~/.bashrc`, `~/.zshrc` for any token values
- Ensure SSH config uses placeholders for hostnames/IPs
- Check shell history files for inline credentials

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
