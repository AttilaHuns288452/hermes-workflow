# CashFlow OS Pro Polish — 2026-08-20 Session

## Context
Repo: `cashflow-os` (Next.js 16 + React 19 + Supabase). Prior state: 4-group IA + PageHeader sweep done (5941c73). Luna audit rated product 8/10, IA 6/10, money-model 5.5/10 — fix spine before more features. 5 parallel subagents dispatched via `delegate_task(tasks=5)`.

## Migrations (commit 18c1bf6)
- **024_budgets_period.sql**: `budgets.period DATE` first-of-month, backfill `COALESCE(created_at,NOW())`, `SET NOT NULL DEFAULT date_trunc('month',CURRENT_DATE)`, `UNIQUE(entity_id,category_id,period)`.
- **025_account_link.sql**: `transactions.account_id uuid REFERENCES accounts(id) ON DELETE SET NULL`, indexes, `adjust_account_balance` RPC `SECURITY DEFINER`.

Both committed but Supabase cloud not yet migrated — app degrades (`PGRST202` → "migration pending").

## Subagent tracks
1. Financial spine — picker/badge/filter + bulk category/tag + XLSX export
2. Dashboard — single Needs Attention rail + persisted disclosure
3. Navigation — sub-links visible when expanded, CommandPalette flatMap, 15 redirects canonical comment
4. Ledger — chip summary + bulk + tabular-nums
5. Wealth — `lib/net-worth.ts` single source + BalanceSheet print + pace

## Verification
- `tsc --noEmit` 0, `next build` 43/43 static (Vercel 59s)
- `adjust_account_balance` verified via `curl POST /rest/v1/rpc/adjust_account_balance` → `{"error":"Not allowed"}` (correct guard) after SQL Editor run.
- `budgets.period` → `2026-08-01` sample, `transactions.account_id` → `null` rows.

## Supabase apply (no Docker)
Dashboard → SQL Editor → paste 024 then 025 → verify `information_schema.columns` + `pg_proc`.

## Deploy
`npx vercel deploy --prod --cwd . --yes` (not `--prefix`). Aliased `cashflow-os-mu.vercel.app` Ready.
