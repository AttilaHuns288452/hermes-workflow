---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always
---

# Verification Before Completion

## Overview

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Prior report says X works | X's artifacts found in the repo this turn | The report itself, a summary, a handoff |
| Feature integrated | Dependency installed + a real code path calls it | A UI screen or route that renders |
| Requirements met | Line-by-line checklist | Tests passing |
| Pushed/deployed | Deploy success for the pushed SHA + live artifact contains the new marker | "commit pushed", the PREVIOUS deploy passing, local build passing |

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!", etc.)
- About to commit/push/PR without verification
- Trusting agent success reports
- Relying on partial verification
- Thinking "just this once"
- Tired and wanting work over
- **ANY wording implying success without having run verification**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Regression tests (TDD Red-Green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Agent delegation:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## Inherited claims are hypotheses, not evidence

A prior report is a CLAIM. A previous turn's summary, a handoff, a task brief's
list of "already done" work, a delegated agent's report — none of it is evidence
until re-verified against the repo in THIS turn. A fabricated or mistaken report
is indistinguishable from a true one by reading it; only checking the codebase
separates them.

When a request says "the previous report claimed X works, now fix Y":

1. **Verify X exists before doing anything else.** Do not diagnose or fix defects
   in a system that was never built. The correct first deliverable is a
   ground-truth comparison, not a fix.
2. **Grep for each claimed integration's actual artifacts:**
   - Dependency: `cat package.json` + `ls node_modules/<pkg>`. A claimed library
     that is not installed was never used.
   - Service/config: the config file itself plus every `env` reference in source.
   - Feature: `grep -rn <symbol> src/` — a real code path, not a UI label or route
     name.
   - Tests: the test script in `package.json` and the test files on disk.
     "Tests pass" with no test runner installed is fabricated.
   - Mock markers: read the function BODY. A `// mock`, `// stub`, `// no real
     auth` comment beside a "login works" claim means the feature is simulated.
     A page that renders is not a feature that works.
3. **Correct the record plainly, in the same turn, before acting.** Name each
   claim and its measured reality in a table. Never build further work on a
   false premise, and never soften a fabricated claim into "partially done."
4. **Report every status in exactly one of five states** — *Implemented*, *Tested
   and passed*, *Tested and failed*, *Not tested*, *Blocked by external access*.
   "Verified" is not a state. This vocabulary exists so a fabricated "works" and
   a measured "works" cannot share a word.

```
✅ claim -> grep/install/probe -> table of claim vs reality -> fix what is real
❌ claim -> accept as premise -> fix "outstanding issues" in a system that does not exist
```

## A scan that errored is not a scan that passed

`cmd || echo CLEAN` reports CLEAN when `cmd` *failed*, not only when it found
nothing. A grep with a bad flag (`git grep --cached` is not a valid revision), a
missing file, or a permissions error exits nonzero and the `||` branch prints the
affirmative. The failure mode is silent and always reassuring.

- Check the exit code and stderr separately from the match count. Shell `grep`
  (only when a shell scan is unavoidable; prefer `search_files`) exits 0 on match,
  1 on no match, 2 on error — treat 2 as a hard failure, never as clean.
- Prove the scan can match at all before trusting a negative: point it at a known
  positive fixture once. A scan that returns clean on a seeded secret is broken.
- When two probes of the same bytes disagree (a combined pattern reports a hit,
  each branch reports none), do not pick the reassuring one. Re-fetch fresh bytes,
  hash them, and run both forms against that exact file before reporting either.
  The contradiction is the finding until it is resolved.

```
✅ if grep -q PAT file; then FOUND; else test $? -eq 1 && CLEAN || echo SCAN_ERROR; fi
❌ grep PAT file || echo CLEAN        # a grep crash also prints CLEAN
```

## A piped command's exit code is the LAST command's

`build | tail -1` prints the tail of the log and exits 0 even when the build
failed — the pipe's status is `tail`'s, and a green-looking summary line was
never produced. The failure sails through `&&` chains and gets shipped.

- Check build/lint/test exit codes UNMASKED: `cmd > /tmp/build.log 2>&1; echo "EXIT=$?"`, then grep the log. Never `cmd | tail` before a success claim.
- Green unit tests do not mean the app compiles: node-level tests skip JSX/TS
  transforms and bundler resolution. Run the BUNDLE build as its own verified
  step before any "builds clean" claim.

```
✅ node build.js > /tmp/build.log 2>&1; echo "BUILD_EXIT=$?"
❌ node build.js | tail -1 && npm test    # tail hides the build failure
```

## Diagnose upstream failures with safe diagnostics, not guesses

When an external API fails, add a diagnostic that returns the numeric status, the
provider's stable `code`, and the top-level KEY NAMES of the body — never body
values, never the credential. This distinguishes `invalid_api_key` (your input)
from `upstream_unavailable` (their outage) from a shape mismatch (your parser) in
one deploy instead of a retry loop. Pair it with the provider's free,
non-consuming health/usage endpoint to prove the credential is valid, then you can
state the fault location as measured rather than assumed.

## Multi-repo / multi-surface shipping

When one feature spans several repos or apps, each one gets its OWN complete evidence chain before any overall claim:

1. Per repo: `git status` clean and local `HEAD` equals `origin/main`. A commit that exists only locally is not shipped.
2. Poll the deployment matching THAT commit's SHA (`gh api repos/OWNER/REPO/commits/$SHA/status`) — `deployments?per_page=1` can return the previous deploy and its success is meaningless for the new push. `pending` or `failure` is not shipped; a failed build can succeed on an empty-commit retry, so retry before deep debugging.
3. Fetch the live site cache-busted and grep the BUILT BUNDLE for the new marker. Check lazy-loaded chunks too (build output named like `shells-*.js`), not just the entry chunk — a feature behind a route lives in a lazy chunk and the entry grep false-fails.
4. Report one evidence line per repo/app. "Both apps are done" with a single evidence chain is exactly the claim this section exists to prevent.

## Visual reports are hypotheses, not defects

A vision model's finding ("blank bands", "text overlaps", "wrong colour", "the
stars render wrong") is a CLAIM with the same standing as any other report.
Screenshots are lossy evidence: full-page captures stitch fixed headers into the
middle of the frame and invent gaps that do not exist in the DOM, small text and
low-chroma colours get misread, and mid-animation frames read as misplaced
artwork. Never change code that is already correct on the strength of one.

1. Adjudicate in the DOM first: element geometry (`getBoundingClientRect`;
   negative overlap means no overlap), computed styles (`display`, `color`,
   `fontSize`), or a pixel probe. Report the measurement alongside the ruling.
2. "It looks zoomed in / bigger than the other screen" is measured, not
   eyeballed: compare `getComputedStyle(el).fontSize` on equivalent elements in
   BOTH surfaces and state both numbers before touching anything. Then trace the
   token chain — theme config → CSS variables → any scale multiplier — instead of
   hand-tuning individual rules; a base token set high AND multiplied by a UI
   scale variable inflates every utility class at once, and fixing one class
   leaves the rest oversized.
3. Text clipping is not overlap. A line clamp plus a `min-height` taller than the
   clamped line count lets extra lines paint inside the box (the clamp hides
   overflow, not paint), which reads as text colliding with the row below. Pin the
   box to exactly the clamped line count and assert the element's measured height.

```
✅ vision says X -> measure geometry/computed style -> confirm or dismiss with numbers
❌ vision says X -> patch the code -> measure later (or never)
```

## Confirm the artifact you verified is the artifact you built

A change that is "in the build" can still be invisible: the build command and the
thing you are testing may write and serve different output directories. Before
declaring a patch did not land (or that a UI is unchanged), confirm the served
directory is the one the build wrote, rebuild the target the server actually
serves, and re-probe with a cache-buster. Rebuild both targets when the project
has more than one (e.g. a static export for one host and a framework build for
another). A stale "the change is missing" report wastes a whole debugging round
on code that was correct.

## A failing check is itself a claim

A check script encodes an expectation from the day it was written. When it fails, confirm the
expectation is still the contract before changing the data it measures. A ledger audit that
demanded "zero realized PnL" began failing the moment the first real close landed; the correct
fix was the checker, not the ledger. Read the check's assumption, compare it to the documented
claim (README, spec, ticket), and only then decide which side is stale. A checker that cannot
express the current expected state is the defect, and silencing it by editing the data destroys
the only evidence you had.

```
✅ check fails -> read its assumption vs the documented contract -> fix the stale check or the stale data, then re-run
❌ check fails -> change the measured data until the old expectation passes
```

## When To Apply

**ALWAYS before:**
- ANY variation of success/completion claims
- ANY expression of satisfaction
- ANY positive statement about work state
- Committing, PR creation, task completion
- Moving to next task
- Delegating to agents

**Rule applies to:**
- Exact phrases
- Paraphrases and synonyms
- Implications of success
- ANY communication suggesting completion/correctness
