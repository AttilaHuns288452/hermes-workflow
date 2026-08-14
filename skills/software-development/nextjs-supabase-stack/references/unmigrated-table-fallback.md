# Reading tables from a not-yet-applied migration (graceful fallback)

CashFlow OS migrations ship as `.sql` files the user pastes into the Supabase SQL
Editor — a feature can be built BEFORE its migration is applied (parallel module
development, e.g. Analytics reading migration-012 `invoices`/`invoice_lines`).
A hard `{ error }` on a missing relation makes the whole page dead for zero
reason. Pattern (from the Analytics module):

## Detect per-query, degrade per-section, never hard-fail on optional tables

```ts
const [entityRes, txnsRes, invoicesRes, linesRes] = await Promise.all([
  supabase.from('entities').select('currency').eq('id', entityId).single(),
  supabase.from('transactions').select('date, type, amount, categories(name)')
    .eq('entity_id', entityId).neq('status', 'rejected').gte('date', start),
  supabase.from('invoices').select('id, issue_date, total').eq('entity_id', entityId).eq('status', 'paid'),
  supabase.from('invoice_lines')
    .select('invoice_id, description, quantity, line_total, invoices(entity_id, status)'),
])
// core table fails → real error; optional tables fail → degraded mode
if (txnsRes.error) return { error: txnsRes.error.message }
const salesAvailable = !invoicesRes.error && !linesRes.error
```

- Check `.error` truthiness only — don't parse the PostgREST message
  (`relation "public.invoices" does not exist` / PGRST205). Any error means
  "table absent or broken", both degrade the same way.
- Return `salesAvailable: boolean` to the client; the page renders a small
  muted note (`'Sales data unavailable — run migration 012'`) under the header
  and inside the affected card. Partial data beats a dead page.
- Fallback content: revenue trend from transaction income when invoices are
  unavailable; product lists become `[]` (with their own empty state).
- When both sources exist: paid-invoice revenue by `issue_date` is the
  business truth; expenses come from transactions; profit = revenue − expense.

## Child tables without entity_id — embed the parent, filter in JS

`invoice_lines` has no `entity_id`; its RLS joins through `invoices`. Fetch
lines with the parent embedded and filter client-side:

```ts
for (const l of linesRes.data || []) {
  const rel: any = Array.isArray(l.invoices) ? l.invoices[0] : l.invoices  // to-one FK: object, typed path may say array
  if (!rel || rel.entity_id !== entityId || rel.status !== 'paid') continue
  // aggregate by l.description: quantity += l.quantity, revenue += l.line_total
}
```

Then sort desc by revenue → top 5; worst 3 = `products.slice(-3).reverse()`
ONLY when `products.length >= 5` (a 2-product list's "worst" is meaningless).

## KPI guards and forecast

- Margin and growth rate: guard the divisor (`revenueTotal > 0`, `prev3Avg > 0`),
  return 0 otherwise. Growth = last-3-month avg revenue vs previous-3 avg.
- `bestMonth`: sort a COPY (`[...months].sort(...)`) — `Array.sort` mutates.
- Forecast: `getForecast`'s `realMonths()` helper is NOT exported — recompute
  inline: last 6 months of transaction net, flat average × 3 months.
- Round money with `Math.round(x * 100) / 100` and `toNum()` (finite-check)
  like every other CashFlow OS action.

## Sidebar / page wiring (parallel-safe)

- Business pages wrap in `<RequireBusinessEntity feature="...">`; the link is
  ONE `navSections` entry (`{ href, label, icon }` — sidebar renders data).
- Verify a lucide icon exists before importing: `grep -c "BarChart3" node_modules/lucide-react/dist/lucide-react.d.ts`.
- Verify with `npx tsc --noEmit` only (no `npm run build` in parallel mode);
  stage only your owned files at commit.
