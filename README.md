<div align="center">

# 🧞 Hermes Workflow

**A battle-tested skill ecosystem + routing brain for [Hermes Agent](https://hermes-agent.nousresearch.com) — 846 skills, one decision layer, cheap-first model routing.**

[![License](https://img.shields.io/badge/license-CC%20BY--NC%204.0-0b0f1c?style=flat&labelColor=0b0f1c&color=7aa9f7)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-846-4a8cf4?style=flat&labelColor=0b0f1c)](#-skill-catalog)
[![Routing](https://img.shields.io/badge/router-%2Fdecide-3ddc84?style=flat&labelColor=0b0f1c)](META_PROMPT.md)
[![Site](https://img.shields.io/badge/docs-live-9b7cf7?style=flat&labelColor=0b0f1c)](https://attilahuns288462.github.io/hermes-workflow/)
[![Built with](https://img.shields.io/badge/built%20with-Hermes%20Agent-6bc5e8?style=flat&labelColor=0b0f1c)](https://hermes-agent.nousresearch.com)

**What is this?** A production skill library for Hermes Agent: install it, point Hermes at it, and your agent gains 846 curated skills across 264 top-level directories — routed through a single decision layer (`/decide`) that probes cheap indexes before spending tokens.

**Why?** Skills without routing rot. This repo pairs every skill with the orchestration that decides *when* to use it — plus a token-saver probe chain that cuts read costs by 50×–1,233× in live use.

</div>

---

## ✨ What's Inside

| Layer | What it does |
|-------|--------------|
| **🧠 `/decide`** | The routing brain: intent → capability class → skill shortlist → availability probe → execution → verification → recovery. See [`META_PROMPT.md`](META_PROMPT.md). |
| **📚 Skills** | 846 `SKILL.md` files in 264 top-level directories: software development, design systems, finance (LLMQuant), media, research, DevOps, security. |
| **⚡ Token Saver** | Probe-before-read chain (CodeGraph → Graphify → LightRAG) so the agent queries indexes instead of raw-reading files. |
| **🛡️ Guardrail** | 6 immutable rules — file protection, secrets safety, injection immunity, system integrity, re-anchoring, safe fallback. |
| **🤝 Delegation** | Subagent orchestration patterns with mandatory read-back verification. |
| **🔍 Verification** | Per-output-type gates: code → tests/build, research → citations, visual → render check. Nothing is "done" unverified. |

## 🚀 Quick Start

> **Prereq:** [Hermes Agent](https://hermes-agent.nousresearch.com) installed (`hermes --version` works).

```bash
git clone https://github.com/AttilaHuns288462/hermes-workflow.git
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
      │ 846 SKILL.md  │      │ 14 enabled      │
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

## 📦 Skill Catalog

Browse all 846 skills in [`SKILLS_CATALOG.md`](SKILLS_CATALOG.md) or the [live site](https://attilahuns288462.github.io/hermes-workflow/).

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
└── ...                  # 264 top-level directories
```

Each skill is a directory with a `SKILL.md` (YAML frontmatter: `name`, `description`, triggers) plus optional `references/` and `scripts/`. Hermes loads skills by frontmatter description — write it like a trigger, not a title.

</details>

## 🔌 MCP / Tool Ecosystem

Configured in `config.yaml.template` (12 server entries, placeholders only). Live profile runs **14 enabled** MCP servers:

`codegraph` · `graphify` · `firecrawl` · `supabase` · `vercel` · `vscode` · `figma-dev` · `flowbite` · `demosmith` · `pagecast` · `llmquant-data` · `21st` · `clawlink` · plus 4 disabled (stripe, figma, opendesign, agentmemory)

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
├── skills/              # 846 SKILL.md files, 264 top-level categories (the main event)
├── docs/                # built website (GitHub Pages — do not edit by hand)
├── src/                 # website source (React + Vite)
├── scripts/             # ecosystem utilities
├── config.yaml.template # sanitized Hermes config (placeholders only)
├── .env.example         # every env var the pipeline understands
├── META_PROMPT.md       # the /decide routing brain, in full
├── SKILLS_CATALOG.md    # generated skill catalog
├── SETUP.md             # 10-step full pipeline setup
├── INTEGRATION.md       # how the layers connect
└── SECURITY.md          # audit history + secret-scrub policy
```

## 🗺️ Roadmap

- [x] `/decide` routing brain with probe-before-use enforcement
- [x] Token Saver probe chain (live-benchmarked 50×–1,233× read reduction)
- [x] 846-skill catalog across 264 top-level directories, zero duplicate names
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

**Responsible disclosure:** open a [security advisory](https://github.com/AttilaHuns288462/hermes-workflow/security/advisories/new) rather than a public issue for anything sensitive.

## 🔗 Related

- [Hermes Agent](https://hermes-agent.nousresearch.com) — the agent framework this ecosystem runs on
- [SkillClaw](https://github.com/AMAP-ML/SkillClaw) — auto-evolving skills daemon
- [oh-my-opencode-slim](https://github.com/alvinunreal/oh-my-opencode-slim) — Pantheon agent swarm

---

<div align="center">

**Built with [Hermes Agent](https://hermes-agent.nousresearch.com) by Nous Research**
Licensed under [CC BY-NC 4.0](LICENSE)

</div>
