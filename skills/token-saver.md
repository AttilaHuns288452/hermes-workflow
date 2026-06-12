---
name: token-saver
description: "Pre-file-read probe chain. Before reading any file, probe Graphify query → Graphify explain → Graphify path → CodeGraph query → CodeGraph callers/callees/impact. Only read files as last resort. Target: 56× token reduction (benchmark verified)."
version: 1.0.0
author: Hermes Workflow
license: MIT
triggers:
  - pre_read_file
  - pre_query
---

# ⚡ Token Saver — Pre-File-Read Probe Chain

## Goal

Never read file contents before probing Graphify and CodeGraph. Turn naive full-corpus reads (~551K tokens) into targeted graph queries (~10K tokens). Verified benchmark: **56.2× average reduction** (max 157.7× per query).

## Decision Tree

Before ANY `read_file()` call, run this probe chain in order:

```
Layer 1 — Graphify query (BFS graph traversal)
  ↓ if answer is sufficient — DONE. No file read needed.
Layer 2 — Graphify explain (symbol + neighbors)
  ↓ if answer is sufficient — DONE. No file read needed.
Layer 3 — Graphify path (between two components)
  ↓ if answer is sufficient — DONE. No file read needed.
Layer 4 — CodeGraph query (FTS5 symbol search)
  ↓ if answer is sufficient — DONE. No file read needed.
Layer 5 — CodeGraph callers (function trace)
  ↓ if answer is sufficient — DONE. No file read needed.
Layer 6 — CodeGraph callees (function trace)
  ↓ if answer is sufficient — DONE. No file read needed.
Layer 7 — CodeGraph impact (blast radius analysis)
  ↓ if answer is sufficient — DONE. No file read needed.
Layer 8 — Targeted file read (LAST RESORT)
    read_file("path", offset=line, limit=50) — minimal, focused
```

Each layer tries the cheaper tool first. Stop as soon as you have the answer.

## Probe Commands

### Layer 1 — Graphify query

```bash
# Full corpus search — answers code questions without reading files
graphify query "how does <concept> work?" --budget 2000

# Cost: ~10K tokens avg
# Returns: relevant nodes with their descriptions and relationships
```

### Layer 2 — Graphify explain

```bash
# Deep dive on a specific symbol or node
graphify explain "<symbol_name>"

# Cost: ~2K tokens
# Returns: symbol definition, neighbors, relationships
```

### Layer 3 — Graphify path

```bash
# Shortest path between two components
graphify path "<component_a>" "<component_b>"

# Cost: ~1K tokens
# Returns: the chain of nodes connecting them
```

### Layer 4 — CodeGraph query

```bash
# FTS5 symbol search — fastest probe
npx codegraph query "<symbol_name>"

# Cost: ~200 tokens
# Returns: symbol locations, file paths, line numbers
```

### Layer 5 — CodeGraph callers

```bash
# Who calls this function?
npx codegraph callers "<function_name>"

# Cost: ~200 tokens
# Returns: list of callers with file paths
```

### Layer 6 — CodeGraph callees

```bash
# What does this function call?
npx codegraph callees "<function_name>"

# Cost: ~200 tokens
# Returns: list of callees
```

### Layer 7 — CodeGraph impact

```bash
# Blast radius analysis — what breaks if I change this?
npx codegraph impact "<symbol_name>"

# Cost: ~300 tokens
# Returns: all nodes that depend on the symbol
```

### Layer 8 — Targeted file read (LAST RESORT)

```python
read_file("path", offset=<line_number>, limit=50)
```

Only read the specific lines needed. Never dump entire files.

## Benchmark Results

| Metric | Naive (Full Read) | Probed (Graph) | Reduction |
|--------|------------------|----------------|-----------|
| Tokens per query (avg) | 551,000 | 9,805 | **56.2×** |
| Best single query | 1,576,000 | 10,000 | **157.7×** |
| Entry point query | 1,065,000 | 10,000 | **106.5×** |
| Core abstractions | 1,154,000 | 10,000 | **115.4×** |
| Error handling | 546,000 | 9,000 | **60.7×** |
| Authentication | 208,000 | 10,000 | **20.8×** |

Source: Graphify v0.8.37 built-in benchmark (`graphify benchmark`) on 413,350-word corpus.

## When to Skip (Graph/CodeGraph Not Available)

If `graph.json` (for Graphify) or `.codegraph/` (for CodeGraph) is missing for the target project, skip the unavailable tool — never block. The remaining tools in the chain still provide savings.

Check for each before probing:

```bash
# Check Graphify availability
if [ -f "graphify-out/graph.json" ]; then
    echo "Graphify available"
else
    echo "Graphify not available — skipping"
fi

# Check CodeGraph availability
if [ -d ".codegraph" ]; then
    echo "CodeGraph available"
else
    echo "CodeGraph not available — skipping"
fi
```

## Enforcement

This probe chain is enforced by the `/decide` skill at step 4 of the execution order. The Core Identity Guardrail (step 2) runs before this to ensure no secrets leak during graph queries. Probing a graph tool is cheaper and safer than reading files — always probe first.
