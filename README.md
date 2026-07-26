# Hermes Workflow 🧞

Agent workflow dashboard for **Hermes Agent** — 668+ skills, `/decide` routing brain, 5-layer free model chain, **Pantheon agent swarm**, **SkillClaw auto-evolution**, CodeGraph + Graphify token saver, and Obsidian knowledge graph visualization.

## What's Here

| What | Where |
|------|-------|
| **Vite dashboard** (React + Tailwind) | `index.html` + `src/` — live at `attilahuns288452.github.io/hermes-workflow/` |
| **Static HTML dashboard** | `dashboard.html` — standalone, JS-free version |
| **Skills catalog** | `skills/` — 668+ agent skills organized by domain |
| **Integration docs** | `INTEGRATION.md` — setup, config, deployment |
| **Setup guide** | `SETUP.md` — full onboarding walkthrough |
| **Legacy tools** | `legacy/` — pre-v2 tools preserved for reference |

## Key Integrations

### Pantheon Agent Swarm (oh-my-opencode-slim)
7 specialized agents orchestrate multi-step coding tasks autonomously:
- **Orchestrator** (GLM 5.2) — plans work graph, dispatches specialists
- **Oracle** (DeepSeek V4 Flash) — strategic advice, code review, debugging
- **Explorer** (DeepSeek V4 Flash) — codebase reconnaissance
- **Librarian** (DeepSeek V4 Flash) — external knowledge, API docs
- **Designer** (DeepSeek V4 Flash) — UI/UX implementation
- **Fixer** (DeepSeek V4 Flash) — fast scoped patches
- **Council** (multi-model) — parallel consensus synthesis

### SkillClaw — Auto-Evolving Skills
Runs as a local proxy on port 30000, automatically improving skills across sessions. Zero manual effort — skills get sharper every time you use them.
- `skillclaw start --daemon` — start the evolution proxy
- `skillclaw doctor hermes` — verify integration health

### ECC Agent Bridge
64 specialized agents across 8 categories, all routed through free models:
- **Code agents:** `opencode/deepseek-v4-flash-free`
- **Vision agents:** `opencode/mimo-v2.5-free`
- **Self-hosted:** 3 interconnected services (AutoGPT :8000, DeepTutor :8005, OpenCharts :5173)

## Quick Start

```bash
npm install
npm run dev       # dev server at localhost:5173
npm run build     # production build to docs/
```

## Customization

- **Skills:** add/edit skills in `skills/` — each is a `SKILL.md` with YAML frontmatter
- **Config:** `config.yaml.template` → copy to `config.yaml` and tweak
- **Tokens:** copy `.env.example` to `.env` and fill in your API keys

## Built With

- [Vite](https://vitejs.dev/) — build tool
- [React 19](https://react.dev/) — UI framework
- [Tailwind CSS 4](https://tailwindcss.com/) — styling
- [Lucide](https://lucide.dev/) — icons
- [Oxlint](https://oxc.rs/) — linting
