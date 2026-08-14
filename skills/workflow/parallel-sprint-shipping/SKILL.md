---
name: parallel-sprint-shipping
description: >-
  Ship parallel subagents on one repo via a parent merge gate.
---

# Parallel Sprint Shipping Loop

Proven pattern — ran 6+ times on cashflow-os in one session, zero working-tree
conflicts, every sprint caught real bugs in review before shipping.

## When to use

- Sprint has 2-4 tasks in the SAME repo that touch different areas
- User says "parallel", "swarm", "keep rolling", or "use subagents"
- Tasks are independent enough to partition by file

## The pattern

### 1. Partition files explicitly (the whole conflict strategy)

Every task brief states **exactly** which files it owns:

```
You own ONLY: src/features/X/, src/app/X/page.tsx, NEW src/components/ui/Y.tsx.
Do NOT touch src/features/Z/ (sibling owns it), AppShell.tsx, src/lib/.
Read-only OK elsewhere.
```

No shared files = no coordination = no conflicts. If two tasks need the same
file, either merge them into one task or have the parent do the shared edit
after merge.

**Foundation-first for UI waves:** when the wave depends on shared tokens or
components (globals.css accent/shadow changes, a new `EmptyState` component),
the PARENT ships those alone BEFORE dispatching — every child brief then says
"already shipped, use it". Parallel children cannot safely co-author one
shared file, and a child waiting on another child's shared file stalls the
wave. This session: parent did tokens + shared component, then 5 agents
partitioned the surfaces. Also: before authoring a NEW shared component,
grep for an existing one (a dead-code `EmptyState` with a different API was
overwritten — harmless there, but merging APIs backward-compatibly
(`description` alias + `children` passthrough) is the fix when it isn't).

### 2. Children: `tsc` only, never `npm run build`

Concurrent builds collide on `.next/`. Every brief must say:

```
CONCURRENCY: no `npm run build` — `npx tsc --noEmit` only. git commit at end, do NOT push.
```

The parent runs the real build after all children land.

### 3. Children commit, never push

Each child lands `git commit` with a clear message. Parent does merge + push.

### 4. Parent merge gate

After the batch re-enters:

```
npx tsc --noEmit        # full typecheck
npm run build           # real build (children couldn't)
<impeccable detect on changed files>   # design detector if UI changed
```

Fix failures at root cause. Classic build-breaker from this pattern:
`useSyncExternalStore` without `getServerSnapshot` crashes prerendering of
static pages (`Missing getServerSnapshot... Export encountered an error`).
One 5-line fix in the store component.

### 5. ECC review gate before push — size it to the surface

Dispatch parallel reviewers on `git diff BASE..HEAD`:
- `code-reviewer` — correctness: races (double-submit!), validation holes,
  RLS/entity scoping, money math (signs, rounding), conditional writes
- `silent-failure-hunter` — UI: swallowed `{error}` returns, empty/loading/
  error states, a11y, double-click races, stale state on entity switch

**Gate sizing (AGENTS.md baseline, scaled by surface):** baseline = the two
above + `security-reviewer` (confirm no security boundaries touched; for a
pure UI diff this is a quick PASS). Add `database-reviewer` when the diff
touches schema/migrations; add `a11y-architect` for ANY UI wave — it catches
real MAJORs (custom popovers with no Escape/focus return, inline confirms
dropping focus to `<body>`, contrast of new tokens) that the other two miss.
Mini-gate = 2 reviewers (code-reviewer + silent-failure-hunter) for deltas
under ~10 lines/3 files — still mandatory per repo rules, but don't burn a
full 4-agent gate on a one-liner. After fixing findings, re-verify with tsc +
build; the fixing itself needs no re-gate — but a NEW delta added AFTER the
gate (e.g. an IA change landing mid-gate) gets its own mini-gate.

Brief format: exact diff range + numbered findings `(severity | file:line |
issue | one-line fix)` + `npx tsc --noEmit` baseline. Both reviewers flagging
the same thing = fix it once at the shared handler (root cause), not
per-caller. Security reviewer can be scoped ("UI-wave only: confirm no
actions.ts/route.ts/api/ in the diff, no dangerouslySetInnerHTML, delete
flows still require an explicit click").

Real bugs this loop caught: RLS owner-only policies making a whole staff
approval workflow inert (app layer right, DB policies missing → migration),
export button ignoring active list filters, `validateOptionalText` conflating
"empty (valid)" with "too long (invalid)", `parseFloat` accepting `Infinity`.

### 6. Fix → verify → push → live check

- Fix findings surgically (smallest diff), re-run tsc + build
- `git push` → wait ~45s → `curl -s -o /dev/null -w "%{http_code}" <live-url>` → 200
- Kanban: note that `delegate_task` child contexts CANNOT mutate kanban via
  CLI (`hermes kanban complete` refused) — the parent/orchestrator must, or
  report completion for the user to mark.

**CRITICAL — auto-deploy can silently break (Vercel, Aug 2026):** pushes
landing on GitHub do NOT guarantee a build. The git integration stopped
triggering while `git push` kept succeeding — the site served a 2-day-old
build through 30+ shipped commits, and every `curl` 200 check passed because
old builds still respond 200. Detect it: `curl -s <prod-url>/` and grep for a
KNOWN-NEW string (new hero line, new route path). A bare status code proves
nothing. Also `vercel ls` can show stale deployment lists — not proof of
liveness. Fix: `vercel --prod --yes` from the repo (CLI deploy bypasses the
git integration and aliases the production URL, ~60s). After every milestone,
grep live HTML for a new-build marker, not just status codes.

## Reading child results

Inline batch results are TRUNCATED — read the full summaries from the cache
files (`~/AppData/Local/hermes/cache/delegation/subagent-summary-*.txt`).
Always read the middle sections; that's where MAJOR findings hide.

## Child timeout salvage (don't re-dispatch blindly)

A child can time out (600s) AFTER writing all its files but BEFORE committing
or verifying. Re-dispatching wastes the work. Instead:

1. `git log --oneline -3` + `git status -s` — see what's committed vs dirty.
2. `tail -50 <live-transcript>/task-0.log` — the final lines show where it
   stalled (usually a type-narrowing rabbit hole, not a real blocker).
3. Take over: run `npx tsc --noEmit`, fix the last error yourself (often a
   one-line `?? 'fallback'` narrowing fix), then grep-verify the key fixes
   actually landed in the files before trusting the rewrite:
   `grep -n "TRANSITIONS\|23505\|'error' in" <files>`.
4. Commit the salvaged work with a message naming the review it implements.

**Triage by api_calls count in the batch result** (both timeout shapes happen):
~7–11 api_calls with the transcript stuck on early read_file/search = provider
slowness, NOTHING was written (`git status` clean) — re-dispatch or build it
yourself; 17–32 api_calls with files modified = work done, salvage per above.

## Git safety in a shared working tree (parallel agents)

Whole-tree git state-changing ops are OFF-LIMITS while siblings have
uncommitted work — they capture or revert OTHER agents' changes:

- Bare `git stash` traps every dirty file in the tree, including the parent
  wave's uncommitted foundation (globals.css, shared components) and other
  subagents' files. `git stash pop` then aborts ("Your local changes to the
  following files would be overwritten by merge") on any file a sibling
  advanced after the stash.
- Same footgun class: `git checkout .`, `git reset --hard`, `git add -A`.
- Want to test "is this tsc error pre-existing?" → DON'T stash. Answer it
  with scope: `git diff --stat -- <your paths>` + `npx tsc --noEmit 2>&1 |
  grep <your-owned-files>` (grep exit 1 = clean). If a snapshot is truly
  needed, scope it: `git stash push -- <your paths>`.

Recovery if the damage is done (files reverted / pop aborted):

1. `git stash show --stat stash@{0}` — inventory what's trapped.
2. Restore selectively — NEVER blind `git stash pop`:
   `git checkout stash@{0} -- <paths>` per file group. Files named in the
   pop conflict were advanced by a sibling AFTER the stash — leave the
   working-tree version, the stash copy is stale.
3. Verify: `git status --short` + tsc filtered to your files.
4. NEVER `git stash drop` — keep the entry for the parent to audit; report
   in the summary which files were restored from stash vs. left to owners.

**Child-side: detect and survive a sibling wipe (Aug 2026 incident).** A
child's completed-but-uncommitted edits were silently reverted mid-task when
a sibling ran a whole-tree `git restore`/`checkout .` — `git status
--porcelain` stopped listing the child's files and file mtimes jumped, while
the patch tool still reported success. Recovery playbook:

- After every edit batch in a shared tree, verify with
  `git status --porcelain -- <your-files>` + `grep -c <marker-string> <file>`
  BEFORE running tsc — the patch tool's success diff proves nothing once a
  sibling can roll the tree.
- Tool disagreement = concurrent writer. If terminal `grep` shows the
  original content but `read_file`/`patch` show your edits (or vice versa),
  a sibling is mid-restore or a twin instance is re-applying the same
  changes. Re-read and re-check; don't blindly re-apply.
- Re-applying after a wipe can DUPLICATE blocks: if a twin instance already
  re-applied the same edits, your re-apply inserts a second import
  block/component. Grep for your marker strings first; if present, only
  remove what's duplicated.
- tsc error lists that change between runs (different non-owned files each
  run) = siblings' in-flight edits, not your regression. Filter tsc output
  to your owned files and report the rest as out-of-scope.

## Shipping a migration the USER must run (no CLI/PAT)

When DDL can't be applied by you (no supabase CLI/PAT), the handoff is
copy-paste, not "go open the file":

- Paste the FULL SQL inline in chat — the user will paste a file path into the
  SQL Editor otherwise ("supabase/migrations/011_staff_rls.sql" as a query =
  syntax error), and will ask "what should I copy" if you point at a file.
- Write migrations idempotent: `CREATE TABLE IF NOT EXISTS`, `ALTER ... ADD
  COLUMN IF NOT EXISTS`, `DO $$ BEGIN CREATE POLICY ... EXCEPTION WHEN
  duplicate_object THEN NULL; END $$` — safe to re-run, no cleanup needed.
- Open the SQL Editor in the preview pane
  (`supabase.com/dashboard/project/<ref>/sql/new`) so login → paste → Run is
  one hop.
- Verify from the API after they report success: anon-key PostgREST probe of
  each new table (`?select=id&limit=1` → 200 = table + RLS live).

**Probe recipes that caught real prod gaps (Aug 2026):**

- **Table-scan loop for unapplied migrations.** The user's paste flow silently
  skips migrations — one page was broken in prod for weeks because its table
  never existed. Don't trust "I ran it". Mint a test-user JWT
  (`POST /auth/v1/token?grant_type=password` with apikey header), then loop
  every table the app queries: `curl -o /dev/null -w "%{http_code}" .../rest/v1/<t>?select=id&limit=1`
  → **404 = migration never applied**. Probe the app's real tables, not your
  guess-list (probing `employees`/`sales`/`automation_rules` 404'd but the app
  doesn't use those names — only `loans` mattered).
- **Unique-index live probe.** A unique index "applied" by the user may not
  be. Insert a deliberate duplicate with the same key: **201 = index NOT
  live; 409 = enforced**. This proved migration 020 was missing (201), then
  live (409) after the paste. Clean up the probe row after (DELETE by a
  marker description).
- **SECURITY DEFINER RPC guard probe.** After shipping an auth guard on a
  definer RPC (e.g. `notify_user` NULL-bypass fix), call it WITHOUT a token
  (anon key only): expect the new error (e.g. `not authorized`). A 200/insert
  = the guard never landed.
- **Seed-data verification of conditional UI.** A feature that hides when
  there's no history (momentum %, empty states) can't be verified with a
  fresh test account. Seed one REST POST (marker description), screenshot,
  then DELETE by the marker — leaves the test account clean.

## Premium landing pages (dark SaaS)

Full recipe in `references/premium-dark-saas-landing.md` — user's mandate:
Stripe/Linear/Vercel caliber, transformation-opening headline, pinned dark
design system, hand-rolled motion, no-JS-safe reveals, honest copy,
`/feedback` testimonial pipeline (insert-only RLS). Note: the `landing-page`
skill in external_dirs covers conversion structure — this reference adds the
premium-execution layer the external skill lacks.

## UI elevation sprint ("app feels generic next to the landing")

Two-audit research wave FIRST (psychology specialist + design-direction
specialist, audit-only), ONE user fork question (accent unification vs
frozen vs dark — default to strongest rec when unanswered), foundation-first
implementation, a11y-architect in the gate, visual verify. Full dispatch
briefs + finance-dashboard psych placement cheat sheet in
`references/ux-psychology-elevation-wave.md`.

## AI feature review checklist (LLM chat/assistant in a web app)

Every AI endpoint shipped in a sprint gets these checked in ECC review — a
finance-app AI assistant review found all of these as real findings:

- **Auth-gate the proxy route** — an unauthenticated `/api/ai/chat` is an open
  credit-burning proxy. `supabase.auth.getUser()` → 401, per-user rate limit,
  history + input length caps (server AND client).
- **Never interpolate client input into the system prompt** (prompt injection).
  Keep the system prompt fully static server-side; ship financial context as a
  delimited `[CONTEXT — untrusted data]` block inside the user message.
- **No fabricated seed data in a finance app.** Demo insights/numbers
  ("subscriptions up 12%", "$4,820") rendered as real cards is a MAJOR —
  users act on them. Seed only a welcome message; the AI says only what the
  API returns.
- **Timeout + generic errors.** `AbortSignal.timeout(30_000)` → 504; log
  upstream detail server-side, return generic text (never leak OpenRouter
  statuses).
- **Provider chain over provider lock-in.** If the user has OpenAI-compatible
  subscriptions (e.g. OpenCode Go/Zen: `https://opencode.ai/zen/go/v1` +
  `.../zen/v1`, keys in hermes `.env`), try the subscription FIRST, then
  pay-as-you-go, then OpenRouter — verify with a one-shot curl
  (`{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"Reply GO_OK"}]}`)
  before wiring. Don't default to OpenRouter just because its key is in env.

## Verifying animated pages (agent-browser screenshots)

Reveal-on-scroll (IntersectionObserver) pages screenshot BLACK if captured
before hydration/reveal. Sequence that works:
`agent-browser open <url>` → `agent-browser wait 2000-3000` → scroll through
the page in steps (`agent-browser scroll down 1200` ×N, waiting ~500ms between
so observers fire) → `eval "window.scrollTo(0,0)"` → `screenshot --full <path>`.

Pitfalls: `screenshot` takes `[selector] [path]` — there are NO
`--width/--height` flags; passing them makes the CLI save to a file literally
named `--width` (then check `git status` — it can get committed by a later
`git add -A`; `git rm --cached -- --width` to purge). Pre-hydration captures
of animated heroes are also black even without reveals — always wait first.

## Supabase migration security checklist (runs BEFORE the user runs it)

Every migration in a financial app gets reviewed for these — two BLOCKERs
were caught by ECC review on this exact checklist. Full detail in
`references/supabase-rls-migration-checklist.md`:

- **Views bypass RLS by default** (security definer) → any authed user reads
  every entity's rows. Always `CREATE OR REPLACE VIEW ... WITH (security_invoker = true)`.
- **Role-based features are inert without staff-scoped policies.** App-layer
  `getCurrentStaffRole()` is useless when RLS denies the SELECT it needs.
  Ship the `current_staff_role(entity_id)` SECURITY DEFINER helper + policies
  in the SAME migration as the feature.
- **Child/line tables need their own staff-read policies** — a parent-policy
  does not cover `invoice_lines`/`po_lines`/`payroll_lines`.
- Money columns get `CHECK (x >= 0)` constraints; server actions validate
  before insert (reject, never silently filter invalid lines).

## Pitfalls

- **File ownership gaps:** if a brief says "only X" but the task needs a shared
  file, the child either breaks the rule or skips the work. Partition first,
  then dispatch.
- **Sub-agents modifying files the parent read:** re-read before editing after
  a batch returns (the summary notes it explicitly).
- **Whole-tree git ops in a shared tree:** bare `git stash` / `checkout .` /
  `reset --hard` trap or revert siblings' uncommitted work — see "Git safety
  in a shared working tree" above. One bare stash mid-sprint trapped a whole
  wave's uncommitted changes; recovery = per-path `git checkout stash@{0} -- <files>`.
- **Two agents, same file, different regions** still conflict at commit time —
  never allow it.
- **User-owned skills refuse curator patches** (`created_by=None`): check with
  `hermes curator adopt <name>` if a delegation-related skill needs updating.
- **Patch tool can redact auth-header lines to `***` on disk.** Editing code that
  contains `Authorization: 'Bearer ' + key` via `patch` produced a literal
  `Authorization: *** ${key}\`` in the file (tool secret-redaction misfire).
  When writing API-key/auth code, prefer `write_file` for the whole file, or
  verify the returned diff shows real content (not `***`) before trusting it.
- **Patch-tool anchor hazard:** an old_string matching N places needs a
  distinctive preceding line as anchor (e.g. the unique `if (res.error)` rollback
  block, not `revalidatePath`+`return` which repeats per function). When
  replacing a block whose FIRST line is a function signature, re-emit the
  signature in the new_string — dropping it orphans the body (deletePayrollRun
  breakage, Aug 2026).
- **PostgREST RPC existence probe:** calling an RPC with `{}` returns 404 even
  when the function exists (arg mismatch) — don't read it as missing. Call with
  full args + a bogus UUID: 409 (FK violation) = exists and enforcing; 404 =
  genuinely absent. New tables probe `?select=id&limit=1` → 200 = table + RLS live.
- **Entity-action → owner notification pattern:** `notify_user` SECURITY DEFINER
  RPC (inserts for the entity owner by user_id) + a `notifyEntityOwner({entityId,
  kind, title, body, link})` helper that looks up `entities.user_id` and wraps
  everything in try/catch — best-effort, a failed notification must never break
  the action. Wire into payroll-paid, claim-approved, invoice-sent after the
  success path, before `return { success: true }`.
- **`@media (scripting: none)` is Firefox-unsupported** — a reveal/animation
  system relying on it for no-JS fallback renders a fully invisible page in
  Firefox without JS. Add `<noscript><style>.lp-reveal{opacity:1;transform:none}</style></noscript>`
  alongside the media query. Also: closed FAQ answers need `aria-hidden` +
  `inert` (grid-rows 0fr hides visually only), and tab switchers need
  `role=tablist/tab` + `aria-selected` — plain buttons leave SR users
  guessing which view is active.
- **Custom popover a11y (Escape + focus return).** Hand-rolled popovers
  (Filter dropdowns, More menus) need: a window `keydown` Escape listener
  closing them, AND focus returning to the trigger on close — implemented
  with a `prevOpenRef` pattern so the effect doesn't fire on mount
  (`if (prev.current && !open) triggerRef.current?.focus(); prev.current = open`).
  Inline row-confirms (Delete?/Cancel/Delete) unmount the clicked trash
  button → focus drops to `<body>`; focus the Cancel button via ref+effect
  when the confirm opens. The a11y-architect gate flags both as MAJORs.
- **`sed -i` is the right tool for one mechanical class-swap across N files**
  (e.g. `.then(setCurrency)` → `.then(setCurrency).catch(() => {})` in 12
  files) — a dozen identical `patch` calls is the wrong tool. Verify after
  with grep count 0 + tsc. Use `patch` for anything with per-site nuance.

## PWA (hand-rolled, zero deps)

`src/app/manifest.ts` (MetadataRoute.Manifest) + `public/sw.js` (~40 lines:
cache-first static, network-first navigations, offline fallback) +
`PwaRegister` client component (register only when NODE_ENV=production) +
`/offline` page. Icons without an image library: `scripts/gen-icons.js`
(minimal PNG encoder — zlib + crc32 + IHDR/IDAT/IEND chunks, rounded-square +
white mark). Run it, commit the PNGs, reference them from the manifest.
