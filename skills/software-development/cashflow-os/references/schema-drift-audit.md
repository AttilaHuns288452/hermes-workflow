# Schema-drift audit (data/schema bug hunt) — methodology + 2026-08-05 findings

Full-data audit recipe for "cross-check every `.from()` query against `supabase/migrations/*.sql`".
Re-run before feature work or after any migration batch lands. Parser: `scripts/parse_migrations.py`.

## Methodology (6 checks)

1. **Query inventory**: `rg -n '\.from\(\s*["\']([a-z_]+)["\']' src/features src/lib` → table per line, then read each action file for select/insert/update columns.
2. **Schema ground truth**: parse migrations (script above) for CREATE TABLE cols, ALTER ADD COLUMN, CHECKs, FKs, `CREATE FUNCTION` signatures, policies. NOTE: live DB can be AHEAD of the migration files (applied via SQL Editor) — files are the reviewable contract; probe live tables with PostgREST curl when a column's existence is in doubt.
3. **Embeds need declared FKs**: every PostgREST embed (`categories(name)`, `staff:submitted_by(name)`, `fa:from_account_id(name)`, `invoice_lines…invoices(entity_id,status)`, `suppliers…purchase_orders(total)`) silently degrades/errors if the FK isn't in a migration. `.or()` with dotted embed paths only works for to-one relations.
4. **RPC arg names must match the migration's `CREATE FUNCTION` exactly** (notify_user: p_user_id/p_entity_id/p_kind/p_title/p_body/p_link). Undefined args (e.g. `(await …maybeSingle()).data?.user_id` on a vanished row) get dropped by JSON serialization → PostgREST 42883 "function does not exist".
5. **CHECK drift**: every status write must be inside the column's CHECK list. Also flag statuses the CHECK allows but the app can never write (invoices 'overdue': transition map has `overdue: []` → overdue filter always empty).
6. **Cross-feature**: grep callers of every exported action after refactors (dead exports survive silently); check TTL caches for mutation-blindness.

## Recurring finding classes seen in this audit

- **Module-scope TTL caches are mutation-blind** — healthCache (accounts/actions.ts:75), debtsCache (assets/actions.ts:72), goalsCache (goals/actions.ts:8), entityCache (business/actions.ts:23), currencyCache (settings/actions.ts:19, 20s), client `shareTTL` (client-cache.ts, 60s). None invalidated by their tables' writes → stale money displays up to 20–60s (e.g. setCurrency never clears currencyCache). Fix: delete key on mutation.
- **Stale "schema has no column" logic survives schema growth** — code + comments claim a column doesn't exist after the migration added it (passive-income/actions.ts still hardcodes `yieldPct: null, amount: 0` after 015 added `investments.yield_pct`, while investments/actions.ts already reads it). Grep for outdated schema claims after each migration.
- **Committed redaction artifacts** — literal `apiKey: ***` in `src/app/api/ai/chat/route.ts:90` (verified via `sed -n '85,95p' | cat -A` + python `repr(data[i:i+60])`): invalid TS, breaks build + feature. When a source line looks like a redaction, check RAW BYTES — display layers redact, the file may be genuinely corrupted.
- **Dead exports after merged-action refactors** — dashboard/actions.ts: getMonthlyStats, getMonthlyTrend, getLiquidIlliquidBreakdown, getSpendingBreakdown, getLastMonthStats, getCurrency, getNetWorthTrend (only getNetWorth is live, via forecast). Harmless but keep the grep habit.
- **Cross-entity guards on FKs**: invoice→customer, PO→supplier pre-checked with `.eq('entity_id', entityId)` — keep that pattern on any new FK write.

## Findings from 2026-08-05 audit (as-of state; re-verify before fixing)

| # | Sev | Location | Issue / one-line fix |
|---|-----|----------|----------------------|
| 1 | CRIT | src/app/api/ai/chat/route.ts:90 | Literal `apiKey: ***` (committed redaction artifact) — invalid TS, breaks route+build. Fix: `apiKey: aiRow.api_key,` |
| 2 | HIGH | src/features/passive-income/actions.ts:34–36,68–69 | Hardcodes `yieldPct: null, amount: 0` despite 015 + getPortfolioWithPrices returning yieldPct/estMonthly → Passive Income KPIs always 0. Fix: map h.yieldPct/h.estMonthly into sources. |
| 3 | MED | src/features/settings/actions.ts:8–16 vs 19–33 | setCurrency never invalidates currencyCache (20s TTL) → old currency symbol up to 20s. Fix: delete cache key in setCurrency. |
| 4 | MED | healthCache/debtsCache/goalsCache/entityCache/shareTTL | Mutation-blind TTL caches → stale money/status up to 20–60s. Fix: invalidate on write. |
| 5 | LOW | src/features/automation/actions.ts:102,119 | `p_user_id` can be undefined → arg dropped → RPC 42883 (race only). Fix: guard `if (!ownerId) continue;`. |
| 6 | LOW | dashboard/actions.ts:110–224 | 7 dead exports (see above). Fix: delete. |
| 7 | LOW | sales/actions.ts:12–18 | 'overdue' unreachable (TRANSITIONS `overdue: []`, nothing writes it). Fix: sweep cron sent+due<today→overdue, or drop the filter. |
| 8 | LOW | assets/actions.ts:146–161 | Debt sim hardcodes 0% APR / balance÷24 (schema has no apr/min_payment cols). Fix: migration + inputs, or label "0% APR projection". |

## Verified clean (don't re-hunt)

notify_user arg names (all 4 call sites) · every embed FK-backed (001/003/005/008/012/013) · all status writes within CHECKs (transactions/invoices/POs/payroll_runs/expense_claims/loans) · ai_settings RLS `auth.uid() = user_id` fits route+settings · net_worth_snapshots upsert onConflict matches UNIQUE(entity_id, snapshot_date) · outstanding_payables view columns · incoming_qty/incoming_eta/note (010) usage · weekSpend/monthNoSpend both consumed.
