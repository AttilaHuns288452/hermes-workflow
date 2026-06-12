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

This is now actively enforced by `/decide` Mandatory Rule #4 and Execution Order.

---

## The 4-Step Probe Chain (DO THIS, don't just read it)

When you need to understand any code in `~/Documents/Projects/`:

### Step A — Detect Project
Extract `$PROJECT` from the file path. All projects live at `~/Documents/Projects/$PROJECT/`.

### Step B — Probe CodeGraph MCP (Always Available)
```bash
# From ~/Documents/Projects/ where the .codegraph/ DB lives
codegraph query "function_name"
codegraph callers "function_name"
codegraph callees "function_name"
codegraph impact "function_name"
```
- **Always works** — CodeGraph covers ALL 945 files across all projects
- **Cost: ~300 tokens** vs reading files directly (~15K+ tokens)
- Returns file paths + line numbers → you know where to read if needed

### Step C — Probe Graphify (Available for 14/16 Projects)
```bash
# Check if this project has a graph
test -f "$PROJECT/graphify-out/graph.json" && echo "EXISTS" || echo "NO GRAPH"

# If yes, query it:
cd ~/Documents/Projects/$PROJECT
~/.local/bin/graphify.exe query "what does X do?" --budget 2000 --graph graphify-out/graph.json
```
- **Available for:** API-mega-list, atm-crypto-bank, atm-machine, countdown-timer,
  ECC, ecosystem-test, free-ai-tools, freebuff-test, free-llm-api, graphify,
  hermes-workflow, hw-new, MoneyPrinterTurbo, task-manager-cli
- **Not available:** hermes-dashboard (single HTML), unit-converter (no code files)
- **ECC index is 34MB across 5,821 files** — builds in ~6 min, queries in ~300 tokens
- **Cost: ~300 tokens** vs reading source tree (~370K tokens)

### Step D — Targeted Read (Last Resort)
```python
read_file("path/to/file.py", offset=<line>, limit=50)
```
Only after probes A-C failed to provide enough context. Read only the specific section needed.

---

## Coverage Summary

| Project | CodeGraph | Graphify |
|---------|-----------|----------|
| API-mega-list | ✅ 945-file global index | ✅ 59KB graph |
| atm-crypto-bank | ✅ global index | ✅ 116KB graph |
| atm-machine | ✅ global index | ✅ 461KB graph |
| countdown-timer | ✅ global index | ✅ 1.4KB graph |
| ECC | ✅ global index | ✅ 34MB graph (5,821 files) |
| ecosystem-test | ✅ global index | ✅ 9.8KB graph |
| free-ai-tools | ✅ global index | ✅ 236KB graph |
| free-llm-api | ✅ global index | ✅ 1MB graph |
| graphify | ✅ global index | ✅ 7.8MB graph (8,267 nodes) |
| hermes-dashboard | ✅ global index | ❌ no code files |
| hermes-workflow | ✅ global index | ✅ 1.9MB graph |
| hw-new | ✅ global index | ✅ 1.9MB graph |
| MoneyPrinterTurbo | ✅ global index | ✅ 830KB graph |
| task-manager-cli | ✅ global index | ✅ 49KB graph |
| unit-converter | ✅ global index | ❌ no code files |

CodeGraph covers **everything**. Graphify covers **14/16 code projects** with dedicated indices.

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

The `/decide` skill's Mandatory Rule #4 now enforces this as an active pipeline step:

```
session_memory → core-identity-guard → task_tier gate → 
  TOKEN SAVER PROBE (Step A→B→C→D) → 
  domain skills (targeted reads only) →
  complementary check → Obsidian (tier-dependent) → KG refresh
```

The probe chain runs for ALL Tier 2 (task) and Tier 3 (project) requests.
Tier 1 (atomic) requests skip the probe.

---

## Quick Reference (Copy-Paste Commands)

```bash
# CodeGraph — always works from ~/Documents/Projects/
cd ~/Documents/Projects && codegraph query "symbol_name"

# Graphify — when project has graph.json
cd ~/Documents/Projects/$PROJECT && ~/.local/bin/graphify.exe query "question?" --budget 2000 --graph graphify-out/graph.json

# Check if Graphify index exists
test -f ~/Documents/Projects/$PROJECT/graphify-out/graph.json && echo "EXISTS" || echo "NO GRAPH"
```
