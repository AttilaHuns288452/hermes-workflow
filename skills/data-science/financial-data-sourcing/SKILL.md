---
name: financial-data-sourcing
description: Wire live market prices or import spreadsheets into DB apps.
---

# Financial Data Sourcing

Two recurring jobs: **live prices** (which provider actually works) and **importing the user's spreadsheet data** into the app's DB. Both are empirical — provider availability and Excel quirks change; verify before wiring.

## Real-time quote providers (verified Aug 2026)

**Keyless sources are dead from cloud/datacenter IPs** (Vercel, most VPS): Stooq serves a JS proof-of-work challenge, CNBC is Akamai-blocked, MSN requires auth. Do not re-test these per project.
**Yahoo is a special case (verified Aug 2026):** keyless requests WITHOUT a browser `User-Agent` header get `Edge: Too Many Requests` from every IP — WITH `User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36` it serves quotes AND history (`/v8/finance/chart/<TICKER>?interval=1d&range=1mo|6mo|1y` → `chart.result[0].timestamp[]` + `indicators.quote[0].close[]`) from servers. It's the only keyless history source that works — use it as the history fallback (Finnhub free tier 403s on `/stock/candle`).

| Asset class | Provider | Key | Notes |
|---|---|---|---|
| Crypto | **CoinGecko** (`/api/v3/simple/price?ids=X&vs_currencies=usd&include_24hr_change=true`) | none | Works keyless from servers; 24h change included; ticker→id map needed (BTC→bitcoin…) |
| US stocks/ETFs | **Finnhub** (`/api/v1/quote?symbol=AAPL&token=KEY`) | free at finnhub.io | Real-time; returns `{c: current, d, dp: changePct, h, l, o, pc}`; ~60 calls/min free; 40-char key |
| US stocks/ETFs (fallback) | **Twelve Data** (`/api/v1/quote?symbol=AAPL&apikey=KEY` → `{close, percent_change}`) | free at twelvedata.com | Works from cloud IPs (unlike Yahoo); ~8 calls/min / 800/day free; 32-hex key. Good middle fallback: Finnhub → Twelve Data → Yahoo |
| PSE (Philippines) | none on free tiers | — | Finnhub doesn't cover it; Yahoo `.PS` feed is DEFUNCT even with UA (BDO.PS returns stale 2019 MUTUALFUND rows, SM.PS empty). **Twelve Data free tier ALSO rejects PSE** (verified Aug 2026 with a real free key: `404 "This symbol is available starting with the Ultra or Enterprise plan"` — a plan-tier error, not an auth error; auth passes, symbol class doesn't). PSE needs a PAID plan on every keyed provider → defer rather than ship a brittle scrape. Board-block the feature with the evidence |

Wiring pattern (Next.js server): `FINNHUB_API_KEY` env var, `fetch(..., { next: { revalidate: 60 } })` (60s = "real-time enough" without rate-limit pain), fallback chain Finnhub → Twelve Data (`TWELVEDATA_API_KEY`, cloud-IP friendly) → Yahoo+UA → null → UI shows `—` and falls back to cost basis. Enrich holdings with `{ price, changePct }` and render ▲/▼ %. Add an 8s `AbortSignal.timeout` on EVERY market-data fetch — a hung provider otherwise freezes the page in "Loading" forever (hit this in prod: no timeout = stuck skeleton; the fix is the timeout, not the provider).

**FX conversion (USD prices → entity currency, verified Aug 2026):** **Frankfurter** (`https://api.frankfurter.app`, ECB rates, keyless, daily — holiday-safe) primary: `GET /latest?from=USD&to=PHP` → `{rates:{PHP: 61.0}}` (Node fetch follows the http→https redirect natively; curl needs `-L`). Convert HISTORY at per-day rates with ONE time-series call: `GET /2026-07-06..2026-08-05?from=USD&to=PHP` → `{rates: {date: rate}}` — apply each point's date rate, fall back to today's rate for missing dates (curve shape stays honest, absolute values drift). Fallbacks: `open.er-api.com/v6/latest/USD` then CoinGecko USDT→fiat (`simple/price?ids=tether&vs_currencies=php`). Any failure → rate 1 (show USD rather than crash). Cache FX hourly (`revalidate: 3600`), prices 60s.

Full matrix, API shapes, and failure signatures: `references/market-data-providers.md`.

## Spreadsheet → database import

When the user says "import my Excel file": the file almost never looks like a clean table. Recipe (full detail in `references/excel-import-pattern.md`):

1. **Inspect with openpyxl `read_only=True, data_only=True`** — never pandas-first (formula sheets break it).
2. **Probe occupancy, don't trust row counts**: finance-tracker templates pre-fill ~8k formula rows; real data is often a handful of rows. Count non-empty cells per column to find where the actual table lives.
3. **Watch the empty-row offset**: blank row 0 before the title, header at index 2 — column indices shift. Print raw rows with indices before assuming.
4. **Check all copies of the file** — users keep duplicates (`file (1).xlsx`) that may differ.
5. **Verify the target account exists** without a password: `POST /auth/v1/token?grant_type=password` with a bogus password → `invalid_credentials` = account exists; `email not registered` = doesn't.
6. **Import via generated SQL** (user pastes in Supabase SQL Editor — the postgres role bypasses auth): a `DO $$` block that resolves `auth.users` by email, upserts the entity, creates categories with `NOT EXISTS` guards, and inserts transactions with an idempotency guard (skip if entity already has rows). Present the SQL in chat explicitly: "copy the code block, not the file name".
7. Map categories honestly: Income→income, everything else→expense; savings/transfer rows are expenses in the source ledger — note that they could be transfers later, don't silently reclassify.

### In-app import (server action + file upload) — pitfalls found in the cashflow-os build (Aug 2026)

When the app itself parses .xlsx/.csv via SheetJS in a server action:

- **Next.js 16: `serverActions.bodySizeLimit` must go under `experimental`** — the root-level key logs "Unrecognized key(s)" and the 1MB default silently 413s uploads. (Proxy body buffer is a separate 10MB `proxyClientMaxBodySize`.)
- **Zip-bomb**: .xlsx is a zip with ~1000:1 expansion; a 5MB cap permits GBs of heap → OOM the serverless fn. Cap at 2MB AND pass `sheetRows: MAX+10` to `XLSX.read` AND `decode_range(ws['!ref'])` before `sheet_to_json` (which materializes everything).
- **SheetJS on npm is frozen at 0.18.5 with known CVEs** (CVE-2023-30533 RCE/prototype-pollution, CVE-2024-22363 ReDoS). Install the patched tarball: `npm i https://cdn.sheetjs.com/xlsx-0.20.3/xlsx-0.20.3.tgz --save-exact`.
- **Type inference**: don't label rows by category name alone ("Salary"/"Refund" never contain "income" → silently expense). Derive income/expense from the amount SIGN first (keep the sign through normalization, abs() only at insert), name heuristic only as tiebreak.
- **Dedupe must fail closed**: if the existing-rows query errors, abort the import — a silent `seen={}` re-imports duplicates. Order the comparison window (`.order('date', {ascending:false}).limit(10000)`).
- **Approval-workflow parity**: bulk insert must set the same `status`/`submitted_by` as the single-create action, or imports bypass pending/approval on business entities.
- **Header scan**: match `/\bdate\b/`/`/\bamount\b/` — substring matching lets "Updated"/"Validated" win the date column.
- **Result survives refresh**: if the success callback triggers a list reload that swaps in a skeleton, the dialog unmounts and the "Imported N" summary vanishes before rendering. Refresh silently (skip the loading gate) or toast the result.

## Supabase RLS gotchas (found while verifying imports)

- **Audit-trigger RLS class bug**: a trigger that writes to an RLS-enabled table (e.g. `transactions_history` created with only a SELECT policy) makes EVERY user UPDATE/DELETE on the parent fail with 403 `new row violates row-level security policy` — the message truncates the table name, so it reads like the parent table. Symptom: UI delete/edit silently fails; REST DELETE with a user JWT returns 403. Fix: `SECURITY DEFINER SET search_path = public` on the trigger function (canonical audit pattern — it only writes OLD rows, no escalation surface; keep the history table's SELECT policy for reads). **Hardening (ECC review, both must ship with the definer change):** (a) guard the body — `IF TG_TABLE_SCHEMA <> 'public' OR TG_TABLE_NAME <> 'transactions' THEN RAISE EXCEPTION ...` — Supabase grants `CREATE` on schema `public` to anon/authenticated by default, so a user could attach the definer function to a forged table and write arbitrary rows as postgres (latent today, since PostgREST exposes no DDL, but cheap to close); (b) `REVOKE ALL ON FUNCTION <fn>() FROM PUBLIC, anon, authenticated;`.
- **RLS 403 vs 0-rows**: a clean USING-only policy that doesn't match returns 0 rows (silent no-op); a 403 means a policy's WITH CHECK (or a trigger insert) actually failed. Different diagnosis paths.
- **Service-role key can't run DDL** via PostgREST — migrations still go through the user's SQL Editor; the service key only powers REST.

## Verification techniques

- **Authenticated E2E without a password**: playwright login → extract the JWT from chunked `sb-<ref>-auth-token` cookies (join `.0/.1/…` chunks, strip `base64-`, base64url-decode, read `access_token`) → call protected endpoints with `Authorization: Bearer <jwt>`.
- **Screenshot timing** (visual audits): wait ~2s after `domcontentloaded` before interacting (clicking pre-hydration fires a native GET submit); pre-warm routes once — the first hit compiles on demand and screenshots catch skeleton/dev-badge states. Re-capture after 5s settle for steady state.
- **Windows/MSYS E2E scripts**: heredocs eat backslashes — always use forward-slash paths (`C:/Users/...`) inside Playwright scripts. Playwright's coordinate-click can fail to trigger shadcn dialog buttons while `el.evaluate(b => b.click())` (native click) works — keep the native-click fallback for dialog submit buttons.
