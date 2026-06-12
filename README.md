# Hermes Workflow

### My AI Agent Pipeline — Skills, Models, Knowledge Graph, and the /decide Routing Brain

---

**Live site:** https://attilahuns288452.github.io/hermes-workflow/

---

## Why I Built This

I use **[Hermes Agent](https://github.com/NousResearch/hermes-agent)** (by Nous Research) as my daily AI agent framework. Over time, I accumulated skills, agents, model providers, and tools — but they were scattered. Every task meant manually deciding which tool, which model, which workflow to use. The overhead of "what should I use for this?" was real.

This website documents the system I built to solve that: a **single routing brain** (`/decide`) that reads every request, decomposes it, picks the right skills, probes code knowledge before touching file contents (saving 56× tokens), applies a permanent safety guardrail, and finishes with mandatory Obsidian documentation + a galaxy-style knowledge graph refresh.

It's not just a collection of tools — it's a **pipeline** with an enforced execution order, conflict resolution rules, and a self-correction loop that patches itself when it routes incorrectly.

---

## The Problem

Three things were broken:

### 1. Token Waste
The naive approach to code questions was to dump file contents into context. A single "how does this work?" would burn ~551K tokens reading the whole corpus. That's expensive, slow, and wasteful — especially on a free-model budget.

**Solution:** The **Token Saver** workflow — probe [Graphify](https://github.com/safishamsi/graphify) and [CodeGraph](https://github.com/colbymchenry/codegraph) *before* reading files. This cut token usage by **56.2× on average** (up to 157.7× per query).

### 2. Model Chaos
I had access to models from multiple sources — [OpenCode](https://github.com/opencode-ai/opencode)'s bundled free models, [Freebuff](https://github.com/CodebuffAI/codebuff)'s cloud APIs, [FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi)'s 110+ local proxies, [OpenRouter](https://openrouter.ai/)'s free tier, and paid fallbacks. But no consistent way to pick the right one.

**Solution:** A **5-layer model routing chain** that tries free first, probes before committing, and falls back gracefully. The system always picks the best available free model — no more guessing.

### 3. Scattered Knowledge
Every project produced documentation, but it lived in different places. No cross-links, no graph, no way to see how things connected. Knowledge didn't compound.

**Solution:** **Mandatory Obsidian documentation** with a consistent template (ATM-Machine quality), plus an **interactive Galaxy Knowledge Graph** that visualizes the entire vault as a physics-based node/edge graph. After every project, the graph refreshes automatically.

---

## Why These Skills?

Every skill category exists because I hit a real problem:

| Category | Why It Exists | Source |
|----------|---------------|--------|
| **`/decide`** (Routing Brain) | Every request needs context before action. /decide runs a 5-step reasoning protocol before a single tool is invoked. | [Hermes Agent](https://github.com/NousResearch/hermes-agent) |
| **Core Identity Guardrail** | Safety is not optional. A permanent guardrail enforces file protection, secrets handling, injection immunity, and system integrity. Loaded before every session. Can't be overridden. | Custom Hermes skill |
| **Token Saver** | The 56.2× insight came from benchmarking. Before this, every code query burned 551K tokens. Now the probe chain (Graphify → CodeGraph → read_file) wastes almost nothing. | Uses [Graphify](https://github.com/safishamsi/graphify) + [CodeGraph](https://github.com/colbymchenry/codegraph) |
| **CodeGraph MCP + Graphify** | Two complementary code knowledge tools. CodeGraph (16K nodes, live MCP) for development queries. Graphify (8.3K nodes, AST traversal) for structural analysis. Both actively used, both real. | [CodeGraph](https://github.com/colbymchenry/codegraph) · [Graphify](https://github.com/safishamsi/graphify) |
| **ECC Agent Bridge** (64 agents) | Everything Claude Code has 261 specialized agent prompts. The bridge strips paid-model requirements and routes through the free model chain — 57 of 64 agents work on free models. | [ECC](https://github.com/affaan-m/ECC) |
| **LLMQuant** (18 domains) | Quant-finance workflows for commodities, credit, crypto, equities, derivatives, macro, risk, and more. Each domain is a self-contained skill with MCP data sources. | [LLMQuant](https://github.com/LLMQuant) |
| **Obsidian Bundle** (3 skills) | Documentation that compounds. Every project gets an ATM-Machine-quality note with Mermaid graph and wikilinks. The vault is scanned into a 276-node galaxy graph. | [Obsidian](https://obsidian.md/) |
| **Model Router** | 5-layer fallback chain (OpenCode → Freebuff → FreeLLMAPI → OpenRouter → Paid). Each layer is probed before commit. The default is always free. | [OpenCode](https://github.com/opencode-ai/opencode) · [Freebuff](https://github.com/CodebuffAI/codebuff) · [FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi) · [OpenRouter](https://openrouter.ai/) · [free-ai-tools](https://github.com/ShaikhWarsi/free-ai-tools) |

---

## The Pipeline (9 Steps)

```
session_memory → guardrail → /decide → token-saver → Graphify/CodeGraph → domain skills → model routing → Obsidian docs → KG refresh
```

Every request, every time. No shortcuts.

1. **session_memory** — Pull prior context from past sessions. Never route blind.
2. **🛡️ Core Identity Guardrail** — Safety check before anything else. Never skipped.
3. **/decide** — Decompose prompt, score confidence, select skills, resolve conflicts.
4. **⚡ Token Saver** — Probe Graphify + CodeGraph before any `read_file()`. 56× reduction.
5. **🧬 Graphify + CodeGraph** — Dual code knowledge: [Graphify](https://github.com/safishamsi/graphify) (AST graph) + [CodeGraph](https://github.com/colbymchenry/codegraph) (live MCP index).
6. **🎯 Domain Skills** — [ECC agents](https://github.com/affaan-m/ECC), [LLMQuant](https://github.com/LLMQuant), coding, creative, research, GitHub, media, etc.
7. **🤖 Model Routing** — Try [OpenCode](https://github.com/opencode-ai/opencode) → [Freebuff](https://github.com/CodebuffAI/codebuff) → [FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi) → [OpenRouter](https://openrouter.ai/) → paid.
8. **📝 Obsidian Docs** — ATM-Machine quality: Overview, Architecture, Code Patterns, Mermaid graph, wikilinks.
9. **🕸️ Galaxy KG Refresh** — Re-scan vault, regenerate interactive graph. Compounding knowledge.

---

## Architecture Decisions

### Why /decide runs on every prompt — not just some
The routing brain needs to see **everything** to learn patterns. If it skipped easy requests, it would miss the context that makes routing better. The overhead is minimal; the upside is a system that self-corrects.

### Why the Core Identity Guardrail is always first
Safety rules that weaken with context length are not safety rules. Re-anchoring every 10 exchanges ensures the guardrail never degrades. The 6 rules (file protection, secrets, injection immunity, system integrity, re-anchoring, safe fallback) form a complete behavioral contract.

### Why Graphify AND CodeGraph — not one or the other
They serve different needs:
- **[CodeGraph](https://github.com/colbymchenry/codegraph)** (v0.9.9) — Pre-indexed semantic code knowledge graph with live MCP auto-sync via file watcher. Best for during-development queries: symbol search, caller tracing, impact analysis, full-text FTS5 search. Benchmarked at 16% cheaper, 58% fewer tool calls.
- **[Graphify](https://github.com/safishamsi/graphify)** (v0.8.37, `uv tool install graphifyy`) — Multi-modal AST code graph with community detection (Leiden), Mermaid diagram export, and Obsidian wikilink output. Best for structural analysis: explain concept, find shortest path, analyze architecture, generate reports.

Both are installed, both work, both are probed by the Token Saver before file reads. The benchmark confirms **56.2× token reduction** with this combined approach.

### Why Obsidian is mandatory — not optional
Documentation that you skip doesn't exist. By enforcing it at the /decide routing level, every project automatically gets:
- An ATM-Machine-quality note with architecture, code patterns, and mermaid graph
- Cross-links to related projects via wikilinks
- A refreshed knowledge graph (now 281 nodes)
- Code-symbol notes from Graphify's ast export

### Why a 5-layer model chain instead of just picking one
Model availability changes constantly. Free models deprecate, rate limits reset, new providers appear. A fallback chain with 5 layers ensures the system keeps working even when individual providers fail. The probe-before-commit pattern means no wasted tokens on dead endpoints.

| Layer | Source | Models |
|-------|--------|--------|
| 1 — OpenCode | [`opencode-ai/opencode`](https://github.com/opencode-ai/opencode) (archived → [Crush](https://github.com/charmbracelet/crush)) | Bundled free models via Zen tier: Big Pickle, MiniMax M2.5 Free |
| 2 — Freebuff | [`CodebuffAI/codebuff`](https://github.com/CodebuffAI/codebuff) (Freebuff variant) | Kimi K2.6, MiniMax M3, MiMo 2.5 Pro |
| 3 — FreeLLMAPI | [`tashfeenahmed/freellmapi`](https://github.com/tashfeenahmed/freellmapi) | 110+ free models from 16 providers behind one `/v1` endpoint |
| 4 — OpenRouter | [openrouter.ai](https://openrouter.ai/) · [free-ai-tools catalog](https://github.com/ShaikhWarsi/free-ai-tools) | 29+ free models, 50 req/day free tier |
| 5 — Paid fallback | BYOK (bring your own key) | Claude, GPT, Gemini Pro — last resort only |

### Why ECC agents run through a bridge instead of directly
[ECC](https://github.com/affaan-m/ECC) (Everything Claude Code) provides 64 specialized agent prompts with 262 skills — but its agents are designed for Claude's paid models (`model: sonnet` / `model: opus` in frontmatter). The bridge strips these paid-model requirements and routes through the free model chain. 57/64 agents work identically on free models; the 7 opus-dependent agents show quality degradation but still produce useful output. This gives me 57 specialized code agents at zero cost.

---

## Stats (Live, Not Aspirational)

| Metric | Value |
|--------|-------|
| Hermes Skills | 50+ |
| LLMQuant Domains | 18 |
| ECC Agents | 64 (57 free-compatible) |
| KG Nodes | 281 |
| KG Edges | 1,101 |
| CodeGraph Indexed Files | 945 |
| CodeGraph Nodes | 16,092 |
| CodeGraph Edges | 43,795 |
| Graphify Nodes | 8,267 |
| Graphify Edges | 13,225 |
| Token Savings (avg) | **56.2×** |
| Best Token Savings (per query) | **157.7×** |
| Free Models Available | 110+ |

---

## What Makes This Different

1. **Self-correcting routing** — /decide patches itself when it routes wrong. Every mistake improves future routing.
2. **Verified token savings** — The 56.2× reduction is benchmarked, not estimated. Real numbers from Graphify's built-in benchmark.
3. **Permanent guardrail** — Not a config file that can be overridden. The [Core Identity Guardrail](https://github.com/NousResearch/hermes-agent) re-anchors every 10 exchanges and cannot be bypassed.
4. **No paid model dependency** — The default is always free. Paid models are a last resort, not a requirement. Model catalog from [free-ai-tools](https://github.com/ShaikhWarsi/free-ai-tools).
5. **Documentation is part of the pipeline** — Not an afterthought. The [Obsidian](https://obsidian.md/) + KG refresh is a mandatory step enforced at the routing level.
6. **57 specialized code agents at zero cost** — The [ECC bridge](https://github.com/affaan-m/ECC) strips paid requirements and routes through the free model chain.

---

## Tech Stack

| Tool | Version | What It Does | GitHub |
|------|---------|-------------|--------|
| **Hermes Agent** | latest | Core AI agent framework (Nous Research) | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) |
| **Graphify** | v0.8.37 (`uv`) | Multi-modal AST knowledge graph | [safishamsi/graphify](https://github.com/safishamsi/graphify) |
| **CodeGraph** | v0.9.9 | Pre-indexed MCP code knowledge graph | [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) |
| **ECC** | v2.0.0 | 64-agent harness (Everything Claude Code) | [affaan-m/ECC](https://github.com/affaan-m/ECC) |
| **free-ai-tools** | 2026 catalog | 238-model free AI tools directory | [ShaikhWarsi/free-ai-tools](https://github.com/ShaikhWarsi/free-ai-tools) |
| **Freebuff** | latest | Free ad-supported coding agent | [CodebuffAI/codebuff](https://github.com/CodebuffAI/codebuff) |
| **FreeLLMAPI** | latest | 110+ free models proxy (16 providers) | [tashfeenahmed/freellmapi](https://github.com/tashfeenahmed/freellmapi) |
| **OpenCode** | v0.0.55 (archived) | Terminal AI coding agent (→ [Crush](https://github.com/charmbracelet/crush)) | [opencode-ai/opencode](https://github.com/opencode-ai/opencode) |
| **OpenRouter** | — | Multi-model API gateway (free tier) | [openrouter.ai](https://openrouter.ai/) |
| **Obsidian** | — | Knowledge vault with graph visualization | [obsidian.md](https://obsidian.md/) |
| **LLMQuant** | — | 18-domain quant-finance skills for AI agents | [LLMQuant](https://github.com/LLMQuant) |
| **This repo** | — | Single-file static HTML + 5 Hermes skills + setup guide | [AttilaHuns288452/hermes-workflow](https://github.com/AttilaHuns288452/hermes-workflow) |

## Repository Structure

This repo is a working reference, not just a showcase. Every file is real and usable:

```
hermes-workflow/
├── index.html                     # Static website (the live site)
├── skills/
│   ├── decide.md                  # /decide — 5-step routing brain
│   ├── core-identity-guardrail.md # 🛡️ Permanent safety guardrail (6 rules)
│   ├── token-saver.md             # ⚡ Graphify→CodeGraph→read_file probe chain
│   ├── model-router.md            # 🤖 5-layer free-model fallback chain
│   └── obsidian-docs.md           # 📝 Mandatory ATM-Machine quality documentation template
├── LICENSE                        # CC BY-NC 4.0 (free to use, share, adapt — no commercial use)
├── SETUP.md                       # Step-by-step replication guide (10 steps)
├── META_PROMPT.md                 # Copy-paste prompt showing full Hermes setup
├── SKILLS_CATALOG.md              # Full catalog: all 120 skills with use cases
├── INTEGRATION.md                 # Pipeline flow, data flow, network diagrams
├── README.md                      # This file — architecture, reasoning, references
└── .nojekyll                      # GitHub Pages config
```

**New files explain the full ecosystem:**
- [`META_PROMPT.md`](./META_PROMPT.md) — A comprehensive prompt you can copy-paste into a fresh Hermes Agent session to load the complete skill ecosystem, model chain, guardrail, and pipeline. Designed for sharing your setup with others or restoring it on a new machine.
- [`SKILLS_CATALOG.md`](./SKILLS_CATALOG.md) — Every skill (120 total, 15 categories) with trigger conditions, use cases, and pipeline integration. Includes the BUNDLE RULE for Obsidian, guardrail enforcement, and model routing flow.
- [`INTEGRATION.md`](./INTEGRATION.md) — Full architecture diagram (ASCII), 8-step data flow with tool-level detail, cross-skill integration points, environment wiring, session learning → self-correction, and common request→pipeline trace table.
- [`SETUP.md`](./SETUP.md) — 10-step guide to replicate the stack from scratch. Covers Hermes Agent, Graphify, CodeGraph, OpenCode, FreeLLMAPI, Obsidian, MCP wiring, pipeline verification, and troubleshooting.

Each skill file is a valid Hermes Agent skill with proper frontmatter (`name`, `description`, `version`, `triggers`) and a detailed markdown body. Install them by copying to `~/.hermes/skills/`.

## License

This work is licensed under **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**.

**You are free to:**
- Use, copy, adapt, and share the material — including through social media, blogs, videos, and podcasts
- Build on it for personal or educational projects
- Modify and redistribute with attribution

**You may NOT:**
- Sell this project or any derivative of it
- Use it in any commercial product or service
- Monetize it in any form (paid tools, SaaS, courses, consulting, etc.)

**Requirements:**
- Credit the original author (Attila, hermes-workflow)
- Link back to https://github.com/AttilaHuns288452/hermes-workflow
- Keep this license intact on all copies and derivatives

See the [LICENSE](./LICENSE) file for the full legal text.

---

## The Name

The repo is called **hermes-workflow** because that's what it documents: the workflow. Not just the tools or the models, but the **process** — the routing, the probe chain, the guardrail, the documentation cycle, the self-correction loop. The website is a snapshot of that process at a point in time.

The site is **static** — it doesn't update automatically. It captures the state of the workflow as it was when published. The actual pipeline evolves through /decide's self-correction loop.

---

## References

Every tool and project referenced in this document:

| Project | GitHub | Notes |
|---------|--------|-------|
| **Hermes Agent** | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | Core AI agent framework by Nous Research |
| **Graphify** | [safishamsi/graphify](https://github.com/safishamsi/graphify) | Multi-modal AST knowledge graph (PyPI: `graphifyy`) |
| **CodeGraph** | [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) | Pre-indexed MCP code knowledge graph (⭐ 47.5k) |
| **ECC** (Everything Claude Code) | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 64-agent harness, 262 skills (⭐ 211.9k) |
| **free-ai-tools** | [ShaikhWarsi/free-ai-tools](https://github.com/ShaikhWarsi/free-ai-tools) | Curated list of 238 free AI tools & models |
| **Freebuff / Codebuff** | [CodebuffAI/codebuff](https://github.com/CodebuffAI/codebuff) | Free ad-supported coding agent |
| **FreeLLMAPI** | [tashfeenahmed/freellmapi](https://github.com/tashfeenahmed/freellmapi) | 110+ free models, 16 providers, one `/v1` endpoint |
| **OpenCode** | [opencode-ai/opencode](https://github.com/opencode-ai/opencode) | Terminal AI coding agent (archived → [Crush](https://github.com/charmbracelet/crush)) |
| **OpenRouter** | [openrouter.ai](https://openrouter.ai/) | Multi-model API gateway with free tier |
| **Obsidian** | [obsidian.md](https://obsidian.md/) | Knowledge vault platform |
| **LLMQuant** | [github.com/LLMQuant](https://github.com/LLMQuant) | 18-domain quant-finance skills for AI agents |
| **This repo** | [AttilaHuns288452/hermes-workflow](https://github.com/AttilaHuns288452/hermes-workflow) | Static website documenting the entire workflow |

---

*Built with [Hermes Agent](https://github.com/NousResearch/hermes-agent) (Nous Research). Model: deepseek-v4-flash-free (opencode-zen). Updated: June 12, 2026.*
