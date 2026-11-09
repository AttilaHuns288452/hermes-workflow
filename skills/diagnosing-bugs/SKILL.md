---
name: diagnosing-bugs
description: Diagnosis loop for hard bugs and performance regressions. Use when the user says "diagnose"/"debug this", or reports something broken/throwing/failing/slow.
---

# Diagnosing Bugs

A discipline for hard bugs. Skip phases only when explicitly justified.

## Match evidence-gathering to the ask

The feedback loop is a means, not the deliverable. When the user says "fix this error" and the cause is already located (a named file/symbol, a clear code or log-level repro), execute the fix and verify it directly — do not substitute a screenshot / visual-investigation loop for the fix. Visual artifacts are for when the UI itself is the unknown (layout, render, state you cannot see in code or logs). Emitting diagnosis artifacts the user did not ask for while the fix is at hand reads as stalling. Err toward the smallest evidence that proves the fix landed.

When exploring the codebase, read `CONTEXT.md` (if it exists) to get a clear mental model of the relevant modules, and check ADRs in the area you're touching.

## Redact

This skill has you show commands, outputs and captured artifacts. **Redact every secret first**: write `<REDACTED>` in its place. Build loops against env vars, so the credential stays in the environment rather than in what you show. Captured artifacts carry auth headers: quote only the lines that carry the signal.

If the redacted output is not enough to diagnose the bug, say so and ask the user.

## Phase 1: Build a feedback loop

**This is the skill.** Everything else is mechanical. If you have a **tight** pass/fail signal for the bug (one that goes red on _this_ bug), you will find the cause; bisection, hypothesis-testing, and instrumentation all just consume it. If you don't have one, no amount of staring at code will save you.

Spend disproportionate effort here. **Be aggressive. Be creative. Refuse to give up.**

### Ways to construct one, in roughly this order

1. **Failing test** at whatever seam reaches the bug: unit, integration, e2e.
2. **Curl / HTTP script** against a running dev server.
3. **CLI invocation** with a fixture input, diffing stdout against a known-good snapshot.
4. **Headless browser script** (Playwright / Puppeteer) that drives the UI and asserts on DOM/console/network.
5. **Replay a captured trace.** Save a real network request / payload / event log to disk; replay it through the code path in isolation.
6. **Throwaway harness.** Spin up a minimal subset of the system (one service, mocked deps) that exercises the bug code path with a single function call.
7. **Property / fuzz loop.** If the bug is "sometimes wrong output", run 1000 random inputs and look for the failure mode.
8. **Bisection harness.** If the bug appeared between two known states (commit, dataset, version), automate "boot at state X, check, repeat" so you can `git bisect run` it.
9. **Differential loop.** Run the same input through old-version vs new-version (or two configs) and diff outputs.
10. **HITL bash script.** Last resort. If a human must click, drive _them_ with `scripts/hitl-loop.template.sh` so the loop is still structured. Captured output feeds back to you.

Build the right feedback loop, and the bug is 90% fixed.

**Place reusable loops in the repo** as checked-in scripts (a `qa/` or test
file). `/tmp` and scratch dirs get pruned between sessions, and rebuilding a
lost harness costs more than committing it.

### Tighten the loop

Treat the loop as a product. Once you have _a_ loop, **tighten** it:

- Can I make it faster? (Cache setup, skip unrelated init, narrow the test scope.)
- Can I make the signal sharper? (Assert on the specific symptom, not "didn't crash".)
- Can I make it more deterministic? (Pin time, seed RNG, isolate filesystem, freeze network.)

A 30-second flaky loop is barely better than no loop; a 2-second deterministic one is tight, a debugging superpower.

### Non-deterministic bugs

The goal is not a clean repro but a **higher reproduction rate**. Loop the trigger 100×, parallelise, add stress, narrow timing windows, inject sleeps. A 50%-flake bug is debuggable; 1% is not, so keep raising the rate until it's debuggable.

### When you genuinely cannot build a loop

Stop and say so explicitly. List what you tried. Ask the user for: (a) access to whatever environment reproduces it, (b) a redacted captured artifact (HAR file, log dump, core dump, screen recording with timestamps), or (c) permission to add temporary production instrumentation. Do **not** proceed to hypothesise without a loop.

### Completion criterion: a tight loop that goes red

Phase 1 is done when the loop is **tight** and **red-capable**: you can name **one command** (a script path, a test invocation, a curl) that you have **already run at least once** (show the invocation and its output, redacted), and that is:

- [ ] **Red-capable**: it drives the actual bug code path and asserts the **user's exact symptom**, so it can go red on this bug and green once fixed. Not "runs without erroring"; it must be able to _catch this specific bug_.
- [ ] **Deterministic**: same verdict every run (flaky bugs: a pinned, high reproduction rate, per above).
- [ ] **Fast**: seconds, not minutes.
- [ ] **Agent-runnable**: you can run it unattended; a human in the loop only via `scripts/hitl-loop.template.sh`.

If you catch yourself reading code to build a theory before this command exists, **stop: jumping straight to a hypothesis is the exact failure this skill prevents.** No red-capable command, no Phase 2.

## Phase 2: Reproduce + minimise

Run the loop. Watch it go red as the bug appears.

Confirm:

- [ ] The loop produces the failure mode the **user** described, not a different failure that happens to be nearby. Wrong bug = wrong fix.
- [ ] The failure is reproducible across multiple runs (or, for non-deterministic bugs, reproducible at a high enough rate to debug against).
- [ ] You have captured the exact symptom (error message, wrong output, slow timing) so later phases can verify the fix actually addresses it.

### Minimise

Once it's red, shrink the repro to the **smallest scenario that still goes red**. Cut inputs, callers, config, data, and steps **one at a time**, re-running the loop after each cut, and keep only what's load-bearing for the failure.

Why bother: a minimal repro shrinks the hypothesis space in Phase 3 (fewer moving parts left to suspect) and becomes the clean regression test in Phase 5.

Done when **every remaining element is load-bearing**: removing any one of them makes the loop go green.

Do not proceed until you have reproduced **and** minimised.

## Interpreting evidence without fooling yourself

A confident wrong cause is worse than a slow right one. These three rules protect
the gap between "the log shows X" and "X is the cause".

**Count the suspect signal across the working state before naming it the cause.**
When one version or state is broken and another works, grep the same suspect line
across *every surviving log of the working state* and count occurrences. A warning
that also appears in the working build, at any count, is **noise, not the bug** —
it is a pre-existing condition the working build tolerated. The cause is what is
unique to the broken state, or what is *absent* there (an expected success marker
that never fires, e.g. a window or connection that was created on every healthy
run and zero times on the failing one). Name that differentiator, not the loudest
line near the crash. Correlating the most prominent warning with the failure is
the single easiest way to ship a confidently wrong root cause.

**When two reports or audits contradict on a severity claim, the code settles it.**
Neither the more alarming nor the more recent wins. Read the exact lines both
sides cite and decide from the real control flow, then correct whichever artifact
carries the wrong claim. Two documents in the repo that disagree on whether a
condition is safe or fatal are themselves a defect: fix them in the same pass.

**Verify audit findings against the live tree before editing.** A long-running
audit reports against a snapshot. Check each cited line against the current file
first, and re-run the gates to learn the real baseline before trusting any count
the audit quotes — findings may already be fixed, and acting on stale ones wastes
the pass or reintroduces old code. Which parts of a finding are already resolved
determines what is actually left to do.

## Phase 3: Hypothesise

Generate **3–5 ranked hypotheses** before testing any of them. Single-hypothesis generation anchors on the first plausible idea.

Each hypothesis must be **falsifiable**: state the prediction it makes.

> Format: "If <X> is the cause, then <changing Y> will make the bug disappear / <changing Z> will make it worse."

If you cannot state the prediction, the hypothesis is a vibe: discard or sharpen it.

**Show the ranked list to the user before testing.** They often have domain knowledge that re-ranks instantly ("we just deployed a change to #3"), or know hypotheses they've already ruled out. Cheap checkpoint, big time saver. Don't block on it; proceed with your ranking if the user is AFK.

## Phase 4: Instrument

Each probe must map to a specific prediction from Phase 3. **Change one variable at a time.**

Tool preference:

1. **Debugger / REPL inspection** if the env supports it. One breakpoint beats ten logs.
2. **Targeted logs** at the boundaries that distinguish hypotheses.
3. Never "log everything and grep".

**Tag every debug log** with a unique prefix, e.g. `[DEBUG-a4f2]`. Cleanup at the end becomes a single grep. Untagged logs survive; tagged logs die.

**Perf branch.** For performance regressions, logs are usually wrong. Instead: establish a baseline measurement (timing harness, `performance.now()`, profiler, query plan), then bisect. Measure first, fix second.

## Phase 5: Fix + regression test

Write the regression test **before the fix**, but only if there is a **correct seam** for it.

A correct seam is one where the test exercises the **real bug pattern** as it occurs at the call site. If the only available seam is too shallow (single-caller test when the bug needs multiple callers, unit test that can't replicate the chain that triggered the bug), a regression test there gives false confidence.

**If no correct seam exists, that itself is the finding.** Note it. The codebase architecture is preventing the bug from being locked down. Flag this for the next phase.

If a correct seam exists:

1. Turn the minimised repro into a failing test at that seam.
2. Watch it fail. If you forced the red by mutating code or a fixture, `diff` against a pristine copy to prove the mutation landed before you trust it.
3. Apply the fix.
4. Watch it pass.
5. Re-run the Phase 1 feedback loop against the original (un-minimised) scenario.

## Failure signatures worth checking first

Cheap checks that outrank hypothesis generation for common web-UI symptoms:

- **Silent hang / page dies with no console error while opening a view:**
  check for mutual recursion across layers — a content loader calling the
  shell/chrome "open" function, which calls back into the content loader.
  Grep the call sites of BOTH directions before reading whole files; the
  cycle is invisible to fuzzy search when the two calls sit in different
  modules, and the stack overflows or hangs without a useful trace.
- **`X is not defined` in the console:** check the Network tab for a 404'd
  `<script src>` first — a wrong path prefix surfaces much later as an
  undefined global at first call, far from the real cause. Fix the path;
  the symbol was never missing.
- **A style "does not apply":** confirm the selector against the live DOM's
  actual class list before editing the rule — a selector naming classes the
  elements do not carry (wrapper class vs element class) silently matches
  nothing, and fuzzy search on the stylesheet will not reveal it.
- **A utility class IS in the built CSS but the computed style shows another
  value:** unlayered legacy CSS beats `@layer` utilities at ANY specificity, so
  an old stylesheet rule silently wins. Find the winner with a live rule walk
  (for every rule in `document.styleSheets`, `el.matches(rule.selectorText)`
  and print the rules that set the property), then fix at the owning layer:
  drop the legacy class name from the utility-authored element or bring the
  legacy rule into a layer — never add `!important` or arbitrary variants to
  out-shout the cascade. A ragged control row (button height ≠ inputs' height)
  is this signature in mild form: a legacy `button`/`.btn` fixed `height` beats
  the `h-*` utility, so measure every control's rect before redesigning.
- **`[object Object]` (or garbled text) where a rail/list should show text:** a
  producer of the shared data structure broke the declared format and the
  consumer coerces (`String(x)`). Grep every PRODUCER of that structure and fix
  the ones that drifted; making the consumer type-aware hides the drift and
  grows per-type branches.
- **Columns swapped / content squeezed at desktop while mobile looks right:** measure each grid child's rect against the container's computed `gridTemplateColumns` at the broken breakpoint. Auto-placement is DOM order, so a one-sided `order-*` pair puts the unclassed child (order 0) ahead of any positive order. Fix = explicit order on BOTH children at both breakpoints (details in the `frontend-patterns` skill, Tailwind defect pitfalls reference).
- **Horizontal overflow on a responsive page:** measure `scrollWidth` vs the
  viewport at the target width and hide suspects one at a time. A `1fr` grid
  track is `minmax(auto,1fr)` and floors at its content's min-content width,
  and `overflow:auto` scrollers clamp their own size but not their
  contribution to the track — `min-width:0` (or `overflow:hidden`) on the
  the grid item is the fix.
- **A degraded/fallback path fires with no error reason:** a deterministic guard
  (scope gate, coverage gate, out-of-scope classifier) fired BEFORE the
  subsystem you are debugging — provider and protocol failures always populate
  a reason field, an empty one means the short-circuit came from upstream. Read
  the guard's conditions before instrumenting the subsystem.
- **A field exists in raw data but vanishes in validated/normalized output:**
  validators that rebuild objects field-by-field (allowlist shapes) silently
  strip additions. Grep the validator/rebuilder for the field before suspecting
  the producer or the transport.
- **The flow works in the app but the user's external tool rejects it (payment
  app, bank app, mail client): check the environment mode before instrumenting
  code.** Sandbox/test credentials and provider test modes (test key prefixes,
  `provider_mode='test'`, staging endpoints) mint artifacts that real-world
  tools legitimately refuse — an app-side success proves only that the sandbox
  accepted it. Confirm which mode actually served the request from the
  provider's own record of it (e.g. the created intent's `livemode` flag), and
  switch the mode/keys before suspecting the code path.
- **A linter or type-checker emits resolution errors for nearly every import
  (`Unknown require`, `cannot find module`, `Key 'X' not found`) across the whole
  tree:** check the project's own documented invocation of that tool before
  blaming a stale generated artifact or a missing config. A dropped required flag
  (`--sourcemap=`, `--project`, `--baseUrl`, `--definitions=`) looks exactly like
  broken resolution and yields hundreds of bogus diagnostics at once. A real
  resolution failure is usually narrow (one or two modules); an all-tree wall is
  almost always the command, not the code. Read the documented command first —
  it is often already in the repo's README or QA notes.

## Phase 6: Cleanup

Required before declaring done:

- [ ] Original repro no longer reproduces (re-run the Phase 1 loop)
- [ ] Regression test passes (or absence of seam is documented)
- [ ] All `[DEBUG-...]` instrumentation removed (`grep` the prefix)
- [ ] Throwaway prototypes deleted (or moved to a clearly-marked debug location)
- [ ] The hypothesis that turned out correct is stated in the commit / PR message, so the next debugger learns
