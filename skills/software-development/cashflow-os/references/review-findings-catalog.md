# ECC Review Findings Catalog — CashFlow OS sprints (2026-08-04)

Recurring finding classes from the dual review (code-reviewer + silent-failure-hunter).
Check every sprint against this list BEFORE shipping.

## Security / money (BLOCKER–HIGH)

1. **Open API routes** — `/api/ai/chat` had zero auth; anyone could burn the provider key.
   Fix: `supabase.auth.getUser()` → 401, per-user rate limit, history/input caps.
2. **Views bypass RLS by default** — `CREATE VIEW` without `security_invoker` = cross-tenant leak.
   Fix: `CREATE OR REPLACE VIEW x WITH (security_invoker = true) AS …` (PG15+).
3. **Client-trusted workflow fields** — `status`/`submitted_by` from the client.
   Fix: derive server-side from role; ignore client values.
4. **Silent money rounding** — `DECIMAL(12,2)` silently rounds `19.999` → `20.00`.
   Fix: validateAmount (≤2 decimals, finite, >0) server-side in EVERY action, not just the new ones.
5. **Views/aggregates with unreachable statuses** — outstanding computed from a view whose
   statuses nothing ever sets → dead 0. Fix: compute from the rows you already fetched;
   make statuses reachable (draft→sent→paid transitions).
6. **Draft → paid** — free status transitions. Fix: explicit transition map.
7. **Silently filtering invalid lines** — creates wrong money math with no error.
   Fix: reject whole record: `Line N: description required / qty must be > 0 / price >= 0`.
8. **RLS-filtered writes no-op silently** — UPDATE without `.eq('entity_id', …)` succeeds
   with 0 rows. Fix: entity-scope every write.
9. **Cross-entity FK refs** — FK checks bypass RLS. Fix: pre-check parent
   `.eq('id', x).eq('entity_id', entityId)` before insert.
10. **App-layer roles without RLS policies** — approvals inert for staff (RLS owner-only).
    Fix: staff-scoped policies via `current_staff_role()` helper + parent-join policies on child tables.

## UX / silent failure (MAJOR)

1. **`{ error }` swallowed** — `await action(); refresh()` discards errors; dialogs close silently.
   Fix: capture result, `if (r && "error" in r)` → inline message, keep dialog open.
2. **Fake empty states** — query error returns `[]` → "No X yet" lies.
   Fix: return `{ error }`, render error + Retry.
3. **Fabricated demo data in finance UI** — seeded fake insights/numbers shown as real.
   Fix: never ship seed data that looks real; only relay API output.
4. **SSR hydration mismatch** — `new Date().getHours()` / `format(new Date(), …)` in render
   (server UTC vs client local). Fix: compute in `useEffect` post-mount; keep hooks before early returns.
5. **No in-flight guard** — double-click submit → duplicate financial records.
   Fix: `submitting` state + early return + `disabled`.
6. **Unbounded growth** — full chat history re-sent each request; unbounded lists.
   Fix: cap history (last ~20) + input (2000 chars).
7. **Error details leaked to client** — upstream provider error text.
   Fix: log server-side, generic client message (keep status mapping).
8. **No timeout on upstream fetch** — hung call = infinite spinner.
   Fix: `AbortSignal.timeout(30_000)`, map to 504.
9. **Dead controls** — buttons with no onClick. Fix: wire or remove.
10. **Nav gating hides features** — reports behind business segment only.
    Fix: put feature links in both segments when the feature serves both.

## Verifier's traps (things that look like bugs but aren't)

- `slice(-4)` toast cap + `useSyncExternalStore` need `getServerSnapshot()` for SSR prerender.
- Keyset pagination `.or("date.lt.X,and(date.eq.X,id.lt.Y)")` is valid PostgREST.
- Client supabase types embed to-one FKs as arrays — normalize with `Array.isArray` guard.
- Subagent timeout ≠ failure: files usually written but uncommitted — take over, run tsc, finish.
- **Redaction false positive** — read_file / execute_code output renders `apiKey: <expr>` as
  literal `***`; the source is usually fine. Raw-byte check (`read_bytes()` / `cat -A`) before
  reporting a committed artifact. The 2026-08-04 CRIT `apiKey: ***` at chat/route.ts:90 was this
  (verified 2026-08-05: raw bytes are `apiKey: aiRow.api_key,`).

## 2026-08-05 · silent-failure-hunter sprint (Cashy context, MCP tools, QuickAddForm, charts)

1. **Read-actions returning `[]` on error kill client error states** — `getCategories`/`getGoals`/
   `getDebts`/`getBudgetVsActual` `return []` on entity/DB error → `.catch()` never fires →
   DashboardPage `categoriesError` unreachable, QuickAdd category select silently empty;
   MCP `isError` detection misses arrays (`"error" in result` false). Fix at the shared action:
   return `{ error }` on failure (route.ts already marks `{error}` as isError).
2. **Try-once prefetch race** — AIAssistant `ensureContext()` sets `contextTried` before the
   await resolves → a fast first send posts with `FALLBACK_CONTEXT`. Fix: hold the in-flight
   promise in a ref; all callers await the same promise.
3. **Dead null-guard** — TransactionList `if (!d) return` — `getTxPage` never returns null
   (sub-actions swallow into `[]`); real failures render the silent empty ledger. Fix: `setPageErr`
   on falsy + treat all-empty-sections on an existing entity as suspect (stale `cf_entity_id` cookie).
4. **Ignored action result + unconditional reload** — AppShell `createEntity` ignores
   `createBusinessEntity`'s `{ error }`, always `location.reload()`. Fix: check result, alert, reload only on success.
5. **`Promise.all` all-or-nothing context** — one failing query discards 6 good ones. Fix: per-query `.catch(() => ({ data: null }))`.
6. **Mount-load vs quick-add refresh race** — slow dashboard `load()` can overwrite fresh
   post-add totals. Fix: request-id ref in the shared fetch/apply path.
7. **Uncontrolled date `defaultValue` SSR drift** — TransactionList add dialog uses
   `defaultValue={format(new Date(), …)}` (server UTC); QuickAddForm's state+effect pattern is the correct one.
8. **tsc incremental-cache false negative** — `npx tsc --noEmit` can skip files via stale
   `.tsbuildinfo`; when tsc output contradicts raw-byte evidence, force `--incremental false`
   and confirm the file is in the program with `--listFilesOnly | grep <file>`.
