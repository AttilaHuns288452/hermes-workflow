# Hermes Workflow

**AI Agent Workflow Engine** — 97 skills, 64 ECC agents, 18 LLMQuant domains, 5-layer free model routing, permanent guardrail, 56× token saver, live ecosystem dashboard, and mandatory Obsidian knowledge graph documentation.

## 🌙 Overview

This repository documents the **Hermes Agent** ecosystem — a multi-model AI agent framework from **Nous Research** that runs skills (reusable workflows) to execute coding, creative, research, finance, media, and productivity tasks.

The system centers on the **`/decide`** skill, a master orchestrator that:
1. Retrieves prior session context via `session_memory`
2. Runs the **Core Identity Guardrail** (permanent, never skipped)
3. Applies a 5-step reasoning protocol to decompose and route requests
4. Probes **CodeGraph MCP** + **Graphify** before any file read (56.2× token savings)
5. Selects and sequences the right skills for every domain
6. Routes models through a 5-layer free chain (OpenCode → Freebuff → FreeLLMAPI → OpenRouter → Paid)
7. Finishes with **mandatory Obsidian documentation** + **galaxy knowledge graph refresh**

## 🖥️ Website

The static GitHub Pages site at **[https://attilahuns288452.github.io/hermes-workflow/](https://attilahuns288452.github.io/hermes-workflow/)** showcases:

- **92+ Skills** — categorized tab grid with descriptions (15 categories)
- **64 ECC Agents** — searchable, filterable library with free-model compatibility badges
- **Live Dashboard** — ecosystem overview: 16 projects, 97 skills, 26K APIs, 8K+16K graph nodes, model layers, MCP servers
- **Model Routing Chain** — 5-layer fallback chain visualization
- **Token Saver** — 56.2× verified token reduction via CodeGraph + Graphify probe
- **Core Identity Guardrail** — 6 permanent safety rules
- **Knowledge Graph** — 276 nodes / 1,091 edges galaxy visualization
- **18 LLMQuant Domains** — quant finance skill suite
- **Use Cases** — real projects executed end-to-end
- **Obsidian Documentation Standard** — ATM-Machine quality template

## 🔧 Key Stats

| Metric | Value |
|--------|-------|
| Skills | 97 across 15 categories |
| ECC Agents | 64 (57 free-compatible via ecc-bridge) |
| Projects | 16 (3 with Graphify graphs) |
| API Mega List | 26,005 APIs across 18 categories |
| CodeGraph MCP | 945 files / 16,092 nodes / 43,795 edges (codegraph repo — reference scale) |
| Graphify | 8,267 nodes / 13,225 edges / 775 communities (graphify repo — reference scale) |
| Token Savings | 56.2× average (up to 157.7× per query) |
| Knowledge Graph | 276 nodes / 1,091 edges |
| Free Models | 156 across 5 routing layers |
| MCP Servers | 6 wired (CodeGraph, Graphify, VS Code, LLMQuant, Obsidian KG, agentmemory) |
| LLMQuant Domains | 18 quant-finance workflows |
| Obsidian Project Notes | 8 (ATM-Machine quality standard) |

## 🏗️ Architecture

```mermaid
graph TD
    User[User Request] --> SM[session_memory]
    SM --> CIG[Core Identity Guardrail]
    CIG --> Decide["/decide Routing Brain"]
    Decide --> TS[Token Saver Probe]
    TS --> G[Graphify - Code Graph]
    TS --> C[CodeGraph MCP]
    G --> DS[Domain Skills]
    C --> DS
    DS --> MR[Model Routing Chain]
    MR --> OB[Obsidian Documentation]
    OB --> KG[Knowledge Graph Refresh]
```

## 🌐 Ecosystem

- **Hermes Agent** — Multi-model agent framework (Nous Research)
- **ECC Agents** — 64 specialized agents bridged via free model chain
- **CodeGraph MCP** — Live code knowledge (v0.9.9)
- **Graphify** — AST code graph (v0.8.37)
- **LLMQuant** — 18 quant-finance domain skills
- **free-ai-tools** — 550+ free AI tools, 238 models
- **OpenCode CLI** — Primary coding agent with 5 free models
- **Freebuff** — Cloud free model extensions (Kimi K2.6, MiniMax M3, etc.)
- **FreeLLMAPI** — 107 models, 84 available (13 provider keys)
- **API Mega List** — 10,498 ready-to-use Apify APIs across 18 categories (searchable via `productivity/api-mega-list` skill)
- **MoneyPrinterTurbo** — AI short video generation (86.1k ⭐)

## 📄 License

This project's documentation and website content are licensed under [CC BY-NC 4.0](LICENSE).

---

*Theme: Dark Navy Moonlight · Updated: Jun 12, 2026*
