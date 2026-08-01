# Session Audit Example — hermes-workflow (June 2026)

This file documents a real security audit run against a Hermes Agent ecosystem repo. Use it as a concrete reference for the expected output format, findings, and remediation patterns.

## Repo Profile
- **Repo**: hermes-workflow (plugin-play Hermes Agent setup mirror)
- **Stack**: Markdown (skills), HTML/CSS/JS (website), GH Pages
- **Clone**: `git clone https://github.com/AttilaHuns288452/hermes-workflow.git /tmp/hermes-security-audit`
- **State**: 843 files, 162 graphify-out artifacts, 137 skills (49 categories)

## Audit Commands (Reproducible)

```bash
# Step 1: Check .gitignore
cat /tmp/hermes-security-audit/.gitignore 2>&1 || echo "MISSING"

# Step 2: Scan for secrets
grep -rnE '(sk-[A-Za-z0-9]{20,}|sk_live_|sk_test_|rk_live_|service_role|SUPABASE_SERVICE_ROLE|STRIPE_SECRET|PAYMONGO_SECRET|ALPHAVANTAGE_API_KEY|TWELVE_DATA_API_KEY)' /tmp/hermes-security-audit/ --include='*.{ts,tsx,js,json,yaml,yml,toml,sh,py,md}' 2>/dev/null
grep -rnE 'BEGIN (RSA )?(PRIVATE|EC) KEY' /tmp/hermes-security-audit/ 2>/dev/null
grep -rnE '(postgresql://[^:]+:[^@]+@|mongodb\+srv://[^:]+:[^@]+@|mysql://[^:]+:[^@]+@)' /tmp/hermes-security-audit/ 2>/dev/null

# Step 3: Check tracked .env files
git -C /tmp/hermes-security-audit ls-files | grep '\.env'

# Step 4: Check tracked build artifacts
git -C /tmp/hermes-security-audit ls-files | grep -E '(graphify-out/|\.next/|dist/|build/|out/)' | wc -l

# Step 5: Check for hardcoded connection strings, JWT secrets
grep -rnE '(JWT_SECRET|NEXTAUTH_SECRET|APP_SECRET)\s*[=:]\s*["\x27]?[A-Za-z0-9_\-]{16,}' /tmp/hermes-security-audit/ --include='*.{ts,tsx,js,json,yaml,yml,toml,sh}' 2>/dev/null

# Step 6: Check for stale hardcoded counts
grep -rnE '(skills|SKILL).*[0-9]{2,}' /tmp/hermes-security-audit/ --include='*.md' --include='*.html' 2>/dev/null | grep -v '90+ languages\|90.*min\|979\|1297\|697\|397\|122 KB'
```

## Audit Findings (Real)

```
PUSH STATUS: REVIEW NEEDED

🔴 CRITICAL (1)
  - skills/workflow/free-ai-model-router/references/freellmapi-setup.md:239
    → Hardcoded FreeLLMAPI bearer token in Python code example
    → Replace with placeholder: `"freellmapi_unified_api_key_here"`

🟠 HIGH (2)
  - graphify-out/ (162 tracked files)
    → Build artifacts (1.9MB graph.json, 1.7MB AST cache) tracked in git
    → Add `graphify-out/` to .gitignore, then `git rm -r --cached graphify-out/`
  - .gitignore MISSING
    → File doesn't exist in repo root
    → Create with: graphify-out/, .env*, node_modules/, __pycache__/, etc.

🟡 MEDIUM (1)
  - skills/decide/SKILL.md + dashboard.html
    → Stale hardcoded skill counts (97 instead of actual 137)
    → Update to match: find skills/ -name "SKILL.md" | wc -l

🔵 INFO (3)
  - .env.example exists ✓
  - LICENSE present (MIT) ✓
  - README.md exists ✓
```

## Remediation Commands

```bash
# 1. Redact the leaked token
sed -i 's/62693564-b5c7-4b32-8b3a-a6a9/freellmapi_unified_api_key_here/' skills/workflow/free-ai-model-router/references/freellmapi-setup.md

# 2. Create .gitignore (use heredoc from terminal, not write_file — avoids Windows path mismatch)
cat > .gitignore << 'GITEOF'
graphify-out/
.env*
!.env.example
node_modules/
__pycache__/
*.pyc
Thumbs.db
.DS_Store
*.swp
*.swo
GITEOF

# 3. Remove graphify-out from tracking
git rm -r --cached graphify-out/

# 4. Fix stale counts
sed -i 's/97 skills/117 skills/g' skills/decide/SKILL.md
sed -i 's/total:97,/total:137,/' dashboard.html

# 5. Verify .gitignore is effective
git status --short       # graphify-out files should show as deleted (D) not untracked (??)
git ls-files graphify-out/ | wc -l   # Should be 0 after commit
```

## Windows Path Divergence

When working on Windows, file paths resolve differently between tools:

| Tool | `/tmp/` resolves to | Used for |
|------|--------------------|----------|
| `terminal` (git-bash) | `C:\Users\<user>\AppData\Local\Temp\` | git, grep, sed, bash commands |
| `write_file` / `patch` (Python) | `C:\tmp\` (or `C:\Users\<user>\AppData\Local\Temp\` if using os.environ TEMP) | File content writes |

**Fix**: Do ALL repo work from a single tool to avoid path divergence:
- Write files (including .gitignore) via `terminal > heredoc` from within the repo directory
- OR pass explicit `C:\Users\...\AppData\Local\Temp\...` paths to write_file
- Verify with `realpath` or `pwd` in terminal before writing files

##  Verification After Commit

```bash
# Verify the remote is clean
curl -s "https://api.github.com/repos/OWNER/REPO/contents/.gitignore" | head -5
git ls-remote origin HEAD
```
