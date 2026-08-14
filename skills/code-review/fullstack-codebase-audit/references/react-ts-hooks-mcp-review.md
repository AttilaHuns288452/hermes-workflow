# React/TS + MCP Review Pass — Worked Example (cashflow-os sprint, ECC gate)

Review-only pass over new React components + a Next.js MCP route. Objective gates run first:
`tsc --noEmit` (clean), `npx eslint <changed files>`, then manual hook counting.

## The one that mattered (CRITICAL, invisible to both gates)

`DashboardPage.tsx`: four `useMemo`s (nwDelta/facts/statCards/liqData) sat AFTER
`if (loading) return` and `if (error) return` early returns. Happy path never noticed
(server page always supplied `initialData` → `loading` started false, hook count
constant at 27). But: mount with `initialData=null` or the error card's "Try again"
(set `loading=true`, then load completes) → render with 23 hooks followed by a render
with 27 → React throws "Rendered more hooks than during the previous render".
tsc: silent. eslint-config-next (react-hooks v6): silent. Only counting hooks on both
sides of the early returns finds it. Fix: hoist the useMemos above the returns.

## Lint triage notes (what the new react-hooks v6 rules actually mean)

- `react-hooks/refs` on `currencyRef.current = currency` during render — real error, but
  the ref was pointless: `formatMoney` could just be `useCallback(fn, [currency])`
  (currency is already a memoized chart prop, so memo still works). Ref patterns that
  stabilize identity the deps array already provides are removable complexity.
- `react-hooks/set-state-in-effect` on localStorage restore + `setLoading(false)` —
  benign mount-sync; note, not a defect.
- `react-hooks/purity` on `Date.now()` inside `send()` — FALSE positive: event handler,
  not render. Suppress with comment.
- `no-explicit-any` on `(t: any) => t.categories?.name` join access — real; one join
  interface fixes both sites.

## Other findings worth remembering

- **Dead error state**: `getCategories().then(setCategories).catch(() => setErr(true))`
  — but `getCategories` swallows errors and returns `[]`, so the catch never fires and
  the error/disabled UI is unreachable. Check the callee's failure mode before trusting
  `.catch` wiring.
- **`clampInt`**: `Math.floor(Number(v)) || dflt` — `limit=0` → 50 (falsy-`||`). Use
  `Number.isFinite` guard.
- **Notification responses**: `tools/call` handler ignored the notification flag → a
  no-id request still got a response. JSON-RPC: notifications must never be answered.
- **MCP cookie injection** (bearer → session cookie for downstream server actions):
  works because Next's `RequestCookies.set()` mutates the per-request store and
  @supabase/ssr reads via lazy `getAll()` — verified against `createClient()` +
  `getEntity()` source before accepting. Fragile across Next upgrades; pin with comment.

## Severity-table output shape that worked

| Sev | file:line | Issue | One-line fix |
|---|---|---|---|
| CRITICAL | `DashboardPage.tsx:382` | useMemos after early returns → hook-count crash on loading/error paths | Hoist above returns |

Plus a "Verified clean" section listing what was checked and found correct
(React.memo identity, JSON-RPC codes/batch/202, structured error unions, import
hygiene, no debug leftovers) — keeps the gate review honest and short.
