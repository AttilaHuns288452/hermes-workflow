# E2E Verification Playbook — Next.js + Supabase (Playwright)

Hard-won from a full-day CashFlow OS verification session. When the UI "doesn't
work" but the code looks right, this is the order to attack it.

## Ground-truth hierarchy

1. **Dev-server log** — `next dev` prints every server action:
   `POST /transactions 200 ... └─ ƒ createTransaction({...}) in 341ms src/features/transactions/actions.ts`
   - Action in log + no DB row → server-side error the UI swallowed (action returned `{error}` and the handler ignored it).
   - NO action in log → the client handler never ran (Escape closed the dialog, click landed on an overlay, validation returned early). Client bug, not server bug.
   - Tail the log with `process(action="log")`; grep for the action name when the window is deep.
2. **PostgREST direct probes** — definitive DB state. See cookie decode below.
3. **UI text** — last resort: flaky selectors, Radix animations, HMR staleness.

## Getting the user JWT for PostgREST probes

`@supabase/ssr` stores the session in a **cookie**, not localStorage
(`localStorage` keys can be completely empty while logged in):

```
sb-<project-ref>-auth-token=base64-<base64url-encoded JSON>
```

Decode (from a Playwright page context):

```js
const token = await page.evaluate(() => {
  const m = document.cookie.match(/sb-[a-z0-9-]+-auth-token=([^;]+)/);
  const v = m[1].replace(/^base64-/, "").replace(/-/g, "+").replace(/_/g, "/");
  return JSON.parse(atob(v)).access_token;
});
```

Then any REST call works — insert (201), delete (204), select — with
`{ apikey: NEXT_PUBLIC_SUPABASE_ANON_KEY, Authorization: "Bearer " + token }`.
Use this to prove/refute rows when the UI says one thing and you suspect another.

## Live schema vs repo migrations

Live Supabase schema is frequently **AHEAD** of `supabase/migrations/`
(columns/policies added via SQL Editor): e.g. `entities.is_active` exists live
but not in `001_schema.sql`. Never conclude "this insert should work" from
migration files — probe `?select=*&limit=1` via PostgREST (or the OpenAPI root)
first. A query filtering on a live-only column (`is_active`) can silently
return `[]` while an insert fails on a live-only NOT NULL column.

## Radix Select (shadcn) automation

- The visible trigger is `[role="combobox"]`; the hidden native
  `<select name="...">` is the FormData source — **clicking it does nothing**.
- **NEVER press Escape to "close the listbox" — Escape closes the whole Radix
  Dialog.** The dialog disappears, "form submitted" looks true, and zero
  server actions fired. Select via keyboard (focus trigger → ArrowDown → Enter)
  or click `[role="option"]` while the listbox is open.
- Listbox entrance animation makes option clicks flaky: wait ~600ms after
  opening, poll for `[role="option"]`, and assert the hidden select's
  `inputValue()` before submitting.
- A `force: true` click on a covered button lands on the portal overlay
  (the open listbox) — it does NOT submit the form. Check
  `[role="listbox"]` visibility first.

## Stale dev server / HMR corruption

- `process(action="kill")` on a Hermes background session kills the bash
  WRAPPER, not the node child → orphan holds the port. A "fresh" server then
  logs `⚠ Port 3000 is in use ... using available port 3001 instead` while
  your tests still hit 3000 (the orphan). Check the `Ready in ... Local:`
  line before trusting any test run. Kill with `taskkill /PID <pid> /T /F`.
  (Full detail: `debugging-spawned-processes` §4.)
- After MANY edits on a hot dev server, Turbopack can serve corrupted client
  chunks (button renders "ss" instead of its source text, pages stuck on
  "Loading...") while all server actions log 200. Compare served DOM to
  source before debugging app logic; restart the server if they differ.
- When the port is held, the real server's log lives in
  `.next/dev/logs/next-development.log`.

## Parallel subagents

- Agent A's `tsc --noEmit` can report Agent B's in-flight edits as errors
  ("6 pre-existing errors in file X") — they're not pre-existing. Run tsc only
  after ALL agents land, then re-check `git diff --stat` for unexpected files.
- A subagent that times out mid-edit leaves the file broken (e.g. 6× identical
  `string | undefined` → `SetStateAction<string>` errors, ~60% of edits
  applied). Fix the residue yourself with `?? ""` guards rather than
  re-dispatching a full agent.
- Subagent summaries are self-reports: re-run tsc + build yourself, and
  remember dev servers don't reload signature changes into the action
  registry reliably — restart before long verification runs.

## Playwright patterns that bite

- `prompt()` dialogs: register `page.once("dialog", d => d.accept(name))`
  BEFORE clicking the trigger. Unhandled dialogs auto-dismiss (return null) →
  silent no-op. A misfired accept can create garbage rows (an entity literally
  named "ss" from an earlier run) — query the DB and clean up before rerunning.
- Poll, don't sleep: `const poll = async (fn, timeout=20000, step=500) => {…}`
  and poll for text/visibility. Fixed `waitForTimeout` races first-compile
  latency after server restarts.
- `await` inside a non-async arrow callback is a SyntaxError — mark callbacks
  `async` when the body uses `await`.
- Assert hidden form values (`inputValue()` on Radix's hidden select) — it
  proves state the visible UI hides.
- Auth-gated pages redirect to /login for logged-out visitors (307) — always
  log in through the form first (`#email`, `#password`, `button[type=submit]`).
