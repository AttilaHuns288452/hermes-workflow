# Obsidian Knowledge Graph MCP Server — Pattern Reference

## Overview

Custom MCP server built for scanning Obsidian vaults and producing structured knowledge graphs with nodes and edges.

## Server Implementation

**File**: `~/.hermes/tools/obsidian_kg_mcp.py`

**Run as MCP stdio server**:
```bash
python -m obsidian_kg_mcp
```

**Hermes Config**:
```yaml
mcp_servers:
  obsidian-kg:
    command: "python"
    args: ["-m", "obsidian_kg_mcp"]
    cwd: "C:\\Users\\<user>\\.hermes\\tools"
    connect_timeout: 30
```

## Tools Exposed

| Tool | Purpose |
|------|---------|
| `obsidian_knowledge_graph` | Full graph — nodes + edges |
| `obsidian_graph_summary` | Lightweight text summary |

## Graph Schema

### Node Types
- `vault` — Root vault node
- `folder` — Directory nodes (hierarchical)
- `note` — Markdown files (`.md`, `.canvas`)
- `code_block` — Fenced code blocks meeting "meaningful" criteria
- `tag` — `#tag` references (global nodes)
- `concept` — Cross-note terms (CamelCase, backtick-quoted) appearing ≥N times
- `alias` — Frontmatter `aliases:` entries

### Edge Types
- `contains` — Parent → child (vault→folder, folder→note, note→code_block)
- `links_to` — Wikilink `[[Note]]` connections
- `tagged` — Note → tag
- `shared_concept` — Note → concept (multi-occurrence terms)
- `alias_of` — Note → alias
- `references` — Code block → code block (future)
- `depends_on` — Code block dependency (future)

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `vault_path` | string | `~/Documents/Obsidian Vault` | Absolute vault path |
| `include_code_blocks` | bool | true | Extract meaningful code blocks |
| `include_concepts` | bool | true | Detect cross-note concepts |
| `concept_min_occurrences` | int | 2 | Min count for concept node |

## "Meaningful" Code Block Detection

Blocks are included when they match patterns indicating:
- Function/class definitions (`def `, `class `, `function `, `fn `)
- Control flow (`if `, `for `, `while `, `try `)
- Imports/dependencies (`import `, `require(`, `export `)
- Shell commands (`npm `, `pip `, `docker `, `git `, `$(`)
- SQL (`SELECT`, `INSERT`, `CREATE TABLE`)

Language-aware: bash/powershell/shell blocks always included.

## Concept Extraction

Two sources:
1. **CamelCase terms** — `PascalCase`, `camelCase` identifiers
2. **Backtick-quoted** — `` `term` `` inline code

Terms normalized, counted across notes. Become `concept` nodes when count ≥ threshold.

## Output Format

```json
{
  "nodes": [{"id", "type", "label", "path", "metadata", "__type": "node"}],
  "edges": [{"source", "target", "type", "label", "metadata", "__type": "edge"}],
  "stats": {"total_nodes", "total_edges", "node_types", "edge_types", "vault"}
}
```

## Visualization

**Standalone renderer**: `render_graph.py` → `knowledge_graph.html`
- Uses `pyvis` / `vis-network` (CDN)
- Hierarchical layout (vault→folder→note→code_block)
- Dimmed semantic nodes (tags/concepts) as overlay
- Search, filter, clickable sidebar

## Mermaid Diagrams in Vault

Each note gets a `## Knowledge Graph Position` section with Mermaid flowchart showing local topology. Renders natively in Obsidian.

## Tags

#obsidian #mcp-server #knowledge-graph #pattern-reference