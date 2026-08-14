#!/usr/bin/env python3
"""Render an Obsidian knowledge-graph JSON into a standalone HTML file using vis-network CDN.

Usage (inside skill_manage context this is a reference asset — call it via terminal):
    python C:\\Users\\YOUR_USERNAME\\.hermes\\skills\\note-taking\\obsidian\\scripts\
ender_kg.py \
        C:\\Users\\YOUR_USERNAME\\Documents\\Obsidian Vault\\kg_output.json \
        C:\\Users\\YOUR_USERNAME\\Documents\\Obsidian Vault\\knowledge_graph.html

If no args given, reads ~/Documents/Obsidian Vault/kg_output.json
and writes ~/Documents/Obsidian Vault/knowledge_graph.html.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DEFAULT_JSON = Path.home() / "Documents" / "Obsidian Vault" / "kg_output.json"
DEFAULT_HTML = Path.home() / "Documents" / "Obsidian Vault" / "knowledge_graph.html"

json_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_JSON
html_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_HTML

if not json_path.exists():
    print(f"ERROR: {json_path} not found. Run scan_vault() first.")
    sys.exit(1)

with open(json_path, encoding="utf-8") as f:
    graph = json.load(f)

COLOR = {
    "vault": "#89b4fa", "folder": "#a6e3a1", "note": "#f9e2af",
    "code_block": "#fab387", "tag": "#cba6f7",
    "concept": "#f38ba8", "alias": "#94e2d5",
}
SIZE = {"vault": 35, "folder": 25, "note": 18, "code_block": 12, "tag": 14, "concept": 10, "alias": 10}

nodes_json = json.dumps([
    {"id": n["id"], "label": n["label"],
     "title": f"{n.get('type','?')}: {n.get('path','')}",
     "color": {"background": COLOR.get(n.get("type", ""), "#888"), "border": COLOR.get(n.get("type", ""), "#888")},
     "size": SIZE.get(n.get("type", ""), 12), "group": n.get("type", "note")}
    for n in graph["nodes"]
], ensure_ascii=False)

edges_json = json.dumps([
    {"from": e["source"], "to": e["target"],
     "label": e.get("label", e.get("type", "")),
     "dashes": e.get("type", "") not in ("contains", "links_to", "shared_concept"),
     "arrows": {"to": {"enabled": True}}}
    for e in graph["edges"]
], ensure_ascii=False)

stats = graph.get("stats", {})
stats_json = json.dumps(stats, ensure_ascii=False)

html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Obsidian Vault Knowledge Graph</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI', system-ui, sans-serif; overflow: hidden; }}
#top {{ position: fixed; top: 0; left: 0; right: 0; z-index: 10; background: rgba(30,30,46,0.92); padding: 8px 16px; border-bottom: 1px solid #45475a; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }}
#top h1 {{ font-size: 0.9rem; font-weight: 600; margin-right: auto; }}
#search {{ background: #313244; border: 1px solid #45475a; color: #cdd6f4; padding: 5px 10px; border-radius: 6px; font-size: 0.78rem; width: 180px; outline: none; }}
#search:focus {{ border-color: #89b4fa; }}
.legend {{ display: flex; gap: 8px; flex-wrap: wrap; }}
.legend-item {{ display: flex; align-items: center; gap: 3px; font-size: 0.68rem; color: #a6adc8; }}
.dot {{ width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }}
#graph {{ position: fixed; top: 42px; left: 0; right: 0; bottom: 0; }}
#sidebar {{ position: fixed; right: 0; top: 42px; bottom: 0; width: 290px; background: #181825; border-left: 1px solid #45475a; overflow-y: auto; padding: 14px; font-size: 0.75rem; transform: translateX(100%); transition: transform 0.25s; z-index: 9; }}
#sidebar.open {{ transform: translateX(0); }}
#sidebar h3 {{ color: #cdd6f4; margin-bottom: 5px; font-size: 0.85rem; }}
#sidebar .st {{ color: #a6adc8; margin-top: 6px; }}
#sidebar .val {{ color: #f9e2af; word-break: break-all; }}
#close-sidebar {{ float: right; cursor: pointer; color: #f38ba8; background: none; border: none; font-size: 1rem; }}
#stats-btn {{ background: #313244; border: 1px solid #45475a; color: #cdd6f4; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; cursor: pointer; }}
</style></head><body>
<div id="top">
  <h1>🧠 Obsidian Vault Knowledge Graph</h1>
  <input id="search" placeholder="Search…" autocomplete="off">
  <select id="filter"><option value="">All types</option>
    <option value="vault">Vault</option><option value="folder">Folder</option>
    <option value="note">Note</option><option value="code_block">Code</option>
    <option value="tag">Tag</option><option value="concept">Concept</option></select>
  <div class="legend">
    <span class="legend-item"><span class="dot" style="background:#89b4fa"></span>Vault</span>
    <span class="legend-item"><span class="dot" style="background:#a6e3a1"></span>Folder</span>
    <span class="legend-item"><span class="dot" style="background:#f9e2af"></span>Note</span>
    <span class="legend-item"><span class="dot" style="background:#fab387"></span>Code</span>
    <span class="legend-item"><span class="dot" style="background:#cba6f7"></span>Tag</span>
    <span class="legend-item"><span class="dot" style="background:#f38ba8"></span>Concept</span>
  </div>
  <button id="stats-btn" onclick="toggleStats()">📊 Stats</button>
</div>
<div id="graph"></div>
<div id="sidebar">
  <button id="close-sidebar" onclick="this.closest('#sidebar').classList.remove('open')">✕</button>
  <div id="sidebar-content"></div>
</div>
<script>
const nodes=new vis.DataSet({nodes_json});
const edges=new vis.DataSet({edges_json});
const data={{nodes,edges}};
const network=new vis.Network(document.getElementById('graph'),data,{{
  physics:{{barnesHut:{{gravitationalConstant:-3000,centralGravity:0.3,springLength:120,damping:0.2}},stabilization:{{iterations:100}}}},
  interaction:{{hover:true,navigationButtons:true,keyboard:true}}
}});
const _n=nodes.get(),_e=edges.get();
document.getElementById('search').addEventListener('input',function(){{
  const q=this.value.toLowerCase();
  const m=new Set(_n.filter(n=>n.label.toLowerCase().includes(q)).map(n=>n.id));
  nodes.update(_n.map(nd=>({{id:nd.id,hidden:q&&!m.has(nd.id),opacity:q&&!m.has(nd.id)?0.15:1}})));
  edges.update(_e.map(e=>({{id:e.id,hidden:q&&!m.has(e.from)&&!m.has(e.to)}})));
}});
document.getElementById('filter').addEventListener('change',function(){{
  const t=this.value;
  nodes.update(_n.map(nd=>({{id:nd.id,hidden:!!t&&nd.group!==t}})));
  edges.update(_e.map(e=>({{id:e.id,hidden:!!t}})));
}});
network.on('click',function(p){{
  if(!p.nodes.length)return;
  const nd=_n.find(n=>n.id===p.nodes[0]);if(!nd)return;
  document.getElementById('sidebar-content').innerHTML=
    `<h3>${{nd.label}}</h3><p class='st'>Type</p><p class='val'>${{nd.group}}</p><p class='st'>ID</p><p class='val' style='font-size:0.6rem'>${{nd.id}}</p><p class='st'>Links</p><p class='val'>${{network.getConnectedNodes(nd.id).length}}</p>`;
  document.getElementById('sidebar').classList.add('open');
}});
function toggleStats(){{document.getElementById('sidebar-content').innerHTML=`<h3>📊 Stats</h3>
<p class='st'>Nodes</p><p class='val'>${{stats.total_nodes}}</p><p class='st'>Edges</p><p class='val'>${{stats.total_edges}}</p>
<p class='st'>Vault</p><p class='val'>${{stats.vault}}</p><hr style='border-color:#313244;margin:6px 0'>
<p class='st'>Node breakdown</p>`+Object.entries(stats.node_types||{{}}).filter(([,c])=>c>0).map(([t,c])=>`<p class='st'>${{t}}</p><p class='val'>${{c}}</p>`).join('')+`<hr style='border-color:#313244;margin:6px 0'><p class='st'>Edge breakdown</p>`+Object.entries(stats.edge_types||{{}}).filter(([,c])=>c>0).map(([t,c])=>`<p class='st'>${{t}}</p><p class='val'>${{c}}</p>`).join('');document.getElementById('sidebar').classList.add('open');}}
</script></body></html>"""

html_path.write_text(html, encoding="utf-8")
print(f"Saved: {html_path}")
print(f"Size: {html_path.stat().st_size / 1024:.1f} KB")
