# Security

## 🔒 This Repo Has Been Security-Audited

**Last audit:** 2026-09-16 (full modernization pass)

- **History rewrite (2026-09-16):** git history contained two real Capafy (`am_sk_…`) access tokens in `skills/capafy-publisher/config.json` and `skills/capafy-user/api-docs/01_auth.md` from earlier skill-mirror syncs. All 5 token-bearing blobs were purged from every commit via `git-filter-repo` (patterns replaced with `***`), and the branch was force-pushed. **Tokens were exposed while public — rotate them at the provider.** Clone caches older than 2026-09-16 still contain the old history.
- **Skill dedupe (2026-09-16):** removed 4 duplicate/misplaced `SKILL.md` files (an `agent-browser` copy inside `skills/vercel/`, a frontmatter-less `karpathy-guidelines` copy, and 2 identical claude-seo mirror copies). Zero duplicate skill names remain in the catalog.
- **2026-08-14:** Removed `graphify-out/` build artifacts (3.8MB) from git tracking — contained local filesystem paths in AST cache JSON files. Added `.gitignore` to prevent re-occurrence.
- **2026-08-14 re-audit:** Re-synced all skills from the live Hermes install, redacted a personal email address (→ `YOUR_EMAIL@gmail.com`) and rclone remote names (→ `YOUR_RCLONE_REMOTE`) found in skill docs/config, regenerated a tracked `.pyc` bytecode cache that embedded the local username in its source path, and added `__pycache__/` to `.gitignore`.

This repository is a public mirror of a Hermes Agent skill ecosystem. The following security measures have been taken:

### ✅ Secrets Scrubbed
All mirrored skill files have been scanned for:
- API keys (OpenAI `sk-*`, FreeLLMAPI, GitHub tokens, OpenRouter, and 16+ provider-specific patterns)
- Authentication tokens and bearer tokens
- Passwords, database credentials, and private URLs
- Hardcoded environment variable values

### 🚫 What Is NOT in This Repo
- Real `.env` files or actual API keys
- Hermes auth credentials
- SSH keys, certificates, or private signing material
- Personally identifying information (beyond what the user's GitHub profile already exposes)

### 🛡️ Pre-Commit Security Gate
Every ecosystem documentation export now runs **Phase 0.5 — Security Audit** before generating docs or committing. This scans all mirrored skill files for >16 provider-specific API key patterns and blocks the commit if any real secrets are detected.

### 🔑 Key Rotation
If you find a real secret in this repo:
1. **Rotate the key** on the service provider immediately
2. **Open an issue** in this repo so the leak location is documented
3. Submit a PR scrubbing the key, or the maintainer will handle it

### Providers Covered by Scanning
OpenAI, Anthropic, Google/Gemini, GitHub (PAT, OAuth, App tokens), Slack, AWS, OpenRouter, HuggingFace, Groq, DeepSeek, Cerebras, Together AI, FreeLLMAPI, and generic bearer tokens.

---

*Security is a process, not a one-time fix. If you notice something suspicious, please open an issue.*
