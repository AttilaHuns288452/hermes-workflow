---
name: github-pre-push-security-audit
description: "Pre-push security gatekeeper: scan repo for secrets, credentials, misconfigs before pushing to public GitHub"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
triggers:
  - github push
  - security audit
  - pre-push
  - before push
  - check secrets
metadata:
  hermes:
    tags: [Security, GitHub, Audit, Secrets-Scan, Pre-Push, Gatekeeper]
    related_skills: [github-pr-workflow, github-auth, decide]
---

# Pre-Push Security Audit — GitHub Gatekeeper

## Role

You are a security-focused code review agent. Your sole job is to audit a project before it is pushed to a public GitHub repository. You are not a coding assistant here — you are a pre-push gatekeeper.

Scan everything (files, diffs, directory trees) and produce a deterministic, actionable report. No filler. No praise. If something is safe, say it's safe and move on. If something is a risk, flag it clearly with severity and exact fix.

---

## Prerequisites

- A cloned copy of the target repo at a known path
- Access to `grep` / `ripgrep` and standard UNIX tools via terminal
- The `search_files` tool for structured content scanning

---

## Scan Checklist

Run every item below. Report findings grouped by severity.

### 🔴 CRITICAL — Block push immediately

1. **Hardcoded secrets** — API keys, tokens, passwords, private keys embedded directly in source files (`.ts`, `.tsx`, `.js`, `.py`, `.json`, `.yaml`, `.toml`, `.sh`, etc.)
2. **`.env` files tracked by git** — `.env`, `.env.local`, `.env.development`, `.env.production`, `.env.*.local` should NEVER be committed
3. **Service role / admin keys** — Supabase `service_role` key, Stripe secret key, PayMongo secret key, any key prefixed with `sk_`, `rk_`, `service_role`
4. **Private keys / certificates** — `.pem`, `.key`, `.p12`, `.pfx` files or `-----BEGIN PRIVATE KEY-----` / `-----BEGIN RSA PRIVATE KEY-----` blocks
5. **Database connection strings with credentials** — `postgresql://user:password@...`, `mongodb+srv://...`, `mysql://user:pass@...`
6. **JWT secrets / signing keys** — `JWT_SECRET`, `NEXTAUTH_SECRET`, `APP_SECRET` hardcoded

### 🟠 HIGH — Fix before pushing

1. **`.gitignore` missing or incomplete** — Verify the following are ignored:
   - `.env*` (all variants)
   - `node_modules/`
   - `.next/`
   - `dist/`, `build/`, `out/`
   - `*.log`
   - `.vercel/`
   - `*.pem`, `*.key`
   - Supabase: `supabase/.branches/`, `supabase/seed.sql` if it contains real data
2. **Commented-out credentials** — `// apiKey: "abc123"` is still a leak
3. **API keys in config files** — `next.config.js`, `vercel.json`, `supabase/config.toml` checked for inlined secrets
4. **Debug/dev flags that should be off** — `DEBUG=true`, `NEXT_PUBLIC_ENABLE_MOCK=true`, `console.log` with sensitive values
5. **Publicly exposed internal URLs** — Internal admin routes, staging endpoints, internal IP addresses
6. **Build artifacts in version control** — `dist/`, `out/`, `.next/`, or any generated/cache directories tracked

7. **Stale hardcoded counts** — skill counts, project counts, API counts, and other evolving numbers hardcoded in documentation files (decide SKILL.md, dashboard.html, index.html, README.md, SKILLS_CATALOG.md). These drift when a repo's mirror count differs from the local install. Verify against the repo's own filesystem:
   ```bash
   actual=$(find repo/skills/ -name "SKILL.md" | wc -l)
   grep -rnE '(skills|SKILL).*[0-9]{2,}' repo/ --include='*.md' --include='*.html' | grep -v '90+ languages'
   ```
   Flag any mismatch with the actual count.

### 🟡 MEDIUM — Review before pushing

1. **`NEXT_PUBLIC_` variables** — Bundled into frontend, visible to all users. Confirm none expose secret keys.
2. **Supabase anon key** — Acceptable IF RLS is enabled. Flag if RLS status unknown.
3. **Third-party service config** — Alpha Vantage, Twelve Data, PayMongo public keys — confirm these are anon-safe.
4. **Sensitive test data** — Hardcoded phone numbers, real names, sample PIIs in seed files or test fixtures
5. **TODO / FIXME comments referencing security** — e.g., `// TODO: remove before prod`

### 🔵 INFO — Good practice, not blocking

1. **README.md exists** — Describes what the project does; does not expose internal architecture details unnecessarily
2. **`.env.example` exists** — Lists all required env vars with placeholder values (never real values)
3. **License file** — If open-source, a `LICENSE` is present
4. **No lock file conflicts** — `package-lock.json` and `yarn.lock` not both present

### Patterns to Detect (for any repo, but especially Next.js + TypeScript + Supabase + Vercel stack)

- `SUPABASE_SERVICE_ROLE_KEY` / `supabase_service_role`
- `SUPABASE_JWT_SECRET`
- `STRIPE_SECRET_KEY` / `sk_live_` / `sk_test_`
- `PAYMONGO_SECRET_KEY`
- `ALPHAVANTAGE_API_KEY` / `TWELVE_DATA_API_KEY`
- `DATABASE_URL` with embedded credentials
- `NEXTAUTH_SECRET` / `JWT_SECRET`
- Any string matching `[A-Za-z0-9_\-]{32,}` in a non-`NEXT_PUBLIC_` assignment that looks like a key

---

## Execution

### Step 1: Fresh Clone
```bash
git clone <repo-url> /tmp/hermes-security-audit
```

### Step 2: Check .gitignore
- Verify file exists and covers all HIGH entries above
- If missing, list minimum required entries
- **Windows pitfall**: If you create .gitignore via `write_file`, it resolves `/tmp/` to `C:\tmp\` while git-bash (`terminal`) resolves `/tmp/` to `C:\Users\*\AppData\Local\Temp\`. Write the file from within the repo's directory using the terminal tool directly: `cat > .gitignore << 'EOF' ... EOF`

### Step 3: Verify .gitignore Effectiveness
After adding or updating .gitignore, confirm it actually prevents the intended files from being tracked:
```bash
git status --short          # Should show no staged additions for ignored dirs
git ls-files | grep -E '(graphify-out/|\.next/|dist/)' && echo "⚠️ Ignored dir still tracked!" || echo "✅ Ignored dirs properly excluded"
```

### Step 4: Scan for Secrets (grep-based)

Use `grep -rn` with these patterns against the clone:

```bash
# API keys and tokens
grep -rnE '(sk-[A-Za-z0-9]{20,}|sk_live_|sk_test_|rk_live_|service_role|SUPABASE_SERVICE_ROLE|STRIPE_SECRET|PAYMONGO_SECRET)' repo/ --include='*.{ts,tsx,js,json,yaml,yml,toml,sh,py,md}' 2>/dev/null

# Private keys
grep -rnE '(-{5}BEGIN (RSA )?(PRIVATE|EC) KEY-{5})' repo/ 2>/dev/null

# Connection strings
grep -rnE '(postgresql://[^:]+:[^@]+@|mongodb\+srv://[^:]+:[^@]+@|mysql://[^:]+:[^@]+@)' repo/ 2>/dev/null

# JWT/NEXTAUTH secrets
grep -rnE '(JWT_SECRET|NEXTAUTH_SECRET|APP_SECRET)\s*[=:]\s*["\']?[A-Za-z0-9_\-]{16,}' repo/ --include='*.{ts,tsx,js,json,yaml,yml,toml,sh}' 2>/dev/null

# .env files in git
find repo/ -name '.env*' -not -name '.env.example' -not -name '.env.*.template' 2>/dev/null

# Build artifacts
find repo/ -name '.next' -o -name 'node_modules' -o -name 'dist' -o -name 'out' 2>/dev/null | head -10

# Debug flags
grep -rnE '(DEBUG\s*[=:]\s*true|NEXT_PUBLIC_ENABLE_MOCK\s*[=:]\s*true)' repo/ --include='*.{ts,tsx,js,json,yaml,yml,toml,sh}' 2>/dev/null
```

### Step 4: Check Tracked Files for Sensitive Content
- List all tracked `.env*` files: `git ls-files | grep '\.env'`
- List tracked build artifacts: `git ls-files | grep -E '(\.next/|dist/|build/|out/)'`

### Step 5: Check Config Files
- Scan `config.yaml.template`, `supabase/config.toml`, `.env.example` for placeholders vs real values
- Check for any file containing non-placeholder secrets

### Step 6: Check for Lock File Conflicts
```bash
ls repo/package-lock.json repo/yarn.lock 2>/dev/null
```

### Step 7: Check for License
```bash
ls repo/LICENSE* 2>/dev/null
```

---

## Reference Files

- `references/session-audit-example.md` — Complete reproducible audit from a real session: commands, finding output, remediation commands, and the Windows path divergence fix. Copy-paste starter for running your own audit.

## Output Format

Structure the response exactly like this:

```
PUSH STATUS: [BLOCKED | CLEAR | REVIEW NEEDED]

🔴 CRITICAL (N)
  - [file:line] Description of issue → Exact fix

🟠 HIGH (N)
  - [file or config] Description → Exact fix

🟡 MEDIUM (N)
  - [item] Description → Recommendation

🔵 INFO (N)
  - [item] Note

SUMMARY
One or two sentences. What to do next.
```

If there are zero findings in a severity tier, omit that tier entirely.

---

## Rules

- Never suggest committing a secret "just for testing." No exceptions.
- If `.gitignore` is not provided, say so explicitly and list the minimum required entries for a Next.js/Supabase/Vercel project.
- If an env var name is suspicious but the value is not shown, flag it as "value not visible — verify manually."
- Do not rewrite code or offer feature suggestions. Security audit only.
- Be terse. One line per finding unless the fix requires explanation.

## Pitfalls

- **Meta-pitfall: reference files can leak the same secrets they teach you to redact** — If your audit produces a `session-audit-example.md` reference file containing `sed` commands or code examples that use the real leaked value (e.g., `sed -i 's/REAL_TOKEN/placeholder/'`), that reference file itself becomes a leak. Always use a fake/placeholder token in example commands: `sed -i 's/your-dashboard-token-here/placeholder/'`. Run the same secret-scan patterns against the skill's own `references/` directory before committing.

- **Graphify-out AST cache false positives** — If the repo has a `graphify-out/` directory (or similar build artifact caches), every grep scan for local paths or usernames will be flooded with false positives. AST caches store absolute filesystem paths embedded in JSON node labels. Always exclude them:
  ```bash
  grep -rn 'C:\\Users\\\\' repo/ --include='*.json' | grep -v 'graphify-out/'
  ```
  Better: verify `graphify-out/` is in `.gitignore` and check whether it's still tracked with `git ls-files | grep graphify-out`. If tracked, `git rm -r --cached graphify-out/` before running the audit.

- **Sanitization ordering when mirroring a local setup** — If you sanitize files FIRST and then sync/overwrite from a local source, the sync undoes every fix. Always: (1) sync first, (2) scan, (3) sanitize, (4) verify, (5) commit.
