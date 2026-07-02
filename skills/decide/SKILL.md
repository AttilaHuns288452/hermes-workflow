---
name: decide
description: Master orchestrator that runs on every prompt, selects and sequences
  the appropriate skills, injects context, and enforces execution order. Always
  runs first. Never skipped.
triggers:
  - always
---

# /decide Skill

> **⚠️ HONESTY NOTE:** Previous versions documented "ACTIVE enforcement" that was never actually followed. This version is restructured so the critical rules are literally the first thing you read. If you find yourself skipping a rule below, stop and check why.

---

## ⚡ Session Startup Protocol (Execute Immediately on Load)

Do these steps in order, right now, before any other action:

```
Step 1 — session_search(): Check for relevant context from past sessions
Step 2 — Determine task_tier: Is this Tier 1, 2, or 3?
Step 3 — Announce compliance: State which rules apply in your first response
Step 4 — Proceed to domain routing below
```

**Mandatory compliance announcement format** in your first response to the user:

```
📋 **Startup Compliance:**
- Tier: [1/2/3]
- Rule 1 (Token Saver): [ACTIVE / SKIP — reason]
- Rule 2 (OpenMontage): [ACTIVE / SKIP — reason]
- Rule 3 (CodeGraph/Graphify): [ACTIVE / SKIP — reason]
```

This serves two purposes:
1. **Forces conscious acknowledgment** — you can't skip what you've just stated
2. **Gives the user a way to verify** — if you claim "Rule 1: ACTIVE" and then call read_file without probing, that's an observable violation

---

## 🔴 ENFORCED RULES — Must Follow, in Order, Every Session

These rules apply to EVERY session. They are not suggestions. If you catch yourself calling `read_file` on a code project without probing CodeGraph first, or writing ad-hoc FFmpeg scripts instead of using OpenMontage, you are violating them.

### Rule 1: Token Saver Probe Chain (Before ANY read_file)

**BEFORE** calling `read_file()` on any file under `~/Documents/Projects/`, you MUST run these probes:

1. **Step A** — Identify `$PROJECT` from the file path. All projects live at `~/Documents/Projects/$PROJECT/`.
2. **Step B** — Probe CodeGraph MCP (always available, ~300 tokens). Use the MCP tools in this order:
   - **Step B1** — `mcp_codegraph_codegraph_explore(query="<symbol_or_term>")` — primary probe. Single call returns definitions, structure, and source of relevant symbols across files. Usually enough on its own.
   - **Step B2** (if B1 insufficient) — `mcp_codegraph_codegraph_search(query="<term>")` for broader name search, or `mcp_codegraph_codegraph_callers/callees/impact` for relation analysis.
   
   Covers ALL projects under `~/Documents/Projects/` (1,607 files, 25,135 nodes, 61,386 edges indexed globally). Returns source code + locations — no terminal command needed. The MCP tools work from any context (no CWD dependency) and are preferred over terminal CLI.

   **Terminal fallback** (use only if MCP tools are unavailable or you need a full list):
   ```bash
   cd ~/Documents/Projects && codegraph query "<symbol_or_term>"
   ```
3. **Step C** — Probe Graphify if index exists (~300 tokens):
   ```bash
   test -f ~/Documents/Projects/$PROJECT/graphify-out/graph.json && \
     cd ~/Documents/Projects/$PROJECT && \
     ~/.local/bin/graphify.exe query "<question>" --budget 2000 --graph graphify-out/graph.json
   ```
   21/24 projects have indices (all except Hermes Skills, hermes-dashboard, unit-converter).
4. **Step D** — Targeted read_file ONLY if A-C were insufficient:
   ```python
   read_file(path, offset=N, limit=50)  # Never full-project reads
   ```

**Consequence:** A full probe chain costs ~1,500 tokens. A raw full-project read can cost 15K–370K tokens. Skipping the probe wastes 50× to 1,233× tokens per query.

**Exception:** System files, temp files, config files under `~/AppData/` or `~/.hermes/` — these are not code projects, skip the probe.

### Rule 2: OpenMontage First for Video

**ANY** video production request (TikTok, Shorts, explainer, cinematic, documentary, talking head, product demo) → route to `media/openmontage-production` FIRST.

- Read `~/OpenMontage/AGENT_GUIDE.md` at session start
- Run preflight (`python -c "from tools.tool_registry import registry; ..."`)
- Follow the pipeline stages via director skills
- Use `video_compose(operation='remotion_render')` for composition — NOT ad-hoc FFmpeg scripts

**Fallback to `media/short-video-production` ONLY if** OpenMontage preflight shows blockers (e.g., Chrome unavailable, pipeline def missing, tool registry empty).

**Why this matters:** OpenMontage has 13 production pipelines, 12 verified API keys, 182/184 passing tests, and proper Remotion-based composition. Last session proved that bypassing it produces a 2.8MB slideshow that looks terrible. This rule exists because the assistant kept writing ad-hoc scripts instead of using the pipeline.

### Rule 3: CodeGraph + Graphify Are Active Tools

- **CodeGraph MCP (preferred):** `mcp_codegraph_codegraph_explore/search/callers/callees/impact` — use MCP tools for any codebase question. Always available, no CWD dependency, returns source code inline.
- **CodeGraph CLI (fallback):** `codegraph query/callers/callees/impact` — use if MCP tools are unavailable.
- **Graphify (v0.8.37):** `~/.local/bin/graphify.exe query` — use for structural BFS traversal
- `read_file` is **LAST RESORT** for code files under `~/Documents/Projects/`

### Rule 4: task_tier Gate

Run `task_tier` immediately after session_memory + core-identity-guard. The structured output governs:

| TIER | Token Saver | Obsidian Bundle | KG Refresh |
|------|------------|-----------------|------------|
| 1 (atomic) | SKIP | SKIP | SKIP |
| 2 (task) | **RUN** | SKIP | SKIP (unless structural change) |
| 3 (project) | **RUN** | **RUN** (all 3 Obsidian skills) | **RUN** |

> **Obsidian Bundle** = create/update note + codebase graph + KG viz
> **KG Refresh** = regenerate `obsidian-knowledge-graph`

---

## 🟡 Aspirational Guidelines (Use Judgment)

### G1: Obsidian Bundle for Tier 3 (trigger-based)

After completing a Tier 3 task — or any time the user says "update the obsidian notes" or "create the obsidian notes after creating a project" — run the full Obsidian bundle:
1. `obsidian-codebase-graph --clean` on the affected project
2. Create/update the project's main Obsidian note (ATM-Machine template: Overview, Features, Structure, Architecture, Code Patterns, Mermaid graph, wikilinks, tags)
3. Run `obsidian-knowledge-graph` to refresh vault-wide interconnectivity viz
4. Refresh the KG render in any dashboard

> **Note:** This is **on-demand only** — don't run automatically after every code change. The triggers are: user asks for note update, user creates a new project, or Tier 3 task completion.
### G2: Self-Audit (Run Before Finishing Each Session)

Before delivering your final response, verify your startup compliance matches reality:

```diff
📋 Startup Compliance (what I announced):
- Rule 1 (Token Saver): [ACTIVE / SKIP]
- Rule 2 (OpenMontage): [ACTIVE / SKIP]

[X] Did I actually probe CodeGraph before every read_file?
    → If I said ACTIVE but didn't probe, this is a violation. Fix it.
[X] Did I route video to OpenMontage (not ad-hoc scripts)?
    → If I said ACTIVE but wrote FFmpeg, this is a violation. Fix it.
[X] Is the task_tier classification still accurate?
[X] Did I use the right tool for the task?
[X] If code-related: did I use CodeGraph + Graphify before read_file?
```

**Consequence of violation:** If any box is unchecked, the startup compliance announcement was misleading. Do NOT deliver results until all boxes are checked. If you cannot fix the violation (e.g., you already read files without probing), disclose it to the user and correct in the next action.

### G3: session_memory Always First
Every session: call session_search() to check for relevant context before routing anything. Never skip.

### G4: On-Demand Over Automatic for Token-Heavy Operations

Any automated post-task workflow that consumes significant tokens should default to **on-demand** (triggered by explicit user request) rather than automatic enforcement after every change. This includes:

- Obsidian code graph regeneration
- Full project analysis passes
- Bulk format exports (e.g., markdown-exporter batch runs)
- Cross-referencing / graph rebuilds
- Dashboard or knowledge graph refreshes

The user explicitly prioritizes **token efficiency** over having everything auto-synced. Only run these automatically if:
- The user explicitly opted in (said "keep doing this automatically")
- OR the task is Tier 3 and the user confirmed they want the full bundle during this session
- OR you asked and they said yes

**Rationale from the user:** "so you know i would not waste tokens when i dont need it"

---

## Execution Order (Summary)

```
1. session_search()              → context retrieval
2. core-identity-guard            → safety
3. task_tier                      → classification gate
4. ENFORCED RULES check           → which rules apply?
   - Rule 1 (Token Saver) if Tier 2/3 and code reading
   - Rule 2 (OpenMontage) if video
   - Rule 3 (CodeGraph/Graphify) if code query
5. Domain skill selection         → routing (see below)
6. Execute                        → with tooling from chosen skill
7. Post-execution                 → Obsidian Bundle if Tier 3 OR user requested note update
8. Self-audit (G2)                → verify rules were followed
```

---

## Selection Rules

### Soul Files (Personality + Constraints)
- Coding / implementation / Next.js / Supabase / TypeScript → `soul`
- Finance / investing / portfolio / cash flow / macro / CFA → `soul_finance`
- Fintech tasks (code + finance) → activate **both** soul and soul_finance

### Domain Skills
| Trigger | Route To |
|---------|----------|
| Video production / TikTok / Shorts / animated explainer | `media/openmontage-production` **first** |
| Writing finance scripts / "What's the Difference" / Mr. Finance Guy / TikTok finance / reel / short / compare X and Y for video | `mr-finance-guy` |
| Setup / install / configure / bootstrap | `software-development/setup` |
| Setup + skill audit / repo reconciliation | `software-development/repo-integration-reconciliation` |
| API search / data source / scraper / MCP server | `productivity/api-mega-list` |
| Ecosystem dashboard / stats / project graph | `productivity/hermes-dashboard` |
| Update / ecosystem integrate / onboard | `software-development/update` |
| Graphify / Obsidian code-graph export | `software-development/graphify-integrate` |
| Update / create Obsidian notes / sync code to vault / "update the obsidian notes" / "create the obsidian notes after creating a project" / codebase-to-Obsidian mapping / project initialization graph / generate codebase notes / visualize architecture in Obsidian | `note-taking/obsidian-codebase-graph` (use `--clean` flag for regenerating) |
| Coding / implementation | `software-development` or domain-specific |
| Design / UI / visual | `creative` |
| ECC agent invocation | `ecc-bridge` |
| Research / papers / monitoring | `research` |
| Email | `email`, `gmail` |
| GitHub / PR / repo | `github` |
| Productivity / docs / PDFs | `productivity` |
| Export markdown to DOCX/PPTX/XLSX/PDF/HTML/CSV/JSON/XML/LaTeX/IPYNB / convert table to spreadsheet / extract code blocks from markdown / generate formatted report / markdown exporter | `productivity/markdown-exporter` |
| Data / notebooks / analytics | `data-science` |
| Media / audio / video | `media` |
| Smart home | `smart-home` |
| MLOps / models | `mlops` |
| Notes / Obsidian / wikilinks / callouts / embeds / properties / vault operations / .base files / Bases / JSON Canvas / .canvas files / Obsidian CLI / plugin dev / theme dev / knowledge graph / KG viz | `note-taking` (bundle all three: `obsidian` for core syntax + operations, `obsidian-codebase-graph` for code graph mapping, `obsidian-knowledge-graph` for vault graph viz) |
| Backup / restore / credential sync / Google Drive backup / rclone / migrate Hermes | `workflow/hermes-backup-workflow` |
| Workflow / model selection | `workflow` |
| SEO / site audit / schema / rankings | `seo` |
| Marketing / sales / content / growth | `productivity/ai-marketing-skills` |
| App building / prototype | `software-development/buildable-plugin` |
| Start new feature / implement spec / design-first workflow / structured dev pipeline / Superpowers methodology / obra superpowers | `software-development/superpowers-methodology` |

### Cross-Cutting Behavioral Guidelines (Load alongside any code task)
| Trigger | Load With |
|---------|-----------|
| Writing / reviewing / refactoring code — remind me to think before coding, keep it simple, make surgical changes, define success criteria / behavioral guardrails / Karpathy principles / avoid overcomplication | `software-development/karpathy-guidelines` |

### Quant & Finance Skills (LLMQuant Domain)
| Trigger | Route To |
|---------|----------|
| Commodities | `llmquant-commodities` |
| Credit | `llmquant-credit` |
| Crypto | `llmquant-crypto` |
| Data query (fetch financial data) | `llmquant-data` (gateway router) |
| Equities | `llmquant-equities` |
| Equity Derivatives | `llmquant-equity-derivatives` |
| ETFs | `llmquant-etfs` |
| Events | `llmquant-events` |
| Investor Lenses | `llmquant-investor-lenses` |
| Macro | `llmquant-macro` |
| Market Intelligence | `llmquant-market-intelligence` |
| Options | `llmquant-options` |
| Portfolio | `llmquant-portfolio` |
| Portfolio Lab | `llmquant-portfolio-lab` |
| Prediction Markets | `llmquant-prediction-markets` |
| Rates & FX | `llmquant-rates-fx` |
| Risk | `llmquant-risk` |
| Strategies | `llmquant-strategies` |

For general finance/investing → activate `soul_finance` + relevant LLMQuant skill.
For fintech-code → `soul` + `soul_finance` + relevant LLMQuant skill.

---

## Reasoning Protocol (Background — Use When Routing Confidence Is Low)

### Step 1 — Decompose the prompt
Break the request into actual components. Name them explicitly before routing.

### Step 2 — Challenge the obvious interpretation
Ask: is the surface reading what's actually being asked? Check for implicit context, user shorthand, prior patterns.

### Step 3 — Score routing confidence
- **High** — intent is unambiguous, skill maps cleanly
- **Medium** — plausible match but alternatives exist
- **Low** — best guess; flag assumption in output. If entire routing is Low, ask clarifying question.

### Step 4 — Second-order thinking
Pre-load skills that step 2 of the workflow will need. Example: new feature → pre-load code review + Obsidian update.

### Step 5 — Self-challenge
Could one skill handle this instead of three? Minimum viable skill set.

---

## Complementary Setup Routing

When the user asks for setup/install/configure of a new repo or tool, proactively check for complementary integrations:

| New Repo | Also Route To |
|----------|---------------|
| Any new project | `graphify-integrate` + Obsidian bundle (build graph via `obsidian-codebase-graph --clean`, create note, cross-link) — only when user requests it |
| Agent framework (ECC, devfleet, etc.) | `external-agent-ecosystem-adapter` |
| Model/provider resource | `free-ai-tools` (model catalog) + `model-recommender-workflow` |
| Freebuff / Codebuff | `free-ai-model-router` (combined model selection) |
| FreeLLMAPI | `free-ai-model-router` (alternative model source) |
| API-mega-list | `productivity/api-mega-list` + check MCP Server candidates |
| Buildable Plugin | `software-development/buildable-plugin` + design/plan/review skills |
| AI Marketing Skills | `productivity/ai-marketing-skills` |

---

## Conflict Resolution

- Two domain skills overlap → activate both; primary soul governs
- No skill matches → fall back to closest soul file, flag the gap in output
- Ambiguous intent → assume, state in one line, proceed (unless entire routing is Low confidence)

## Output Format

State once at the start of each session, then execute immediately:

```
**Intent:** [what was detected]
**Skills activated:** [list in execution order]
**Tier:** [from task_tier]
```

Then proceed. No lengthy reasoning blocks printed — output is the work.

## Self-Correction

If routing produces a wrong result:
1. Record what went wrong
2. Record what should have been selected
3. Patch /decide with the correction
4. Notify the user

Update /decide when: new repo integrated, new routing pattern discovered, complementary relationship found, conflict resolved.

---

## Quick Reference: Token Saver Commands

Use MCP tools FIRST (always available, no CWD dependency):
```
mcp_codegraph_codegraph_explore(query="<term>")     # Primary — one call, returns source + locations
mcp_codegraph_codegraph_search(query="<term>")      # Broader name search
mcp_codegraph_codegraph_callers(symbol="<fn>")      # Who calls this function
mcp_codegraph_codegraph_callees(symbol="<fn>")      # What this function calls
mcp_codegraph_codegraph_impact(symbol="<fn>")       # Refactoring impact analysis
mcp_codegraph_codegraph_files(pattern="*.tsx")      # File tree with metadata
mcp_codegraph_codegraph_status()                    # Index health check
```

Terminal fallback (if MCP tools are unavailable):
```bash
# Step B — CodeGraph (always works)
cd ~/Documents/Projects && codegraph query "<term>"
cd ~/Documents/Projects && codegraph callers "<function>"
cd ~/Documents/Projects && codegraph callees "<function>"
cd ~/Documents/Projects && codegraph impact "<function>"

# Step C — Graphify (if index exists)
test -f ~/Documents/Projects/$PROJECT/graphify-out/graph.json && \
  cd ~/Documents/Projects/$PROJECT && \
  ~/.local/bin/graphify.exe query "<question>" --budget 2000 --graph graphify-out/graph.json
```
