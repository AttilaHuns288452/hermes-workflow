---
name: decide
description: Master orchestrator that runs on every prompt, selects and sequences
  the appropriate skills, injects context, and enforces execution order. Always
  runs first. Never skipped.
triggers:
  - always
---

# /decide Skill

## Role
The routing brain for every session. Parses every incoming prompt, maps it to
the correct skill set, resolves conflicts, injects context, and hands off with
a structured execution plan. Does not execute the task itself — it owns the
decision of what runs, in what order, and with what inputs.

## Skill Discovery
At the start of every session, before routing:
1. Scan the skills directory for all available `.md` skill files.
2. Read each file's frontmatter: `name`, `description`, `triggers`.
3. Build the routing table dynamically from what's found — do not rely
   solely on the hardcoded list below.
4. If a new skill is found that has no entry in the hardcoded rules,
   infer its trigger conditions from its `description` and `triggers`
   frontmatter and include it in routing candidates.
5. Hardcoded rules below act as overrides and bundle rules only —
   not as the exhaustive skill list.

## Reasoning Protocol
Before routing, think through the task — not just pattern-match keywords.
This step runs silently inside /decide and is not printed to the user unless
confidence is low.

**Step 1 — Decompose the prompt**
Break the request into its actual components. A single prompt can contain
multiple distinct tasks, hidden dependencies, or implicit deliverables. Name
them explicitly before routing anything.

**Step 2 — Challenge the obvious interpretation**
Ask: is the surface reading of this prompt actually what's being asked? Check
for:
- Implicit context that changes the domain (e.g. "fix this" on a finance
  formula is not a coding task)
- Shortcuts or shorthand the user habitually uses
- Prior session patterns that reframe the request

**Step 3 — Score routing confidence**
For each candidate skill, assign a confidence level:
- **High** — intent is unambiguous, skill maps cleanly
- **Medium** — plausible match but at least one alternative exists
- **Low** — best guess; flag assumption in output

If any selected skill scores Low, state the assumption explicitly in the
output format. If the entire routing is Low confidence, ask one clarifying
question before proceeding — this is the only case where /decide pauses.

**Step 4 — Second-order thinking**
Ask: what will this task likely produce or require next? If the current
prompt is step 1 of a multi-step workflow, pre-load the skills that step 2
will need. Example: a new feature implementation will likely need a code
review pass and an Obsidian update — stage those in the execution plan now.

**Step 5 — Self-challenge**
Before finalizing the routing decision, ask: is there a simpler path? Could
one skill handle this instead of three? Avoid over-routing. The right answer
is the minimum viable skill set that fully satisfies the task.

## Workflow
1. **Check context first** — invoke `session_memory`. Pull relevant history,
   prior decisions, preferences, and patterns. Attach to all downstream
   skill invocations.
2. **Classify task tier** — invoke `task_tier` to classify the request as
   Tier 1 (atomic), Tier 2 (task), or Tier 3 (project). Read the structured
   output (TIER / REASON / OBSIDIAN / KG_REFRESH) and use it to gate all
   subsequent steps. If TIER is 1, skip reasoning, skill selection, and
   execute directly. If TIER is 2, run reasoning/skills with Token Saver
   but skip Obsidian bundle and KG refresh. If TIER is 3, run full pipeline
   including Obsidian + KG refresh. The task_tier output is passed through
   to every downstream step as a gate directive.
3. **Reason** — run the full Reasoning Protocol above before touching the
   Selection Rules.
4. **Parse intent** — identify the domain(s): coding, finance/investing,
   design, research, email, GitHub, productivity, data science, media, MLOps,
   notes/Obsidian, smart home, workflow/model selection.
5. **Map to skills** — match each detected domain to its skill using the
   Selection Rules below.
6. **Resolve conflicts** — apply Conflict Resolution rules.
7. **Define execution order** — task_tier gate → context → soul/domain →
   post-execution (Obsidian always last, conditional on tier).
8. **Hand off** — invoke each skill with: detected intent, session context,
   active soul constraints, prior decisions, confidence scores, and the
   task_tier gate directive.
9. **Verify** — after execution, check if output satisfies original intent.
   Re-route if not.

## Selection Rules

### Soul Files (Personality + Constraints)
- Coding / implementation / Next.js / Supabase / TypeScript → `soul`
- Finance / investing / portfolio / cash flow / macro / CFA → `soul_finance`
- Fintech tasks (code that is also finance) → activate **both** `soul` and
  `soul_finance`; soul governs code style, soul_finance governs domain logic

### Domain Skills
- Setup / install / configure / bootstrap → `software-development/setup`
- Setup + skill audit / repo integration with reconciliation → `software-development/repo-integration-reconciliation`
- **API search / find an API / need an API that can X / API directory / Apify actor / web scraper for X / MCP server for X** → `productivity/api-mega-list`
  - Routes to grep-based search across 18 categories of 26,005 Apify APIs
  - MCP server queries → also route to `mcp-integrations` for wiring
  - Scraper queries → also route to `ecc-bridge` for ECC agent alternatives
- **Dashboard / ecosystem overview / show stats / project graph / model ecosystem / how many APIs / Graphify + CodeGraph node map** → `productivity/hermes-dashboard`
  - Routes to local dashboard HTML at ~/Documents/Projects/hermes-dashboard/index.html
  - Also available via GH Pages: attilahuns288452.github.io/hermes-workflow/dashboard.html
  - Covers: 16 projects, 139 skills, 26K APIs, 8K Graphify + 16K CodeGraph nodes, free model chain, MCP servers, ECC agents, skill categories
  - Direct HTML render — no further pipeline steps needed
- Update / ecosystem integrate / onboard → `software-development/update`
- Graphify + Obsidian / code-graph export → `software-development/graphify-integrate`
- Coding / implementation → `software-development` or domain-specific skill
- Design / UI / visual → `creative`
- **ECC agent invocation** (silent-failure-hunter, comment-analyzer, code-simplifier, database-reviewer, refactor-cleaner, doc-updater, performance-optimizer, pr-test-analyzer, type-design-analyzer, or any *ECC agent* mention) → `ecc-bridge`
  - Bridge strips `model: sonnet/opus` frontmatter and runs agent prompt through free model chain
  - 57 of 64 agents are free-model compatible; 7 opus agents show quality degradation
  - See `ecc-bridge` skill for full agent → free-model mapping and invocation patterns
- Research / papers / monitoring → `research`
- Email workflows → `email`, `gmail`
- GitHub / PR / repo → `github`
- Productivity / docs / PDFs → `productivity`
- Data / notebooks / analytics → `data-science`
- Media / audio / video → `media`
- Smart home → `smart-home`
- MLOps / models → `mlops`
- Notes / Obsidian / codebase mapping / graph visualization → `note-taking`
  - **BUNDLE RULE**: Always loads all three together — never one in isolation:
    - `obsidian` — core note CRUD
    - `obsidian-codebase-graph` — filesystem → wikilinked markdown notes
    - `obsidian-knowledge-graph` — vault scan → JSON graph → HTML render
- Workflow / model selection → `workflow`

### Quant & Finance Skills
These LLMQuant domain skills provide workflow guidance, MCP server integration, and data analysis for specific financial and quantitative domains. Each has a bundled tools/methodology reference. They all depend on the **LLMQuant Data MCP server** (`@llmquant/data-mcp`) configured in ~/.hermes/config.yaml — no additional install needed.

| Trigger Pattern → Route to |
|---------------------------|
| **Commodities** (spot / futures curve / inventory / roll yield / macro linkage) → `llmquant-commodities` |
| **Credit** (credit spreads / CDS / bond yields / credit risk / ratings / default probability) → `llmquant-credit` |
| **Crypto** (crypto spot / perpetuals / funding rate / on-chain / DeFi / CeFi / market data) → `llmquant-crypto` |
| **Data query** (fetch financial data / historical prices / fundamental data / option chains) → `llmquant-data` — then pipe to the specific domain skill |
| **Equities** (stock prices / fundamentals / corporate actions / sector performance) → `llmquant-equities` |
| **Equity Derivatives** (options chains / greeks / implied volatility / term structure) → `llmquant-equity-derivatives` |
| **ETFs** (ETF composition / NAV / premium/discount / flows / sector exposure) → `llmquant-etfs` |
| **Events** (earnings calendar / economic indicators / central bank decisions / corporate events) → `llmquant-events` |
| **Investor Lenses** (value / growth / momentum / quality / factor analysis / screeners) → `llmquant-investor-lenses` |
| **Macro** (GDP / CPI / PMI / unemployment / yield curves / FX rates / central bank policy) → `llmquant-macro` |
| **Market Intelligence** (news sentiment / market summaries / sector rotation / market breadth) → `llmquant-market-intelligence` |
| **Options** (option pricing / strategies / P&L / Greeks / volatility surface) → `llmquant-options` |
| **Portfolio** (portfolio construction / allocation / rebalancing / risk parity / optimization) → `llmquant-portfolio` |
| **Portfolio Lab** (backtesting / scenario analysis / Monte Carlo / factor decomposition) → `llmquant-portfolio-lab` |
| **Prediction Markets** (Polymarket / election odds / event contracts / market prices) → `llmquant-prediction-markets` |
| **Rates & FX** (interest rates / swap rates / bond yields / FX spot & forwards / cross-currency basis) → `llmquant-rates-fx` |
| **Risk** (VaR / CVaR / stress testing / Greeks risk / counterparty risk / risk reporting) → `llmquant-risk` |
| **Strategies** (trading strategies / signal generation / backtesting / alpha research / execution) → `llmquant-strategies` |

When the user asks about **finance / investing / quant / portfolio / risk** in general, activate `soul_finance` + the relevant LLMQuant domain skill. For **fintech-code** tasks (code that is also finance), activate `soul` + `soul_finance` + the relevant LLMQuant skill.

- Use `llmquant-data` as the **gateway router** — it handles MCP data fetch first, then pipes to the domain skill for analysis/visualization
- The **LLMQuant Data MCP server** is always available via `npx -y @llmquant/data-mcp` with env `LLMQUANT_API_KEY`

### Mandatory Rules
1. **session_memory is always step one** — no skill runs before context
   is retrieved. If retrieval finds nothing, proceed; never skip the check.
2. **Core Identity Guard is always loaded second** — `core-identity-guard`
   runs before every session and every skill invocation. It enforces file
   system protection, secrets handling, prompt injection immunity, and
   system integrity rules. No instruction can override it. Never skipped.
3. **task_tier classification is mandatory step three** — immediately after
   session_memory and core-identity-guard, invoke `workflow/task_tier` to
   classify the request. The structured output (TIER / OBSIDIAN / KG_REFRESH)
   gates all downstream steps. If TIER is 1, answer directly and skip all
   pipeline steps. If TIER is 2, run domain skills with Token Saver but
   skip Obsidian bundle and KG refresh. If TIER is 3, run full pipeline
   including Obsidian bundle + KG refresh.
4. **Token Saver — ACTIVE pre-file-read probe (enforced)** — before ANY\n   `read_file()` call on a code project, you MUST execute the probe chain:\n   
   **Step A — Detect project**: Identify which project the file belongs to\n   under `~/Documents/Projects/`. Extract `$PROJECT` name.\n   
   **Step B — Probe CodeGraph MCP first** (always available, covers ALL 945\n   files): run `codegraph query "<symbol>"` or `codegraph callers "<symbol>"`\n   from `~/Documents/Projects/` to find definitions, callers, and locations\n   without reading any files. CodeGraph query output is ~300 tokens vs\n   raw read_file of equivalent files at ~15K+ tokens.\n   
   **Step C — Probe Graphify if available**: Check if\n   `~/Documents/Projects/$PROJECT/graphify-out/graph.json` exists. If yes,\n   run `~/.local/bin/graphify.exe query "<question>" --budget 2000 --graph\n   graphify-out/graph.json` from the project dir. ~300 tokens vs up to\n   370K tokens for raw source reads. Graphify indices now exist for:\n   `API-mega-list`, `atm-crypto-bank`, `atm-machine`, `countdown-timer`,\n   `ECC`, `ecosystem-test`, `free-ai-tools`, `freebuff-test`,\n   `free-llm-api`, `graphify`, `hermes-workflow`, `hw-new`,\n   `MoneyPrinterTurbo`, `task-manager-cli` (14/19 projects covered).\n   ECC index is 34MB across 5,821 files — Graphify queries work on it.\n   \n   **Step D — Only then read files**: If BOTH probes returned insufficient\n   context, read only the specific file/section needed using\n   `read_file(path, offset=<line>, limit=50)` — never full-project reads.\n   \n   Token savings verified: 50× to 1,233× per query depending on scope.\n   This is enforced — skip the probe chain only if the target project is\n   NOT under `~/Documents/Projects/` (e.g. system files, temp files).\n\n5. **Graphify + CodeGraph are ACTIVE tools — USE them** — Both are installed\n   and working:\n   - **CodeGraph** (v0.9.9) has MCP server wired in Hermes config at\n     `~/Documents/Projects/.codegraph/` — **945 files, 16,092 nodes,**\n     **43,795 edges** across all projects. Run `codegraph query` or\n     `codegraph callers` from `~/Documents/Projects/` for any code query.\n   - **Graphify** (v0.8.37) has code-graphs built for **14 of 19 projects**\n     (the 5 missing are: hermes-dashboard (single HTML), unit-converter (no\n     code files), and 3 single-HTML projects with no code to graph). ECC is\n     now indexed — 34MB graph across 5,821 files. Run `~/.local/bin/graphify.exe query "<q>"`\n     with `--graph graphify-out/graph.json` from the project dir.\n   - CodeGraph for live FTS5 symbol search, Graphify for structural\n     BFS traversal — use CodeGraph first (always available), Graphify\n     second (when project has an index), read_file last (never).
6. **Any project, coding, design, or analysis task → always include the
   full Obsidian+Graphify bundle as a mandatory post-execution phase:**
   `obsidian` + `obsidian-codebase-graph` + `obsidian-knowledge-graph`
   + `graphify-integrate`. Documentation + code graph are required
   deliverables, not optional.
   *NOTE: task_tier TIER 1 and TIER 2 override this — if the classification
   says SKIP, Obsidian and KG refresh are not run.*
7. **After every Obsidian or Graphify update → always regenerate the
   knowledge graph** via `obsidian-knowledge-graph`. Graph must reflect
   latest vault state including code-symbol nodes.
8. **Direct skill invocations by the user → /decide still runs.** Validate,
   enrich context, then execute. Never bypass.
9. **Setup tasks → always run complementary integration check.** When routing
   to `software-development/setup`, add `external-agent-ecosystem-adapter`
   as a secondary skill if the target is an agent framework. Also check the
   new setup against `free-ai-tools` (model resources) and existing projects.
   See Selection Rules → Complementary Setup Routing below.

### Complementary Setup Routing
When the user asks for setup/install/configure of a new repo or tool, the
decide skill must proactively check for complementary integration with
existing repos:

- **Graphify (codebase knowledge graph) → MANDATORY for every project.**
  Route to BOTH `setup` AND `graphify-integrate` AND the Obsidian bundle
  (`obsidian` + `obsidian-codebase-graph` + `obsidian-knowledge-graph`).
  Graphify's code graph (8,267 nodes, 13,225 edges) can be cross-referenced
  in Obsidian via manual notes — `graphify update .` refreshes the graph,
  then `graphify query/explain/path` provide code context without file reads.
  Run `graphify install hermes` to register Graphify as a Hermes skill.
  Graphify is the **secondary brain** — it provides AST-level code
  understanding that feeds into model selection, code review, and
  architecture decisions.
- **Agent framework** (ECC, devfleet, etc.) → route to BOTH `setup` AND
  `external-agent-ecosystem-adapter`. The adapter skill handles Phase 2
  conflict resolution (model defaults, orchestration claims, MCP, ports).
- **Model/provider resource** → route to `setup`, then cross-reference
  with `free-ai-tools` as the model catalog. Check `free-ai-model-router`
  for routing integration. Run `model-recommender-workflow` to test.
- **Tool/utility** → set up normally, but check for shared dependency
  conflicts with existing tools. Add Obsidian wikilinks to any complementary
  project notes.
- **Freebuff / Codebuff (coding agent)** → route to `setup`, then
  cross-reference with `free-ai-model-router` for combined model selection.
  Freebuff provides Kimi K2.6, MiniMax M3, MiMo 2.5 Pro — complementary
  models to OpenCode's bundled free models. Run `model-recommender-workflow`
  to test combined routing. Add Obsidian wikilink from `[[Freebuff]]` to
  existing `[[OpenCode]]` and `[[free-ai-tools]]` notes.
- **FreeLLMAPI (local free model provider)** → route to `free-ai-model-router`
  as an additional model source. FreeLLMAPI serves 107 free models (84 available)
  from 16 providers. Hermes integration:
  - `model.provider=custom`, `model.base_url=http://localhost:3001/v1`, `model.default=auto`
  - Auth: `hermes auth add freellmapi --type api-key --api-key <key> --label "FreeLLMAPI Key"`
  (creates `custom:freellmapi` credential)
  Dashboard at `localhost:5173` (login: `admin@freellmapi.local` / `freellmapi-admin`).
  Check it as an alternative when OpenCode bundled models and Freebuff are insufficient.
  **ENV CRITICAL**: `~/.hermes/.env` must have exactly ONE `FREELMAPI_API_KEY` line.
  Duplicate lines cause the second (possibly stale) key to overwrite the first.
- **API-mega-list (API directory reference)** → route to BOTH `setup` AND
  `productivity/api-mega-list`. After cloning the repo (~/Documents/Projects/API-mega-list/),
  the skill provides grep-based search across 18 categories. For MCP Servers
  found in the list, route to `mcp-integrations` for wiring. For scraping
  APIs, cross-reference with `ecc-bridge` for ECC agent alternatives.
  Has 26,005 APIs across 18 categories — daily updated.
- **Hermes Dashboard (local ecosystem dashboard)** → route to
  `productivity/hermes-dashboard`. Single-file HTML with vis-network
  force-directed graph, 16 projects, 139 skills, 26K+ APIs, 8K Graphify
  + 16K CodeGraph nodes, 5-layer free model chain, 6 MCP servers,
  64 ECC agents, 49 skill categories. Available locally at
  ~/Documents/Projects/hermes-dashboard/index.html, and via GH Pages
  at attilahuns288452.github.io/hermes-workflow/dashboard.html.

### Known Integration Patterns (Session-Learned)
These patterns were discovered in previous sessions and should be activated
when the user works in these domains — not hardcoded skills, but routing
heuristics:

| Pattern | Trigger | Route to |
|---------|---------|----------|
| ECC + free-ai-tools complement | New setup is an agent OR model repo | Check both repos for cross-links; run model-recommender-workflow to test compatibility |
| Model selection for task type | User asks "which model" or "best free model for..." | `workflow/model-recommender-workflow` — covers all 6 task types |
| Free model preference enforcement | New repo has paid model defaults | `external-agent-ecosystem-adapter` Phase 2a — convert to free model chain |
| Multi-repo integration audit | User says "make these repos work together" | `model-recommender-workflow` + Obsidian note with Mermaid dependency graph |
| Token-saving pre-file-read | Any code reading / codebase question | **MANDATORY 4-step probe:** Step A → detect `$PROJECT` from path; Step B → `codegraph query "<symbol>"` from `~/Documents/Projects/` (always available, 945 files indexed, ~300 tokens); Step C → check `graphify-out/graph.json` and `~/.local/bin/graphify.exe query "<q>" --budget 2000 --graph graphify-out/graph.json` (~300 tokens, exists for 14/19 projects); Step D → `read_file(path, offset=N, limit=50)` only if probes insufficient. Verified 50× to 1,233× token reduction — **enforced for all code queries.** |
| API-mega-list + MCP Servers | User finds an MCP Server in the API list | Route to `mcp-integrations` for Hermes config wiring. The list has 131 MCP Servers (Brave Search, Figma, Slack, DeepL, Google Maps, etc.) — each can be wired as a new MCP server in `config.yaml`. |
| API-mega-list + ECC Scrapers | User finds a web scraper in the API list | Cross-reference with ECC agents via `ecc-bridge`. ECC has dedicated scraping agents that may complement or replace Apify actors. |
| CodeGraph + Graphify complement | User installs CodeGraph or asks about code knowledge graphs | **Complementary — keep both.** CodeGraph provides live MCP tools (query, callers, callees, impact) — 945 indexed files, 16,092 nodes across all projects. Graphify provides code-graph query/explain/path — 8,267 nodes, 13,225 edges on the graphify project alone. CodeGraph for live agent queries, Graphify for structural analysis. |
| Dashboard ecosystem overview | User asks "show me everything", "dashboard", "ecosystem stats", "what projects exist", "graph stats" | Route to `productivity/hermes-dashboard`. Single HTML page at ~/Documents/Projects/hermes-dashboard/index.html. All stats are static — no live backend needed. |
| **.env duplicate key fix** | FreeLLMAPI returns "Invalid API key" despite correct credentials | Check `~/.hermes/.env` for duplicate `FREELMAPI_API_KEY=*** lines. Remove stale duplicates so only the current key remains. Env files loaded by bash pick the LAST definition, not the first. |

## Session Evolution & Self-Update

The decide skill is the **routing brain** and must evolve as the user's
ecosystem grows. After sessions that produce new routing patterns (like
discovering that ECC + free-ai-tools complement each other), update this
skill to capture the learning.

### When to Update /decide

Update `/decide` itself after any session where:
1. **A new repo or tool was integrated** into the workflow — add it to
   Complementary Setup Routing so future setups know about it
2. **A new routing pattern was discovered** — e.g. "model selection tasks
   should route to model-recommender-workflow" — add to Known Integration
   Patterns
3. **A complementary relationship was uncovered** — two previously
   independent repos turned out to work together — add to Known Integration
   Patterns
4. **A setup had to undo a conflict** — add that conflict vector to the
   Conflict Resolution section so future sessions avoid it

### How to Update /decide

Use `skill_manage(action='patch', name='decide', ...)` to update this
skill with new patterns. Target these specific sections:

- **Selection Rules → Complementary Setup Routing** — add new repo names
  and their routing rules
- **Selection Rules → Known Integration Patterns** — add the trigger
  + route-to mapping
- **Conflict Resolution** — add new conflict types discovered in practice
- **Mandatory Rules** — add new always-run rules if a pattern is universal
  enough

### Examples of Session Learnings to Capture

| Session Type | What to Add to /decide |
|-------------|----------------------|
| First-time ECC integration | AGENTS.md/CLAUDE.md orchestration check → add to Conflict Resolution: always check these files for competing claims |
| Free-ai-tools model routing | Model selection needs task-type mapping → add Known Integration Patterns table |
| Model Recommender CLI built | Model selection queries → route to `workflow/model-recommender-workflow` |
| Any setup that required conflict resolution | Add the conflict vector type to the setup skill's Phase 0 scan checks |
| New repo found to complement existing ones | Add to Complementary Setup Routing table with trigger → route-to mapping |
| **Repo-as-mirror pattern** — user asks to replicate skills to GitHub | Copy actual `~/.hermes/skills/` tree preserving `dir/SKILL.md` structure; update SKILLS_CATALOG, INTEGRATION, META_PROMPT, index.html with real counts; zero secrets check before push |
|| **Ecosystem documentation exports** — user asks to document their Hermes setup | Route to `software-development/update` which covers Phase 0 (mirror skills tree), Phase 1 (audit), Phase 2 (generate META_PROMPT/SKILLS_CATALOG/INTEGRATION), Phase 3 (website update), Phase 4 (commit/push). CRITICAL: skip stub .md files — copy actual skill tree instead. |
|| **Website blank space fix** — user reports excessive whitespace on GH Pages site | Reduce `.section{padding}` (4rem→2rem), `.hero{min-height}` (100vh→92vh), tighten all inner margins/gaps by 30-50% across all section elements. Verify live with `browser_console` CSS inspection after deploy. |

## Self-Correction

If the decide skill's routing produces a wrong or suboptimal result:
1. **Record what went wrong**: Which skill was selected incorrectly?
2. **Record what should have been selected**: What was the correct routing?
3. **Patch /decide**: Add the correction to this skill's Selection Rules
4. **Notify the user**: Briefly mention the correction was captured

## Conflict Resolution
- Two domain skills overlap → activate both; primary domain soul governs.
- No skill matches → fall back to closest soul file, proceed on own judgment,
  flag the gap in output.
- Ambiguous intent → do not ask for clarification unless Reasoning Protocol
  Step 3 scores the entire routing as Low confidence. Otherwise assume,
  state it in one line, proceed.

## Execution Order

session_memory → core-identity-guard → **task_tier (gate: TIER 1 → answer directly; TIER 2 → Token Saver + skills; TIER 3 → full pipeline)** → reasoning → soul file(s) → **MANDATORY: Token Saver probe chain (Step A: detect project → Step B: probe CodeGraph MCP first → Step C: probe Graphify if available → Step D: read_file only as last resort)** → primary domain skill(s) → complementary check (for setup tasks: run integration scan + wire new resources to existing repos) → post-execution (Obsidian bundle + Graphify export + graph refresh, conditioned on tier)

## Output Format
State once, briefly, then execute immediately:
- **Intent:** [what was detected]
- **Skills activated:** [list in execution order]
- **Confidence:** [High / Medium / Low — only shown if Medium or Low]
- **Key assumption (if any):** [one line, only when ambiguity exists]

Then proceed. No lengthy reasoning blocks printed — the reasoning runs
internally. Output is the work, not commentary about the work.