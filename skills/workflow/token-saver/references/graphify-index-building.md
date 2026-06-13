# Building Graphify Indices — Large Project Patterns

## Standard Build
```bash
cd ~/Documents/Projects/$PROJECT
~/.local/bin/graphify.exe update .
# Output: "graph.json, graph.html and GRAPH_REPORT.md updated in graphify-out"
```

## Large Projects (ECC — 5,821 files, 34MB graph)

**Problem**: `graphify update .` timed out at 120s, 300s, 600s in foreground mode.

**Solution**: Background with notify_on_complete
```bash
# Terminal (background, notify on complete)
cd ~/Documents/Projects/ECC
terminal(command="~/.local/bin/graphify.exe update .", background=true, notify_on_complete=true)
# Returns session_id immediately; you get notification when done
```

**Verification** (poll after notification):
```bash
ls -lh ~/Documents/Projects/ECC/graphify-out/graph.json
# -rw-r--r-- 1 Attila 197121 34388793 Jun 12 17:44 graph.json  (34MB)

~/.local/bin/graphify.exe query "agents" --budget 2000 --graph graphify-out/graph.json
# Returns 18 nodes — graph is valid and queryable
```

**Timing**: ~6 minutes for 5,821 files. Background mode is essential.

## Projects That Don't Need Indices

| Project | Reason | Action |
|---------|--------|--------|
| hermes-dashboard | Single HTML file, no code | Skip |
| unit-converter | No source code files | Skip |
| Single-file HTML projects | No AST to extract | Skip |

## Skip Logic in Probe Chain

The 4-step probe chain handles missing indices gracefully:
1. **Step A** detects project
2. **Step B** CodeGraph — **always works** (945 files global index)
3. **Step C** Graphify — `ls graphify-out/graph.json` check first, skip if missing
4. **Step D** `read_file` — only if B+C insufficient

**No blocking** — missing Graphify index just means CodeGraph-only probe.

## Updating Indices After Code Changes

```bash
# Incremental update (fast, no LLM)
cd ~/Documents/Projects/$PROJECT
~/.local/bin/graphify.exe update .
# Re-extracts changed files only
```

## Cache Location

```
~/Documents/Projects/$PROJECT/graphify-out/
├── graph.json          # Main graph (nodes + edges)
├── graph.html          # Visualization
├── GRAPH_REPORT.md     # Build stats
├── manifest.json       # File manifest
├── .graphify_labels.json
├── .graphify_root
└── cache/
    ├── ast/            # Per-file AST caches (hashed filenames)
    └── stat-index.json
```

ECC cache: ~62MB across ~5,800 AST cache files.