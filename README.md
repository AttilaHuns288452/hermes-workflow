<div align="center">

# 🧞 Hermes Workflow

**A portable skill ecosystem + routing brain for [Hermes Agent](https://hermes-agent.nousresearch.com) — 1,484 repository skills, one decision layer, and config-driven model routing.**

This repository is licensed under **CC BY-NC 4.0**. It is a public reference and skill collection, not a bundled model provider or a guaranteed runtime environment.

> **Live-state rule:** this public repository is a template and documentation surface. Your installed Hermes profile is authoritative for enabled skills, MCP servers, models, credentials, and subagent availability. Inspect it with `hermes config check`, `hermes config path`, `hermes config env-path`, `hermes mcp list`, and `hermes skills list`.

[![License](https://img.shields.io/badge/license-CC%20BY--NC%204.0-0b0f1c?style=flat&labelColor=0b0f1c&color=7aa9f7)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-1484-4a8cf4?style=flat&labelColor=0b0f1c)](#-skill-catalog)
[![Routing](https://img.shields.io/badge/router-%2Fdecide-3ddc84?style=flat&labelColor=0b0f1c)](META_PROMPT.md)
[![Site](https://img.shields.io/badge/docs-live-9b7cf7?style=flat&labelColor=0b0f1c)](https://attilahuns288452.github.io/hermes-workflow/)
[![Built with](https://img.shields.io/badge/built%20with-Hermes%20Agent-6bc5e8?style=flat&labelColor=0b0f1c)](https://hermes-agent.nousresearch.com)

**What is this?** A portable skill library for Hermes Agent: point Hermes at it, and your agent can discover 1,484 repository skills routed through a decision layer (`/decide`). Actual availability depends on your active profile and installed tools.

**Why?** Skills without routing rot. This repo pairs skills with guidance for deciding *when* they fit. Indexed discovery can reduce unnecessary file reads when the relevant index and MCP are available.

</div>

---

## ✨ What's Inside

| Layer | What it does |
|-------|--------------|
| **🧠 `/decide`** | The routing brain: intent → capability class → skill shortlist → availability probe → execution → verification → recovery. See [`META_PROMPT.md`](META_PROMPT.md). |
| **📚 Skills** | 1,484 repository `SKILL.md` files across engineering, design, finance, media, research, DevOps, and security. Availability still depends on the installed profile. |
| **⚡ Discovery** | Use CodeGraph for indexed project-code discovery and LightRAG for skill/reference lookup when those services are available; neither is assumed to be enabled everywhere. |
| **🛡️ Guardrail** | 6 immutable rules — file protection, secrets safety, injection immunity, system integrity, re-anchoring, safe fallback. |
| **🤝 Delegation** | Subagent orchestration patterns with mandatory read-back verification. |
| **🔍 Verification** | Per-output-type gates: code → tests/build, research → citations, visual → render check. Nothing is "done" unverified. |

## 🚀 Quick Start

> **Prereq:** [Hermes Agent](https://hermes-agent.nousresearch.com) installed (`hermes --version` works).

```bash
git clone https://github.com/AttilaHuns288452/hermes-workflow.git
cd hermes-workflow

# 1. Inspect the active profile, then merge the repo skills path into its external_dirs
hermes config path
hermes config edit
#   skills:
#     external_dirs:
#       - /path/to/hermes-workflow/skills

# 2. Reload and verify
hermes -z "List three skills you can use from the hermes-workflow catalog"

# 3. Try the routing brain
hermes -z "What does the decide skill do?"
```

For profile setup and optional integrations, see [`SETUP.md`](SETUP.md).

## 🏗️ How It Works

```text
User request
     │
     ▼
┌─────────────────────────────────────────────────────┐
│ /decide — routing brain                              │
│  intent → capability class → skill shortlist         │
│  → availability probe (before trusting any name)     │
└─────────────┬───────────────────────┬───────────────┘
              │                       │
      ┌───────▼───────┐      ┌────────▼────────┐
      │ Skills        │      │ MCPs / Tools    │
      │ 1,484 files    │      │ optional tools  │
      │ cataloged in  │      │ configured per  │
      │ this repo     │      │ active profile  │
      └───────┬───────┘      └────────┬────────┘
              │                       │
              └───────────┬───────────┘
                          ▼
              Execution / Delegation
           (subagents for parallel work)
                          │
                          ▼
              Verification ──fail──▶ Recovery ladder
                          │           (retry → diagnose →
                          ▼            alternative → degrade)
                    Memory / State
                          │
                          ▼
                      Result
```

**The rule that makes it work:** verify a binary, path, model, skill, or MCP before relying on it. A skill or integration that is not available in the active environment should not be presented as enabled.

## 🤝 Multi-Agent Team

Beyond single-agent skills, this repo documents a **coordinated specialist team**: a Project Manager role plus seven domain-specialist role contracts, a shared charter, and cross-functional handoff rules. These documents do not install Hermes profiles or configure delegation; direct profile delegation and Kanban require those capabilities to be set up in the active environment.

| Specialist | Profile | Owns |
|---|---|---|
| **Project Manager** | `default` | Scope, routing, integration, delivery |
| **Engineering** | `engineering` | Architecture, implementation, tests, deploy |
| **Design** | `designer` | UX flows, design systems, accessibility |
| **Marketing** | `marketing` | Positioning, SEO, content, acquisition |
| **Sales / Business** | `sales` | Discovery, pricing, funnels, revenue |
| **Research** | `research` | Evidence-first technical & market research |
| **Documents** | `documents` | Reports, proposals, DOCX/XLSX/PPTX/PDF |
| **QA** | `qa` | Test plans, regression, defect reproduction |

Everything lives under [`team/`](team/):

- [`team/CHARTER.md`](team/CHARTER.md) — shared operating model, role table, handoff contract, lifecycle.
- [`team/SOUL.md`](team/SOUL.md) — the PM / Team Lead contract.
- `team/profiles/<role>/SOUL.md` — each specialist's role contract (Owns · Rules · Handoff · Stay in lane · Alignment).
- `skills/autonomous-ai-agents/hermes-multiagent-team/` — how to build and verify the org.
- `skills/autonomous-ai-agents/team-alignment-traceability/` — the cross-functional owner / dependency / acceptance-criteria contract.

## 2026-10 Four-Repository Integration

The live Hermes integration added eight curated capabilities from four upstream repositories without installing competing runtimes or bulk-importing reference material:

- UI/UX Pro Max structured design search and data.
- Statistical analysis, ML leakage prevention, property-based testing, code-model evaluation, SHAP, and TransformerLens guidance from Vibe-Skills.
- Safe legacy-code change workflow from Agent Rules Books.
- Task Observer review methods merged into the existing Hermes maintenance loop.

All imported specialist skills were adapted for Hermes, corrected against upstream/API evidence, provenance-tagged, and validated. The full study and dispositions are in [`docs-four-repo-integration.md`](docs-four-repo-integration.md), with source pins in [`four-repo-integration-manifest.json`](four-repo-integration-manifest.json).

## 📦 Skill Catalog

Browse all 1,484 repository skills in [`SKILLS_CATALOG.md`](SKILLS_CATALOG.md) or the [live site](https://attilahuns288452.github.io/hermes-workflow/).

| Area | Examples |
|------|----------|
| `external/` | Vendored upstream skill collections |
| `opendesign/` | OpenDesign design-system skills |
| `software-development/`, `development/` | Engineering, testing, debugging, and setup workflows |
| `creative/`, `media/` | Design, creative coding, and media workflows |
| `workflow/`, `productivity/` | Routing, task workflows, and integrations |
| `llmquant-*` | Finance, markets, and quantitative-research topics |

<details>
<summary><strong>How skills are organized</strong></summary>

```text
skills/
├── workflow/            # routing, orchestration, token-saver
├── software-development/# code review, TDD, setup, debugging
├── opendesign/          # od-* design systems (66 brands)
├── external/            # vendored upstream collections
│   ├── claude-seo/      # SEO suite
│   └── superpowers/     # debugging, planning skills
├── autonomous-ai-agents/# hermes-agent skill + agent CLI ops
└── ...                  # see SKILLS_CATALOG.md for the current inventory
```

The catalog is a repository inventory, not an installed-profile inventory. Run the repository validators after skill-tree changes.

Each skill is a directory with a `SKILL.md` (YAML frontmatter: `name`, `description`, triggers) plus optional `references/` and `scripts/`. Hermes loads skills by frontmatter description — write it like a trigger, not a title.

</details>

## 🔌 MCP / Tool Ecosystem

Configured in `config.yaml.template` (placeholders only). The template provides a small set of portable MCP examples, including an explicitly disabled OpenDesign example. Your installed profile may enable a different set. Always treat `hermes mcp list` as the live source of truth:

```bash
hermes mcp list          # inspect enabled/disabled state now
hermes mcp add NAME      # add a server (--url or --command)
hermes mcp test NAME     # verify connectivity
```

A server being present in this repository does not mean it is installed, authenticated, or enabled in your profile.

## 🔑 Configuration

Do not replace your active profile with a repository template. Inspect its paths and merge only the settings and credentials needed for integrations you choose to enable:

```bash
hermes config path
hermes config env-path
hermes config check
```

[`config.yaml.template`](config.yaml.template) is merge guidance, not a drop-in replacement. [`.env.example`](.env.example) is a placeholder-only reference; add only the credential variables needed by integrations you explicitly configure. Keep secrets in the active profile's environment file or Hermes auth store, never in this repository.

## 🧬 Model Routing (profile-configured)

```text
Configured primary route ─ `model.provider` + `model.default`
         │
         ├── Fallback routes ──────── ordered `fallback_providers` (if configured)
         │
         ├── Auxiliary routes ─────── only when configured
         │
         └── Local/offline routes ─── only when configured

Model IDs, provider availability, and billing are runtime facts. Probe the exact pair before relying on it.
```

Provider/model routes are profile-specific. Store credentials in the active profile's environment file or Hermes auth store; never commit them to the repository.

## 🛠️ Creating a Skill

```bash
mkdir -p skills/my-category/my-skill
cat > skills/my-category/my-skill/SKILL.md <<'EOF'
---
name: my-skill
description: "Use when <trigger condition>. <What it does, one line>."
---

# My Skill

Instructions, commands, and pitfalls. Write the description
like a trigger — Hermes routes on it.
EOF
```

Conventions:
- `description:` = routing key. "Use when…" beats "This skill…".
- Pitfalls and lessons go in the skill itself — skills are the memory of the workflow.
- Verify it loads: `hermes -z "Load the my-skill skill and summarize it"`.

## 🗂️ Project Structure

```text
hermes-workflow/
├── skills/              # 1,484 SKILL.md files (the main event)
├── docs/                # built website (GitHub Pages — do not edit by hand)
├── src/                 # website source (React + Vite)
├── scripts/             # ecosystem utilities
├── config.yaml.template # sanitized Hermes config (placeholders only)
├── .env.example         # placeholder-only optional environment reference
├── META_PROMPT.md       # portable, profile-aware session context
├── SKILLS_CATALOG.md    # generated skill catalog
├── SETUP.md             # 10-step full pipeline setup
├── INTEGRATION.md       # how the layers connect + workflow operations
├── CHANGELOG.md         # dated change history
└── SECURITY.md          # audit history + secret-scrub policy
```

## 🗺️ Roadmap

- [x] `/decide` routing brain with probe-before-use enforcement
- [x] Indexed code and skill/reference discovery guidance, conditional on available integrations
- [x] 1,484-skill catalog; duplicate-name checks report possible vendor/curated overlaps
- [x] Live docs site (React + Vite → GitHub Pages)
- [x] Skill drift detection (`scripts/repo_drift.py`; weekly audit runs it)
- [ ] Catalog regeneration in CI on skill-tree changes (counts are checked by `repo_drift.py`; the 174-card site showcase is still hand-curated)
- [ ] Per-category skill browser with search on the docs site

## 🤝 Contributing

1. Fork, branch, add your skill under the right `skills/<category>/`.
2. Frontmatter must have unique `name:` + trigger-style `description:`.
3. Run the pre-commit scan: no secrets, no machine-specific paths (see [`SECURITY.md`](SECURITY.md)).
4. PR with a one-line "when to use" for the catalog.

## 🔒 Security

This is a **public mirror** — all config is templated with placeholders (`YOUR_API_KEY`, `<your-path>`). Secrets, tokens, and personal paths are scrubbed on every sync; the full audit history and scanning policy live in [`SECURITY.md`](SECURITY.md). If you find a leaked credential: **rotate it immediately**, then open an issue.

**Responsible disclosure:** open a [security advisory](https://github.com/AttilaHuns288452/hermes-workflow/security/advisories/new) rather than a public issue for anything sensitive.

## 🔗 Related

- [Hermes Agent](https://hermes-agent.nousresearch.com) — the agent framework this ecosystem runs on
- [SkillClaw](https://github.com/AMAP-ML/SkillClaw) — auto-evolving skills daemon
- [oh-my-opencode-slim](https://github.com/alvinunreal/oh-my-opencode-slim) — Pantheon agent swarm

---

<div align="center">

**Built with [Hermes Agent](https://hermes-agent.nousresearch.com) by Nous Research**
Licensed under [CC BY-NC 4.0](LICENSE)

</div>

## Hermes team audit

See `HERMES_TEAM_AUDIT_2026-10-11.md` for the verified team architecture, profile roles, Kanban smoke-test IDs, media capability audit, backups, and remaining gaps.

- Local protocol: `/home/attila/.hermes/TEAM_PROTOCOL.md`
- Reusable workflows: `/home/attila/.hermes/TEAM_WORKFLOWS.md`
