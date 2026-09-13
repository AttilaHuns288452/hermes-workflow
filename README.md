<div align="center">

# 🧞 Hermes Workflow

**850 agent skills · /decide routing brain · GLM 5.3 Flash model chain**

[![GitHub stars](https://img.shields.io/github/stars/AttilaHuns288452/hermes-workflow?style=flat&label=Stars&labelColor=0b0f1c&color=3ddc84)](https://github.com/AttilaHuns288452/hermes-workflow/stargazers)
[![License](https://img.shields.io/badge/license-MIT-0b0f1c?style=flat&labelColor=0b0f1c&color=7aa9f7)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-850-4a8cf4?style=flat&labelColor=0b0f1c)](https://attilahuns288452.github.io/hermes-workflow/)
[![Agents](https://img.shields.io/badge/ECC%20Agents-64-9b7cf7?style=flat&labelColor=0b0f1c)](https://attilahuns288452.github.io/hermes-workflow/#agents)
[![Model](https://img.shields.io/badge/Model-GLM%205.3%20Flash&labelColor=0b0f1c&color=f0d060)](https://attilahuns288452.github.io/hermes-workflow/#models)
[![CodeGraph](https://img.shields.io/badge/CodeGraph-144K%20nodes%20%C2%B7%20326K%20edges-6bc5e8?style=flat&labelColor=0b0f1c)](https://attilahuns288452.github.io/hermes-workflow/#pipeline)
[![Built with](https://img.shields.io/badge/built%20with-Hermes%20Agent-6bc5e8?style=flat&labelColor=0b0f1c)](https://hermes-agent.nousresearch.com)

---

**One install, zero config.** Clone this repo, run one command, and your AI assistant gets 850 skills across 10 domains — coding, design, finance, media, research, DevOps, and more — all routed through a cheap-first model chain.

</div>

## ✨ What's Inside

| Layer | What |
|-------|------|
| **🧠 /decide** | 6-step routing brain — context retrieval → guardrail → decompose → probe → execute → document |
| **⚡ CodeGraph** | 144,827 nodes · 326,322 edges · 8,421 files — probe the graph before any raw file read (token-saver skill) |
| **🤖 Pantheon Swarm** | oh-my-opencode-slim agent swarm — 7 specialists (Orchestrator, Oracle, Explorer, Librarian, Designer, Fixer, Council) auto-split multi-step tasks |
| **🔄 SkillClaw** | Daemon on `:30000` — auto-evolves skills from every session, zero manual effort |
| **🔗 ECC Bridge** | 64 specialized agents routed through GLM 5.3 Flash (code and vision in one model) |
| **📘 Obsidian KG** | Vault → knowledge graph with community detection, ATM-Machine quality docs |
| **🛡️ Guardrail** | 6 immutable rules — file protection, secrets safety, injection immunity, system integrity |

## 🚀 Quick Start

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | sh
git clone https://github.com/AttilaHuns288452/hermes-workflow.git
cd hermes-workflow
# Install 850 skills in one shot
find ./skills -name SKILL.md -exec dirname {} \; | while read dir; do hermes skills install -y "$dir"; done
```

**First pipeline:** `hermes -z "What does the decide skill do?"`

Then pick your daily-driver model — copy `config.yaml.template` to `~/.hermes/config.yaml` and set `model.default` (GLM 5.3 Flash via [xKiro](https://xkiro.com) is a solid default; any OpenAI-compatible provider works).

## 📊 Stats

```
📦 850     Skills across 10 domains
🧠 64      ECC specialized agents
🔌 14      MCP servers
⚡ 144,827 CodeGraph nodes · 326,322 edges · 8,421 files indexed
💸 $0      Local fallbacks — OmniRoute gateway ladder → local Ollama
🤖 GLM     GLM 5.3 Flash daily driver — chat, delegation, and vision in one model
🔄 7       oh-my-opencode-slim agent specialists for parallel coding
🔧 1       SkillClaw daemon — self-improving skills
```

## 🧩 Skill Categories

| Category | Count | Highlights |
|----------|-------|------------|
| Software Development | 26 | TDD, Debugging, Setup, Architect, Plan |
| LLMQuant (Finance) | 18 | Equities, Options, Macro, Risk, 13F |
| Creative & Design | 20 | Claude Design, Excalidraw, p5.js, ComfyUI |
| Workflow & Core | 14 | /decide, Token Saver, ECC Bridge, Pantheon |
| Productivity & Comms | 16 | Gmail, Notion, Maps, OCR, PowerPoint |
| Media & Content | 11 | OpenMontage, YouTube, TikTok, MoneyPrinter |
| Research & MLOps | 13 | arXiv, llama.cpp, W&B, HuggingFace |
| GitHub & DevOps | 8 | PR Workflow, CI/CD, Code Review |
| OpenCode Power Pack | 11 | Feature Dev, Code Explorer, MCP Builder |
| More Categories | 33 | Obsidian, iMessage, Agent Harness, Wix |

## 🧬 Model Chain (cheap first)

```
GLM 5.3 Flash (xKiro API) ────── daily driver: chat, delegation, vision
         │
         ├── OmniRoute Gateway ── local fallback ladder, localhost:20128
         │   (24 models · 7 providers — Poolside, OpenRouter free, MiniMax)
         │
         ├── Local Ollama ─────── offline layer, localhost:11434
         │   (qwen3.5:4b for code, phi4-mini for speed)
         │
         └── Paid (last resort) ─ stdcmpt, z.ai GLM
```

Every provider is configured by name in `config.yaml.template` — API keys are referenced via environment variables (`XKIRO_API_KEY`, `STDCMT_API_KEY`, `ZAI_API_KEY`), never stored in the repo.

## 🔗 Related

- [Hermes Agent](https://hermes-agent.nousresearch.com) — the agent framework
- [oh-my-opencode-slim](https://github.com/alvinunreal/oh-my-opencode-slim) — Pantheon agent plugin
- [SkillClaw](https://github.com/AMAP-ML/SkillClaw) — auto-evolving skills

---

<div align="center">

**Built with [Hermes Agent](https://hermes-agent.nousresearch.com) by Nous Research**

</div>
