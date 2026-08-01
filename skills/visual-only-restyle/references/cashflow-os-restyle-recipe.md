# CashFlow OS restyle recipe (proven)

Project: `C:/Users/Attila/Documents/Projects/cashflow-os` — Next.js App Router, Tailwind v4, shadcn, Supabase via `@/lib/entity` (`getEntity()` → `{ supabase, entityId }`).

## Token utilities (landed in src/app/globals.css by foundation agent)
- `:root` light = prototype look: `--bg #f8f9fb`, `--surface #fff`, `--fg #1a1d23`, `--border #e5e7eb`, `--accent #2563eb`, `--green #16a34a`, `--red #dc2626`, `--orange #ea580c`, `--purple #7c3aed`, `--radius 0.5rem` (8px; `rounded-xl` = 12px).
- `.dark` keeps existing oklch values; status colors get lighter variants (`--green: #22c55e` etc.).
- `-soft` variants via `color-mix(in oklch, <c> 10%, transparent)` → utilities `bg-green-soft`, `text-green`, `stroke-green`, `bg-fg-soft` (progress track), `border-green/30`.
- Fonts: `font-display` (Iowan Old Style/Charter/Georgia serif), `font-sans`, `font-mono`. Global `h1,h2,h3 { font-family: var(--font-display) }` — CardTitle divs need explicit `font-display`.
- shadcn mapping: `--background: #f8f9fb`, `--card: #ffffff`, `--primary: #2563eb`, `--muted-foreground: #6b7280`, `--input: #d1d5db`, `--ring: #2563eb`.

## Standard section markup
- Page header: mono eyebrow (`Portfolio · Net Worth` / `Personal Finance · July 2026`) + serif `text-2xl md:text-3xl font-bold` + muted subtitle; actions right.
- Summary stat card: eyebrow label, `font-mono text-2xl font-bold tabular-nums` value (colored for +/-), muted sub-line, 36px `rounded-lg` soft-tint icon chip.
- Section header inside cards: mono eyebrow + `CardTitle className="font-display text-lg font-bold"`.
- Table: thead `font-mono text-[11px] uppercase tracking-[0.05em] text-muted-foreground`, numerics `font-mono tabular-nums text-right`, P&L `text-green`/`text-red` with explicit +/-.
- Alerts: `border-l-[3px]` + soft bg (`bg-green-soft border-l-green` etc.) + 8px dot, level tiers ok/warn/error.

## Section recipes
- **Donut with center label**: Recharts `<Pie innerRadius={62} outerRadius={95} paddingAngle={2} strokeWidth={0}>` + `Cell` per slice from frozen palette `["#2563eb","#16a34a","#ea580c","#7c3aed","#dc2626"]`; center overlay = absolutely-positioned flex column over the chart (`pointer-events-none`), value + "Total". Legend rows: 12px color square, name, mono value, right-aligned pct.
- **SVG health ring**: `viewBox="0 0 120 120"`, `r=52`, track circle `stroke-border` + progress circle `strokeDasharray={C}` `strokeDashoffset={C*(1-score/100)}` (`C = 2π·52`), `strokeLinecap="round"`, `-rotate-90`; center = score + "/100". Stroke color by tier (≥60 green / ≥40 orange / else red).
- **CSS bar chart**: group holdings by `asset_type`, `style={{ height: % }}` fills `rounded-t-md`, mono value above, label below; `bg-fg-soft` for tracks.
- **Goal/budget cards**: name + colored pct, `h-2 rounded-full bg-fg-soft` track with colored fill `style={{ width: min(pct,100)% }}`, mono "X of Y" meta. Budget fill tier: `bg-green` ≤50, `bg-orange` ≤100, `bg-accent` over.

## Action inventory (compose across features, never add)
- `@/features/goals/actions` → `getGoals()` → `{ id, name, current_amount, target_amount }`; emergency fund = goal whose name matches `/emergency/i`.
- `@/features/budgets/actions` → `getBudgetVsActual()` → `{ id, category, budget, spent, remaining, pct }` (month-scoped).
- `@/features/accounts/actions` → `getHealthScore()` → `{ score, savingsRate, debtRatio, income, expense }`.
- `@/features/assets/actions` → `getDebts()` → `{ id, name, amount }`.
- Server actions are typed client-side: `type X = Awaited<ReturnType<typeof action>>[number]`.

## Feature layout
- `src/features/<name>/components/*.tsx` = restyle target; `src/features/<name>/actions.ts` = "use server" actions (`getEntity()` → supabase → `revalidatePath`); `src/app/<name>/page.tsx` = thin wrapper, untouched.
- Standard mutation: `{ error } | { success: true }`; delete buttons call action then re-fetch.
- Component data flow: `fetch()` in `useEffect`, `loading` gate early-returns "Loading...", empty states render message.

## Verification
- `npx tsc --noEmit` → exit 0. Full `npm run build` reserved for the orchestrator (parallel builds corrupt `.next`).
