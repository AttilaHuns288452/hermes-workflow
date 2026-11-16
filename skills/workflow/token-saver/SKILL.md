---
name: token-saver
description: Use before reading code or loading skills. CodeGraph + RAG first.
triggers:
  - token saving
  - reduce token usage
  - codegraph
  - lightrag
  - rag first
  - skill lookup
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

### Step 0 — RAG first (the cheapest move, 0.3s, ~100 tokens)

Before opening any SKILL.md or starting a grep/find spree:

```bash
python3 ~/.hermes/scripts/lightrag_find.py "your query terms"     # top-5 skill paths
python3 ~/.hermes/scripts/lightrag_hermes.py ask "cross-skill q"  # only when paths are not enough
```

Then open only the one or two paths it returns. A full SKILL.md costs 2K-6K tokens;
opening three "just in case" is the waste this whole skill exists to prevent.
Measured 2026-11-14: `lightrag_find` = 0.32s / 392 chars output, vs 7.9K chars for
one skill body and 25.8K for `software-engineering`.

CodeGraph answers *where is this code*, LightRAG answers *which skill covers this*,
`session_search` answers *did we already do this*. Probe all three before
re-deriving anything from scratch. Freshness is automatic (cron `d41d3840aec4`, 03:00).

---

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

Freshness is automated: cron `d41d3840aec4` runs `~/.hermes/scripts/discovery_refresh.py`
nightly at 03:00 — `codegraph sync` on any index older than its newest source file,
`codegraph init --yes` on projects with >=15 source files and no index, then an
incremental `lightrag_hermes.py index-skills`. Silent when everything is fresh.
Manual escape hatch after a bulk edit: `python3 ~/.hermes/scripts/discovery_refresh.py`
(self-check: `python3 ~/.hermes/scripts/discovery_refresh.py --selftest`; it lives inside
the script because standalone `test_*.py` files keep disappearing from `~/.hermes/scripts`).
`codegraph index` refuses to create an index; new projects need `init --yes`. A stale index
is healed with `sync` (incremental), not a full rebuild.

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
- **Project coverage is live, not a fixed list.** Check each project with `[ -d ~/Documents/Projects/$PROJECT/.codegraph ]` and use `codegraph status`; initialize a code-bearing project with `codegraph init` when needed.
- Graphify coverage and size are also live. If `graphify-out/graph.json` exists, query it; otherwise skip Graphify.

**Do not hardcode a project list.** Discover indexed projects from the filesystem and verify the target project directly.

### Step D — Targeted Read (Last Resort)
```python
read_file("path/to/file.py", offset=<line>, limit=50)
```
Only after probes A-C failed to provide enough context. Read only the specific section needed.

---

## Per-turn fixed cost: measure before optimizing (this is where the real money is)

When the question is "are we saving tokens", separate the three costs, because they differ by an order of magnitude and only one of them is worth engineering:

| Cost | What it is | Rough size (this box) |
|---|---|---|
| Fixed, every turn | skills catalog rows + MEMORY.md + SOUL.md + USER.md | 50-55K tok |
| Per skill load | SKILL.md body | 2-6K tok |
| Per probe | `lightrag_find` / `codegraph explore` | 60-4K tok |

Measure, do not estimate:

```bash
# rendered catalog, exactly as the prompt renders it
cd ~/.hermes/hermes-agent && python3 -c "
import sys; sys.path.insert(0,'.')
from agent import prompt_builder as pb
t = pb.build_skills_system_prompt(available_tools={'skill_view','skill_manage','skills_list','terminal','web_search'})
print(f'catalog: {len(t)//4:,} tok, {t.count(chr(10)+\"  - \")} rows')"

# fixed text files injected every turn
wc -c ~/.hermes/memories/MEMORY.md ~/.hermes/SOUL.md ~/.hermes/memories/USER.md

# real billed tokens from your own history (the cache truth)
sqlite3 ~/.hermes/state.db "SELECT sum(input_tokens), sum(cache_read_tokens) FROM sessions WHERE input_tokens>0"
```

**Prompt caching changes the arithmetic by ~8-10x.** On this box 97% of all-time input tokens were cache reads, so a 17.8K catalog costs ~1.8K token-equivalents per turn, not 17.8K. Any "let's cut the catalog" plan must be sized against the cached number or it overstates the win by an order of magnitude. Corollary: cache misses are the expensive event — adding a skill, editing memory, or editing SOUL flushes the prefix and bills full price once, so batch those edits and avoid churning them mid-session.

**MEMORY.md can silently outgrow the whole skills catalog.** It is injected whole every turn with no truncation pressure, so it grows unbounded while the catalog self-limits via truncated descriptions. Check its size before blaming the catalog.

## Usage evidence: use the telemetry file, never a grep over messages

Before disabling/archiving skills to save tokens, get the authoritative usage data:

```bash
python3 -c "import json,os;d=json.load(open(os.path.expanduser('~/.hermes/skills/.usage.json')));print(len([k for k,v in d.items() if not v.get('view_count') and not v.get('use_count')]))"
```

Each entry carries `view_count`, `use_count`, `pinned`, `state`. Skills under `skills.external_dirs` have NO telemetry — they are untracked, not unused; never treat a missing record as zero usage.

`hermes config set skills.disabled '[...]'` prints `⚠ 'skills.disabled' is not a recognized config key — it was saved anyway` — this warning is WRONG and the key does work: `agent.skill_utils.get_disabled_skill_names()` reads `skills.disabled` (global list) and `skills.platform_disabled` without any schema registration. Verify a config edit by exercising the reader (`python3 -c "from agent.skill_utils import get_disabled_skill_names; print(get_disabled_skill_names())"` from `~/.hermes/hermes-agent`), never by trusting that warning. The same pattern applies to any block the CLI did not know about at release: it round-trips the YAML regardless.

A `LIKE '%skill_view%'` scan over the messages table is NOT a substitute: it silently covers only the rows that happen to contain the string and will over-report "never used" by an order of magnitude (2403 of 205190 messages scanned read as 736 unused skills, versus 74 from the telemetry file). Acting on the grep number would have disabled actively-used skills.

## Cutting catalog tokens: disabling is NOT safe, names-only is

`skills.disabled` removes the row from the prompt catalog — but it ALSO makes
`skill_view(name)` refuse the skill outright (`Skill '<name>' is disabled. Enable it with
hermes skills or inspect the files directly on disk.`). A disabled skill is therefore
gone from the catalog AND unloadable, so `lightrag_find` cannot rescue it either: the
telemetry-indexed name comes back as a dead end. Treat disabling as archiving, not as a
cache. Never disable a skill to save tokens on the assumption it stays reachable.

A monkeypatch test that stubs `_get_disabled_skill_names` and reads the catalog WILL
appear to prove loadability (the stub never reaches the tool-side gate) — always verify a
disable experiment by calling `skill_view` on the live path, not by inspecting a catalog
object.

`compact_categories` is the lever that does preserve capability: it renders whole
categories as names-only lines, so every name stays in the prompt and every body stays
loadable. But it is not independently reachable — it only activates when
`agent.coding_context: focus`, and focus mode ALSO collapses the toolset to
`CODING_TOOLSET`. Turning it on to slim the catalog is not a pure catalog change; budget
for the tool regression or leave the catalog alone.

Measured cost of the levers (865-row catalog): demoting 8 categories = ~2,838 tok;
disabling all 74 never-used tracked skills = only ~1,314 tok. Neither is worth a
capability loss. **The catalog is usually not the win — MEMORY.md is.**

## What each layer does NOT cover (probe-verified, not assumed)

Pick the layer by what it indexes, or you will search a layer that structurally cannot answer:

| Layer | Covers | Blind spots |
|---|---|---|
| CodeGraph | code symbols (functions, classes, call edges) in each project's `.codegraph/` | **Markdown entirely** — a test dir with one `.md` and one `.py` indexed 1 file, python only. Skill references are invisible to it. `~/.hermes/skills` has no index at all. |
| BM25 skill index | every `SKILL.md` body, `body[:12000]` chars, plus `name` 4x / `description` 3x / `triggers` 2x boost | `references/`, `templates/`, `scripts/` content — and siblings beyond char 12000 of a long body |
| LightRAG | `SKILL.md` files under the corpus roots | reference files unless run with `--with-references` (thousands of files, hours) |

Consequence for skills you build: depth parked in `references/` is invisible to all three search layers, so the SKILL.md routing table is the ONLY index that can reach it. Two things follow: put the reference vocabulary in the frontmatter `triggers:` list (it is 2x-weighted and it is what lets a reference-heavy skill win a query its body does not mention), and keep every reference named in the routing table by full path. Verify with `lightrag_find.py` on a natural request, not by reading the table and assuming.

For a fact that exists only inside a reference file, skip the layers and grep the skill dir — `grep -rl 'Needle' ~/.hermes/skills/<skill>/` is ~15 ms and exact.

---

## Coverage Summary (per-project indexes, measured)

There is no longer a single global index. Each project has its own `.codegraph/`; coverage, file counts, nodes, and disk usage change over time. Query live status for the target project instead of relying on a stored count. Bulk initialization may skip documentation- or asset-only directories.

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
