# hermes-workflow

Serious personal project (see projects_registry.json). Follow the global engineering guidelines from AGENTS.md conventions in this environment.

## Security Gate — CyberSecurity Skill Collection (2026-08-29)

Before ANY auth, session, secret, upload, backup, or infrastructure change — and before shipping any user-facing or money-touching feature — run the relevant review from the **Claude-Code-CyberSecurity-Skill** collection (installed at `C:/Users/Attila/skills-external/claude-code-cybersecurity/skills/`). Load the matching `SKILL.md` by path:

- `09-web-security` — OWASP Top 10, auth/session, API security, headers (default gate for web work)
- `10-cloud-security` — Vercel/Supabase/infra posture
- `16-ai-llm-security` — AI features, MCP endpoints, prompt-injection surface
- `02-vulnerability-scanner` — dependency & vulnerability triage (CVSS/EPSS/CISA KEV)
- `15-blue-team-defense` — system/app hardening checklists
- `07-incident-response` — if anything leaks, breaks in, or is exposed

Defensive use only. Findings follow the standard flow: fix at root cause → validate (tsc/build/tests/browser) → ECC review → deploy → production verify.
