---
name: subagent-delegation
description: "When and how to delegate to subagents. Models come from config.yaml — orchestrator = model.default, delegate = delegation.model, vision = auxiliary.vision. Never hardcode model IDs here."
version: 2.0.0
author: Hermes Agent
triggers:
  - delegate
  - subagent
  - coding agent
  - delegation
  - vision
---

# Subagent Delegation & Model Roles

## Model Roles (config-derived — never name IDs here)

| Role | Source of truth | When |
|------|-----------------|------|
| **Orchestrator / Planning / Architecture** | `config.yaml` → `model.default` | Understanding tasks, delegation, architecture decisions, reviewing output. Does not implement product code. |
| **Delegate / Implementation** | `config.yaml` → `delegation.model` | ALL substantial coding, git, deploy, build, patches, multi-file edits — via `delegate_task`. |
| **Vision** | `config.yaml` → `auxiliary.vision` | Image/screen analysis. Simple inline checks may use `vision_analyze` directly; heavy multi-image visual audits go to a delegate with the image attached. |
| **Fallback** | `config.yaml` → `fallback_providers` | Automatic on provider failure; do not hand-route unless the ladder demands it. |

If this table and config disagree, config wins — and patch this file.

## When to Delegate vs Go Direct

**Delegate:** features, refactors, multi-file edits, builds, anything touching `~/Documents/Projects/` product code, parallelizable independent work (batch `delegate_task(tasks=[...])` — one entry per agent, agents don't share files). For this user, fan-out is the DEFAULT for substantial work — cost/time efficiency is an explicit standing request, reaffirmed more than once, so make the delegation call at task start and parallelize with disjoint file ownership instead of editing serially by hand; never wait for the user to remind you. Use `parallel-implementation-contracts` when the files are interdependent.

Decide the delegation split BEFORE any hand edits: when the work decomposes into independent units (multiple repos, multiple features, disjoint file sets), dispatch the fan-out first. Hand-editing "just the quick part" beforehand gives children an unknown baseline and burns the wall-clock time the fan-out exists to save.

**Direct is fine:** ≤3-line diffs, bounded one-off ops, Hermes-internal maintenance (skills/config/cron/scripts), when delegation overhead exceeds the work.

**Known constraint:** delegate children can time out writing one huge file in a single go. For big single-file builds, instruct sectioned writes (write the skeleton, then append sections).

## Brief Discipline

A delegation brief is decision-complete: goal, success criteria, interfaces, expected files, edge cases, test criteria, assumptions. Every unknown either resolved by exploring before delegating, or asked as one batched question with a recommended default. When several children need the same long shared context (mission brief, spec), write it once to a scratch file and make every brief reference that path instead of pasting it per-brief: briefs stay small and consistent, and edits to the shared context are picked up by children dispatched later. When the parent has already partially edited files the child will own, the brief names those files and tells the child to treat the on-disk tree as the sole source of truth — a parent's prose summary of its own in-flight edits drifts from disk, and the child patching from it corrupts code with phantom anchors.

Your own last-minute edits are the children's baseline: after any pre-dispatch edit to files the children will touch or import, build+test YOURSELF before fanning out. A stray brace in a shared file makes every child burn turns diagnosing a parent error; a child may also patch a file outside its manifest just to unblock its own verification — diff such cross-ownership edits and consciously keep or revert them. When children hand back items marked "outside my ownership", treat that list as the integration backlog with their file:line leads attached: those files are now yours or the next wave's, not dropped.

Read-only subagents (exploration/planning/review) get read-only instructions verbatim. A planning subagent that edits has escaped its contract.

When children work in ONE shared project directory rather than isolated workspaces, each brief carries an explicit writable-path manifest and no two live children may own overlapping paths. Re-owning files a previous child is still writing silently overwrites verified work mid-run; check for live writers before reassigning shared paths, and serialize the children instead when the work is inherently one pipeline (one scene, one renderer, one manifest). In shared-tree UI waves keep children patch-only (edit files; no builds, no browsers, no commits) and let the parent own build + QA + commit centrally: parallel children driving browsers against one dev server collide, and each redundant build burns minutes of the wall clock the fan-out exists to save. When children must capture screenshots (visual polish loops), give each its own dev-server port — a shared server makes `networkidle` waits flake for every consumer of it, including the parent's own QA runs. Likewise, when a child must build to verify its own work, give it a private `--outDir` (e.g. `/tmp/<child>`): a shared build output is emptied and rewritten by a sibling mid-run, and every consumer then QA's half-written bundles. When one feature must land in several repo variants (a mock/demo build and a production build of the same product), dispatch one child per variant, put that variant's architecture contract in its brief (data layer, allowed dependencies, what must NOT be ported from the other variant), and give schema/migration work its own child so no frontend brief also owns database changes.

### Shared-Tree Integration Gate

Concurrent children editing one tree invalidate each other's test counts: a child's "N/N pass" is a snapshot of a tree its siblings were still writing, and children will report failures that belong to a sibling's in-flight files. Only the parent's full-suite run on the merged tree is authoritative — run it before every commit and report that number, never a child's. Commit each verified integrated wave so the next wave (or a replacement child) diffs against a clean baseline; unattributed WIP in `git status` makes children misattribute ownership and skip work as "not mine". While other children are still live, stage with explicit pathspec exclusions (`git add -A -- ':!path'`) so a running child's half-finished edits never ride into a verified wave commit. On long multi-session waves, leave a CHECKPOINT.md with resume steps at each committed boundary so an interrupted run resumes from verified state instead of re-deriving it.

## Post-Delegation Verification (mandatory)

Never relay a child's "done" as success:
1. Read back actual output before integrating — files exist, state changed. A completion message is a self-report and can carry convincing specifics (feature lists, test counts, filenames) while nothing landed: diff the claimed file list first (`git diff --stat` / `git status`, grep the claimed feature's marker strings) and treat any claimed file with zero mutation as fabricated — re-implement that slice yourself instead of debugging phantom work.
2. Run the relevant test/build/check from the brief on the merged tree yourself (child pass counts are per-run snapshots — see Shared-Tree Integration Gate). "Full suite" includes the repo's ESTABLISHED browser/QA scripts, not just the unit runner: children verify the tests they wrote and rarely re-run pre-existing QA suites, so stale assertions in untouched features surface only in the parent run.
3. Treat file-mutation-verifier warnings as leads, not verdicts: a "file not found" verdict usually names the path the child tried, which may be wrong (relative path resolved outside the project). Confirm with `git status` + syntax check at the real project root before concluding a deliverable is missing — or before re-dispatching work that already landed.
4. When re-deriving a child's quantitative claims (counts, totals from a database or
   log), reproduce its exact filter semantics before disputing a mismatch: schema
   columns differ from assumptions (epoch `timestamp`, not `created_at`), and raw
   tables carry inactive/compacted rows that inflate counts several-fold. A child's
   number that disagrees with a naive re-query is usually the naive query being
   wrong — resolve the query shape first, then accept or challenge the figure.
5. For substantial Tier-3 work: `hermes verify <project>` records evidence
6. Only then report, with evidence
7. Revalidate a child's capability/credential claims before acting on them: env-var absence does
   not mean no credential (auth registries hold registered credentials), an installed binary can
   sit on a PATH the child never probed, and error text echoed from old logs is not a live
   failure. One probe of the authoritative registry (`hermes auth list`, `command -v`, a fresh
   run) prevents "fixing" what was never broken.
8. When an async completion message arrives for superseded work (an obsolete script generation, an abandoned pipeline version), identify the producing command and output markers before accepting it as the current result — completions from dead runs interleave with live ones and read like deliverable confirmations. When an approach is rejected mid-flight, kill its still-running background jobs explicitly (poll, then kill) — otherwise their heartbeats keep re-running and delivering the rejected output for hours.

### Acting on a delegated audit or review

A read-only audit's FINDINGS are self-reports of the same class as its completion claims, and they go stale for the same reason: the run spans minutes against a tree that later edits have already moved. Re-verify every finding against the current on-disk file:line before editing anything. Three failure shapes to expect: a defect already fixed by a concurrent edit, a claim that something "does not exist" when it does (grep for it before accepting any absence), and behaviour that is deliberate design rather than a bug (check the comment or contract that says so). A finding that does not reproduce is recorded as stale and left alone — patching correct code from a stale finding churns it and can reintroduce the very bug it claims to fix. Findings that DO reproduce get fixed at the root cause, and the QA record names which reported items were stale so the audit trail stays honest. An unverified audit is worse than no audit: it manufactures confident edits against code that was already right.

### A killed worker's last words are not its verdict

A run that dies mid-task (host shutdown, OOM, provider kill, budget exhaustion) often leaves its work **already on disk** and stops during the report. Its final message is a snapshot of its own in-flight reasoning, not a verified conclusion — it may name a bug it was about to look at next, or flag its own work as incomplete when it is done.

After an unexpected termination, reconstruct state from artifacts before believing the narration:

1. Read the task's event log for the terminal kind (`crashed`, `worker_lost`, `timed_out`) and the `exit_code` — `Iteration budget exhausted (60/60)` means the work was too large for one run, not that it was wrong.
2. Diff what actually landed: the claimed file list, the row counts, the test suite. A crashed run that wrote the fix and died before its summary reads identically to a run that did nothing.
3. Re-run the verification yourself before accepting or rejecting the dying claim. A worker's parting "still needs X fixed" is a hypothesis; a targeted test decides it. Close the task with the evidence you produced, and say in the summary which of the worker's claims you disproved — a wrong closing note left in the record becomes the next session's bug report.

Corollary: an iteration-budget kill on a broad task is a signal to narrow the card, not to re-dispatch it unchanged. The retry burns the same budget on the same scope.

Before re-dispatching a BLOCKED card, check whether the work already landed: an iteration-budget kill usually means the worker finished the edits and stopped before the completion call. Grep for the expected fix, run that repo's suite, then close the card with the evidence (`hermes kanban complete <id> --result "..."`) instead of reopening it. Reopen only what the tree proves is missing, and re-scope it smaller than the run that died.

## Re-dispatch after mid-task failure

When the user overrides scope mid-flight (an "ignore the previous X, just do Y" message), steer every live child immediately (`action=steer`) with the new contract and an instruction to delete the superseded machinery — un-steered children keep finishing the old spec and their output arrives as work you must undo.

A brief that EXTENDS the active work (adds a QA loop, a polish pass, or extra screens over in-flight implementation) stacks as a layer instead: keep the running waves, queue the new scope as the next wave or loop, and never restart or re-dispatch work already in flight.

A child killed mid-task by a provider-wide error (billing, rate limit) often leaves useful partial artifacts (scripts, drafts, half-built files). Do not restart from scratch: read the partial output, and brief the replacement child to continue from those exact paths ("read X first; rewrite only where it violates the spec"), keeping the same write-ownership manifest. Re-dispatch only after the provider is demonstrably live again — probe the provider DIRECTLY with a one-token completion (a child's failure text is not proof the provider is down), not just with a succeeding parent turn. Billing exhaustion follows the ACCOUNT, not the model: a retry pinned to a fallback model fails with the identical 402, so when the direct probe confirms billing, go hands-on immediately instead of re-dispatching. When the user supplies a replacement key mid-mission, the delegation path can be revived instead: probe the delegate model through the NEW key first (one-token completion), register it as an ADDITIVE provider entry in `config.yaml` `providers` (never overwrite the dead entry — the old key may be revived or belong to a different account), and pin each dispatch with `delegate_task(model=…, provider=…)` to the new entry. Land one real dispatch before batching the rest of the fan-out. Repeated 402/rate-limit dispatch failures are one provider outage, not bad briefs; re-spawning into it just burns the queue. Surface the wallet/entitlement state to the user as the fix, and note in the final report which workstreams ran hands-on. Outages can clear MID-SESSION (top-ups, provider recovery), so do not write delegation off for the whole session: one cheap retry at the next phase boundary is both the probe and the recovery — if it lands, resume delegating; if it fails again, stay hands-on and retry at the following boundary. Entitlement is per-model and can drain MID-MISSION: one fan-out batch can exhaust a single model's quota, so later dispatches through the same working key 402 while direct probes of other models still return 200. Re-probe the model the dispatcher will actually route to before EACH new wave, not once per session — and when a failure notice names a model different from your `model:` pin, the pin is advisory; treat the routed model as the real dependency (pin through the provider entry's `default_model` or go hands-on) instead of re-pinning the same way.

After 2-3 dispatch attempts at the SAME unit that end in non-completion (quota kills, interruptions, no-answer errors, whatever the cause), stop re-dispatching it and finish hands-on from the partial output — delegation only pays when children complete, and at that failure rate direct execution of the remainder is strictly faster. Validate whatever the dead children left before building on it (syntax-parse touched files; see `patch-hygiene` rule on edits you did not make), and shrink the remaining scope to just the unfinished gap.

## No-Progress Recovery

Treat repeated identical tool output as a failed approach, not a transient failure. After one unchanged result or a loop warning, stop replaying the same call, inspect the tool's required inputs and the last useful result, then switch to a targeted query or a different mechanism. Do not ask the user to choose a recovery path when the task can continue from the evidence already collected.

## Visual QA Pattern (when interfaces are involved)

1. Orchestrator plans (minimal spec, single-file when sensible)
2. Delegate implements
3. Render the result (browser/screenshot) → `vision_analyze` or delegate-with-image for the audit
4. Orchestrator reports: code-path trace + visual findings together

Full recipes in `references/` of this skill.

## Model-Switch Rule

Don't switch models per-task unless the current one demonstrably fails (timeout on large writes, repeated malformed output). First remedy: smaller briefs / sectioned writes, not a different model. Provider fallback is config-automatic.

## Deliver What Was Authorized — Offer the Alternative, Don't Substitute

When the user authorizes a specific artifact ("create a dedicated bot and a group chat if you think that's better"), the authorization covers **building it**. Having a better idea is not permission to build something else instead and explain why in the summary.

- Ship the authorized thing. If you believe a different shape is better, build the authorized one **and** state the alternative in one line ("built X; a Kanban board would also cover this — say the word"), so the user can redirect a running system instead of discovering a substitution.
- "I chose Y instead of the X you asked for, here is why" reads as a completed task and is not one. It is the failure mode this rule exists to prevent: the user re-asks, the work is redone, and trust drops.
- The same applies to scope: an explicit "only these screens"/"do not touch X" stays authoritative even when the surrounding work would obviously benefit. Raise the objection; do not quietly expand or contract.
- Corollary for audits: when your own findings argue the authorized thing is unnecessary, that is an argument to present **before** declining to build it, not a substitute for building it.

A related trap on the analysis side: **do not answer a request for work with a status report.** "No, not everything — here is what remains" is the right answer only when genuinely blocked. If the remaining items are things you can do yourself, the correct move is to do them and report the result, not to enumerate them as a gap the user must now close by asking again.

## Named teammates (plugin)

The `hermes-teammates` plugin registers a standing roster (`teammates_roster`, `teammate_assign`, `teammate_check`, `teammate_wait`, `teammate_message`, `teammate_stop`). Prefer it over one-shot `delegate_task` children when the same specialist must keep context across several turns, or when a named reviewer should be addressable by role. Roster entries live in the plugin's `teammates` settings.
