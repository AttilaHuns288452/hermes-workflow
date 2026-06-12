# Hermes Workflow

### My AI Agent Pipeline — Skills, Models, Knowledge Graph, and the /decide Routing Brain

---

**Live site:** https://attilahuns288452.github.io/hermes-workflow/

---

## Why I Built This

I use **Hermes Agent** (by Nous Research) as my daily AI agent framework. Over time, I accumulated skills, agents, model providers, and tools — but they were scattered. Every task meant manually deciding which tool, which model, which workflow to use. The overhead of "what should I use for this?" was real.

This website documents the system I built to solve that: a **single routing brain** (`/decide`) that reads every request, decomposes it, picks the right skills, probes code knowledge before touching file contents (saving 56× tokens), applies a permanent safety guardrail, and finishes with mandatory Obsidian documentation + a galaxy-style knowledge graph refresh.

It's not just a collection of tools — it's a **pipeline** with an enforced execution order, conflict resolution rules, and a self-correction loop that patches itself when it routes incorrectly.

---

## The Problem

Three things were broken:

### 1. Token Waste
The naive approach to code questions was to dump file contents into context. A single "how does this work?" would burn ~551K tokens reading the whole corpus. That's expensive, slow, and wasteful — especially on a free-model budget.

**Solution:** The **Token Saver** workflow — probe Graphify and CodeGraph *before* reading files. This cut token usage by **56.2× on average** (up to 157.7× per query).

### 2. Model Chaos
I had access to models from multiple sources — OpenCode's bundled free models, Freebuff's cloud APIs, FreeLLMAPI's 110+ local proxies, OpenRouter's free tier, and paid fallbacks. But no consistent way to pick the right one.

**Solution:** A **5-layer model routing chain** that tries free first, probes before committing, and falls back gracefully. The system always picks the best available free model — no more guessing.

### 3. Scattered Knowledge
Every project produced documentation, but it lived in different places. No cross-links, no graph, no way to see how things connected. Knowledge didn't compound.

**Solution:** **Mandatory Obsidian documentation** with a consistent template (ATM-Machine quality), plus an **interactive Galaxy Knowledge Graph** that visualizes the entire vault as a physics-based node/edge graph. After every project, the graph refreshes automatically.

---

## Why These Skills?

Every skill category exists because I hit a real problem:

| Category | Why It Exists |
|----------|---------------|
| **`/decide`** (Routing Brain) | Every request needs context before action. /decide runs a 5-step reasoning protocol before a single tool is invoked. |
| **Core Identity Guardrail** | Safety is not optional. A permanent guardrail enforces file protection, secrets handling, injection immunity, and system integrity. Loaded before every session. Can't be overridden. |
| **Token Saver** | The 56.2× insight came from benchmarking. Before this, every code query burned 551K tokens. Now the probe chain (Graphify → CodeGraph → read_file) wastes almost nothing. |
| **CodeGraph MCP + Graphify** | Two complementary code knowledge tools. CodeGraph (16K nodes, live MCP) for development queries. Graphify (8.3K nodes, AST traversal) for structural analysis. Both actively used, both real. |
| **ECC Agent Bridge** (64 agents) | Everything Claude Code has 261 specialized agent prompts. The bridge strips paid-model requirements and routes through the free model chain — 57 of 64 agents work on free models. |
| **LLMQuant** (18 domains) | Quant-finance workflows for commodities, credit, crypto, equities, derivatives, macro, risk, and more. Each domain is a self-contained skill with MCP data sources. |
| **Obsidian Bundle** (3 skills) | Documentation that compounds. Every project gets an ATM-Machine-quality note with Mermaid graph and wikilinks. The vault is scanned into a 276-node galaxy graph. |
| **Model Router** | 5-layer fallback chain (OpenCode → Freebuff → FreeLLMAPI → OpenRouter → Paid). Each layer is probed before commit. The default is always free. |

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
5. **🧬 Graphify + CodeGraph** — Dual code knowledge: AST graph + live MCP index.
6. **🎯 Domain Skills** — ECC agents, LLMQuant, coding, creative, research, GitHub, media, etc.
7. **🤖 Model Routing** — Try OpenCode → Freebuff → FreeLLMAPI → OpenRouter → paid.
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
- **CodeGraph** (v0.9.9, npm) provides live, real-time code context via MCP. It auto-syncs via file watcher — perfect for during-development queries (symbol search, caller tracing, impact analysis).
- **Graphify** (v0.8.37, uv) provides post-hoc AST code graphs with community detection. It's better for structural questions (explain this concept, find the path between components, analyze the overall architecture).

Both are installed, both work, both are probed by the Token Saver before file reads. The benchmark confirms **56.2× token reduction** with this combined approach.

### Why Obsidian is mandatory — not optional
Documentation that you skip doesn't exist. By enforcing it at the /decide routing level, every project automatically gets:
- An ATM-Machine-quality note with architecture, code patterns, and mermaid graph
- Cross-links to related projects via wikilinks
- A refreshed knowledge graph (now 281 nodes)
- Code-symbol notes from Graphify's ast export

### Why a 5-layer model chain instead of just picking one
Model availability changes constantly. Free models deprecate, rate limits reset, new providers appear. A fallback chain with 5 layers ensures the system keeps working even when individual providers fail. The probe-before-commit pattern means no wasted tokens on dead endpoints.

### Why ECC agents run through a bridge instead of directly
ECC agents are designed for Claude's paid models. The bridge strips `model: sonnet/opus` frontmatter and routes through the free chain. 57/64 agents work identically on free models; the 7 opus-dependent agents show quality degradation but still produce useful output. This gives me 57 specialized code agents at zero cost.

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
3. **Permanent guardrail** — Not a config file that can be overridden. The Core Identity Guardrail re-anchors every 10 exchanges and cannot be bypassed.
4. **No paid model dependency** — The default is always free. Paid models are a last resort, not a requirement.
5. **Documentation is part of the pipeline** — Not an afterthought. The Obsidian + KG refresh is a mandatory step enforced at the routing level.
6. **57 specialized code agents at zero cost** — The ECC bridge strips paid requirements and routes through the free model chain.

---

## Tech Stack

- **Hermes Agent** (Nous Research) — Core framework
- **Graphify** (v0.8.37, uv) — AST code graph
- **CodeGraph** (v0.9.9, npm) — Live MCP code indexing
- **ECC** (Everything Claude Code) — 64 agent prompts
- **free-ai-tools** — 238-model catalog
- **Freebuff** — 6 cloud free models
- **FreeLLMAPI** — 110+ local free models
- **Obsidian** — Knowledge vault with galaxy graph visualization
- **Vanilla HTML/CSS/JS** — This website (single file, no build tools, no frameworks)

---

## The Name

The repo is called **hermes-workflow** because that's what it documents: the workflow. Not just the tools or the models, but the **process** — the routing, the probe chain, the guardrail, the documentation cycle, the self-correction loop. The website is a snapshot of that process at a point in time.

The site is **static** — it doesn't update automatically. It captures the state of the workflow as it was when published. The actual pipeline evolves through /decide's self-correction loop.

---

*Built with Hermes Agent (Nous Research). Model: deepseek-v4-flash-free (opencode-zen). Updated: June 12, 2026.*
