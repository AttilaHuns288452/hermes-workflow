---
name: nextjs-supabase-e2e-qa
description: End-to-end verification of Next.js + Supabase apps with Playwright. Use when verifying swarm-built features, pre-deploy QA loops, or debugging why an E2E script "submits" but nothing lands in the DB. Covers Radix Select automation traps, Supabase session-token extraction, direct PostgREST verification, migration-application paths, and poll-based script structure.
---

# Next.js + Supabase E2E QA

## When to Use

- Verifying features built by subagents (swarm) before commit/deploy
- Any "fix loop" request: build → verify → fix → re-verify
- E2E scripts that pass their own checks but produce no DB rows
- Pre-deploy sanity of auth-gated pages

## The Loop

1. `npx tsc --noEmit` + `npm run build` (your verification, not the subagent's claim)
2. Dev server: tree-kill orphans first (`taskkill /PID <pid> /T /F`), confirm port free, start, **warm it** (logged-in playwright pass over every route — Turbopack compiles action chunks on first hit; cold first-run can take 30s+ and look like a hang)
3. Run poll-based playwright script (see structure below)
4. Cross-check DB state directly (PostgREST + user JWT — see references/playwright-supabase-notes.md) — UI says PASS ≠ row exists
5. Vision QA on screenshots (mimo via vision_analyze), ECC reviewers on the diff
6. Fix, rebuild, redeploy

## Pitfalls (all hit in real sessions)

1. **Radix Select (shadcn) — never automate via the hidden native select.** `<Select name="x">` renders a hidden `<select name="x">` for form submission only; clicking it does nothing. Click the visible trigger (`getByRole("combobox")`), then click `[role="option"]`. And **never press Escape to close a listbox — Escape closes the whole Radix Dialog**, silently "submitting" the check without firing the form submit (dialog disappears, zero server-action traces).
2. **Force-click on a covered element lands on the overlay.** `click({force: true})` bypasses actionability checks but the click still hits whatever is topmost (open listbox portal) → nothing happens. Close the overlay properly instead.
3. **Supabase session lives in a cookie, not localStorage** (supabase-ssr). Extract the JWT from `sb-<ref>-auth-token` (value is `base64-` + base64url JSON) → use it as `Authorization: Bearer` on PostgREST to verify rows directly. Full snippet in references.
4. **No server-action trace = form never submitted.** Dev log shows `ƒ createTransaction(...)` per action call. Grep the log before blaming the action; a missing trace means the click/submit path is broken.
5. **`prompt()` dialogs in headless**: register `page.once("dialog", d => d.accept(v))` BEFORE the click; a dismissed prompt returns null; accepted garbage can create probe data (an entity literally named "ss" once) — when the UI shows unexpected rows/buttons, query the DB before trusting the UI.
6. **Live schema ≠ repo migrations.** The live Supabase DB may have columns the repo migrations lack (e.g. `is_active`). Check live schema via PostgREST `information_schema.columns` (it IS exposed) before writing queries/verification.
7. **Migration application to live DB**: service role key is NOT the postgres DB password (pooler auth fails), pg-meta `/pg/query` is removed ("requested path is invalid"), PostgREST can't do DDL. Working paths: SQL Editor (paste), DB password via pooler (`aws-0-<region>.pooler.supabase.com:6543`, user `postgres.<ref>`), or Management API with a PAT (`sbp_...`). Verify columns after applying.
8. **Poll, don't sleep.** Fixed sleeps race Turbopack cold-compile; use a `poll(fn, timeout, step)` helper and assert on visible text, not elapsed time.
9. **`innerText` reflects CSS `text-transform`.** A label styled `uppercase` renders `STOCK VALUE` — `includes("Stock Value")` never matches. A check can PASS while the DB is empty (empty-state fallback text matched) and FAIL after seeding real data (fallback gone, case mismatch exposed). Always `.toLowerCase().includes(...)` both sides.
10. **`page.evaluate` has no closures.** Outer variables (`token`, `key`) are `undefined` inside the evaluated function — silent auth failures (`Bearer undefined` → 401). Pass every value explicitly as function args.
11. **DOM text ≠ source file = stale dev bundle, not an app bug.** After many edits on a long-running `next dev`, served JSX can diverge (`</svg> ss</button>` where source says `Create business entity`); server-action signature changes mid-run hang client calls on a stale registry. Dump `el.outerHTML` and diff before debugging the "bug"; fix is a full tree-kill restart (`taskkill /PID <pid> /T /F` + verify port free — see `debugging-spawned-processes` §4b). A "fresh" server logging `using available port 3001 instead` means you're still hitting the orphan on 3000.
12. **Locator "resolved but never actionable" = check for the Next.js dev error overlay.** The pattern: `locator resolved to <button>…</button>` + `attempting click action` + `click action done` repeated, then 30s timeout. A `[role="dialog"]` containing `data-nextjs-dialog-sizer` = the dev error overlay (console hydration/runtime errors), which sits above the page and eats clicks. It also shows as a red "N Issues" badge with a close icon in screenshots — grep source before hunting it as app UI; it's dev-only. Fix the underlying error and clicks work again. Catch errors early: `p.on("console", m => { if (m.type()==="error") errs.push(m.text()); })` + `p.on("pageerror", ...)`.
13. **Hydration error pattern to watch in swarm output: `<div>` inside `<p>`.** Badges rendered inside `<p className="font-medium">` produce `In HTML, <div> cannot be a descendant of <p>` → dev overlay opens, prod would hit the error boundary. Fix: wrap name + badges in a `<div className="flex flex-wrap items-center gap-2">`. Grep new card components for `Badge` nested inside `<p>` before E2E.
14. **Click whose handler re-renders the list → `click({ force: true, noWaitAfter: true })`.** Opening a dialog re-renders rows; playwright's post-click re-resolution hangs ("click action done" ×N, still waiting). Force+noWaitAfter is correct when nothing actually covers the button (verify with `elementFromPoint` at the button center — returns the button = no overlay). This is distinct from pitfall 2: force-click is WRONG when an overlay is on top, RIGHT when the hang is the post-click check.
15. **Card-scoped locators — `first()` hits the wrong card.** Lists sorted by name + seeded items mean `.first()` targets the alphabetically-first row (false-passing badge checks). Scope to the item you created: `page.locator("main").getByText(itemName).locator("xpath=ancestor::div[.//button[contains(.,'Stock')]][1]")`. Also: **getByText under an XPath-root locator is flaky** (resolves but never actionable) — the text-first chain above works; an XPath-root chain of the same target doesn't. And badge checks after mutations need `poll()`, not instant `isVisible()` (re-fetch re-render races).
16. **Per-feature skip mode, not all-or-nothing.** Preflight each feature's schema separately (`information_schema.columns` for loans vs inventory columns) — run what's testable without the pending migration (status tiers computed from existing columns) and SKIP only what needs it. Script reports `PASS/FAIL — SKIP — apply <migration>` per section.
17. **Server actions: never send explicit `null` for a not-yet-migrated column.** `note: note || null` makes supabase-js send `null` → `Could not find the 'note' column` schema-cache error → every insert fails pre-migration. Send the key only when present: `const m = {...}; if (note) m.note = note;` — the feature then works before AND after the migration. The dialog's inline error line is what surfaces this — keep it; it makes E2E failures diagnosable.

## Script Structure (proven shape)

```js
const poll = async (fn, timeout = 20000, step = 500) => { /* retry loop */ };
const check = (name, ok, extra) => results.push(...);       // collect, print at end
const step = (s) => console.log("[step]", s);               // trace where it died
// login → preflight (schema guard via information_schema → graceful SKIP if migrations missing)
// → interact (combobox trigger click, keyboard-select, no Escape) → DB cross-check
// → screenshot at failure points → print PASS/FAIL table, exit 1 on FAIL
```

Keep scripts in the repo (QA harness is repeatable); name them `verify-*.cjs`, run with `node`, launch `chromium.launch({ channel: "chrome" })` to reuse installed Chrome (no browser download).

## References

- `references/playwright-supabase-notes.md` — copy-paste snippets: JWT from cookie, schema guard, Radix-safe select sequence.
