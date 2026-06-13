# Knowledge Graph Render Workflow

Authoritative pipeline: vault scan → `kg_output.json` → `render_kg.py` → `knowledge_graph.html`

## Pipeline

```
Step 1: Scan vault       → kg_output.json   (67+ nodes, 150+ edges for full vault)
Step 2: Render HTML      → knowledge_graph.html  (38.5 KB, interactive vis-network)
Step 3: Open in browser  → user explores clickable graph
```

## Exact Script Paths

| Step | Script | Path (Windows) |
|------|--------|----------------|
Original scan_vault.py for full vault — see `scripts/scan_vault.py` under this skill. Produces `source`/`target` edge keys. | `scripts/scan_vault.py` (from this skill directory) |
| Render | `render_kg.py` (from obsidian skill) | `~/AppData/Local/hermes/skills/note-taking/obsidian/scripts/render_kg.py` |

## Commands

```bash
# Step 1: Vault scan (use the MCP server or a custom scanner)
# MCP approach: obsidian-knowledge-graph MCP server (registered as 'obsidian-kg')
#   Tool: obsidian_knowledge_graph(vault_path="~/Documents/Obsidian Vault")

# Step 2: Render the interactive HTML
python ~/AppData/Local/hermes/skills/note-taking/obsidian/scripts/render_kg.py

# The script reads kg_output.json from ~/Documents/Obsidian Vault/kg_output.json
# and writes knowledge_graph.html to ~/Documents/Obsidian Vault/knowledge_graph.html
# by default. Pass explicit paths as arguments to override.
```

## Default Paths (script)

| File | Default Path |
|------|-------------|
| Input JSON | `~/Documents/Obsidian Vault/kg_output.json` |
| Output HTML | `~/Documents/Obsidian Vault/knowledge_graph.html` |

Override with positional args:
```bash
python render_kg.py /path/to/input.json /path/to/output.html
```

## Output

- `knowledge_graph.html` is a standalone single-file HTML (~38 KB) with no external dependencies beyond the vis-network CDN script
- Features: search, type filter, click-to-inspect sidebar, stats panel, physics layout
- Open in any browser — no server needed

## Stats Reference

A scan of the full vault typically produces:
- **Nodes**: 60–80 (vault root, folders, notes, tags)
- **Edges**: 140–180 (contains, links_to, tagged relationships)

## Tips

- Run the render script **after** any Obsidian note update to refresh the graph
- The knowledge_graph.html is referenced by the main `Countdown Timer.md` (and similar project notes) as `[[knowledge_graph.html]]`
- The MCP server `obsidian-kg` can also produce the JSON directly if you prefer not to write a local scan script
- **Edge key format**: If writing a custom scanner, edges must use `source`/`target` keys (not `from`/`to`). The render script fails with `KeyError: 'source'` on `from`/`to` format.
