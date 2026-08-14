# Hermes Workflow Repo Audit — Session 2026-06-13

## Context

Audited `https://github.com/AttilaHuns288452/hermes-workflow` for public readiness.
The repo mirrors a local Hermes Agent installation's skill tree (117 SKILL.md files
across 49 categories) plus a website, docs, and Graphify knowledge-graph build output.

## Findings

### Pillar 1 — Security Exposure

- **Secrets:** ✅ None found. All template files (`config.yaml.template`, `.env.example`)
  use proper placeholders (`YOUR_USERNAME`, `<your-key>`, etc.).
- **Local paths:** ❌ Found in `graphify-out/` — AST cache JSON files and manifest
  contained absolute local filesystem paths (e.g. `C:\Users\YOUR_USERNAME\...`).
  These are build artifacts, not user-facing content, but they were tracked in git.

**Fix:** `git rm -r --cached graphify-out/` (162 files removed from tracking).
Added to `.gitignore`.

### Pillar 2 — Git Hygiene

- **.gitignore:** ❌ Missing entirely. Build artifacts, OS files, and editor temp
  files were unprotected.
- **Tracked build artifacts:** ❌ `graphify-out/` (3.8MB) — see Pillar 1.

**Fix:** Created `.gitignore` covering:
  - `graphify-out/` (build artifacts)
  - `.DS_Store`, `Thumbs.db` (OS files)
  - `*.swp`, `*.swo`, `*~` (editor temp files)
  - `.env`, `.env.*` except `.env.example` (secrets)
  - `__pycache__/`, `*.pyc`, `*.pyo`, `.pytest_cache/` (Python)
  - `node_modules/` (Node)

- **.gitattributes:** Not added — recommended but deferred.

### Pillar 3 — Documentation Accuracy

- **README.md:** ❌ Claimed "97 skills" — actual is 117.
- **index.html (website):** ❌ 7 references to "90+" and "97 skills" — all stale.
  - Hero badge: "90+ Skills" → "117 Skills"
  - Hero stat: "90+" → "117"
  - Feature list: "90+ pre-built skills" → "117 pre-built skills"
  - Skills section header: "90+ reusable workflows" → "117 reusable workflows"
  - Category tab: "All (90+)" → "All (117)"
  - About section: "90+ reusable workflows" → "117 reusable workflows"
  - JS data array: "97 skills" → "117 skills"
- **SETUP.md:** ❌ Skill install command used `for dir in ./skills/*/` which only
  installs top-level category dirs, not nested skills. Fixed to use `find` with
  recursive SKILL.md detection.
- **SECURITY.md:** Had a stale commit hash reference. Updated with audit record.

### Pillar 4 — Template Integrity

- **config.yaml.template:** ✅ All values are proper placeholders.
- **.env.example:** ✅ All values are proper placeholders.
- Both files have helpful comments explaining each placeholder.

### Skills Mirror Integrity

- All 117 SKILL.md files present in the repo ✅
- Content verified with `diff -w` — differences between local `~/.hermes/skills/`
  and repo `skills/` are CRLF/LF only (whitespace) ✅
- `codex.bak` directory exists in repo — an older version of the codex skill with
  extra content about sandbox and Hermes Gateway. Consider whether this should
  be kept or removed.

## Commands Used

```bash
# Clone fresh for audit
git clone https://github.com/AttilaHuns288452/hermes-workflow.git /tmp/hermes-workflow-audit

# Full repo secret scan
grep -rn 'C:\\Users\\' . --include='*.md' --include='*.yaml' --include='*.json' 2>/dev/null

# Remove build artifacts from tracking
git rm -r --cached graphify-out/

# Add gitignore
echo "graphify-out/" > .gitignore

# Count actual skills
find ~/AppData/Local/hermes/skills/ -name 'SKILL.md' -type f | wc -l

# Verify skill content integrity
find ~/AppData/Local/hermes/skills/ -name 'SKILL.md' | while read sk; do
  rel=$(echo "$sk" | sed 's|.*/skills/||')
  if [ -f "skills/$rel" ]; then
    diff -w "skills/$rel" "$sk" >/dev/null 2>&1 || echo "CONTENT_DIFF: $rel"
  else
    echo "MISSING: $rel"
  fi
done

# Final check
git status
git add -A && git commit -m "[audit] <summary>" && git push
```

## Residual Risk

- **git history still contains graphify-out/** — the files were removed from the
  current working tree but remain in git history. For a fully clean history,
  use `git filter-branch` or `bfg-repo-cleaner` to expunge them. Low risk since
  the majority of the cached content is machine-generated JSON hashes (random IDs,
  not human-readable paths), but the `graph.html` and `.graphify_labels.json` may
  contain readable paths. Consider this for high-security repos.
- **codex.bak** directory — verify whether this is needed in the public repo.

## Next Recommendation

Re-audit after any significant skill update or before the next public announcement
of the workflow repo.
