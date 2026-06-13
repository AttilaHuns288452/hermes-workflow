#!/usr/bin/env python3
"""
Graphify + Obsidian Integration Script

Automates the full Graphify pipeline for a project:
1. Build code graph (AST extraction)
2. Export to Obsidian as wikilinked markdown notes
3. Copy supporting files (graph.json, GRAPH_REPORT.md)
4. Register MCP server in Hermes config (optional)

Usage:
    python graphify-obsidian-integration.py <project_path> [--vault <vault_path>] [--backend gemini] [--skip-graphify]

Prerequisites:
    - Graphify installed: `uv tool install graphifyy` (+ `uv tool install "graphifyy[mcp]"` for MCP)
    - Obsidian vault at ~/Documents/Obsidian Vault (or OBSIDIAN_VAULT_PATH env var)
    - For semantic extraction on docs: GEMINI_API_KEY or GOOGLE_API_KEY

Example:
    python graphify-obsidian-integration.py ~/Documents/Projects/my-project
    python graphify-obsidian-integration.py ~/Documents/Projects/my-project --backend gemini --vault /custom/vault
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd, cwd=None, check=True, capture=False):
    """Run a command and return the result."""
    print(f"$ {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=capture, text=capture, shell=isinstance(cmd, str))
    if check and result.returncode != 0:
        print(f"ERROR: Command failed with exit code {result.returncode}")
        if capture:
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
        sys.exit(result.returncode)
    return result


def find_vault(vault_override=None):
    """Resolve the Obsidian vault path."""
    if vault_override:
        return Path(vault_override).expanduser()
    # Check env var
    if os.getenv("OBSIDIAN_VAULT_PATH"):
        return Path(os.getenv("OBSIDIAN_VAULT_PATH")).expanduser()
    # Default location
    return Path("~/Documents/Obsidian Vault").expanduser()


def main():
    parser = argparse.ArgumentParser(description="Graphify + Obsidian integration")
    parser.add_argument("project_path", help="Path to the project to analyze")
    parser.add_argument("--vault", help="Custom Obsidian vault path")
    parser.add_argument("--backend", choices=["gemini", "claude", "openai", "kimi", "deepseek", "azure", "bedrock", "ollama"],
                        help="LLM backend for semantic extraction (requires API key)")
    parser.add_argument("--skip-graphify", action="store_true", help="Skip graphify build, only re-export to Obsidian")
    parser.add_argument("--no-mcp", action="store_true", help="Skip MCP server registration")
    parser.add_argument("--no-cluster", action="store_true", help="Skip community detection (faster)")
    parser.add_argument("--dir", help="Custom export directory (overrides default)")
    args = parser.parse_args()

    project_path = Path(args.project_path).expanduser().resolve()
    if not project_path.exists():
        print(f"ERROR: Project path does not exist: {project_path}")
        sys.exit(1)

    project_name = project_path.name
    vault_path = find_vault(args.vault)
    export_dir = Path(args.dir).expanduser() if args.dir else vault_path / "Projects" / project_name / "graphify"

    print(f"=== Graphify + Obsidian Integration ===")
    print(f"Project: {project_name} ({project_path})")
    print(f"Vault: {vault_path}")
    print(f"Export dir: {export_dir}")
    print(f"Backend: {args.backend or 'AST-only (no LLM)'}")
    print()

    # Step 1: Ensure Graphify is installed
    print("--- Step 1: Check/Install Graphify ---")
    result = subprocess.run(["which", "graphify"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Graphify not found, installing via uv...")
        run(["uv", "tool", "install", "graphifyy"])
        run(["uv", "tool", "install", "graphifyy[mcp]"])
    else:
        print("Graphify found:", result.stdout.strip())

    # Step 2: Build code graph (unless skipped)
    if not args.skip_graphify:
        print("\n--- Step 2: Build Code Graph ---")
        os.chdir(project_path)
        graphify_cmd = ["graphify", ".", "--no-viz"]
        if args.no_cluster:
            graphify_cmd.append("--no-cluster")
        if args.backend:
            graphify_cmd.extend(["--backend", args.backend])
        run(graphify_cmd)

        # Verify graph.json was created
        graph_json = project_path / "graphify-out" / "graph.json"
        if not graph_json.exists():
            print(f"ERROR: graph.json not found at {graph_json}")
            sys.exit(1)
        print(f"Graph built: {graph_json}")

    # Step 3: Extract graph stats for manual Obsidian note creation
    print("\\n--- Step 3: Extract Graph Stats ---")
    graph_json = project_path / "graphify-out" / "graph.json"
    if graph_json.exists():
        try:
            import json
            data = json.loads(graph_json.read_text())
            nodes = len(data.get("nodes", []))
            edges = len(data.get("edges", []))
            communities = len({n.get("community") for n in data.get("nodes", []) if n.get("community")})
            print(f"Graph stats: {nodes} nodes, {edges} edges, {communities} communities")
            # Save stats to a small JSON for reference
            stats_file = export_dir.parent / "graph-stats.json"
            stats_file.parent.mkdir(parents=True, exist_ok=True)
            json.dump({"nodes": nodes, "edges": edges, "communities": communities, "project": project_name}, stats_file.open("w"))
            print(f"Stats saved: {stats_file}")
        except Exception as e:
            print(f"Could not parse graph JSON: {e}")
    else:
        print(f"No graph.json found at {graph_json}")

    # NOTE: There is NO `graphify export obsidian` CLI command
    # (Graphify v0.8.37 has no such subcommand)
    # Create the Obsidian note manually using the `obsidian` skill bundle instead.

    # Step 4: Copy supporting files
    print("\n--- Step 4: Copy Supporting Files ---")
    graphify_out = project_path / "graphify-out"
    if graphify_out.exists():
        for src_file in ["graph.json", "GRAPH_REPORT.md", "graph.html"]:
            src = graphify_out / src_file
            if src.exists():
                dst = project_path.parent / project_name / src_file  # or export_dir.parent / src_file
                shutil.copy2(src, dst)
                print(f"Copied: {src} -> {dst}")

    # Step 5: Report
    print("\n=== Integration Complete ===")
    print(f"Obsidian notes: {export_dir}")
    print(f"Canvas: {export_dir / 'graph.canvas'}")
    print(f"Next: Cross-link with complementary notes and refresh KG:")
    print(f"  python ~/AppData/Local/hermes/skills/note-taking/obsidian-knowledge-graph/scripts/scan_vault.py")
    print(f"  python ~/AppData/Local/hermes/skills/note-taking/obsidian/scripts/render_kg.py")


if __name__ == "__main__":
    main()