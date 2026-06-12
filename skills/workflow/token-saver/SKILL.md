---
name: token-saver
description: Enforces CodeGraph MCP + Graphify probing before raw file reads to save 56× on tokens. Probes knowledge graphs first, reads files only when necessary.
triggers:
  - token saving
  - reduce token usage
  - codegraph
  - graphify query
  - token optimization
---

# Token Saver — CodeGraph + Graphify Probe Workflow

## Purpose
Eliminate unnecessary full-file reads by probing CodeGraph MCP and Graphify before reading files. This reduces token consumption per code query from ~551K (naive) to ~10K (probed) — a **56× average reduction**.

## How It Works

```
Before: read_file("file.ts", limit=500) → 500 lines = ~7K tokens
After:  graphify query → codegraph query → read only the needed file/section
```

## Probe Order (Fast → Slow)

### Layer 1 — Graphify `query` (BFS graph traversal)
```bash
graphify query "<question>" --budget 2000 --graph <project>/graphify-out/graph.json
```
Returns a scoped subgraph of related nodes with file locations. Examples:
```bash
graphify query "how does CLI arg parsing work?" --budget 2000
graphify query "what is the main entry point?" --budget 2000
graphify query "what are the core abstractions?" --budget 2000
```
Token cost: ~10K per query vs ~551K naive.

### Layer 2 — Graphify `explain` + `path`
```bash
graphify explain "<symbol>" --graph <project>/graphify-out/graph.json
graphify path "<A>" "<B>" --graph <project>/graphify-out/graph.json
```
- `explain` — plain-language summary of a symbol + neighbors
- `path` — shortest relationship between two concepts

### Layer 3 — CodeGraph `query` + `callers` + `callees`
```bash
codegraph query <symbol>
codegraph callers <symbol>
codegraph callees <symbol>
codegraph impact <symbol>
```
- `query` — finds symbol definitions, sends back file paths and line numbers
- `callers` — who calls a function
- `callees` — what a function calls
- `impact` — refactoring impact (what touches this symbol?)

### Layer 4 — Targeted file read (last resort)
Only after all probes fail:
```bash
read_file("path", offset=line, limit=50)
```

## Mandatory Pre-File-Read Checklist
Before ANY `read_file()` call, you MUST check ALL of:

1. **Does a graph.json exist in the project?** → `graphify query` first
2. **Is CodeGraph indexed?** (check `.codegraph/` exists) → `codegraph query` first
3. **Can Graphify explain the symbol?** → `graphify explain "<symbol>"`
4. **Can CodeGraph find callers/callees?** → `codegraph callers <symbol>`

Only proceed to `read_file()` if ALL probes returned insufficient context.

## Integration with /decide
The `/decide` skill now enforces this as a mandatory pipeline step:

```
session_memory → decide → Graphify/CodeGraph probe (token-saver) → domain skill execution with targeted reads only → Obsidian → KG refresh
```

The token-saver layer runs BEFORE any primary domain skill that might read files. It ensures the knowledge graphs are consulted and answers synthesized from their compact representations first.

## Verification
After probing, check:
- **Graphify benchmark** shows 56.2× token reduction (413K words → 10K per query)
- **Per-query savings**: Entry point 106.5×, Data layer 157.7×, Authentication 20.8×, Error handling 60.7×, Core abstractions 115.4×
- **CodeGraph MCP** indexed 945 files across projects (16,092 nodes, 43,795 edges)
- **Graphify** code-graph: 8,267 nodes, 13,225 edges, 775 communities
