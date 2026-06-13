# Security

## 🔒 This Repo Has Been Security-Audited

**Last audit:** 2026-06-13
**Commit:** e62a67d

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
