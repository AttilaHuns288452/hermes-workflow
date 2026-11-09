---
name: token-saver
description: Enforces CodeGraph MCP + Graphify probing before raw file reads. 4-step probe chain saves 50× to 1,233× tokens per query. Active enforcement in /decide.
triggers:
  - token saving
  - reduce token usage
  - codegraph
  - graphify query
  - token optimization
  - code reading
  - codebase query
---

# Token Saver — 4-Step Probe Chain (ACTIVE ENFORCEMENT)

## Purpose
Eliminate unnecessary full-file reads by probing CodeGraph MCP and Graphify before reading files. Live benchmarks show **50× to 1,233× token reduction** per query depending on scope.

This is enforced by `/decide` Rule 1 (Token Saver Probe Chain).

---

## The 4-Step Probe Chain (DO THIS, don't just read it)

When you need to understand any code in `~/Documents/Projects/`:

### Step A — Detect Project
Extract `$PROJECT` from the file path. All projects live at `~/Documents/Projects/$PROJECT/`.

### Step B — Probe CodeGraph (MCP First)

CodeGraph 1.6.2 exposes exactly **one** MCP tool. There is no per-project global
index any more: each project has its own `.codegraph/`, and you pass `projectPath`
because the session root (`/home/attila`) sits above all of them.

```
mcp__codegraph__codegraph_explore(query="AuthService loginUser", projectPath="/home/attila/Documents/Projects/$PROJECT")
```

- One call returns verbatim source of the relevant symbols, grouped by file, plus
  the call path and a blast-radius list. Treat the returned code as already Read.
- `query` accepts a natural-language question or a bag of symbol/file names.
- `maxFiles` (default 12) caps how much source comes back.

**Terminal fallback** (same output, use when the MCP server is unavailable):
```bash
codegraph explore 'query terms' --path ~/Documents/Projects/$PROJECT
codegraph query 'symbol' -p ~/Documents/Projects/$PROJECT
codegraph callers 'symbol' -p ~/Documents/Projects/$PROJECT
codegraph callees 'symbol' -p ~/Documents/Projects/$PROJECT
codegraph impact  'symbol' -p ~/Documents/Projects/$PROJECT
codegraph node    'symbol' -p ~/Documents/Projects/$PROJECT
codegraph status  ~/Documents/Projects/$PROJECT
```

### CodeGraph maintenance (do this after every upgrade)

```bash
codegraph upgrade --check          # current vs latest
codegraph upgrade                  # upgrade in place (npm/bundle aware)
codegraph index ~/Documents/Projects/$PROJECT   # full rebuild on the new engine
codegraph sync  ~/Documents/Projects/$PROJECT   # or incremental
```

- An index built by an older engine keeps working but `codegraph status` flags it
  (`Index was built by vX; re-index to pick up this engine's improvements`).
- **The running MCP server keeps the old version in memory after an upgrade.** Its
  tool calls then fail with `(0, directory_1.statInode) is not a function`. Kill the
  stdio child (`kill $(pgrep -f 'codegraph serve --mcp')`) — Hermes respawns it on the
  next call and the error disappears.
- The upgrade rewrites `~/.hermes/config.yaml`'s `mcp_servers.codegraph` block; that
  is expected, not a clobber.

### Step C — Probe Graphify (per-project, if present)
```bash
# Quick check if this project has a graph
test -f ~/Documents/Projects/$PROJECT/graphify-out/graph.json \
  && echo "✅ EXISTS" || echo "❌ NO GRAPH"

# If yes, query it:
cd ~/Documents/Projects/$PROJECT && \
  graphify query "<question>" --budget 2000 --graph graphify-out/graph.json
```
- **21/24 projects indexed** — all except: Hermes Skills (exported skills tree, not a code project), hermes-dashboard (single HTML), unit-converter (no code files)
- **ECC index is 34MB across 5,821 files** — queries in ~300 tokens
- **Cost: ~300 tokens** vs reading source tree (~370K tokens)
- **Savings: up to 1,233× per query**

**Full project list:** ai-marketing-skills, AI-Youtube-Shorts-Generator, anime-waifu-quiz, API-mega-list, atm-crypto-bank, atm-machine, buildable-plugin-skills, countdown-timer, ECC, ecosystem-test, free-ai-tools, freebuff-test, freelance-rate-calculator, freellmapi, free-llm-api, graphify, hermes-workflow, hw-new, MoneyPrinterTurbo, MoneyPrinterV2, task-manager-cli

### Step D — Targeted Read (Last Resort)
```python
read_file("path/to/file.py", offset=<line>, limit=50)
```
Only after probes A-C failed to provide enough context. Read only the specific section needed.

---

## Coverage Summary (per-project indexes, measured)

There is no longer a single global index. As of the last rebuild: **44 of 74 project
directories indexed**, 12,942 files, 248,632 nodes, 864 MB of `.codegraph/`.
Only projects with real code (≥15 source files) are indexed; docs/asset dirs are
skipped on purpose.

```bash
# What is indexed / what is missing
ls -d ~/Documents/Projects/*/.codegraph | wc -l
for d in ~/Documents/Projects/*/; do [ -d "$d/.codegraph" ] || echo "missing $(basename $d)"; done

# Per-project statistics
codegraph status ~/Documents/Projects/$PROJECT

# (Re)build everything: ~/.hermes/scripts/codegraph_init_all.sh   (new projects)
#                       ~/.hermes/scripts/codegraph_rebuild_all.sh (new engine)
```

A project with no `.codegraph/` still works — `codegraph init` takes seconds for a
small repo and the graph auto-syncs on file change afterwards.

---

## Token Cost Comparison (Live-Tested)

| Method | Tokens | vs Raw Read | Savings |
|--------|--------|-------------|---------|
| `codegraph query "symbol"` | ~300 | 15K (10 files) | **50×** |
| `graphify query` (BFS traversal) | ~300 | 370K (full tree) | **1,233×** |
| `codegraph callers "fn"` | ~200 | 10K (grep+3 files) | **50×** |
| `graphify explain "symbol"` | ~145 | 5K (1 file) | **35×** |
| Full probe chain (3+2 queries) | ~1,500 | 350K (feature understanding) | **233×** |

---

## Integration with /decide

The `/decide` skill enforces this via **Rule 1 (Token Saver Probe Chain)** and the **Session Startup Protocol**:

At session start, the agent announces:
```
📋 Compliance: Rule 1 (Token Saver) = ACTIVE
```

This makes the probe chain a **stated commitment**, not just documented best practice. The self-audit at session end verifies compliance matches the announcement.

```
session_memory → core-identity-guard → task_tier gate → 
  TOKEN SAVER PROBE (Step A→B→C→D) → 
  domain skills (targeted reads only) →
  complementary check → Obsidian (tier-dependent) → KG refresh
```

The probe chain runs for ALL Tier 2 (task) and Tier 3 (project) requests.
Tier 1 (atomic) requests skip the probe.

---

## Support Files

- `references/live-benchmarks.md` — Live token savings benchmarks (35×–1,233×), 4-step probe commands, Graphify coverage table
- `references/graphify-index-building.md` — Large project build patterns (ECC 34MB/5,821 files), background mode, skip logic

```bash
# CodeGraph (preferred — one tool, pass projectPath)
mcp__codegraph__codegraph_explore(query="symbol_name or a question", projectPath="/home/attila/Documents/Projects/$PROJ")

# CodeGraph — terminal fallback (same output)
codegraph explore "symbol_name" --path ~/Documents/Projects/$PROJ

# Graphify — when project has graph.json
cd ~/Documents/Projects/$PROJECT && graphify query "question?" --budget 2000 --graph graphify-out/graph.json

# Check if Graphify index exists
test -f ~/Documents/Projects/$PROJECT/graphify-out/graph.json && echo "EXISTS" || echo "NO GRAPH"
```
