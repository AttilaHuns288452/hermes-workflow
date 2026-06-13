# Graphify CLI Capabilities (v0.8.37)

Verified commands from the actual CLI — NOT aspirational features.

## Available Commands

| Command | Purpose | Notes |
|---------|---------|-------|
| `update <path>` | Re-extract code files and rebuild the code graph | No LLM needed. Use `--force` after refactors that delete code |
| `query "<question>"` | BFS graph traversal answering code questions | `--budget N` caps output tokens (default 2000). `--dfs` for depth-first |
| `explain "<symbol>"` | Plain-language explanation of a node and its neighbors | Uses graph.json |
| `path "A" "B"` | Shortest relationship path between two nodes | Cross-community traversal |
| `affected "X"` | Reverse traversal to find nodes impacted by X | `--depth N` and `--relation R` flags |
| `cluster-only <path>` | Rerun clustering on existing graph.json | `--no-viz` skips graph.html (useful for >5000 nodes) |
| `diagnose multigraph` | Report same-endpoint edge collapse risk | `--json` for machine-readable |
| `install [--platform P]` | Copy skill to platform config dir | Supports: claude, cursor, codex, opencode, hermes, gemini, etc. |
| `benchmark [graph.json]` | Measure token reduction vs naive full-corpus | **56.2× avg reduction verified** |
| `watch <path>` | Watch folder and rebuild graph on code changes | |
| `label <path>` | (Re)name communities with configured LLM backend | Regenerates report |
| `merge-graphs <g1> <g2>` | Merge two or more graph.json files into one cross-repo graph | |
| `clone <github-url>` | Clone a repo locally and print its path | |
| `add <url>` | Fetch URL and save to ./raw, then update graph | |

## What Does NOT Exist

- ❌ No `export obsidian` command
- ❌ No `--obsidian` flag on any command
- ❌ No native Obsidian note generation
- ❌ No `graphify-mcp` MCP server (the `graphify-mcp.exe` binary is a separate bridge, not an MCP server in the standard sense)

## Obsidian Integration (Manual Workflow)

Since there's no export command, the actual workflow for Obsidian integration is:

1. **Refresh the code graph:** `graphify update .` (no LLM, fast)
2. **Query for context:** `graphify query "<question>" --budget 2000`
3. **Explain specific nodes:** `graphify explain "<symbol>"`
4. **Create Obsidian note manually** with wikilinks to related notes
5. **Cross-reference Graphify stats** (node count, edge count, community count) in the note
6. **Install as Hermes skill:** `graphify install hermes`

## Benchmark Data

```
Corpus:          413,350 words → ~551,133 tokens (naive)
Graph:           8,267 nodes, 13,225 edges
Avg query cost:  ~9,805 tokens
Reduction:       56.2× fewer tokens per query

Per question:
  [20.8×] how does authentication work
  [106.5×] what is the main entry point
  [60.7×] how are errors handled
  [157.7×] what connects the data layer to the api
  [115.4×] what are the core abstractions
```
