# Craft sweep — personal finance pages (2026-08-06)

Wave scope: 7 files — `src/features/accounts/components/AccountsPage.tsx`, `assets/components/{AssetManager,BalanceSheet,DebtPayoffSimulator}.tsx`, `budgets/components/BudgetManager.tsx`, `categories/components/CategoryManager.tsx`, `goals/components/GoalsPage.tsx`. Ran as a fix-wave subagent (600s cap, `tsc --noEmit` only, no build, no commit).

## EmptyState adoption
- Component: `src/components/ui/empty-state.tsx` (props icon/title/copy/ctaLabel/onCta/error). Card-wrap it: `<Card><CardContent><EmptyState …/></CardContent></Card>` — matches the page's card rhythm (tables/sections live in Cards).
- Keep the existing copy verbatim as `title`; add a one-line `copy`.
- **CTA only when an add-open state exists** to reuse: AssetManager dialogs → `onCta={() => setShowAddAsset(true)}` / `setShowAddDebt(true)` (pass an `onAdd` prop into the table component). Inline always-visible add forms (accounts/budgets/goals/categories) → NO CTA (redundant, form is 10px above).
- Icons chosen: Wallet (accounts), ArrowRightLeft (transfers), HandCoins (IOUs), Wallet/Building2 (assets/debts), Scale (balance sheet, page-level), Sparkles (payoff — replaces the 🎉), PiggyBank (budgets), Tags (categories ×2), Target (goals).
- BalanceSheet: page-level EmptyState only when assets AND debts are both empty; keep the compact italic section notes ("No liquid assets") otherwise — a report must stay tight. Implement as a `<>…</>` fragment conditional, not duplicated headers.
- Verify new lucide icons exist in the installed version first: `node -e "const l=require('lucide-react'); console.log('HandCoins' in l, 'Scale' in l)"`.

## `.num` ledger numbers
- `.num` (globals.css) = font-mono + tabular-nums + letter-spacing -0.02em. It SUBSUMES `font-mono tabular-nums` — drop both when adding `.num`.
- Apply to money figures ONLY: amounts, totals, balances, net worth, health score value, payoff projections. NOT to % stats (savings rate, budget pct) or dates.
- Keep existing size/weight. Where `.num` would fight `tracking-tight`, drop the tracking class (`.num`'s -0.02em wins by cascade order anyway).

## Inline row-state confirms
- Grep first: NO `window.confirm()` existed in these files (callers lived in other agents' files: TransactionList, SuppliersPage, EmployeesPage, CustomersPage, PurchasingPage, SalesPage, PortfolioView). Report that finding; the one-click trash deletes still got the row-state pattern (explicitly requested):
  - `const [confirmId, setConfirmId] = useState<string | null>(null)` per table component.
  - Trash → `setConfirmId(id)`; row renders `Delete?` span + Cancel (`variant="ghost"`) + Delete (`variant="destructive"`); Delete clears state then `await onDelete(id)`; Cancel clears.
  - Widen the actions header `<TableHead className="w-20">` → `w-32` (the transient buttons are ~150px).

## Goals skeletons
- Replace bare `Loading...` with the page-mirroring pattern: header block (h-3 w-24 / h-8 w-48 / h-4 w-64), New Goal form card (h-24), grid of 4 goal-card blocks (h-44), wrapper `aria-busy="true"` + sr-only "Loading". Use the `Skeleton` component — it IS `animate-pulse rounded-md bg-fg-soft` already.

## Eyebrows
- Mechanical `tracking-[0.06em]` → `tracking-[0.12em]` for every eyebrow in owned files (page eyebrows + stat captions like "out of 100").
- None of these eyebrows labeled a form field (all forms use `<Label>`). If one does: demote to plain `text-xs font-medium text-muted-foreground` — eyebrows are reserved for section labels.

## Palette leftovers
- `text-green-600`/`text-red-600`/`text-red-700`/`text-red-500` → var tokens `text-green`/`text-red` (Tailwind-600/500 shades break dark mode; every other feature file already used `text-red`).
- `border-green-200`/`border-red-200` → `border-green/30`/`border-red/30`.
- No raw hex in owned files (only globals.css token definitions + manifest/layout `themeColor`, which belong to other agents).

## Pitfalls (this host + parallel sweeps)
- **V4A multi-hunk patch fails validation on non-unique old_string** ("Found 2 matches") — add surrounding context to disambiguate or use replace mode with `replace_all: true`.
- **V4A rewrite hunks can silently DUPLICATE** a line when the hunk adds instead of replaces (old+new both present) — inspect the returned diff and re-grep after patching.
- **Concurrent writers:** sibling agents + the parent edit/stage the same repo mid-sweep. Observed: external `git add` of MY files (staged `M `, no unstaged diff — harmless, never unstage/commit), CRLF rewrites, file_size changing between reads, one torn/stale read_file. Verify on-disk state with terminal: `git hash-object <file>` vs `git rev-parse :<file>` (working tree == index), `grep -c` your marker strings; re-read before each patch.
- **search_files on this host:** absolute Windows paths fail (IO error, converted to /c/… MSYS form) — use relative paths from cwd (`src/features/...`). Regex `\(` breaks it ("unclosed group") — drop parens from patterns or use terminal grep.
- `grep -c` exits 1 on zero matches (not an error) — append `|| true` in shell loops.
- tsc: fix ONLY errors in owned files. The only error this wave hit was `IncomeStatement.tsx(62,87) TS2322` — a sibling agent's in-progress edit; report, don't fix.
