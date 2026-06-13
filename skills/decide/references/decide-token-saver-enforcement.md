# Token-Saver Enforcement in /decide — Session 2026-06-12

## What Changed

**Before**: Mandatory Rule #4 was passive prose — "before ANY read_file() call, run the token-saver workflow... If graph.json or .codegraph/ is missing for the target project, skip — never block."

**After**: Active 4-step probe chain with concrete commands, explicit coverage, and live-tested savings.

## Mandatory Rule #4 (Patched)

```
4. **Token Saver — ACTIVE pre-file-read probe (enforced)** — before ANY
   `read_file()` call on a code project, you MUST execute the probe chain:
   
   **Step A — Detect project**: Identify which project the file belongs to
   under `~/Documents/Projects/`. Extract `$PROJECT` name.
   
   **Step B — Probe CodeGraph MCP first** (always available, covers ALL 945
   files): run `codegraph query "<symbol>"` or `codegraph callers "<symbol>"`
   from `~/Documents/Projects/` to find definitions, callers, and locations
   without reading any files. CodeGraph query output is ~300 tokens vs
   raw read_file of equivalent files at ~15K+ tokens.
   
   **Step C — Probe Graphify if available**: Check if
   `~/Documents/Projects/$PROJECT/graphify-out/graph.json` exists. If yes,
   run `~/.local/bin/graphify.exe query "<question>" --budget 2000 --graph
   graphify-out/graph.json` from the project dir. ~300 tokens vs up to
   370K tokens for raw source reads. Graphify indices now exist for:
   `API-mega-list`, `atm-crypto-bank`, `atm-machine`, `countdown-timer`,
   `ECC`, `ecosystem-test`, `free-ai-tools`, `freebuff-test`,
   `free-llm-api`, `graphify`, `hermes-workflow`, `hw-new`,
   `MoneyPrinterTurbo`, `task-manager-cli` (14/19 projects covered).
   ECC index is 34MB across 5,821 files — Graphify queries work on it.
   
   **Step D — Only then read files**: If BOTH probes returned insufficient
   context, read only the specific file/section needed using
   `read_file(path, offset=<line>, limit=50)` — never full-project reads.
   
   Token savings verified: 35× to 1,233× per query depending on scope.
   This is enforced — skip the probe chain only if the target project is
   NOT under `~/Documents/Projects/` (e.g. system files, temp files).
```

## Execution Order (Patched)

```
session_memory → core-identity-guard → task_tier (gate) →
  reasoning → soul file(s) → 
  **MANDATORY: Token Saver probe chain (Step A→B→C→D)** →
  primary domain skill(s) → complementary check →
  post-execution (Obsidian bundle + KG refresh, tier-conditioned)
```

## Known Integration Pattern (Updated)

| Pattern | Trigger | Route to |
|---------|---------|----------|
| Token-saving pre-file-read | Any code reading / codebase question | **MANDATORY 4-step probe:** Step A → detect `$PROJECT`; Step B → `codegraph query` (~300t, always); Step C → `graphify query` if index (~300t, 14/19 projects); Step D → `read_file` offset/limit. **35×–1,233× live savings — enforced for all code queries.** |

## Why This Matters

The token-saver skill existed but was **never invoked** in any prior session. The enforcement had to live in `/decide` because:
- `/decide` is the routing brain that runs on EVERY prompt
- It controls execution order
- It can gate downstream skills
- Skills alone can't enforce — they can only document

Now the probe chain is a **required pipeline step**, not a suggestion.