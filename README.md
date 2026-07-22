# Hermes Workflow 🧞

Agent workflow dashboard for **Hermes Agent** — 668+ skills, `/decide` routing brain, 5-layer free model chain, CodeGraph + Graphify token saver, and Obsidian knowledge graph visualization.

## What's Here

| What | Where |
|------|-------|
| **Vite dashboard** (React + Tailwind) | `index.html` + `src/` — live at `attilahuns288452.github.io/hermes-workflow/` |
| **Static HTML dashboard** | `dashboard.html` — standalone, JS-free version |
| **Skills catalog** | `skills/` — 668+ agent skills organized by domain |
| **Integration docs** | `INTEGRATION.md` — setup, config, deployment |
| **Setup guide** | `SETUP.md` — full onboarding walkthrough |
| **Legacy tools** | `legacy/` — pre-v2 tools preserved for reference |

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
