# CashFlow OS — feature-build recipe

App: `~/Documents/Projects/cashflow-os` (Next.js 16 App Router + Supabase + Tailwind + shadcn/ui). Feature-based: `src/features/<name>/` + `src/app/<route>/`. This is the exact sequence that built Inventory, Staff, and Loans — copy it for the next roadmap feature (payroll, receivables/payables, budgets, etc.).

## Sequence (fastest proven path)

1. **Read the migration first.** `supabase/migrations/NNN_<feature>.sql` is the source of truth for table/column names (schema may already be applied live via SQL Editor — see umbrella SKILL.md "Live schema is often AHEAD of migrations"). Take column names verbatim from here.
2. **Copy an existing feature's server actions** — `src/features/<name>/actions.ts` mirroring `features/assets/actions.ts` or `features/investments/actions.ts`:
   - `"use server"`, `getEntity()` from `@/lib/entity` (`if ("error" in entity) return [];`)
   - select `*` `.eq("entity_id", entityId)`, order by `created_at desc` (or `name`)
   - every mutation checks `.error`, returns `{ error: error.message }` or `{ success: true }`, then `revalidatePath("/<route>")` (+ any dependent routes)
   - build insert payloads explicitly (no `...data` spread carrying `undefined` fields)
3. **Copy an existing client page** — `src/app/inventory/page.tsx` is the reference business-feature page:
   - `"use client"`; `useState<any[]>` + `fetch()` fn + `useEffect`; `getCurrencySetting().then(setCurrency)` from `@/features/settings/actions`; `formatCurrency(n, currency)` from `@/lib/currency`
   - wrap in `<RequireBusinessEntity feature="<name>">` (`@/components/layout/RequireBusinessEntity`)
   - header: mono eyebrow `Business · <Name>` (`font-mono text-[11px] uppercase tracking-[0.06em] text-muted-foreground`) + `font-display` h1 + one-line subtitle
   - 3-card summary strip (`grid gap-4 grid-cols-1 sm:grid-cols-3`, `CardContent pt-6`, mono stat numbers, `tabular-nums`)
   - add form as a Card with `flex flex-wrap items-end gap-4 py-4`, inline `err` state shown under the form (`text-red-500`), `alert()` for row-action errors
   - row cards `card-hover`, loading state `Loading...`, empty state card
   - `ponytail:` comments on any deliberate simplification
4. **Nav entry** — `src/components/layout/AppShell.tsx`: add a lucide icon import + `{ href, label, icon }` in the right `navSections` block (business features under `segment: "business"`, label "Business"). Nothing else changes.
5. **Verify** — `npx tsc --noEmit` must exit 0.

## Overview/dashboard variant (read-only aggregate page)

For a stats page (e.g. business overview) instead of a CRUD page: no forms, no revalidatePath.

- **Action:** one `Promise.all` of parallel entity-scoped queries (month txns via `gte/lte` on `startOfMonth/endOfMonth` date strings, inventory, staff, pending `count: "exact", head: true`), compute sums/groups in the action, return one summary object + `{ error }` on failure. Mirror `getDashboardData`'s merged-query-set shape.
- **Component:** `"use client"`, fetch on mount; skeleton state = `animate-pulse bg-muted/50` blocks mirroring the real layout; error = `text-xs text-red-500` + Retry button; empty/defensive state = centered Card (unreachable when the page is gated — keep it one small branch).
- **Type the success shape** with `type Overview = Exclude<Awaited<ReturnType<typeof action>>, { error: string }>` instead of hand-writing it.
- **Stat cards:** `text-[28px] font-bold leading-none tabular-nums` + mono eyebrow `font-mono text-[11px] uppercase tracking-[0.06em] text-muted-foreground` labels + flat token color classes (`text-green`/`text-red`/`text-accent`, chips `bg-green-soft text-green` etc.); low-stock warnings use `text-amber-600 dark:text-amber-400`.
- **Low-stock semantics:** `quantity <= (low_stock_alert ?? 5)` — includes out-of-stock (qty 0), matches the inventory page's `statusOf`.
- **Page:** same `"use client"` + `<RequireBusinessEntity feature="…">` wrapper as CRUD pages — the guard IS the empty state for no-business-selected.

## Forecasting / analytics variant (worked: Forecast + what-if pages)

Read-only aggregate pages can share one action across two charts via a private helper:

- **One 6-month query, group in JS.** `select('date, type, amount').eq('entity_id', entityId).neq('status', 'rejected').gte('date', startOfMonth(subMonths(now, 5))...)`, then loop `i = 5..0` filtering rows by `startOfMonth/endOfMonth` string bounds (mirrors `getDashboardData`'s trend loop). Label months `format(d, 'MMM yyyy')`. One round trip; the per-month queries in `getMonthlyTrend` are the slow anti-pattern.
- **Transaction status semantics:** `pending | approved | rejected`. Personal entities auto-approve (`approved` on insert); business submissions go `pending` until a reviewer approves/rejects. Analytics exclude `rejected`; decide on `pending` per spec (forecast used only `neq('status','rejected')`).
- **Flat projection (ponytail):** next N months = average of the last 3 real months' income/expense, flagged `// ponytail: naive flat projection — no seasonality/trend`. Return `{ months, currency } | { error }` — include `currency` (entity query, same as `getDashboardData`) so the client can `formatCurrency` without a second fetch.
- **🚨 Domain fact — investments are already inside `assets`.** `investments/actions.ts` syncs the portfolio into `assets` as a `type: "liquid"` row named `📈 Investment Portfolio`. Net worth = `assets.value − debts.amount` via the **exported** `getNetWorth(entityId)` from `@/features/dashboard/actions` — importing an action from a sibling feature read-only is fine and correct. Never query `investments` again for net worth or you double-count. (Get investments' live value only for portfolio screens, via its market-data enrichment.)
- **What-if action:** validate at the trust boundary — `Number.isFinite` on both params, clamp months `1..24` server-side; `netWorth += avgNet + monthlyExpenseChange` per month; label with `addMonths(now, i)`.
- **Chart with a projection boundary:** one `<Line dataKey="net" stroke="var(--accent)" strokeWidth={2}>` (never hardcoded hex) + `<ReferenceLine x={5.5} stroke="var(--muted-foreground)" strokeDasharray="4 4" />` — the x is a category index sitting between the last real month (5) and first projected (6). Add a mono caption under the chart explaining the naive projection. `tickFormatter={(v: any) => formatCurrency(Number(v), currency)}` (recharts `any` allowed); tooltip `contentStyle` uses `var(--popover)`/`var(--border)`.
- **Cards:** two flat `rounded-xl` Cards in `lg:grid-cols-2`; per-card skeleton (`h-[280px] animate-pulse rounded-xl bg-muted/50`), `text-xs text-red-500` + Retry, empty state when every real month is zero (`months.some(m => m.income > 0 || m.expense > 0)`).
- **Scenario inputs:** `<input type="number" inputMode="decimal">` with `₱` placeholder, Project/Reset buttons, `disabled={loading}` in-flight guard (same rule as money forms).

## ERP module variant (worked: Purchasing + Suppliers, migration 012)

Header + child-lines tables (`purchase_orders` + `po_lines`, `suppliers` + FK to POs) with a status workflow. Differences from the plain CRUD recipe:

- **Server page wrapping a client component** (vs inventory's all-in-one client page): `src/app/<route>/page.tsx` is a plain server component rendering `<RequireBusinessEntity feature="…"><FeaturePage /></RequireBusinessEntity>`; the feature page lives in `src/features/<name>/components/<Name>Page.tsx` as `"use client"`. Same guard, same states, but the page file stays dumb.
- **List as shadcn `Table`** (`Table/TableHeader/TableBody/TableRow/TableHead/TableCell` from `@/components/ui/table`), wrapped in `Card className="rounded-xl"` with `CardContent className="p-0"`; empty row = `<TableCell colSpan={N} className="py-12 text-center text-muted-foreground">`. Flat status text (no badges): `text-green-600 dark:text-green-400` / `text-accent` / `text-orange-600 dark:text-orange-400` / `text-muted-foreground` from a `STATUS_CLS: Record<string, string>` map.
- **Row actions with `window.confirm`** for destructive/irreversible ops (Mark received, Cancel, delete supplier) — native confirm, no dialog needed; guard with status checks so buttons only render for actionable rows.
- **New-PO dialog with dynamic line rows:** `useState<LineDraft[]>` (`{description, quantity, unit_price}` as STRINGS — inputs are strings), add-line button, per-row remove (disabled when `lines.length === 1`), `parseFloat` at submit. Server action re-validates and computes totals (trust boundary). In-flight guard `disabled={saving}`.
- **Supplier select in the PO dialog** imports `getSuppliers` from `@/features/suppliers/actions` — cross-feature action import is the house reuse path (same as dashboard importing `getNetWorth`).
- **Summary strip values from a dedicated `getPurchasingSummary()`** (month spend = received POs this month via `gte/lte` on month-range strings; outstanding = count+total from the `outstanding_payables` VIEW; upcoming = `in('status', ['ordered','partial']).not('expected_date','is',null)` ordered asc limit 5). Views exist for exactly this — query them like tables.
- **Dual revalidation:** PO mutations `revalidatePath('/purchasing')` AND `revalidatePath('/suppliers')` (supplier totals change); supplier mutations revalidate both too.
- **AppShell reality under parallel agents:** the nav is shared — a sibling added a "Sales" group while this module added links to "Operations". Both sets of links coexist because navSections is pure data; verify by re-reading the file after every edit (umbrella §Parallel subagents).
- New-PO page fetch = `Promise.all([getPurchaseOrders(), getPurchasingSummary(), getSuppliers()])` with per-result `'error' in r` checks; a shared `run()` helper + `rowErr`/`dlgErr`/`fetchErr` triple (same as accounts/inventory).

## House rules (AGENTS.md + observed practice)

- No new npm deps; shadcn components already present: `badge, button, card, dialog, input, label, select, table, tabs, separator, progress, avatar`.
- No new `as any` (recharts callbacks excepted); `any[]` state and `as "union"` casts are fine.
- Structured `{ error: string }` returns, never raw throws; no empty catch blocks.
- Dark mode via CSS vars — colored badges use `border-X-500 text-X-600 dark:border-X-600 dark:text-X-400` (e.g. inventory's amber Low-stock badge; loans' emerald Loaned-out / red Overdue).
- ECC review before merge per AGENTS.md dispatch table (code-reviewer always; database-reviewer for schema changes).

## Gotchas hit in practice

- `search_files` (Hermes tool) can return 0 results for `*.tsx`/`*` globs on this host — fall back to `find src -type f | sort` via terminal.
- write_file's syntax check can report `TS6053: File not found` on a brand-new `.ts` file — it wrote fine; ignore and re-run tsc.
- `"error" in r` narrows `r.error` to `string | undefined` → use `r.error || "Something went wrong"` (umbrella SKILL.md §Server Actions).
- After adding a route, stale `.next/dev/types/` breaks tsc → `rm -rf .next/dev/types` (umbrella SKILL.md §Build & Typecheck).
- Long-running `next dev` serves corrupted chunks after many edits → restart dev server before debugging UI text (umbrella SKILL.md §E2E Verification).
