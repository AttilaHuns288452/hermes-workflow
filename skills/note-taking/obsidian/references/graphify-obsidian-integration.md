# Graphify ↔ Obsidian Vault Integration

How to use safishamsi/graphify (65.2k ⭐) to generate code-level knowledge graphs
and export them as [[wikilinked]] Obsidian notes that feed into the vault's
knowledge graph scanner.

## Overview

Graphify is a CLI tool that scans a codebase with tree-sitter AST parsing,
builds a NetworkX graph with Leiden community detection, and exports to
multiple formats. Its `--obsidian` export generates one `.md` note per code
symbol, community-overview notes, a Canvas file, and `.obsidian/graph.json`
for community coloring in Obsidian's native graph view.

This complements the Obsidian bundle:
- **obsidian-codebase-graph** — filesystem paths → wikilinked notes
- **obsidian-knowledge-graph** — vault scan → JSON graph → HTML render
- **Graphify** — code symbol relationships → wikilinked notes in the vault

Together they provide **dual-view project intelligence**: file-structure notes
(codebase-graph) + code-relationship notes (Graphify) + vault graph
(knowledge-graph).

## Installation

```bash
uv tool install graphifyy
uv tool install "graphifyy[mcp]"   # optional: MCP protocol server
graphify install --platform hermes # register as Hermes skill
```

Two executables installed: `graphify` (CLI), `graphify-mcp` (MCP server).

## Two-Step Workflow (Verified Behaviour)

The `--obsidian` flag on `graphify .` does **not** trigger the Obsidian
export — it enters extract-only mode. The correct workflow is:

### Step 1 — Build the graph

For a **code-only** project (no .md/.pdf/.txt docs, no images):

```bash
cd /path/to/project
graphify . --no-viz
# Produces: graphify-out/graph.json + .graphify_analysis.json
```

For a project with **documentation files** (markdown, PDFs, images), Graphify
requires an LLM API key for semantic extraction. Set:

```bash
export GEMINI_API_KEY="..."
graphify . --backend gemini --no-viz
```

If no API key is set and docs are present, Graphify errors and stops —
even for code files. For code-only corpora no key is needed.

### Step 2 — Export to Obsidian

```bash
graphify export obsidian --dir ~/Documents/Obsidian\ Vault/Projects/<name>/graphify
```

This produces:
- One `.md` note per code symbol (class, function, variable, module, file)
  with YAML frontmatter (`source_file`, `type`, `community`, `location`, tags)
- Wikilinks (`[[SymbolName]]`) for every relationship with `[EXTRACTED]` /
  `[INFERRED]` / `[AMBIGUOUS]` confidence tags
- Community overview notes (`_COMMUNITY_Community N.md`) with Dataview queries
- `.obsidian/graph.json` for community-coloring in Obsidian's graph view
- `graph.canvas` — interactive canvas with community groupings

### Automation Script

A convenience script lives at `~/.hermes/scripts/graphify-obsidian-integration.py`:

```bash
python ~/.hermes/scripts/graphify-obsidian-integration.py /path/to/project
# optional: --backend gemini --vault /custom/vault/path
```

Runs both steps and copies graph.html, GRAPH_REPORT.md, graph.json alongside
the vault notes under `Projects/<name>/`.

## MCP Server

Register in `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  graphify:
    command: "python"
    args: ["-m", "graphify.serve"]
    cwd: "C:\\Users\\<user>\\Documents\\Projects\\<project>"
    env:
      PATH: "C:\\Users\\<user>\\.local\\bin;%PATH%"
    connect_timeout: 30
```

The server loads `graphify-out/graph.json` and exposes:

| Tool | Purpose |
|------|---------|
| `query_graph` | BFS/DFS search of code graph |
| `get_node` | Full details for a node by label |
| `get_neighbors` | Direct neighbors with edge types |
| `path` | Shortest path between two nodes |
| `explain` | Plain-language node explanation |

`graphify-mcp` (the CLI binary) with no args starts the server on
`graphify-out/graph.json` from the current directory. It hot-reloads when
the graph file changes (polled by mtime+size).

## Cross-Referencing with Project Notes

After exporting to the vault, add wikilinks from existing project notes:

```markdown
## Related Files
- [[Projects/Graphify|Graphify]] — code-level knowledge graph
```

Then refresh the vault knowledge graph:

```bash
python ~/.hermes/skills/note-taking/obsidian-knowledge-graph/scripts/scan_vault.py \
  "~/Documents/Obsidian Vault" \
  "~/Documents/Obsidian Vault/kg_output.json"
python ~/.hermes/skills/note-taking/obsidian/scripts/render_kg.py
```

## Known Limitations

1. **API key for docs**: `graphify .` on a project with `.md`/`.pdf`/image
   files requires `GEMINI_API_KEY` or `GOOGLE_API_KEY`. Code-only projects
   work without one.
2. **No `--obsidian` flag on main command**: Despite the skill doc showing
   `graphify <path> --obsidian`, this enters extract-only mode. Always use
   `graphify export obsidian` as a separate step.
3. **Windows paths**: MSYS paths (`/c/Users/...`) work for `--dir` but native
   `C:\...` paths are more reliable.
4. **Exit code 0 with empty output**: Graphify sometimes exits 0 but produces
   only one line of output (extract-only mode). Check `graphify-out/` contents
   to verify.

## Related Files

- `Projects/Graphify.md` — Obsidian note documenting the integration
- `~/Documents/Projects/graphify/` — cloned repository
- `~/.hermes/scripts/graphify-obsidian-integration.py` — automation script
- `../obsidian-codebase-graph/SKILL.md` — complementary codebase-mapping skill
- `../obsidian-knowledge-graph/SKILL.md` — vault graph scanner
- `decide/SKILL.md` — Complementary Setup Routing entry for Graphify
