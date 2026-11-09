---
name: research-synthesis
description: Use for multi-source research with citation discipline.
triggers:
  - research
  - find
  - compare
  - sources
  - citations
---

# Research Synthesis Skill

> **Source:** Extracted from Perplexity Deep Research methodology — generalized for Hermes.

## Core Principle

Every factual claim from external sources gets an inline citation. Period.

## Research Workflow

### 1. Skill Activation
Before calling tools, activate the relevant skill:
- General research → use `web_search` / `web_extract` / `firecrawl-search`
- Financial data → use LLMQuant skills
- Academic papers → use `arxiv` skill
- Deep multi-source → use `firecrawl-deep-research`

### 2. Tool Selection Hierarchy

| Tool | When to use |
|------|-------------|
| `firecrawl-search` | Multi-source research, change monitoring, cited reports |
| `web_search` / `web_extract` | Quick single-source lookups |
| `firecrawl-scrape` | Deep dive into specific URLs |
| `firecrawl-deep-research` | Comparing 5+ entities, industry deep-dives |
| `agent-reach` | Multi-backend research (Twitter, YouTube, Reddit, etc.) |

### 3. Query Formulation

- Write queries like a human would type into Google — natural phrases, not keyword lists
- Start broad; add constraints only if results are too general
- Use separate parallel queries to explore different possibilities
- Use the actual current date in queries for time-sensitive topics

### 4. Citation Format

**For web sources:**
```
According to [Source Name](URL), the population grew 5%.
```

**For multiple sources in one sentence:**
```
Revenue rose 8% ([Bloomberg](url)), consistent with [SEC filings](url).
```

**For general knowledge tools (no specific URL):**
```
According to [tool output], ...
```

**Rules:**
- Cite every sentence that includes information from tool outputs
- Never cite generic words like "source" or "link" — use the actual source name
- Cite inline, not in a separate References section
- Anchor text must be the source name or a natural descriptive phrase

### 5. Cross-Validation

For important claims:
- Find at least 2 independent sources
- Highlight conflicting information when present
- Don't present uncertain findings as confirmed

### 6. When to Stop Research

Stop when:
- You have enough sources to support the answer
- Consecutive searches return mostly previously-seen entries
- The user's question is fully addressed

### 7. Output Format

- Begin with a direct 1-2 sentence answer to the core query
- Organize into sections with Markdown headers when appropriate
- Use Markdown tables for comparisons
- Every section: 2-3 well-cited sentences

## Quantitative claims and cost models

When research feeds a cost, quota, or feasibility model (not just prose):

- Source every quota/price claim to the provider's official pricing or limits
  page; a search snippet is a lead, not evidence. Log each source in a sources
  table with what it establishes (limit, price, term) so every modeled number
  traces to a page.
- Make the workload an explicit assumptions block (cadence, payload size, row
  size, retention) BEFORE deriving any ceiling. Quota ceilings are capacity
  arithmetic: usage per device per month × devices vs published limit, with a
  stated safety threshold (e.g. 80%); name the first bottleneck and say it is
  not the hard provider maximum.
- Separate cash outlay from imputed economic cost (unpaid labor valued as
  hours × rate). Never fold them into one number; a funding target is cash
  plus contingency only.
- Label modeled values as estimates with their assumption ("70 W at 30% duty
  cycle, not measured"). Never present an assumed draw, cadence, or rate as
  measured fact.
- When a funding source or commitment is not evidenced in the supplied
  material, write "requires confirmation" — do not assume school, sponsor, or
  team contributions.
- Put the arithmetic in a rerunnable calculation script with assertions that
  emits machine-readable output (JSON); every figure quoted in the deliverable
  must trace to that output, and re-running the script must reproduce the
  deliverable's numbers exactly.

## What NOT to Do

- Don't fabricate URLs or sources
- Don't present your memory as current fact for time-sensitive topics
- Don't use one source when the claim requires cross-validation
- Don't bury citations in a References section

## Handling Uncertainty

- If sources conflict: present both views with their citations
- If no reliable source exists: say "I couldn't find a reliable source for X"
- If you're uncertain: use "appears to", "reportedly", "according to"
- Never state something as fact without a source