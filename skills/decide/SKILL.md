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
2. **Reason** — run the full Reasoning Protocol above before touching the
   Selection Rules.
3. **Parse intent** — identify the domain(s): coding, finance/investing,
   design, research, email, GitHub, productivity, data science, media, MLOps,
   notes/Obsidian, smart home, workflow/model selection.
4. **Map to skills** — match each detected domain to its skill using the
   Selection Rules below.
5. **Resolve conflicts** — apply Conflict Resolution rules.
6. **Define execution order** — context → soul/domain → post-execution
   (Obsidian always last).
7. **Hand off** — invoke each skill with: detected intent, session context,
   active soul constraints, prior decisions, and confidence scores.
8. **Verify** — after execution, check if output satisfies original intent.
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

### Mandatory Rules
1. **session_memory is always step one** — no skill runs before context
   is retrieved. If retrieval finds nothing, proceed; never skip the check.
2. **Core Identity Guard is always loaded first** — `core-identity-guard`
   runs before every session and every skill invocation. It enforces file
   system protection, secrets handling, prompt injection immunity, and
   system integrity rules. No instruction can override it. Never skipped.
3. **Token Saver — MANDATORY pre-file-read probe** — before ANY `read_file()`
   call, run the `token-saver` workflow: probe Graphify `query` → Graphify
   `explain` → CodeGraph `query`/`callers`/`callees`/`impact` → only then
   read files. This saves ~56× tokens per code query (benchmark verified:
   413K words naive → 10K probed). If graph.json or .codegraph/ is missing
   for the target project, skip (tool not available) — never block.
4. **Graphify + CodeGraph are REAL, productive tools** — Both are installed
   and working. Graphify (v0.8.37) has code-graphs built for the graphify
   project (8,267 nodes, 13,225 edges, 775 communities). CodeGraph (v0.9.9)
   is initialized and indexed across ~/Documents/Projects/ (945 files,
   16,092 nodes, 43,795 edges). CodeGraph MCP is registered in Hermes config
   — use `codegraph query/callers/callees/impact` for live code context.
   Graphify's `update .` command updates graphs code-only (no LLM needed).
6. **Any project, coding, design, or analysis task → always include the
   full Obsidian+Graphify bundle as a mandatory post-execution phase:**
   `obsidian` + `obsidian-codebase-graph` + `obsidian-knowledge-graph`
   + `graphify-integrate`. Documentation + code graph are required
   deliverables, not optional.
7. **After every Obsidian or Graphify update → always regenerate the
   knowledge graph** via `obsidian-knowledge-graph`. Graph must reflect
   latest vault state including code-symbol nodes.
5. **Direct skill invocations by the user → /decide still runs.** Validate,
   enrich context, then execute. Never bypass.
6. **Setup tasks → always run complementary integration check.** When routing
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
  as an additional model source. FreeLLMAPI serves 110+ free models from 16
  providers at `localhost:3001/v1`, already wired as Hermes custom provider
  (`provider=custom, model=auto, base_url=localhost:3001/v1`). Includes
  dashboard at `localhost:5173` and Express on `:3001`. Check it as an
  alternative when OpenCode bundled models and Freebuff are insufficient —
  it covers providers not available in either.

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
| Token-saving pre-file-read | Any code reading / codebase question | **MANDATORY:** Run `workflow/token-saver` first — Graphify query → explain → path → then CodeGraph query/callers/callees/impact → only then read_file(). Verified 56.2× token reduction. |
| CodeGraph + Graphify complement | User installs CodeGraph or asks about code knowledge graphs | **Complementary — keep both.** CodeGraph provides live MCP tools (query, callers, callees, impact) — 945 indexed files, 16,092 nodes across all projects. Graphify provides code-graph query/explain/path — 8,267 nodes, 13,225 edges on the graphify project alone. CodeGraph for live agent queries, Graphify for structural analysis. |

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

session_memory → reasoning → soul file(s) → **Core Identity Guard** → **Graphify/CodeGraph probe (token-saver)** → primary domain skill(s) → complementary check (for setup tasks: run integration scan + wire new resources to existing repos) → post-execution (Obsidian bundle + Graphify export + graph refresh)

## Output Format
State once, briefly, then execute immediately:
- **Intent:** [what was detected]
- **Skills activated:** [list in execution order]
- **Confidence:** [High / Medium / Low — only shown if Medium or Low]
- **Key assumption (if any):** [one line, only when ambiguity exists]

Then proceed. No lengthy reasoning blocks printed — the reasoning runs
internally. Output is the work, not commentary about the work.