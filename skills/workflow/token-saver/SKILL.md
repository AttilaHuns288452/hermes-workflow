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

### Step B — Probe CodeGraph (MCP Tools First)

Use the built-in MCP tools — no terminal command needed, always available.

**⚠️ IMPORTANT:** If CWD is not inside a project (e.g. `C:\Users\YOUR_USERNAME`), you MUST pass `projectPath` or the MCP server can't find the index:

```
mcp_codegraph_codegraph_explore(query="function_name", projectPath="C:\\Users\\Attila\\Documents\\Projects\\$PROJECT")  # PRIMARY — single call returns defs + source
mcp_codegraph_codegraph_search(query="function_name")      # Broader name search
mcp_codegraph_codegraph_callers(symbol="function_name")    # Who calls it
mcp_codegraph_codegraph_callees(symbol="function_name")    # What it calls
mcp_codegraph_codegraph_impact(symbol="function_name")     # Refactoring impact
mcp_codegraph_codegraph_files(pattern="*.tsx")             # File tree
```

- **Always works** — CodeGraph covers ALL 3,425 files across all projects (104.46 MB index, 52,747 nodes, 125,822 edges)
- **Cost: ~300 tokens** vs reading files directly (~15K+ tokens)
- Returns source code + file paths and line numbers → you know exactly where to read if needed

**Terminal fallback** (use only if MCP tools are unavailable):
```bash
cd ~/Documents/Projects && codegraph query "function_name"
cd ~/Documents/Projects && codegraph callers "function_name"
cd ~/Documents/Projects && codegraph callees "function_name"
cd ~/Documents/Projects && codegraph impact "function_name"
```

### Step C — Probe Graphify (Available for 21/24 Projects)
```bash
# Quick check if this project has a graph
test -f ~/Documents/Projects/$PROJECT/graphify-out/graph.json \
  && echo "✅ EXISTS" || echo "❌ NO GRAPH"

# If yes, query it:
cd ~/Documents/Projects/$PROJECT && \
  ~/.local/bin/graphify.exe query "<question>" --budget 2000 --graph graphify-out/graph.json
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

## Coverage Summary (24 Projects Total)

### Full-Index Table

| Project | CodeGraph | Graphify |
|---------|-----------|----------|
| ai-marketing-skills | ✅ 945-file global index | ✅ 2,270 nodes, 2,885 edges |
| AI-Youtube-Shorts-Generator | ✅ global index | ✅ indexed |
| anime-waifu-quiz | ✅ global index | ✅ indexed |
| API-mega-list | ✅ global index | ✅ 59KB graph |
| atm-crypto-bank | ✅ global index | ✅ 116KB graph |
| atm-machine | ✅ global index | ✅ 461KB graph |
| buildable-plugin-skills | ✅ global index | ✅ 3,152 nodes, 3,352 edges |
| countdown-timer | ✅ global index | ✅ 1.4KB graph |
| ECC | ✅ global index | ✅ 34MB graph (5,821 files) |
| ecosystem-test | ✅ global index | ✅ 9.8KB graph |
| free-ai-tools | ✅ global index | ✅ 236KB graph |
| freebuff-test | ✅ global index | ✅ indexed |
| freelance-rate-calculator | ✅ global index | ✅ indexed |
| freellmapi | ✅ global index | ✅ indexed |
| free-llm-api | ✅ global index | ✅ 1MB graph |
| graphify | ✅ global index | ✅ 7.8MB graph (8,267 nodes) |
| hermes-workflow | ✅ global index | ✅ 7.8MB graph (11,501 nodes, 13,727 edges, built Jun 30) |
| hermes-token-test | ✅ global index | ✅ 33KB graph (45 nodes, 74 edges, built Jun 30) |
| hermes-workflow | ✅ global index | ✅ 7.8MB graph (11,501 nodes, 13,727 edges) |
| MoneyPrinterTurbo | ✅ global index | ✅ 830KB graph |
| MoneyPrinterV2 | ✅ global index | ✅ indexed |
| task-manager-cli | ✅ global index | ✅ 49KB graph |

### Non-Code Projects (No Graphify Index — Correct)
| Project | Reason |
|---------|--------|
| Hermes Skills | Export of ~/.hermes/skills/ tree — documentation, not code |
| hermes-dashboard | Single HTML page |
| unit-converter | No code files |

CodeGraph covers **all 24 projects**. Graphify covers **21/24 projects** with dedicated indices.

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
# CodeGraph MCP tools (preferred — pass projectPath when CWD is outside a project)
mcp_codegraph_codegraph_explore(query="symbol_name", projectPath="C:\\Users\\Attila\\Documents\\Projects\\$PROJ")
mcp_codegraph_codegraph_search(query="symbol_name")

# CodeGraph — terminal fallback (use if MCP tools unavailable)
cd ~/Documents/Projects && codegraph query "symbol_name"

# Graphify — when project has graph.json
cd ~/Documents/Projects/$PROJECT && ~/.local/bin/graphify.exe query "question?" --budget 2000 --graph graphify-out/graph.json

# Check if Graphify index exists
test -f ~/Documents/Projects/$PROJECT/graphify-out/graph.json && echo "EXISTS" || echo "NO GRAPH"
```
