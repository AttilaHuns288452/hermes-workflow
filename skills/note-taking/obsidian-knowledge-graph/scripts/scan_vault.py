#!/usr/bin/env python3
"""
Obsidian vault scanner — produces kg_output.json in the format render_kg.py expects.

Usage:
    python scan_vault.py [vault_path] [output_path]

Defaults:
    vault_path  = ~/Documents/Obsidian Vault
    output_path = <vault_path>/kg_output.json

Output: JSON with {nodes: [...], edges: [...], stats: {nodes: N, edges: M}}
Edge keys: "source" / "target" (render_kg.py expects these, NOT "from"/"to")
"""

import json
import re
import sys
from pathlib import Path


def scan(vault_root: Path) -> dict:
    nodes = []
    edges = []
    seen_ids = set()

    def add_node(id_: str, label: str, type_: str):
        if id_ not in seen_ids:
            nodes.append({"id": id_, "label": label, "type": type_})
            seen_ids.add(id_)

    def add_edge(source: str, target: str, label: str):
        edges.append({"source": source, "target": target, "label": label})

    # Root node
    add_node("vault", vault_root.name, "vault")

    folders_seen = set()

    for f in sorted(vault_root.rglob("*.md")):
        rel = f.relative_to(vault_root)
        note_id = str(rel.with_suffix(""))
        label = rel.stem
        parts = list(rel.parts[:-1])
        folder_id = "/".join(parts) if parts else "vault"

        # Ensure folder hierarchy exists
        for i in range(len(parts)):
            fid = "/".join(parts[: i + 1])
            if fid not in folders_seen:
                add_node(fid, parts[i], "folder")
                folders_seen.add(fid)
                parent = "/".join(parts[:i]) if i > 0 else "vault"
                add_edge(parent, fid, "contains")

        # Note node
        add_node(note_id, label, "note")
        parent = folder_id
        add_edge(parent, note_id, "contains")

        # Parse content
        content = f.read_text(encoding="utf-8", errors="replace")

        # Wikilinks
        for m in re.finditer(r"\[\[([^\]|#]+)", content):
            target = m.group(1).strip()
            if target:
                add_edge(note_id, target, "links_to")

        # Tags
        for m in re.finditer(r"#([a-z][\w-]*)", content):
            tag = m.group(1)
            if tag == "":
                continue
            tid = f"tag:{tag}"
            add_node(tid, f"#{tag}", "tag")
            add_edge(note_id, tid, "tagged")

    return {"nodes": nodes, "edges": edges, "stats": {"nodes": len(nodes), "edges": len(edges)}}


if __name__ == "__main__":
    vault_arg = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Documents" / "Obsidian Vault"
    if not vault_arg.exists():
        print(f"ERROR: vault not found at {vault_arg}")
        sys.exit(1)

    graph = scan(vault_arg)
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else vault_arg / "kg_output.json"
    out_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    print(f"Scanned {graph['stats']['nodes']} nodes, {graph['stats']['edges']} edges → {out_path}")
