---
name: project-documentation
description: Generate structured documentation folder for a codebase — overview, architecture, modules, data flow, dependencies, gaps. Creates 6 subfolders with README.md files inside the Obsidian vault.
platforms: [linux, macos, windows]
on_demand: true
related_skills:
  - note-taking/obsidian-codebase-graph
  - note-taking/obsidian
  - note-taking/obsidian-knowledge-graph
---

# Project Documentation Generator

> **ON-DEMAND ONLY** — Never auto-generate documentation without explicit user request. Trigger phrases: "create documentation for", "document [project]", "generate project docs", or "organize and recreate my whole obsidian notes" which triggers for ALL active projects.

Generates a 6-folder documentation tree for a given project inside the Obsidian vault under `Documentation/<Project Name>/`.

## Folder Structure

```
Documentation/<Project Name>/
├── 01_overview/
│   └── README.md          — One-paragraph purpose, tech stack, entry point(s)
├── 02_architecture/
│   └── README.md          — ASCII/Mermaid system diagram, major component roles
├── 03_modules/
│   └── *.md               — One file per major module/directory in the actual codebase
├── 04_data_flow/
│   └── README.md          — 2-3 real execution paths end-to-end with file/function names
├── 05_dependencies/
│   └── README.md          — Internal module deps + external libs/services + why
└── 06_gaps_and_todos/
    └── README.md          — Undocumented/fragile/uncertain parts flagged honestly
```

## Workflow

### Step 1 — Explore the Codebase
Use these tools to understand the actual code:
- **CodeGraph MCP** (primary): `codegraph_files()` for tree, `codegraph_explore()` for symbols, `codegraph_search()` for specific functions
- **Terminal**: `find` for directory tree, `grep` for patterns
- **search_files**: find by content pattern
- **read_file**: read specific files (entry points, configs, main modules)

### Step 2 — Read These Files Always
- `package.json` / `pyproject.toml` / `Cargo.toml` — dependencies, scripts
- `README.md` — stated purpose
- Config files (next.config, tsconfig, etc.)
- Entry point files (main.ts, app.tsx, __init__.py, main.py)
- Key module files in src/ or app/

### Step 3 — Base on Actual Code, Not Assumptions
- Use real file names and function names from the codebase
- If unsure how something connects, say so in `06_gaps_and_todos/README.md`
- NEVER invent explanations or make up data flow paths
- Include line numbers and file paths where relevant

### Step 4 — Writing Rules
- Keep each file scannable: short sections, code references, no filler prose
- Use actual file/function names, not generic placeholders
- Each README stands alone (don't assume reader has read the others)
- Output is Markdown inside the Obsidian vault

### Step 5 — Output Location
All documentation goes to `~/Documents/Obsidian Vault/Documentation/<Project Name>/<section>/README.md`

## Pitfalls

- **CodeGraph MCP may be rate-limited** — if it fails, fall back to terminal `find` + `grep` + `read_file`
- **Project may not have CodeGraph index** — run `codegraph init` first in that project, or use terminal-only exploration
- **Some projects are Next.js** — the automated `generate_codebase_graph.py` script only handles TS/JSX; Python/C# projects need manual exploration
- **Don't auto-run this** — wait for explicit user trigger ("create documentation for X" or "organize and recreate my whole obsidian notes")
- **Subagent exploration** is useful for deep dives — delegate codebase exploration to subagents for large projects, then compose the docs from their summaries
