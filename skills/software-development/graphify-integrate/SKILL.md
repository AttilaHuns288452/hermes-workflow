---
name: graphify-integrate
description: "Run Graphify codebase knowledge graph on any project and produce Obsidian-compatible notes. Covers: graph build, manual Obsidian note creation (no native CLI export — see `references/graphify-cli-capabilities.md`), vault cross-linking, and knowledge graph refresh."
triggers:
  - "graphify . on a project and export to obsidian"
  - "run graphify on a project"
  - "integrate graphify with obsidian"
  - "codebase knowledge graph for obsidian"
---

# /graphify-integrate

> ⚠️ **PITFALL:** Graphify v0.8.37 CLI has NO `export obsidian` command. The Obsidian integration is a manual workflow: run `graphify update .` to refresh the code graph, then create notes manually using data from `graphify query/explain/path`. See `references/graphify-cli-capabilities.md` for the full CLI command set.
>
> 🪟 **Windows binary**: On Windows, Graphify ships as `graphify.exe` at `~/.local/bin/graphify.exe`, NOT via `uv tool graphifyy`. `which graphify` may not find `graphify.exe` — use `~/.local/bin/graphify.exe --version` or `ls ~/.local/bin/graphify*` to detect it. All CLI commands (`update`, `query`, `explain`, `benchmark`) work identically on both.

## Role
Run the codebase knowledge graph pipeline on any project and wire the results into the Obsidian vault. Creates wikilinked code-symbol notes that complement the vault's knowledge graph and the codebase-graph's file/symbol mapping.

Two complementary tools exist for code knowledge:

| Tool | Approach | Best For |
|------|----------|----------|
| **Graphify** (v0.8.37, `~/.local/bin/graphify.exe` on Windows, or `uv tool graphifyy` via pip) | Post-processing AST code graph | Obsidian export, community detection, reports — **documentation** |
| **CodeGraph** (v0.9.9, `npm i -g @colbymchenry/codegraph`) | Real-time MCP server | Live agent queries (explore/search/impact/callers) — **development** |

Both are kept. Neither replaces the other. See the **CodeGraph vs Graphify** comparison section for when to use which.

**Mandatory per /decide**: The code-graph layer runs on EVERY project/coding/analysis task as part of the Obsidian+Graphify bundle. It is the secondary brain — code-level AST knowledge that feeds all downstream skills (model selection, code review, architecture decisions, refactoring, debugging).

## Prerequisites
- Graphify installed: via `~/.local/bin/graphify.exe` (Windows native binary) OR `uv tool install graphifyy` (Python package)
- CodeGraph (complementary): `npm install -g @colbymchenry/codegraph` then `codegraph init .` in target project
- Obsidian vault at `~/Documents/Obsidian Vault/`
- Integration script at `~/.hermes/scripts/graphify-obsidian-integration.py`

### Windows Binary Detection
On Windows, Graphify may be a native binary rather than a Python package:
```bash
# Check for the native binary
ls ~/.local/bin/graphify.exe 2>/dev/null && ~/.local/bin/graphify.exe --version
# Alternative: check Python package
which graphify 2>/dev/null && graphify --version
# If neither exists, install via Python:
uv tool install graphifyy
```

## Workflow

### Step 1 — Ensure Graphify Is Installed
```bash
# Check for graphify (Windows: try ~/.local/bin/graphify.exe)
if command -v graphify &>/dev/null; then
  echo "Found: $(which graphify)"
elif [ -f ~/.local/bin/graphify.exe ]; then
  echo "Found: ~/.local/bin/graphify.exe ($(~/.local/bin/graphify.exe --version))"
else
  # Install via Python package
  uv tool install graphifyy -q 2>&1 | tail -3
fi
graphify --help 2>/dev/null || ~/.local/bin/graphify.exe --help 2>/dev/null | head -5
```

If graphify is missing, install it:
```bash
uv tool install graphifyy
uv tool install "graphifyy[mcp]"  # for MCP server
```

### Step 2 — Detect the Target Project
The target can be:
- A **GitHub URL**: `https://github.com/<owner>/<repo>` — clone first:
  ```bash
  git clone <url> ~/Documents/Projects/<repo>
  ```
- A **local path**: already on disk at `~/Documents/Projects/<name>`

### Step 3 — Determine Obsidian Export Target
Build the vault path:
- Format: `<vault>/Projects/<ProjectName>/graphify/`
- Example: `~/Documents/Obsidian Vault/Projects/MyProject/graphify/`

Create the parent directory:
```bash
mkdir -p "~/Documents/Obsidian Vault/Projects/<ProjectName>"
```

### Step 4 — Run Graphify (code-only) + Obsidian Export
Run the full pipeline. Graphify will detect whether the project has code files (AST extraction, free) or docs/papers (needs API key).

```bash
cd ~/Documents/Projects/<ProjectName>

# Step 4a: Build the code graph (code-only, no API key needed)
graphify update . 2>&1

# For first-time extraction with doc support (needs GEMINI_API_KEY etc.):
# graphify extract . --no-cluster --no-viz 2>&1

# Check if graph.json was generated
ls graphify-out/graph.json
```

**Note:** `graphify update .` performs AST-only re-extraction on changed code files (incremental, no API key needed). For initial extraction on a fresh clone, it auto-detects the corpus and runs AST on code files. Documentation files (`.md`, `.txt`) need `GEMINI_API_KEY` or `GOOGLE_API_KEY` for semantic extraction.

**Incremental updates:** For subsequent runs on the same project:
```bash
graphify . --no-viz  # Detects changes, only re-extracts new/modified files
```

### Step 4b — Create Obsidian Note from Graph Data

⚠️ **Graphify has no `export obsidian` CLI command.** The Obsidian documentation is created manually using the `obsidian` skill bundle. The graph data feeds into the note rather than generating notes directly.

```bash
# Create a project note in the vault using the `obsidian` skill
# The note should reference graph stats from graphify-out/
cat graphify-out/graph.json | python -c "import json,sys; d=json.load(sys.stdin); print(f'{len(d.get(\"nodes\",[]))} nodes, {len(d.get(\"edges\",[]))} edges, {len({n.get(\"community\") for n in d.get(\"nodes\",[]) if n.get(\"community\")})} communities')"
```

This inspects the graph.json to get real stats for the note. Then create a note manually following the ATM-Machine template (see the `obsidian` skill bundle).

The created note should include:
- Real graph statistics from `graphify-out/graph.json` (node count, edge count, community count)
- One-sentence summary of what the project does (from the graph report or manual review)
- `[[wikilinks]]` to related projects (e.g. `[[Obsidian Knowledge Graph]]`, `[[free-ai-tools]]`)
- Tags: `#project #graphify` plus language tags

**Do NOT** run `graphify export obsidian` — this command doesn't exist.
**Do NOT** search for an `export` subcommand — Graphify (v0.8.37) has no such subcommand.

### Step 4c — Copy Supporting Files
```bash
# Optional: Copy HTML visualization and report for reference
cp graphify-out/graph.json "~/Documents/Obsidian Vault/Projects/<ProjectName>/"
cp graphify-out/GRAPH_REPORT.md "~/Documents/Obsidian Vault/Projects/<ProjectName>/" 2>/dev/null
```

### Step 4d (Optional) — Full Pipeline (AST-only)
If the project only has code files (no markdown/docs needing semantic extraction):

```bash
cd ~/Documents/Projects/<ProjectName>
graphify update .

# Get real stats for the manual Obsidian note (stay in project root)
python -c "
import json
d = json.load(open('graphify-out/graph.json'))
print(f\"{len(d['nodes'])} nodes, {len(d['edges'])} edges, {len({n.get('community') for n in d['nodes']})} communities\")
"
```

### Step 5 — Register MCP Server (Optional)
For code-level graph queries via Hermes, add the Graphify MCP server:

```yaml
# In ~/.hermes/config.yaml
mcp_servers:
  graphify:
    command: "python"
    args: ["-m", "graphify.serve"]
    cwd: "C:\\Users\\<user>\\Documents\\Projects\\<ProjectName>"
    env:
      PATH: "C:\\Users\\<user>\\.local\\bin;%PATH%"
    connect_timeout: 30
```

Then the MCP protocol exposes these tools in Hermes:
- `query_graph` — search the knowledge graph (BFS/DFS)
- `get_node` — full details for a specific node
- `get_neighbors` — all direct neighbors with edge details
- `path` — shortest path between two nodes
- `explain` — plain-language explanation of a node

### Step 6 — Create Obsidian Project Note
Create a project overview note at `<vault>/Projects/<ProjectName>.md` (or `<vault>/Projects/<ProjectName>/README.md`). Use the graph stats from `graphify-out/graph.json` to populate the note with real data.

The note should include:
- Overview section describing the project
- Graphify integration sub-section with actual graph stats (node count, edge count, communities)
- Mermaid graph showing the integration architecture
- `[[wikilinks]]` to related projects (e.g. `[[Obsidian Knowledge Graph]]`, `[[ECC & Free AI Tools]]`)
- Tags: `#project #graphify` etc.

**Important**: There is no `graphify export obsidian` CLI command. Generate graph stats from `graphify-out/graph.json` and create the note manually via the `obsidian` skill bundle.

### Step 7 — Add Cross-Linking Wikilinks
Add `[[wikilinks]]` from complementary project notes to this new one:
- If it's an agent framework → cross-link with `[[ECC & Free AI Tools]]`
- If it's a model provider → cross-link with `[[free-ai-tools]]`
- If it's a graph/visualization tool → cross-link with `[[Graphify]]`

### Step 8 — Refresh Obsidian Knowledge Graph
Run AFTER every Graphify update to keep the vault graph current.

```bash
# Standard scan (always run first)
python ~/AppData/Local/hermes/skills/note-taking/obsidian-knowledge-graph/scripts/scan_vault.py

# Option A — Standard pyvis render
python ~/AppData/Local/hermes/skills/note-taking/obsidian/scripts/render_kg.py

# Option B — Galaxy-style render (preferred for visual impact)
python ~/Documents/Obsidian\ Vault/render_galaxy_kg.py
```

Option B produces a galaxy-themed force-directed graph with deep space background, glowing nebula cluster colors, and pulsing star nodes. It reads the same `kg_output.json` as Option A.

### Step 9 — Report
Report the full integration summary:
- Project path
- Obsidian notes path (graphify export)
- Number of graph nodes/edges/communities (from `graphify-out/graph.json`)
- MCP status (registered or not)
- Cross-links added
- Knowledge graph stats (from scan)

## Automation Script
The integration script at `~/.hermes/scripts/graphify-obsidian-integration.py` automates Steps 4a-4c:

```bash
python ~/.hermes/scripts/graphify-obsidian-integration.py ~/Documents/Projects/<ProjectName>
```

Optional flags:
- `--backend gemini` — enable LLM-based semantic extraction for docs
- `--vault /path/to/vault` — custom vault path
- `--skip-graphify` — re-export only (graph already built)

**Local copy**: The skill includes a standalone version at `scripts/graphify-obsidian-integration.py` that can be copied and run independently.

## Quick Reference
```bash
# Quick pipeline for any project
cd ~/Documents/Projects/<name>
graphify update .

# Benchmark token savings (new index)
~/.local/bin/graphify.exe benchmark graphify-out/graph.json

# Create a manual Obsidian note with graph stats (NO export CLI command exists)
python -c "
import json
d = json.load(open('graphify-out/graph.json'))
print(f\"{len(d['nodes'])} nodes, {len(d['edges'])} edges\")
"

# Then cross-link + refresh (same as Steps 6-8 above)
```

## Integration Points
| System | Integration Type |
|---|---|
| Obsidian vault | Direct export — one `.md` per code symbol with [[wikilinks]] |
| Obsidian graph view | `.obsidian/graph.json` — community-colored graph |
| Obsidian Canvas | `graph.canvas` — community groupings as canvas |
| Dataview queries | Community notes include Dataview queries for live filtering |
| Hermes MCP | `graphify-mcp` — query the code graph from Hermes sessions |
| CodeGraph MCP | `codegraph` — 6 live tools (explore, search, callers, impact, framework routes, deps) — real-time alternative |
| Obsidian Codebase Graph | Complementary — Graphify = code symbols, Codebase Graph = file layout |
| Obsidian Knowledge Graph | Complementary — Graphify = AST relations, KG = note/tag relations |

## CodeGraph vs Graphify — Reconciliation

Both tools provide code knowledge graphs. They overlap in domain but are **complementary in practice**. Keep both.

### Decision Guide

| Criterion | Use Graphify | Use CodeGraph |
|-----------|-------------|---------------|
| When you need | Post-processing docs, Obsidian export, community detection | Live MCP queries during development |
| Tool type | `uv tool graphifyy` (Python) | `npm -g @colbymchenry/codegraph` (Node) |
| Interface | CLI + HTML report | MCP server (6 tools) |
| Languages | Python/JS/TS/Go/Rust/Java | 22+ languages |
| Output | Obsidian notes, canvas, report | JSON query results via MCP |
| Syncing | Manual re-run | Auto-sync via file watcher |
| Key strength | Community detection, vault integration | Real-time explore/search/impact |

### Installation

```bash
# CodeGraph — one-time
npm install -g @colbymchenry/codegraph
codegraph install -y  # auto-configure Hermes, Claude Code, Codex, etc.
codegraph init .       # index current project (3,596 files in ~30s)

# Available MCP tools after install:
#   explore     — project symbols, definitions, structure
#   search      — FTS5 full-text search across indexed files
#   callers     — who calls a function (cross-file)
#   callees     — what a function calls
#   impact      — refactoring impact analysis
#   routes      — auto-detect API routes (Express, FastAPI, Next.js, Django)
```

### When Both Are Installed

If both Graphify and CodeGraph are present on a project:
- Use **CodeGraph** during active development (ask it "show me the callers of X", "find all files that import Y")
- Use **Graphify** at documentation checkpoints (export Obsidian notes, run community detection)
- Both index the same codebase — no conflict, they operate on separate indices

### Verification

```bash
codegraph --version      # → 0.9.9 expected
codegraph help           # → lists all MCP tools
graphify --version       # → 0.8.37 expected (if installed)
```

## Galaxy-Style Knowledge Graph Render

The standard `render_kg.py` uses pyvis with default settings. For a stunning **galaxy-style** visualization (deep space background, glowing nebula cluster colors, pulsing star nodes, force-directed galaxy clusters), use the alternative renderer:

```bash
# Galaxy-style render (requires pyvis)
cd ~/Documents/Obsidian\ Vault
python render_galaxy_kg.py
# Output: knowledge_graph.html (~575 KB, galaxy aesthetics)
```

### Galaxy Renderer Features
- Deep space gradient background with animated particles
- vis-network force-directed layout with galaxy-like clustering physics
- Nodes rendered as glowing orbs with halos (pulsing animation)
- Edge colors matching source node cluster (thin glowing lines)
- Cluster colors mapped to nebula palettes (blue nebula, red nebula, green nebula, etc.)
- Hover reveals node details with expanded glow
- Physics settings tuned for galaxy-cluster separation
- Title bar shows live node/edge count

The galaxy renderer at `render_galaxy_kg.py` reads the same `kg_output.json` as the standard renderer so no scan re-run is needed — just swap the render script.

## Pitfalls
- **Windows binary vs Python package**: If `graphify` is not found by `which`, check `~/.local/bin/graphify.exe`. The native binary has all the same commands (`update`, `query`, `explain`, `benchmark`) but no built-in MCP server — that's only available via `uv tool install "graphifyy[mcp]"`. If you need the MCP server, install the Python package instead.
- **No API key for docs**: Graphify needs `GEMINI_API_KEY` for semantic extraction of markdown/docs. Code-only repos work fine without it.
- **Large repos (>2000 files)**: Graphify's cluster step can be slow. Use `--no-viz` to skip HTML generation, or `--no-cluster` to skip community detection.
- **Re-running**: Graphify has incremental detection — `graphify update .` only re-processes changed files.
- **No `graphify export obsidian` command**: Graphify (v0.8.37) has NO `export` subcommand. Do NOT search for one or try to call it — it doesn't exist. Create Obsidian notes manually using the `obsidian` skill bundle with graph stats extracted from `graphify-out/graph.json`.
- **Windows paths**: When specifying paths, use forward slashes or escaped backslashes.
- **MCP server per project**: Each project needs its own `graphify-mcp` registration pointing to that project's `graphify-out/graph.json`.
- **Cross-platform paths in integration script**: The `graphify-obsidian-integration.py` script handles path resolution; use `--vault` to override the vault path if the default doesn't exist.

## Related
- `software-development/setup` — Phase 2.5 references Graphify integration
- `decide` — Complementary Setup Routing includes Graphify
- `graphify` skill — the raw Graphify CLI skill installed via `graphify install --platform hermes`
- `update` — general-purpose "add repo to ecosystem" workflow that calls this skill
