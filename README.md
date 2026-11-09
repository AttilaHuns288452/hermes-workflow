<div align="center">

# 🧞 Hermes Workflow

**A battle-tested skill ecosystem + routing brain for [Hermes Agent](https://hermes-agent.nousresearch.com) — 1482 skills, one decision layer, cheap-first model routing.**

[![License](https://img.shields.io/badge/license-CC%20BY--NC%204.0-0b0f1c?style=flat&labelColor=0b0f1c&color=7aa9f7)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-1482-4a8cf4?style=flat&labelColor=0b0f1c)](#-skill-catalog)
[![Routing](https://img.shields.io/badge/router-%2Fdecide-3ddc84?style=flat&labelColor=0b0f1c)](META_PROMPT.md)
[![Site](https://img.shields.io/badge/docs-live-9b7cf7?style=flat&labelColor=0b0f1c)](https://attilahuns288452.github.io/hermes-workflow/)
[![Built with](https://img.shields.io/badge/built%20with-Hermes%20Agent-6bc5e8?style=flat&labelColor=0b0f1c)](https://hermes-agent.nousresearch.com)

**What is this?** A production skill library for Hermes Agent: install it, point Hermes at it, and your agent gains 1482 curated skills across 715 top-level directories — routed through a single decision layer (`/decide`) that probes cheap indexes before spending tokens.

**Why?** Skills without routing rot. This repo pairs every skill with the orchestration that decides *when* to use it — plus a token-saver probe chain that cuts read costs by 50×–1,233× in live use.

</div>

---

## ✨ What's Inside

| Layer | What it does |
|-------|--------------|
| **🧠 `/decide`** | The routing brain: intent → capability class → skill shortlist → availability probe → execution → verification → recovery. See [`META_PROMPT.md`](META_PROMPT.md). |
| **📚 Skills** | 1482 `SKILL.md` files in 715 top-level directories: software development, design systems, finance (LLMQuant), media, research, DevOps, security. |
| **⚡ Token Saver** | Probe-before-read chain (CodeGraph → Graphify → LightRAG) so the agent queries indexes instead of raw-reading files. |
| **🛡️ Guardrail** | 6 immutable rules — file protection, secrets safety, injection immunity, system integrity, re-anchoring, safe fallback. |
| **🤝 Delegation** | Subagent orchestration patterns with mandatory read-back verification. |
| **🔍 Verification** | Per-output-type gates: code → tests/build, research → citations, visual → render check. Nothing is "done" unverified. |

## 🚀 Quick Start

> **Prereq:** [Hermes Agent](https://hermes-agent.nousresearch.com) installed (`hermes --version` works).

```bash
git clone https://github.com/AttilaHuns288452/hermes-workflow.git
cd hermes-workflow

# 1. Point Hermes at these skills — add the repo's skills/ dir to your external_dirs
hermes config edit
#   skills:
#     external_dirs:
#       - /path/to/hermes-workflow/skills

# 2. Reload and verify
hermes -z "List three skills you can use from the hermes-workflow catalog"

# 3. Try the routing brain
hermes -z "What does the decide skill do?"
```

For the full pipeline (model chain, MCP servers, gateway), see [`SETUP.md`](SETUP.md).

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
      │ 1482 SKILL.md  │      │ 11 enabled      │
      │ indexed by    │      │ codegraph,      │
      │ LightRAG      │      │ firecrawl, ...  │
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

**The rule that makes it work:** every capability is probed before use (`command -v`, `test -f`, `hermes mcp list`). A skill that isn't reachable is never routed to.

## 🤝 Multi-Agent Team

Beyond single-agent skills, this repo ships a **coordinated specialist team**: a Project Manager (the default Hermes profile) plus 7 domain specialists, each with its own role contract, shared charter, and cross-functional handoff rules. It works through **direct profile delegation and Kanban**; no group chat is required.

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

Browse all 1482 skills in [`SKILLS_CATALOG.md`](SKILLS_CATALOG.md) or the [live site](https://attilahuns288452.github.io/hermes-workflow/).

| Category | Count | Highlights |
|----------|-------|------------|
| External collections | 341 | claude-seo, superpowers, design systems, agent-skills |
| OpenDesign | 66 | od-* brand design systems (Linear, Stripe, Notion…) |
| Software Development | 47 | TDD, debugging, code review, planning |
| Creative | 19 | excalidraw, p5.js, pixel art, memes |
| Workflow | 18 | /decide, token-saver, kanban, cron |
| Productivity | 17 | PDF, Office docs, Notion, Obsidian |
| LLMQuant (finance) | 25 | equities, options, macro, prediction markets |

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
└── ...                  # 715 top-level directories
```

Each skill is a directory with a `SKILL.md` (YAML frontmatter: `name`, `description`, triggers) plus optional `references/` and `scripts/`. Hermes loads skills by frontmatter description — write it like a trigger, not a title.

</details>

## 🔌 MCP / Tool Ecosystem

Configured in `config.yaml.template` (placeholders only). Live profile runs **11 enabled** MCP servers:

`codegraph` · `firecrawl` · `llmquant-data` · `pagecast` · `supabase` · `vercel` · `blender` · `packet-tracer` · `rea` · `earshot` · `opensandbox` — plus 14 configured-but-disabled (21st, agentmemory, clawlink, demosmith, figma, figma-dev, flowbite, graphify, opendesign, stripe, twelve-data, vscode, artemis, roblox_studio). Disabled is not broken: each one is either credential-gated or duplicated by an enabled server.

```bash
hermes mcp list          # see what's enabled on your install
hermes mcp add NAME      # add a server (--url or --command)
hermes mcp test NAME     # verify connectivity
```

## 🔑 Configuration

Copy the templates, fill in your own values — the repo ships **placeholders only**:

```bash
cp config.yaml.template ~/.hermes/config.yaml   # model, providers, skills paths
cp .env.example ~/.hermes/.env                  # API keys — never commit this
```

| Variable | Purpose |
|----------|---------|
| `XKIRO_API_KEY` | Daily-driver model access (GLM 5.3 Flash) |
| `OPENROUTER_API_KEY` | Fallback provider pool |
| `HERMES_USERNAME` | Your OS username (path templating) |

Full variable list: [`.env.example`](.env.example).

## 🧬 Model Chain (cheap first)

```text
GLM 5.3 Flash (xKiro API) ────── daily driver: chat, delegation, vision
         │
         ├── Free ladder ─────── local gateway fallbacks (Poolside, OpenRouter free)
         │
         ├── Local Ollama ────── offline layer, localhost:11434
         │
         └── Paid (last resort) ─ escape hatch when free tiers rate-limit
```

Every provider is configured by name in `config.yaml.template` — API keys live in environment variables, never in the repo.

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
├── skills/              # 1482 SKILL.md files, 715 top-level categories (the main event)
├── docs/                # built website (GitHub Pages — do not edit by hand)
├── src/                 # website source (React + Vite)
├── scripts/             # ecosystem utilities
├── config.yaml.template # sanitized Hermes config (placeholders only)
├── .env.example         # every env var the pipeline understands
├── META_PROMPT.md       # the /decide routing brain, in full
├── SKILLS_CATALOG.md    # generated skill catalog
├── SETUP.md             # 10-step full pipeline setup
├── INTEGRATION.md       # how the layers connect + workflow operations
├── CHANGELOG.md         # dated change history
└── SECURITY.md          # audit history + secret-scrub policy
```

## 🗺️ Roadmap

- [x] `/decide` routing brain with probe-before-use enforcement
- [x] Token Saver probe chain (live-benchmarked 50×–1,233× read reduction)
- [x] 1,482-skill catalog across 715 top-level directories, no duplicate names inside a category (vendored upstream copies excepted)
- [x] Live docs site (React + Vite → GitHub Pages)
- [ ] Skill auto-sync script (live install ↔ repo, bidirectional)
- [ ] Catalog regeneration in CI on skill-tree changes
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
