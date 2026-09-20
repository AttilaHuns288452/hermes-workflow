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
- **REFUTED** only when constructible from the code: quote the line that's
  factually wrong, show the type/invariant that makes it impossible, cite the
  guard that already handles it, or classify as pure style with no effect.
- Keep CONFIRMED + PLAUSIBLE. Drop only REFUTED.

This one pattern is the difference between an agent that hallucinates
"findings" and one that surfaces real ones.

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
