# CashFlow OS — Polish Pass Recipe (headers, hover, focus rings)

From the app-wide polish pass (Aug 2026). Applies to `src/features/*/components/*.tsx` + inline pages `src/app/{calendar,inventory,staff}/page.tsx`.

## Canonical header block (every page)

```tsx
<div>
  <p className="font-mono text-[11px] uppercase tracking-[0.06em] text-muted-foreground">Finance · Section</p>
  <h1 className="mt-1 font-display text-2xl font-bold md:text-3xl tracking-tight">Title</h1>
  <p className="mt-1 text-sm text-muted-foreground">Subtitle</p>
</div>
```

Variants:
- Header row with action buttons (Assets, Calendar, Transactions, Portfolio): wrap in `flex items-start justify-between gap-4`, pattern block left, buttons right.
- Centered report pages (BalanceSheet, IncomeStatement): keep the `text-center` wrapper div, same inner block.
- Dashboard: eyebrow `Overview`, subtitle = the dynamic welcome line (it was previously a mono line BELOW the h1 — that's the drift variant; eyebrow goes above).

## Per-page eyebrow / subtitle (as shipped)

| Page | Eyebrow | Subtitle |
|---|---|---|
| Dashboard | Overview | Welcome back{email} |
| Accounts | Finance · Accounts | Manage accounts, transfers, and IOUs |
| Assets & Debts | Finance · Assets | Track assets, debts, and net worth |
| Balance Sheet | Reports · Balance Sheet | As of {today} |
| Budgets | Finance · Budgets | Set monthly limits and track spending |
| Categories | Finance · Categories | Organize your income and expenses |
| Goals | Finance · Goals | Save toward your targets |
| Calendar | Finance · Calendar | Monthly transaction calendar |
| Inventory | Business · Inventory | Track stock and inventory value |
| Staff | Business · Staff | Manage staff members and pending approvals |
| Income Statement | Reports · Income Statement | {data.period} |
| Transactions | Personal Finance · {MMMM yyyy} | (existing) |
| Portfolio | Portfolio · Net Worth | (existing) |

## Icons dropped from headers (remove the orphaned import!)

Wallet (AccountsPage), Target (GoalsPage), Package (inventory page), Users (staff page), FileText (IncomeStatement). AGENTS.md requires no unused imports; `tsc --noEmit` does NOT flag them here — clean by hand.

## Hover: reuse `.card-hover`, don't inline

Task said "hover:-translate-y-0.5 hover:shadow-md transition" but globals.css already has:
```css
.card-hover { transition: transform 150ms ease, box-shadow 150ms ease; }
.card-hover:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
```
Add `className="card-hover"` to interactive cards. Added to: IOU cards, HealthScore/ActivityTimeline widgets, BudgetDashboard, budget cards, goal cards, inventory item cards, staff + pending-approval cards. Cards combining conditional classes use `cn(cond ? "opacity-50" : "", "card-hover")` (import `cn` from `@/lib/utils`).

## Focus rings

- Base: `components/ui/button.tsx` + `input.tsx` — `focus-visible:ring-1 focus-visible:ring-ring` → `focus-visible:ring-2 focus-visible:ring-primary/50`. One-line change covers every Button/Input in the app.
- Raw elements needing explicit rings (they bypass shadcn): calendar nav buttons (`px-3 py-1 border rounded-md text-sm hover:bg-muted transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50`), CategoryManager edit input + category-name button.
- Radix Select trigger already has `focus:ring-1` — leave it.

## Verification for a compliance pass

1. `npx tsc --noEmit` → exit 0.
2. Negative grep: `grep -rn "text-2xl font-bold" src --include="*.tsx"` → remaining hits must be stat VALUES (tabular-nums money), never `<h1>`.
