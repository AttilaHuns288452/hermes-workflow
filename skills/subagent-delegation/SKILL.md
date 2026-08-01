---
name: subagent-delegation
description: "When and how to delegate to subagents. Hermes chat model = planning, DeepSeek V4 Flash = coding, MiMo = multimodal."
version: 1.1.0
author: Hermes Agent
triggers:
  - delegate
  - subagent
  - coding agent
  - deepseek
  - mimo
  - vision
---

# Subagent Delegation & Model Roles

## Model Roles

| Role | Model | When |
|------|-------|------|
| **Orchestrator / Planning / Architecture** | **Hermes chat model** (currently `opencode-go/deepseek-v4-pro`) | Understanding tasks, delegation, architecture decisions. NEVER writes code, runs git, patches files, or does build/deploy. |
| **Implementation / Edits / Coding / Execution** | `opencode/deepseek-v4-flash-free` | **ALL coding, git, deploy, build, patches, merge conflicts, terminal commands.** Delegate via `opencode run` or `delegate_task`. |
| **Multimodal / Vision QA / Screenshots** | `opencode/mimo-v2.5-free` | **ALL image/video/visual tasks.** Delegate via `delegate_task` → MiMo subagent reports findings; orchestrator feeds results to coding agent for fixes. |
| **Difficult multimodal** | `opencode-go/mimo-v2.5-pro` | Complex, long-running multimodal reasoning tasks. |

## Vision Delegation Rule (ALWAYS)

When the orchestrator needs to see something — screenshot, UI visual QA, design review, video analysis — **delegate it to a MiMo subagent**, never call `vision_analyze` directly from the orchestrator. The subagent returns a report; the orchestrator reads it and routes findings to DeepSeek for fixes.

## End-to-End Workflow Pattern (ALWAYS)

When building anything visual that needs QA, follow this three-agent split:
1. **Orchestrator** plans — what to build, minimal spec, single-file when possible
2. **DeepSeek** codes — `delegate_task` or `opencode run`
3. **MiMo** QAs — `delegate_task` with a screenshot for visual audit
4. **Orchestrator** reports — code-path trace + visual findings in one summary

The orchestrator NEVER builds, NEVER QAs visually. DeepSeek handles code. MiMo handles vision. This is the entire workflow.

Concrete pipeline: `npx serve` → PowerShell `CopyFromScreen` → `delegate_task` to MiMo. Full recipe in `references/visual-qa-pipeline.md`.

```
delegate_task(goal="QA the page at http://localhost:63551 — report every visual defect")
```

## QA Agent Responsibilities

**Primary Model:** MiMo V2.5

### Primary Responsibilities
- Review UI screenshots for layout, spacing, alignment, typography, and visual consistency
- Perform UX critiques and identify usability issues
- Detect visual bugs, rendering problems, responsive design issues, accessibility concerns, and design inconsistencies
- Compare before/after screenshots to identify regressions
- Review diagrams, PDFs, images, and other visual assets

### Escalate to DeepSeek V4 Pro when
- Verifying whether the implementation satisfies the original requirements
- Reviewing code quality beyond visual inspection
- Analyzing business logic or architecture
- Evaluating design patterns, scalability, maintainability, or edge cases
- Determining whether a feature is logically complete

### Delegate to DeepSeek V4 Flash when
- Generating unit tests
- Creating integration tests
- Producing test cases or mock data
- Writing automated testing code

### Decision Rules
- Visual task → MiMo V2.5
- Software engineering reasoning, architecture, requirement verification → DeepSeek V4 Pro
- Implementation-focused (tests, test code) → DeepSeek V4 Flash

**Goal:** Act as the project's quality gate — ensure both visual experience and implementation quality meet production standards while delegating specialized reasoning and coding tasks to the appropriate models.

## Vision Delegation Rule (ALWAYS)

When the orchestrator needs to see something — screenshot, UI visual QA, design review, video analysis — **delegate it to a MiMo subagent**, never call `vision_analyze` directly from the orchestrator. The subagent returns a report; the orchestrator reads it and routes findings to DeepSeek for fixes.

```
delegate_task(goal="QA the page at http://localhost:63551 — report every visual defect")
```

## QA Testing Depth Rule (ALWAYS)

When QAing something you built — **test EVERYTHING.** Every button, every state transition, every edge case. Not just "does it render" — actually click every button, verify every behavior, test edge cases (empty states, double-clicks, rapid inputs, responsive breakpoints). Report what was tested and what failed.

## Cache-Busting Rule (ALWAYS)

Static sites served from local files or simple HTTP servers can serve stale cached versions after edits. **Always add a cache-busting query param or meta tag** so fixes are visible immediately without hard refresh: `<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">` in `<head>`. Or append `?v=1` to the URL when re-testing.

## Agent Utilization Checklist (ALWAYS)

Before building any UI or coding task, check which agents should be involved:

| Agent | When | How |
|-------|------|-----|
| **21st.dev** | Any UI/design work | `get_inspiration(query)` → extract design tokens → feed to DeepSeek |
| **MiMo V2.5** | Visual QA, screenshots, design review | `delegate_task` — never `vision_analyze` from orchestrator |
| **ECC agents** | Code review, architecture, security, a11y | Route via ecc-bridge; check agent roster before generic delegation |
| **Pantheon swarm** | 3+ subtasks needing parallel work | `opencode run` with oh-my-opencode-slim plugin |

**21st.dev is NOT a code source** (shadcn needs build system). Use it for design TOKENS only — colors, spacing, card styles, font choices. Feed extracted tokens to DeepSeek for implementation.

See `references/agent-utilization-workflow.md` for the full end-to-end pattern from this session.

## Delegation Decision

**Do directly** (1-2 patches, trivial):
```
# Delegate to DeepSeek V4 Flash
delegate_task(goal="Fix the typo in config.ts", context="...")
```

**Delegate** (3+ independent changes, reasoning-heavy):
```
delegate_task(tasks=[
  {"goal": "Fix auth bug in login.ts", "context": "..."},
  {"goal": "Add tests for user service", "context": "..."},
  {"goal": "Update README with new API", "context": "..."}
])
```

**Parallel bug-fix dispatch** (3+ independent bug clusters across different files):
```
# Partition files into non-overlapping sets, one agent per cluster
delegate_task(tasks=[
  {"goal": "Fix core bugs: currency, entity bypass, dark mode", "context": "YOU OWN THESE FILES: ...\nDO NOT EDIT any other files"},
  {"goal": "Fix all feature components: formatCurrency, missing fields", "context": "YOU OWN THESE FILES: ...\nDO NOT EDIT any other files"},
  {"goal": "Premium visual overhaul: sidebar, auth pages", "context": "YOU OWN THESE FILES: ...\nDO NOT EDIT any other files"},
])
```
See `references/parallel-bugfix-dispatch.md` for the full pattern: file-ownership partitioning, context block anatomy, read-before-dispatch discipline, post-return recovery.

**OpenCode one-shot** (bounded coding task):
```
terminal(command="opencode run 'Add retry logic to API calls' --model opencode/deepseek-v4-flash-free", workdir="~/project")
```

## Agent Roster — Check BEFORE Generic Delegation

**ECC Agents** (64 agents, free chain): reviewers, build resolvers, architects, security, ML, DevOps, language specialists. Route to matching specialty first.

**Pantheon Swarm** (OpenCode): Orchestrator/chat-model, Oracle/DeepSeek (strategy+review), Explorer/DeepSeek (codebase recon), Librarian/DeepSeek (docs+APIs), Designer/DeepSeek (UI), Fixer/DeepSeek (fast patches), Council (consensus).

**Agency Agents** (254+ specs): broadest roster — check `agency-agents` skill for specialized roles.

### Routing Priority
1. Task matches an ECC/Agency agent specialty? → Route to that agent
2. 3+ independent subtasks? → Pantheon swarm via `opencode run`
3. 1-2 edits or single bounded task? → `delegate_task` to DeepSeek V4 Flash or `opencode run`

### Common ECC Routes
| Task Type | ECC Agent |
|-----------|-----------|
| Code review | `reviewer-*` agents (python, typescript, rust, etc.) |
| Build errors | `build-error-resolver` |
| Architecture/planning | `architect-*` / `planner-*` |
| Security audit | `security-*` / `e2e-*` |
| ML/data | `mle-*` / `gan-*` |
| DevOps/infra | `network-*` / `harness-*` |
| Language-specific | `python-reviewer`, `typescript-reviewer`, etc. |

**The orchestrator (Hermes chat model) must NOT be used for:**
- Writing or editing code
- Running git commands (push, pull, commit, merge)
- Running builds (npm run build, etc.)
- Patching files
- Any terminal command that could be delegated

**The orchestrator should ONLY:**
- Route tasks to the right model
- Reason about architecture/decisions
- Resolve merge conflict decisions (the *what to keep*, not the *git commands*)

**DeepSeek V4 Flash handles ALL implementation work.**

## Rate-Limit Fallback

Free model hit 429? Auto-switch, don't ask:
- `opencode/deepseek-v4-flash-free` → `opencode-go/deepseek-v4-flash`
- `opencode/mimo-v2.5-free` → `opencode-go/mimo-v2.5`

## Pitfalls

- **Subagent model inherits parent unless pinned in config.** `delegate_task` subagents use the parent session's model, NOT the model you describe in the goal. Pin DeepSeek for all subagents:
  ```bash
  hermes config set delegation.model deepseek-v4-flash-free
  hermes config set delegation.provider opencode-zen
  ```
  This pins every subagent to DeepSeek V4 Flash regardless of parent model. Verify with `grep -A5 '^delegation:' ~/AppData/Local/hermes/config.yaml`.
- **600s timeout** on delegated tasks. Break large batches into 4-6 items max.
- **Never delegate mundane work to paid models** unless rate-limited.
- **Always specify `--model`** when using `opencode run` — defaults can be wrong.
- **Subagents have no memory** — pass all context in the `context` field.
- **Subagent timeout ≠ no work done** — a 600s timeout with 15-20 API calls means code was written but build/deploy didn't finish. Check `git diff --stat` before re-dispatching. CashFlow OS session: all 3 agents hit 600s timeout with 15-20 API calls each, but had written 21 files (+917/-337 lines). Build failed on only 2 TypeScript errors that the orchestrator fixed in 3 minutes.
- **Supabase sequential inserts** — when delegating Supabase code, explicitly tell DeepSeek to use batch inserts (`supabase.from('t').insert(array)`) not loops. See `references/supabase-crud-patterns.md`.
- **Orchestrator drift — 5-turn self-audit**: If the orchestrator has written more than 5 consecutive `write_file`/`patch` calls without dispatching a single subagent, it has drifted out of role. Stop, dispatch the remaining work, and report what was done and what was delegated. CashFlow OS session: 50+ turns of inline coding, no subagents dispatched for the last 5 hours of work.
- **Secret handling in delegation** — when tasks involve API keys, tell the subagent NEVER to print keys to stdout. Use `sed` to inject. See `references/supabase-crud-patterns.md`.
- **Vision rule violation is self-reinforcing** — the skill says "ALWAYS delegate to MiMo, never `vision_analyze` from orchestrator." But when MiMo is dispatched as a background agent and you're impatient for a visual read, the temptation is to call `vision_analyze` directly. This happened in the CashFlow OS session: orchestrator called `vision_analyze` twice on login/signup screenshots while MiMo was running in the background. The fix is NOT to call `vision_analyze` — wait for MiMo. If you need an instant read, that's a sign the MiMo agent should have been dispatched earlier, not that you should bypass the rule. The orchestrator reading screenshots directly is a role violation even if the analysis is accurate — it desensitizes you to the rule and makes the next violation easier.
- **Post-timeout recovery: TypeScript fix cascade** — after 3 parallel agents timeout, `npm run build` may fail with 2-3 TypeScript errors. These are caused by agents changing function signatures (e.g., removing `userEmail` from a return type) or adding nullable returns (e.g., `exportTransactionsCSV()` now returns `null`). The orchestrator CAN fix these — they are not feature code, they are type-bridge fixes (add a null guard, add back a returned field, annotate a callback parameter). Pattern: `git diff --stat` → `npm run build` → read the error line → `patch` the one line → rebuild → repeat 2-3 times. Total time: 3 minutes. Then continue to visual QA + deploy. Do NOT re-dispatch agents for trivial TS fixes — that wastes 10 minutes of agent time on a 30-second patch.

## Timeout Recovery (when a subagent hits 600s limit)

See `references/visual-audit-workflow.md` for the Firecrawl→MiMo→DeepSeek visual audit pattern and Firecrawl screenshot URL pitfall.

Subagents that time out often DID save partial work — they just ran out of time before finishing build/deploy/verify. Don't re-dispatch blindly; recover the work:

```bash
# 1. Check what was actually changed
git diff --stat
git diff --name-only

# 2. Verify the changes compile
npm run build  # or whatever the project build command is

# 3. If build passes → finish remaining steps yourself (deploy, push, verify)
# 4. If build fails → fix the specific error, then continue
# 5. If no changes were saved → re-dispatch with a smaller scope
```

Key insight: a timed-out subagent with 30+ API calls almost certainly wrote code. The timeout means it didn't finish the *post-coding* steps (build, test, deploy), not that it did nothing. Check `git diff` before deciding to re-dispatch.

### Ponytail Gap-Fill for Greenfield Builds

For greenfield app builds (40+ files), the subagent typically finishes complex components (shadcn primitives, auth flows) but times out before completing route pages, layout wrappers, and middleware. The fastest path: **orchestrator fills the gaps directly** — route pages are one-liners, layout wrappers are thin. Full recipe in `references/greenfield-app-spec-template.md` and `references/supabase-crud-patterns.md`.

## ECC Agent Dispatch — PROVEN PATTERN

**Always dispatch ECC agents in parallel for code review. Minimum 3 agents per significant change, 2 for small fixes.**

Pattern from CashFlow OS session (2026-07-30):
```
delegate_task(tasks=[
  {"goal": "Review database schema — RLS, indexes, constraints", "context": "..."},  # database-reviewer
  {"goal": "Scan for silent failures, empty catches, unhandled throws", "context": "..."},  # silent-failure-hunter
  {"goal": "Full code quality review — DRY, types, imports, patterns", "context": "..."},  # code-reviewer
])
```

**Proven impact:** 3 agents found 52+ issues in one pass: duplicated getEntity() in 5 files, empty catch blocks, missing CHECK constraints, silent signup failures, unused imports. Applying fixes eliminated 20+ bugs before production.

**Dispatch rules:**
- Schema changes → database-reviewer ALWAYS
- New features → code-reviewer + silent-failure-hunter  
- Build errors → build-error-resolver
- Minimum 2 agents, prefer 3-4 in parallel
- ECC agents use free-tier DeepSeek V4 Flash — ZERO token cost. Never skip.

**Workflow:** dispatch parallel → wait for reports → apply fixes in severity order → commit between rounds.

## Supabase Migration Pitfalls (from CashFlow OS)

- **Trigger functions break when SQL is split by semicolon**: Supabase's REST API `/database/query` runs ONE statement. Splitting migration SQL naively by `;` cuts PL/pgSQL function bodies in half ($$...$$ blocks contain semicolons). Fix: move triggers to app code (server actions), or use `DO $$` blocks with EXCEPTION handling.
- **`CREATE POLICY IF NOT EXISTS` is NOT valid PostgreSQL**: Use `DO $$ BEGIN CREATE POLICY ... EXCEPTION WHEN duplicate_object THEN NULL; END $$` for idempotent policy creation.
- **Auth trigger on `auth.users` requires SECURITY DEFINER**: The Supabase auth schema restricts triggers. Moving entity creation to app code (signUp server action) is more reliable than DB triggers.

## Greenfield App Build Pattern

When the user asks you to build a full-stack app from scratch (Next.js + Supabase + Vercel, or similar), use this split:

1. **Orchestrator scaffolds** — `create-next-app`, install deps, write foundational files (migrations, env templates, architecture docs)
2. **Orchestrator writes comprehensive spec** — every file, every requirement, every edge case, in one dense `context` block
3. **DeepSeek builds** — `delegate_task(goal=..., context=<the full spec>)` with the entire spec as context
4. **Orchestrator does prep work** while subagent runs — docs, README, V1_NOTES, env templates. Don't sit idle.
5. **On subagent return** — check `git diff --stat`, run `npm run build`, fix any remaining errors

Key rule: the orchestrator writes NO component code. Only scaffolding commands, config files, docs, and the delegation spec. All `.tsx`, `.ts`, UI components go to DeepSeek.

The spec must include: full file list with paths, database schema SQL, component descriptions, styling rules, the exact `cn()` pattern, all server action patterns, and a clear "when done, run `npm run build`" instruction.

## Reference Files

- `references/parallel-bugfix-dispatch.md` — Parallel multi-agent write dispatch with non-overlapping file ownership (10+ bugs across 80 files pattern)
- `references/visual-audit-workflow.md` — Firecrawl→MiMo→DeepSeek visual audit pattern for "make this premium" tasks
- `references/nextjs-server-action-pitfalls.md` — `redirect()` anti-pattern, entity creation in app code, migration execution gotchas
- `references/supabase-architecture-pitfalls.md` — Supabase anti-patterns for delegation briefings
- `references/entity-switching-via-cookie.md` — Multi-tenant entity switching pattern for Supabase apps (cookie-based, zero API changes, proven in CashFlow OS)
