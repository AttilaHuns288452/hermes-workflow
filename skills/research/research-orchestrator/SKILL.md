---
name: research-orchestrator
description: Full research loop — decompose, parallel keyword search, cross-validate with conflict flagging, synthesize with claim-level citations. Use for multi-source research, comparative analysis, deep investigations, and cited reports.
triggers:
  - research
  - investigate
  - find
  - compare
  - analyze
---

# Research Orchestrator Skill

> **Source:** Perplexity Deep Research methodology (captured 2026-07, `system_prompts_leaks/Perplexity/deep-research.md`), adapted to Hermes tooling. Techniques applied, not wording copied.

## When to Use

Multi-source research · comparative analysis · deep investigations · cited reports.
Single quick fact → `hermes_web_search` directly; do not run the full loop.

## Pre-flight gates (before searching)

1. **Memory first for personal queries.** If the question depends on the user's context ("my project", "best framework *for me*", preferences, past decisions) → `session_search` / `agentmemory memory_recall` BEFORE web search. Never search the web for facts the environment already knows.
2. **Clarify only true unknowns.** Ask clarifying questions ONLY when ambiguity would materially change the research: undefined scope, subjective terms ("best"), or a decision the answer hinges on. Offer 2–4 options with a recommended default. Skip for single factual answers or when scope is already specified. If already asked once this session and skipped, proceed with reasonable defaults — never re-ask.
3. **Route verticals.** Finance/market/SEC → `llmquant-*` + `llmquant-data` MCP. Papers → `research--arxiv`. URL-specific extraction → `firecrawl_scrape` directly. Everything else → the loop below.

## The Loop

### Step 1 — Decompose into single-entity sub-questions
Break the query into discrete, independently searchable sub-questions. One entity or relationship per sub-question — never compound ("A and B and C market cap" fails; "A market cap" / "B market cap" works). Each sub-question becomes its own search query.

### Step 2 — Search with short keyword queries (parallel)
- Queries are SHORT and keyword-based; search engines reward keywords, not sentences.
- Batch all independent searches into ONE turn (parallel tool calls) — never drip-feed.
- Tool order per `decide`: `firecrawl_search` (primary) → `hermes_web_search` (fallback) → `agent-reach` (multi-backend). 3–5 sources max per sub-question before synthesis.
- Reference the current date in time-sensitive queries; never present model memory as current fact.

### Step 3 — Extract
`firecrawl_scrape` the top results that warrant depth (tables, lists, long sections). Batch URL fetches in one turn. Skip scraping when snippets answer the sub-question — extraction costs tokens.

### Step 4 — Cross-validate (the step that prevents hallucinations)
For every claim that matters:
- **2+ independent sources agree** → report as confirmed.
- **Sources conflict** → report the conflict explicitly with each source and a confidence level. NEVER silently average or pick one without saying so.
- **Single uncorroborated source** → mark as single-source, state the source.
- **Not found** → say "not found", do not fill the gap from model memory.

### Step 5 — Synthesize
Merge validated findings into a direct answer. Structure: direct answer first (1–2 sentences), then sections. Comparison of entities across dimensions → markdown table. Use only information found during research; no inferred or fabricated content.

### Step 6 — Cite at the claim level
Every sentence containing externally-derived fact carries its source inline at the sentence — not in a footnotes dump. Distinguish your analysis from external facts. If a source is uncertain, say so rather than presenting it as confirmed.

## Failure behavior

| Failure | Response |
|---|---|
| `firecrawl_search` fails/errors | `hermes_web_search` → `agent-reach` → state blocker honestly |
| Paywalled/blocked source | Note the blockage, use the snippet + alternate source |
| Sources contradict irreconcilably | Present both positions + confidence, do not resolve |
| Time budget exceeded | Synthesize what is gathered; list un-answered sub-questions explicitly |

## Output contract

Report with: direct answer → sections with claim-level citations → explicit "sources conflict" markers where they exist → list of what could NOT be verified. A research deliverable without citations is incomplete, not done.
