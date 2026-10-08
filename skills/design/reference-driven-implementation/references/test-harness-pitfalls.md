# Test-harness pitfalls (agent-run Playwright suites)

Rules for writing/maintaining the QA scripts that verify a shipped SPA against a live Supabase-style backend.

## Assertions

- **Regression guards assert ABSENCE.** When a feature was removed by user demand, the suite must fail if it reappears (scan page text + routes for the banned strings). A check asserting the removed feature EXISTS is a bug in the check.
- **Scope text assertions to the region that can contain the string.** Whole-page `includes()` matches history sections and other cards; split textContent on a section header and assert within the relevant part (e.g. the pending list only, not the approved-history list).
- **Locators must match visible copy exactly.** Role/name substring matching treats `Male` as matching `Female` — use `text-is`/`exact`. Prefer `getByLabel` over positional `input` fills (restyling moves fields). CSS `text-transform` does not affect `textContent` but DOES affect `innerText` — pick one deliberately.
- **Submit-button selectors like `form button).last()` break whenever the form grows a trailing button** (a "Log in" link inside the form silently becomes the clicked target). Click the submit button by its own label text.
- **Never bulk-regex a suite without context review.** A credential/selector fix aimed at registered-user steps also rewrites demo-account steps that share the pattern. Patch by surrounding context, then grep the file for BOTH variants to confirm each landed where intended.

## Test data

- **Dynamic dates beat cleanup for unique constraints.** One leftover confirmed row (same date/slot) blocks every rerun under a DB uniqueness guard. Create with `today + N days` per suite + a varying slot; ALSO purge created entities before each run — belt and braces.
- **DB-truth probes must authenticate as the actor whose data they assert on.** An anon client under RLS sees zero rows and false-fails "latest row" checks. Sign the probe client in.
- **Security probes must use the role named in the check.** "Patient cannot self-confirm" tested with a doctor session tests nothing — the update succeeds and the check fails for the wrong reason.

## Triage

- **Suite crash ≠ app bug.** Before patching app code: does the assertion's target still exist (the UI may have been intentionally redesigned)? Reproduce the flow by hand once. Most "broken app" suite crashes during a redesign are stale locators or stale expectations.
- Keep suites in the repo, not /tmp; update them in the same commit as intentional behavior changes so a red run always means a real regression.