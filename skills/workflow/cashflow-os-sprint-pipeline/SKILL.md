---
name: cashflow-os-sprint-pipeline
description: Sprint pipeline for cashflow-os and Next.js+Supabase apps.
---

# CashFlow OS Sprint Pipeline

Proven over ~20 build→review→deploy cycles (Aug 2026). Every step is load-bearing; skip one and a money bug or a11y gap ships.

## 1. Schema-first recon (before ANY brief)

- Read the migrations: `supabase/migrations/*.sql` — the live DB can be AHEAD of repo migrations (user runs DDL manually in SQL Editor). Verify table reality with PostgREST probes: `curl "$URL/rest/v1/<table>?select=id&limit=1" -H "apikey: $KEY" -H "Authorization: Bearer $KEY"` → 200 = exists, 404 = not applied.
- Check what the feature actually has (grep the feature dir). Agents must write against REAL schema — e.g. `investments` table (not `assets`) has ticker/quantity/avg_price; `debts` has NO apr column → defaults + ponytail comments, never invented fields.

## 2. Parallel subagent dispatch (disjoint ownership)

- 1 brief per agent with: exact file ownership list, CONCURRENCY rules (`npx tsc --noEmit` only — NEVER `npm run build` from children, `.next` contention), style (2-space, no semicolons, single quotes), frozen design language (light #f8f9fb/#2563eb, serif font-display, mono eyebrows `font-mono text-[11px] uppercase tracking-[0.06em]`, flat, rounded-xl, divs not spans), `{ error }` returns never throw, `getEntity()` scoping.
- File ownership MUST be disjoint. AppShell.tsx is the common collision point — give it to ONE agent, mount the other's components yourself after merge.
- Model: deepseek-v4-flash via delegate_task. Timeout risk: agents that finish writing files then burn 5-10 min on tsc rabbit holes — check the live transcript tail; if files are written and tsc nearly passing, finish it yourself (see Step 4).

## 3. Merge verify (parent-only)

```bash
npx tsc --noEmit && npm run build 2>&1 | grep -E "error|✓ Compiled|Failed"
node "C:/Users/YOUR_USERNAME/AppData/Local/hermes/skills/impeccable/scripts/detect.mjs" --json <changed files>
```
Detector `[]` = clean. Watch for: duplicate keys, hooks-after-early-return (Rules of Hooks!), hardcoded hex (must be CSS vars), border-l-2 side-tab slop (use border-l).
**Pitfall (bit twice 2026-08-05):** adding skeleton/loading early returns to a component that has `useMemo`s BELOW them = "Rendered more hooks" crash on the loading→loaded transition (tsc can't see it; prod error boundary catches it). Rule: ALL hooks must sit above EVERY early return. Verify new loading states with a browser probe (`h1` present + no Reset button + 0 pageerrors), not just tsc.

## 4. ECC gate (MANDATORY per AGENTS.md — scaled since 2026-08-05)

Baseline 3 parallel agents, full 5 for UI-heavy sprints (ALL on `git diff <base>..HEAD`):
- **code-reviewer**: React/TS correctness, Rules of Hooks (memos AFTER early returns = "rendered more hooks" crash — tsc can't see it), currencyRef render-phase writes, dead code.
- **silent-failure-hunter**: loading/error/empty states, double-submit guards, hydration mismatches (SSR UTC vs client local — pass client date into actions!), stale-response races (capture filters at call, compare ref after await), in-flight-promise races (context prefetch vs send).
- **security-reviewer**: auth on new API routes (MCP bearer→cookie injection!), prompt injection, auth error enumeration (map Supabase codes to generic copy), unvalidated user input into Intl (currency whitelist).
- **a11y-architect** (UI batches): label/for pairs, aria-pressed, role=alert, focus trap + restore on custom dialogs, live regions, contrast (green #16a34a fails 4.5:1 → #15803d, orange → #c2410c), reduced-motion guard.
- **performance-optimizer** (UI batches): controlled inputs re-rendering whole pages (extract colocated form components), inline recharts formatters (hoist to module scope), rAF-throttle drag handlers, useMemo derived data.
- Fix findings yourself (surgical) or dispatch one agent with the numbered list. Then verify + build + deploy (`vercel --prod --yes`) + grep live HTML for a new-build string.

## 5. Migration handoff (user runs DDL)

- I have NO CLI/PAT for the live DB — DDL runs via Supabase SQL Editor (project `kjsvupescrlywsdyywyu`). Write `supabase/migrations/0XX_name.sql`, commit, then PASTE the full block in chat with dead-simple steps (user's known failure: pasting the file PATH instead of the SQL — say explicitly "copy the code block, not the file name").
- Migration pattern: `CREATE TABLE IF NOT EXISTS`, RLS enabled + owner-full + staff-read via `public.current_staff_role(entity_id)` (defined in 011), views MUST have `WITH (security_invoker = true)` (default definer = cross-tenant leak), CHECK constraints for money >= 0.
- After "done" from user: PostgREST probe each new table (200) — 404 means they pasted the wrong thing.

## 6. Verify live

`curl -s -o /dev/null -w "%{http_code}" https://cashflow-os-mu.vercel.app/login` → 200. Then summarize per-phase with the scoreboard table.

**CRITICAL — auto-deploy can silently break:** pushes landing on GitHub do NOT guarantee a Vercel build. The git integration stopped triggering (Aug 2026) while `git push` kept succeeding — the site served a 2-day-old build while we shipped 30+ commits. Detect it: `curl -s <prod-url>/` and grep for a KNOWN-NEW string (e.g. the new hero line) — a 200 on /login proves nothing (old builds still 200). Fix: `vercel --prod --yes` from the repo (CLI deploy bypasses the git integration and aliases the production URL directly, ~60s). After every milestone, grep the live HTML for a new-build marker, not just status codes.

## Pitfalls learned

- **Patch tool redacts `Bearer` in Authorization headers** (writes `***`) — use `'Bearer ' + key` string concat, never a template literal in a patch.
- **`agent-browser screenshot` has NO --width/--height flags** — `open` → `wait <ms>` → `screenshot [--full] <path>`. Reveal-on-scroll pages capture BLACK unless you scroll through first (IntersectionObserver never fires for below-fold in a full-page capture).
- **Timeout recovery**: agent timed out ≠ work lost — `git status` shows written-but-uncommitted files; check transcript tail for the last tsc error, fix it yourself, commit.
- **Vercel env**: `vercel env add <KEY> <scope>` pipes the value via stdin. Push auto-deploys (no need for `vercel redeploy --prod` — wrong flag anyway).
- **PostgREST embed filters** work with dotted paths inside `or()`: `or('description.ilike.%x%,categories.name.ilike.%x%')`.
- **Money math**: round2 every line total AND header total (1.335×2 ≠ 2.67); reject-not-filter invalid lines; explicit status transition maps; `.eq('entity_id', entityId)` on EVERY write (RLS-filtered updates silently no-op).
