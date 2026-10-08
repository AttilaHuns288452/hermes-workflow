# Multi-Angle Diff Review Mode (imported technique)

> Source: Claude Code's `code-review` skill (captured 2026-09, `system_prompts_leaks/Anthropic/claude-code/skills/code-review/SKILL.md`). Use this mode when the review goal is **finding real bugs** in a diff. The parent skill's two-axis mode (Standards/Spec) remains the default for "does this match the spec/standards" reviews; this mode answers "what is broken here".

## When to use which mode

| Goal | Mode |
|---|---|
| "Review since X" / spec conformance / standards conformance | Parent two-axis mode (Standards + Spec) |
| "Find the bugs in this diff/PR" / pre-merge correctness hunt | **This mode** |
| User asks for both | Run both; correctness findings outrank cleanup findings |

## Phase 0 — Pin the diff

`git diff @{upstream}...HEAD` (or `main...HEAD` / `HEAD~1` if no upstream). If uncommitted changes exist or the range diff is empty, also `git diff HEAD`. A PR number/branch/path argument replaces the target. Confirm the ref resolves and the diff is non-empty BEFORE analyzing — fail here, not mid-review.

## Phase 1 — Candidate angles (run each; batch as parallel subagents when 3+ independent, else sequential inline)

Each angle surfaces up to 6 candidates: `file`, `line`, one-line `summary`, concrete `failure_scenario`.

**Correctness angles:**

- **A — Line-by-line scan.** Read every hunk, then the enclosing function of each hunk (bugs in unchanged lines of a touched function are in scope). Per line: what input/state/timing/platform makes this wrong? Hunt: inverted conditions, off-by-one, null deref, missing `await`, falsy-zero checks, wrong-variable copy-paste, swallowed errors in catch, unescaped regex metachars.
- **B — Removed-behavior audit.** For every DELETED/replaced line, name the invariant it enforced, then search the new code for where that invariant is re-established. Not found → candidate (removed guard, dropped error path, narrowed validation, deleted test covering a real case).
- **C — Cross-file trace.** For each changed function, find its callers (grep the symbol) and check whether the change breaks any call site: new precondition, changed return shape, new exception, ordering dependency. Also check callees against parallel changes in the same diff.

**Cleanup angles** (same output shape; `failure_scenario` states the concrete cost instead of a crash):

- **Reuse** — new code re-implementing an existing helper; name the helper.
- **Simplification** — redundant/derivable state, copy-paste variants, deep nesting, dead code; name the simpler form.
- **Efficiency** — repeated I/O, independent ops run sequentially, blocking work on hot paths, closure-captured long-lived objects; name the cheaper alternative.
- **Altitude** — fixes at the wrong depth: special cases layered on shared infrastructure where a deeper general fix belongs.

**Conventions angle:** if `AGENTS.md`/`CONTRIBUTING.md`/`CODING_STANDARDS.md` govern the changed code, flag only violations where you can quote the exact rule AND the exact offending line — no style vibes.

**Recall rule:** pass every candidate with a nameable failure scenario through to verification. Finders that silently drop half-believed candidates are the dominant cause of misses.

## Phase 2 — One-vote verification (recall-biased)

Dedup near-duplicates first (same defect + location + reason → keep one). Then one verifier per candidate returns exactly: **CONFIRMED / PLAUSIBLE / REFUTED**.

- **PLAUSIBLE by default** for realistic-but-uncertain states: races, rare-but-reachable nil paths (error handlers, cold cache, missing optional field), falsy-zero, boundary off-by-ones the code does not exclude, retry storms, partial failures.
- **REFUTED only when constructible from the code:** factually wrong (quote the line), provably impossible (show the type/constant/invariant), already handled in this diff (cite the guard), or pure style with no observable effect.

Keep CONFIRMED + PLAUSIBLE. Drop REFUTED.

## Output

JSON array, max 10 findings, ranked most-severe first; correctness outranks cleanup when cutting:

```json
[
  {"file": "path/to/file.ext", "line": 123, "summary": "one-sentence bug statement", "failure_scenario": "concrete inputs/state → wrong output/crash"}
]
```

Nothing survives → `[]`. Say so plainly; an empty result after real verification is a valid review outcome.
