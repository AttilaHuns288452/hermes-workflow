# Passive Income Module (built 2026-08-04 sprint)

Feature dir: `src/features/passive-income/` (actions.ts + components/PassiveIncomePage.tsx), page `src/app/passive-income/page.tsx`, sidebar link in AppShell Wealth group after Investments (icon `HandCoins`, already imported).

## Schema facts that shaped it

- **Yield column EXISTS since migration 015 (2026-08-04):** `investments.yield_pct DECIMAL(5,2) NOT NULL DEFAULT 0` (e.g. 3.00 = 3% annual). `getPortfolioWithPrices()` enriches holdings with `yieldPct` (null when 0/unset) and `estMonthly = marketValue * yieldPct / 100 / 12`. The Investments page has an inline-editable Yield column (`YieldCell` in PortfolioView.tsx, calls `updateInvestmentYield(id, pct)` — validates 0–100) plus a yield input in the Add Investment dialog. Passive Income KPIs render '—' + a banner when `!hasYieldData` (no holding has yield set) so zeros never read as computed truth; empty-state branches: no holdings → "Add investments to get started" + link, holdings but no yields → "add dividend yield" hint.
- Dividend history works without schema change: transactions with description **or category name** ILIKE `%dividend%` (user logs 'Investment monthly dividend' income lines with rates).

## getPassiveIncome() shape

```ts
{ sources: { id, ticker, name, type, value, yieldPct, amount }[], monthlyTotal, monthlyProjection, yearlyProjection, passiveRatio, dividendHistory: { id, date, description, amount }[], hasYieldData } | { error }
```

- sources = `getPortfolioWithPrices().holdings` mapped (value = marketValue).
- monthlyTotal = Σ amount; yearlyProjection = monthlyTotal * 12; monthlyProjection = yearlyProjection / 12.
- passiveRatio = monthlyTotal / avgIncome, where avgIncome = income txns over last 3 calendar months (date ≥ startOfMonth(subMonths(now,2))) summed / 3; null when avgIncome ≤ 0 (guarded division).
- dividendHistory = 12 rows, `.or('description.ilike.%dividend%,categories.name.ilike.%dividend%')`, order date DESC, entity-scoped via getEntity().
- 3 parallel fetches in one Promise.all (portfolio, income sum, dividend history).

## UI (frozen design)

Header mono eyebrow 'Wealth · Passive Income' + serif 'What your money does while you sleep'. 3 KPI cards (Monthly / Projected Yearly / Ratio, '—' when null), sources table (ticker, type badge, value, '—' yield, '—' est. monthly), dividend history flat list (date via date-fns `format`), pulse-div loading skeleton (no Skeleton in ui/), error + Retry button. Empty states: 'Add dividend yield to your investments to see projections' / 'No dividend payments recorded yet'.
