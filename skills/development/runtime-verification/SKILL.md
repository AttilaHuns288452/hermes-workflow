---
name: runtime-verification
description: 'Use before committing or shipping any nontrivial change that has a runtime
  surface: run the actual app, drive the changed flow end-to-end through its real
  interface, capture evidence, then probe around the change for what the author didn''t
  test. Produces runtime evidence, not green checks. Complements verification-before-completion
  (which gates completion claims with tsc/tests); this skill is about observing the
  running system. Skip for diffs that only touch tests, docs, or config with no behavior
  to observe.'
version: 1.0.0
author: Hermes Agent (distilled from Anthropic Claude Code /verify)
license: MIT
platforms:
- linux
- macos
- windows
metadata:
  hermes:
    tags:
    - verification
    - testing
    - evidence
    - runtime
    - quality-assurance
    related_skills:
    - verification-before-completion
    - test-driven-development
    - debug
    - requesting-code-review
---

# Runtime Verification

**Verification is runtime observation.** Build the app, run it, drive it to
where the changed code executes, and capture what you see. That capture is
your evidence. Nothing else is.

**Don't count tests or typecheck as verification.** Running them proves you
can run CI — not that the change works. Not as a warm-up, not "just to be
sure," not as a regression sweep. The time goes to running the app instead.
(A separate gate — `verification-before-completion` — still applies to
completion *claims*; this skill produces the *evidence*.)

**Don't import-and-call.** `import { foo } from './src/...'` then
`console.log(foo(x))` is a unit test you wrote. The app never ran. Whatever
calls `foo` in the real codebase ends at a CLI, a socket, or a window. Go there.

## 1. Find the change

The scope is the diff — full range, not just HEAD~1. In a git repo:

```bash
git log --oneline @{u}..        # count commits (if upstream set)
git diff @{u}.. --stat          # committed work vs upstream
git diff HEAD --stat            # uncommitted work
```

State the commit count. Repo but no diff → say so, stop. No repo → the scope
is whatever the user named; ask if they didn't.

**The diff is ground truth. Any description is a claim about it.** Read both.
If they disagree, that's a finding.

## 2. Find the surface

The surface is where a user — human or programmatic — meets the change.

| Change reaches | Surface        | You do                                           |
|----------------|----------------|--------------------------------------------------|
| CLI / TUI      | terminal       | type the command, capture the pane               |
| Server / API   | socket         | send the request, capture the response           |
| GUI / web      | pixels         | drive it (Playwright/xvfb), screenshot           |
| Library        | package export | sample code via the public API, not `./src/...`  |
| Prompt / agent | the agent      | run the agent, capture its behavior              |
| CI workflow    | Actions        | dispatch it, read the run                        |

Internal function? Not a surface — follow the caller until it ends at a row
above. No runtime surface at all (docs-only, types-only) → report
**SKIP — no runtime surface: (reason)**. Tests-only diff → SKIP.

Check the repo for existing run/verify helper scripts before cold-starting a
build — and **persist what you learn**: when you got the app running through a
non-obvious recipe, write it into the project's docs or an agent memory so the
next session skips the cold start.

## 3. Drive it

Smallest path that makes the changed code execute:

- Changed a flag? Run with it.
- Changed a handler? Hit that route.
- Changed error handling? Trigger the error.
- Changed a UI flow? Click the buttons — don't curl the API underneath the UI.

**Read your plan back before running.** If every step is build / typecheck /
run tests, you've planned a CI rerun, not a verification. Find a step that
reaches the surface or report BLOCKED.

**Destructive path?** If the change deletes, publishes, sends, or writes
outside the workspace and there's no dry-run or safe target, don't drive it
live — verify what you can around it and say which path you didn't exercise.

## 4. Push on it

The claim checking out is the first half, not the job. Probe *around* the
change at the same surface — what the author didn't test:

- **New flag/option** → empty value, passed twice, conflicting flag, typo'd (does the error name it?)
- **New handler/route** → wrong method, malformed body, missing required field, oversized payload
- **Changed error path** → the adjacent errors it didn't touch
- **Interactive** → interrupt mid-op, rapid-fire the key, Esc at the wrong moment, paste garbage
- **State/persistence** → do it twice, do it with stale state, do it in two sessions at once

Not a checklist — pick the ones the change points at. **A probe that finds
nothing is still a step**: "🔍 passed `--from ''` → clean `error: --from
requires a value`, exit 2." At least one 🔍 probe per verification; a report
with none is a happy-path replay.

## 5. Capture

Stdout, response bodies, screenshots. Captured output is evidence; memory
isn't. Unexpected output? Don't route around it — capture, note, decide
whether it's the change or the environment. Unrelated breakage is a finding,
not noise. Keep evidence inline in the report (pane captures, response
bodies) unless the reader shares your filesystem.

## 6. Report

```
## Verification: <one-line what changed>

**Verdict:** PASS | FAIL | BLOCKED | SKIP
**Claim:** <what it's supposed to do; note any claim/diff mismatch>
**Method:** <how you got a handle; what you launched>

### Steps (each step = one thing done to the RUNNING app → what it showed)
1. ✅/❌/⚠️/🔍 <action> → <observation> (+ evidence)
(🔍 marks a probe; build/install are setup, not steps; test runs don't belong)

### Findings
<Anything that made you pause, work around, or go "huh" — friction and
surprises count, not just bugs. Each probe gets a line even when it held.>
```

**Verdicts:**
- **PASS** — you ran the app; the change did what it should at its surface. Not: tests pass, build clean.
- **FAIL** — you ran it and it doesn't work, breaks something else, or claim and diff disagree. No partial pass.
- **BLOCKED** — couldn't reach an observable state; say exactly where. Not a verdict on the change.
- **SKIP** — no runtime surface exists. One line why.

**When in doubt, FAIL.** A false PASS ships broken code; a false FAIL costs
one more human look. Ambiguous output is FAIL with the raw capture attached.
