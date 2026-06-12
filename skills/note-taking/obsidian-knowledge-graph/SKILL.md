---
name: obsidian-knowledge-graph
description: "Scan an Obsidian vault and produce an interactive knowledge graph: nodes (folders, notes, code blocks, tags, concepts) plus edges (contains, links_to, tagged, shared_concept, aliases, backlinks). Also covers the pipeline endpoint: vault scan → JSON → render → browser preview."
platforms: [windows, linux, macos]
---

# Obsidian Knowledge Graph

Turn an Obsidian vault into a navigable node/edge graph. Captures folder hierarchy, markdown files, code blocks, tags, wikilinks, aliases, backlinks, and cross-note concepts as a force‑directed network you can render to an interactive HTML file.

## When to Use

- "map my vault" / "visualize my Obsidian notes" / "create a knowledge graph"
- Project-level graph for a specific project folder inside the vault
- Refresh the graph after adding new notes

## Prerequisites

- Obsidian vault path (`OBSIDIAN_VAULT_PATH` env or `~/Documents/Obsidian Vault`)
- `mcp` for server mode: `pip install mcp`
- `pyvis` for HTML render: `pip install pyvis`

## Two Deployment Modes

### Mode 1 — Standalone vault scanner + render script (no MCP)

Use when the `obsidian-kg` MCP server is unavailable or you want a one-shot scan.

```bash
# Step 1: Scan vault → kg_output.json
python scripts/scan_vault.py ~/Documents/Obsidian\ Vault

# Step 2: Render JSON → interactive HTML
python ~/AppData/Local/hermes/skills/note-taking/obsidian/scripts/render_kg.py

# Step 3: Open in browser (Windows)
start ~/Documents/Obsidian\\ Vault/knowledge_graph.html
```

> **Galaxy-style alternative:** For a visually stunning force-directed graph with deep space background, glowing nebula cluster colors, and pulsing star nodes, use the galaxy renderer instead:
> ```bash
> cd ~/Documents/Obsidian\ Vault
> python render_galaxy_kg.py
> ```
> It reads the same `kg_output.json` — no re-scan needed.
```

Custom paths:
```bash
python scripts/scan_vault.py ~/Documents/Obsidian\ Vault /tmp/kg_output.json
python render_kg.py /tmp/kg_output.json /tmp/kg.html
```

### Mode 2 — MCP server (reusable from Hermes)

Register under `mcp_servers` in `~/.hermes/config.yaml` with server name `obsidian-kg`:

```yaml
mcp_servers:
  obsidian-kg:
    command: "python"
    args: ["-m", "obsidian_kg_mcp"]
    connect_timeout: 30
```

## MCP Tools

| Tool | Purpose | Params |
|------|---------|--------|
| `obsidian_knowledge_graph` | Full graph (nodes + edges + stats) | `vault_path`, `include_code_blocks`, `include_concepts`, `concept_min_occurrences` |
| `obsidian_graph_summary` | Text summary | `vault_path` |

## HTML Render

`scripts/render_graph.py` reads `kg_output.json` and writes `<vault>/knowledge_graph.html`.
Launch with:
```bash
python scripts/render_graph.py
start <vault>/knowledge_graph.html
```

### Windows Python pitfall
Multiple Pythons usually exist (system Python vs Hermes venv). In that order:
1. Run `where python`
2. If `ModuleNotFoundError: No module named 'pyvis'`, use the full path to the system interpreter:
   ```bash
   "C:\Users\<user>\AppData\Local\Programs\Python\Python311\python.exe" scripts/render_graph.py
   ```

### pyvis layout values that work well
```python
net.set_options("""
{
 "physics": {
   "barnesHut": { "gravitationalConstant": -6000, "centralGravity": 0.08,
     "springLength": 180, "springConstant": 0.04, "damping": 0.25,
     "avoidOverlap": 0.85 },
   "stabilization": { "iterations": 200, "updateInterval": 25 }
 },
 "nodes": { "borderWidth": 2, "font": { "size": 14, "face": "Segoe UI" } },
 "edges": { "arrows": { "to": { "enabled": true, "scaleFactor": 0.5 }},
   "smooth": { "type": "curvedCW", "roundness": 0.2 } }
}
""")
```

## Node type map

| Type | Group-level | Color | Shape | Purpose |
|------|-------------|-------|-------|---------|
| vault | 0 | #89b4fa | diamond | Root |
| folder | 1 | #a6e3a1 | hexagon | Directories |
| note | 2 | #f9e2af | box | .md / .canvas files |
| code_block | 3 | #fab387 | triangle | Meaningful code fenced blocks |
| tag | 4 | #cba6f7 | dot | #tag nodes |
| concept | 5 | #f38ba8 | ellipse | Cross‑note terms |
| alias | 6 | #94e2d5 | square | YAML frontmatter aliases |

## Refresh cycle

When a new note or project is added:

1. Re-run the renderer
2. Browser refresh picks up the new graph
3. Add `[[wikilinks]]` to inter‑connect new notes — edges appear in next render

## Pitfalls

- **Edge key format mismatch.** `render_kg.py` expects edges with `source`/`target` keys (`{"source": "...", "target": "..."}`). If you write a custom scanner using `from`/`to`, the render step fails with `KeyError: 'source'`. The bundled `scripts/scan_vault.py` produces correct output.
- **Windows path escaping in config.yaml**. Use doubled backslashes in literal paths.
- **MCP `cwd` must be absolute** — it resolves from the scheduler, not the project.
- **`npx -y` for ephemeral npm packages** — preferred over a global install.
- **Concept false positives** — leave `concept_min_occurrences >= 2` unless you want noise.
