---
name: decide
description: Master orchestrator that runs on every prompt, selects and sequences the appropriate skills, injects context, and enforces execution order. Always runs first. Never skipped.
triggers:
  - always
---

# /decide — Capability Router

> **Structure (2026-09-16 rewrite):** this skill is a *policy*, not a database. It contains no model names, no MCP counts, no paths that the live system doesn't confirm. Environmental truth lives in: `config.yaml` (models/providers), `hermes mcp list` (MCPs), `skills_list` (skills), live probing (binaries/files/keys). If this file and live state disagree, live state wins — and patch this file to match.

## The Routing Chain

**TIER GATE (hard):** orchestration must scale with task complexity (tier from SOUL Step 0 / `task_tier`). Complexity budget — Tier 1: <=1 skill, no composition, no preloading, no research, no delegation, verify only the specific change; Tier 2: few directly relevant skills, limited composition, targeted verification; Tier 3: full orchestration subject to relevance. The user's explicit scope outranks everything below; "only fix X" is authoritative.

```
USER REQUEST
  → TIER (hard gate: orchestration scales with task complexity; tier from task_tier / SOUL Step 0)
  → INTENT (the user's stated request IS the intended scope — broaden only with concrete evidence it cannot be completed as stated)
  → CAPABILITY CLASS (one of seven, below)
  → SKILL SHORTLIST (primary → secondary → fallback; ≤3, verified names)
  → AVAILABILITY CHECK (probe before use)
  → EXECUTION (direct tool | MCP | skill | delegate_task)
  → VERIFICATION (per output type — table below)
  → RECOVERY (ladder below, on failure)
  → MEMORY (durable facts only → memory tool; everything else → session state)
```

## The Seven Capability Classes

| Class | Signals | Primary skills (verify resolve before first use) |
|---|---|---|
| **code** | build/fix/refactor/debug/implement, PRs, tests, architecture, database/API work, auth/payments/security, production deploy, reliability, performance, incident debugging | `software-engineering` (universal production-grade method — load for ANY substantial or high-risk engineering work, composes with the project skill), then `code-review`, `security-review`, `simplify`, `test-driven-development`, `systematic-debugging` |
| **design** | UI/UX/visual/brand/style, landing pages, components | OpenDesign (`open-design-ade`, web UI on localhost:7456 — probe; app must be running) is the standing first choice for design work, then `impeccable` (full design workflow), brand kit (`<brand>-ui-skills` or `od-<brand>`), bare style name (`glassmorphism`…) — `creative` is the generic fallback |
| **research** | search/look up/compare/cite, current events, papers | builtin `web_search` (quick) → `firecrawl` leaves (`firecrawl-search/scrape/deep-research`) → `scrapling`/`blocked-page-recovery` (fallback) |
| **ops/system** | system state, disk, installs, cron, services, backups | `devops` leaves (`docker-management`, `linux-system-backups`…), `workflow/hermes-backup-workflow`, `hermes-kanban-setup` |
| **media** | images, video, audio, TTS, documents | `hyperframes`/`media/openmontage-production` (video — environment-gated), `sensenova-image-gen` (images), `media` leaves (audio), `productivity` leaves (docx/pdf/pptx) |
| **data** | analysis, market data, notebooks, finance | `data-science` leaves, `llmquant-*` (finance routes here + `llmquant-data` MCP), `note-taking` leaves |
| **hermes-internal** | config, skills, MCPs, gateway, profiles, cron | `hermes-agent` skill (always first), `subagent-delegation`, `workflow` leaves |

**Routing discipline:**
- **Engineering work composes two layers:** `software-engineering` (generic production method: correctness, state, concurrency, security, reliability, ops) + the project-specific skill (schema, routes, business rules). Both load together; the universal skill never overrides project rules. Trivial edits (copy, styling, one-liners) skip the universal skill — its risk tiers govern how much rigor to apply.
- Verify before `skill_view`: confirm the name resolves BY NAME in `skills_list` (or `~/.hermes/scripts/reference_find.py "<name>"`). Do NOT probe directories — skills nest up to two levels (`devops/docker-management`), so path checks (`ls ~/.hermes/skills/<name>`) false-MISSING skills that resolve fine by name. Same name on two SKILL.md files = collision: use the path-qualified form `<dir>/<name>/SKILL.md`.
- Two skills overlap → activate both ONLY if the task genuinely needs both; otherwise load the more specific one. No skill matches → `python3 ~/.hermes/scripts/reference_find.py "<query>"` (TF-IDF over the reference library, sub-second) → closest class, flag the gap.
- Ambiguous intent → assume, state in one line, proceed. Genuinely ambiguous AND consequential → one batched clarifying question.
- Pre-load a second-step skill ONLY for Tier 2+ when the next step is highly predictable and directly required (feature work → code-review will follow). Tier 1 never preloads.

**Composition (multi-skill chains):** `decide` composes workflows, not single picks. Composition is demand-driven and tier-gated: Tier 1 never composes (0-1 skills, no chain); Tier 2 composes only what the implementation actually requires; Tier 3 may chain full workflows. Derive the chain from the actual request; never force steps the task doesn't need. Pre-load the next step only when the chain is active (Tier 2+, highly predictable, directly required); verify each step at the depth its tier demands (Tier 1/2: the affected behavior only), iterate per the Recovery ladder when verification fails. Standard chains:
- Research: `web_search` → `firecrawl` leaves → verify + cite → summarize
- Code: inspect (CodeGraph) → `software-engineering` + project skill → implement → test → `code-review`
- Repo change: inspect architecture → pick relevant skills → modify → test → review
- Long-running: plan → execute → checkpoint (kanban card / CHECKPOINT.md) → verify → continue
- External tool: select MCP → `hermes mcp list` probe → execute → inspect result → validate
Derive the chain from the actual request; never force steps the task doesn't need.

## Availability Check (Rule 3 — universal)

A name in documentation is a hypothesis. Before relying on any dependency:
- binary: `command -v <tool>` · file/key: `test -f <path>` · MCP: `hermes mcp list` (never route to a disabled/degraded server) · tool: `tool_search` before declaring a capability missing · model/provider: `config.yaml`.
- Missing dependency = fallback trigger, not a violation. Record the gap once, take the sanctioned fallback, move on.
- Profile-gated tools (kanban orchestrator tools, vision, desktop panes) may not exist in the current session — probe or degrade instead of hunting.

## Delegation

Config (`config.yaml`: `delegation.model`) defines the delegate model — never name it here. Full patterns: `subagent-delegation` skill.

- **Delegate:** substantial implementation (features, refactors, multi-file edits, builds), parallelizable independent work (batch `delegate_task(tasks=[...])`), anything touching `~/Documents/Projects/` product code.
- **Direct is fine:** ≤3-line diffs, bounded one-off ops, Hermes-internal maintenance, when delegation overhead exceeds the work.
- **Children need decision-complete briefs:** goal, success criteria, interfaces, edge cases, test criteria — and sectioned-write instructions for large single files (children can time out writing one huge file).
- **Read-only subagents** (exploration/planning) get read-only instructions verbatim; a planning subagent that edits has escaped its contract.
- **Mandatory read-back on completion:** never relay a child's "done" as success. Verify actual output (files exist, tests/build pass, state changed), then report. For substantial Tier-3 work, `hermes verify <project>` records evidence.

## ECC Specialist Library

64 specialist agents (reviewers, resolvers, architects per language/stack) exist at `~/Documents/SkillReferences/ECC/agents/*.md` — a library, NOT active routing. When a request clearly needs a specialist (e.g. django/rust/kotlin review, build-error resolution):
1. `ls ~/Documents/SkillReferences/ECC/agents/ | grep -i <domain>` → pick the matching specialist
2. Read its `.md`, fold its instructions into a `delegate_task` brief
3. Verify the result per the Verification table

## Verification (per output type — no "done" without it)

| Output | Verify |
|---|---|
| Code | run test/build/check + inspect resulting state |
| Delegated work | read back actual output; `hermes verify` for Tier 3 |
| Visual | render + vision check |
| Research | sources cross-checked; every external claim cited at the claim site; conflicts stated, never averaged |
| Deploy | production behavior check |
| File op | reopen/inspect |
| MCP-dependent task | server healthy in `hermes mcp list` before starting |

## Recovery Ladder (on any failure)

```
RETRY (once, if plausibly transient)
→ DIAGNOSE (read the actual error; fix root cause over symptom — e.g. "not initialized" → run init)
→ ALTERNATIVE TOOL (same capability, different mechanism)
→ ALTERNATIVE SKILL (next name on the shortlist)
→ ALTERNATIVE MODEL (config fallback_providers; for delegation, split into smaller briefs)
→ DEGRADE (deliver partial result, state what's missing)
→ REPORT (honest blocker + what was tried)
```

Framework guardrails (tool-loop warnings, watchdogs, fallback providers) handle the mechanical layer — connect to them, never build parallel recovery infrastructure.

## Memory Policy

Durable user/context facts → `memory` tool (declarative, compact). Everything else → session state / kanban / session_search. Reference-material discovery → `python3 ~/.hermes/scripts/lightrag_find.py "<query>"`. Never treat in-RAM state as persistent.

## Token Discipline (Rule 1)

Reading code under `~/Documents/Projects/` → probe CodeGraph first (`mcp__codegraph__codegraph_explore` with `projectPath`, or CLI `codegraph query`). `read_file` is last resort for project code. Exception: `~/.hermes/` and `~/.config/` system/config files — no probe needed. Graphify MCP for structural graph questions.

## Self-Correction

Wrong routing outcome → record what should have been selected → patch this file → tell the user. Update this file when: a new integration lands, a routing pattern proves wrong, a route target dies. Never add content that live state can answer.
