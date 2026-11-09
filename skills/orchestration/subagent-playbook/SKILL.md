---
name: subagent-playbook
description: 'Patterns for getting reliable work out of subagents: strict read-only
  sandboxing, depth-vs-breadth role separation, recall-biased finding verification,
  and self-reporting end-stops. Use when dispatching agents to explore, plan, review,
  verify findings, or run autonomous loops. Read as a reference alongside dispatching-parallel-agents
  — that one covers when to parallelize; this covers how to spec each agent so its
  output is trustworthy.'
version: 1.0.0
author: Hermes Agent (distilled from Anthropic Claude Code subagent prompts)
license: MIT
platforms:
- linux
- macos
- windows
metadata:
  hermes:
    tags:
    - delegation
    - subagent
    - orchestration
    - prompting
    - parallel
    related_skills:
    - subagent-driven-development
    - dispatching-parallel-agents
    - requesting-code-review
    - code-review
---

# Subagent Playbook

Distilled from how Anthropic actually specs Claude Code's built-in subagents
(Explore, Plan, general-purpose) and its autonomous-loop prompt. Patterns you
can copy into any dispatch.

## 1. Sandbox by contract, explicitly

Read-only roles (exploration, planning) get a hard, enumerated prohibition
list — not a vibe. Copy this block:

> **READ-ONLY — you are STRICTLY PROHIBITED from:**
> - Creating new files (no Write/touch/file creation of any kind)
> - Modifying existing files (no Edit operations)
> - Deleting, moving, or copying files
> - Creating temporary files anywhere, including /tmp
> - Redirect operators (`>`, `>>`, `|`), heredocs, or any command that changes system state
> - Bash limited to read-only: `ls`, `git status`, `git log`, `git diff`, `find`, `grep`, `cat`, `head`, `tail`

Back it with tool-level enforcement too (deny Edit/Write/etc. in the agent's
config) — the prompt is the contract, the tool list is the lock.

## 2. Match depth to the job — and say which

The Explore agent ships **two dispatch descriptions** and a declared
thoroughness knob:

- **Breadth role** ("Explore"): locate code, find where X is defined, sweep
  many files, return conclusions — explicitly *not* for review or auditing,
  because it reads excerpts, not whole files, and will miss content past its
  read window. Tell the dispatcher this limitation in the agent's own
  description so future-you doesn't misuse it.
- **Depth role** ("Plan"/architect): read thoroughly, trace code paths,
  consider trade-offs, produce step-by-step strategy.

Always pass a breadth knob with the dispatch — `"quick"` (one targeted
lookup), `"medium"` (moderate exploration), `"very thorough"` (multiple
locations and naming conventions).

**Required-output contract for planners:** end with a fixed artifact so
results compose, e.g. `### Critical Files for Implementation` — 3–5 paths.
A plan without named files is a vibe.

## 3. Verifier pattern: recall-biased, one vote each

When agents produce *findings* (review, security, research claims), verify
each candidate before it reaches the user:

- **PLAUSIBLE by default.** Never refute for being "speculative" when the
  runtime state is realistic: races, null on rare-but-reachable paths
  (error handlers, cold caches), falsy-zero, retry storms, boundary values.
- **REFUTED** only when constructivable from the code: quote the line that's
  factually wrong, show the type/invariant that makes it impossible, cite the
  guard that already handles it, or classify as pure style with no effect.
- Keep CONFIRMED + PLAUSIBLE. Drop only REFUTED.
- **Audit the metric before the claim.** A count finding ("N dead controls",
  "N broken links") inherits the precision of its measurement method — a
  click→text-diff-within-700ms heuristic will count every slow write as dead.
  When a child reports a suspiciously large N, read its detection method first;
  if the method is false-positive-prone, re-measure on a small sample before
  treating the count as a defect list.

This one pattern is the difference between an agent that hallucinates
"findings" and one that surfaces real ones.

## 3b. Verify implementation claims per named file

A worker's completion summary is a self-report — it can name files it never
touched and "pass" because the build was already green before it started.
Before accepting implementation work: diff against the pre-dispatch state
(`git diff --stat`, then per-path diff) and require EVERY named file to show
changes, then spot-check one claimed feature in the actual code. A green build
and a confident summary are not evidence; the diff is. When a child's
implementation diverges from the spec's wording (a different button label than
specified), adjudicate spec-vs-code before touching any test.

Run the build and suites YOURSELF against the tree before accepting any
completion claim — "build passes" is the most commonly fabricated line in a
child's summary; the same applies to "tests green".

## 3c. Scope read-only agents to the stable surface

When audits or reviews run while implementers are editing the same tree,
findings read from in-flight files are stale the moment the edit lands. Give
every read-only agent an explicit file scope that EXCLUDES the files live
writers own (name them in the brief and have the report mark them "in
flight"), or serialize the audit until the wave lands. Findings on half-edited
files waste the fix cycle and read as product defects when they are edit-state
artifacts.

## 3d. Dead children leave partial edits — continue, don't restart

A child killed mid-run (provider outage, timeout) leaves its half-applied edits
in the tree, sometimes syntactically broken (missing brace, duplicate import).
Before re-dispatching: diff the tree against the pre-dispatch state to see what
survived, then brief the replacement to CONTINUE the partial work — name the
edits already on disk and keep file ownership disjoint. Restarting blind spawns
a second agent that collides with the first one's leftovers. Run a fast build
before the suites: a transform error fails in seconds and names the broken
edit, where the suite driver would die mid-run and discard every verdict.

Repeated child deaths within the first minutes = provider flake, not bad
briefs. Stop burning dispatches and go hands-on. Before re-dispatching a fan-out
that died on a billing wall or outage, fail-fast probe the delegation model with
one trivial task and pin the batch to a model with confirmed working billing.

## 4. Efficiency instruction for search agents

Verbatim intent from the Explore spec: *"You are meant to be a fast agent. Be
smart about how you search — wherever possible spawn multiple parallel tool
calls for grepping and reading."* Add it to any search/exploration dispatch;
subagents default to cautious serial tool use unless told otherwise.

## 5. Autonomous-loop stewardship (self-reporting end-stops)

For long-running/polling dispatches, the leaked loop prompt's rules translate
directly:

- **Steward, not initiator.** Continue work the conversation already
  established; do not invent new work. When unsure whether something is
  "continuing established work" or "inventing new work," lean toward the
  former only when the transcript provides clear evidence. If you find
  yourself writing justifications for why an irreversible action is probably
  fine — that's the signal to wait.
- **Reversibility ladder:** reversible actions (local edits, running tests) —
  make your best call and proceed. Irreversible ones (push, delete, send,
  deploy) — keep waiting no matter how many cycles pass.
- **Silence is a result.** "Nothing actionable" is a complete answer — one
  line, no narrating what you checked. Three consecutive nothings → scale
  back to a minimal check and stop.
- **Prefer doing over describing.** "Run the tests" — don't say "you could
  run the tests."
- **Rebase, don't merge**, when continuing work someone else pushed to.

## 6. Multi-cycle audit → fix-wave loop

For "make the whole app meet a quality bar" missions: dispatch parallel
read-only auditors with DISJOINT lenses (visual design, UX/accessibility,
responsive/interaction), each returning ranked findings (P0/P1/P2) with concrete
measurements and marking deliberate design choices "by design" so fixers don't
churn them. Then one fix worker per disjoint file set, briefed with the exact
measurements. Verify each wave yourself (build + full suites + an end-to-end
probe of the riskiest change) and commit per wave; repeat with a fresh triad
until it finds no real defects. Two triad→fix→verify cycles is strong evidence;
score the rubric honestly and name what would confirm the remaining points
instead of claiming a clean sweep.

## 7. Live-system audit dispatch contract

When auditors probe a deployed app + live database (not just the repo):

- **Pin a structured findings schema in every brief** so batches compose:
  `severity, confidence (confirmed/likely/potential), file:line, evidence
  (probe output), root cause, minimal fix, touches_protected`. Free-text
  findings cannot be deduped, ranked, or turned into a fix plan mechanically.
- **Read-only probes against write-capable APIs still write.** A REST endpoint
  mis-specified as a read will happily INSERT. Probes must use read verbs /
  `select` only; if a probe must write to prove a hole, pin the created row id
  and delete + count-verify in the same script. After ANY audit against live
  data, sweep for probe residue (marker-named rows like `PROBE SHOULD NOT
  PERSIST` / `Qa *probe*`) and restore the baseline count before reporting —
  including residue left by earlier investigations in the same session.
- **Ingest large batches programmatically.** Truncated subagent summaries are
  saved whole to a file; extract the finding headers with one regex pass over
  the structured schema instead of paging through 50k chars by hand.
- **Claims carry `touches_protected` against the scope at dispatch time.** If
  the scope was revised mid-run, re-interpret the flag against the NEW scope
  before deciding what may be fixed.
