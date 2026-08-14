# Dashboard spreadsheet widgets (weekly-spend; nospend-calendar DELETED)

> **2026-08-06 UPDATE:** `nospend-calendar.tsx` was **deleted** (user call: "no spend
> day tracker is useless") and `monthNoSpend` was removed from `getDashboardData`
> + DashboardPage (import/state/setter/render). The shared dayTxns query is now
> **week-bounded**: `.gte("date", weekStart).lte("date", todayStr)` and feeds ONLY
> `weekSpend` (no more month window, no `getDaysInMonth`). Do NOT re-add the widget
> or expect `monthNoSpend` to exist — grep before trusting this file's old text.

Built 2026-08-04 sprint. Mirrors the user's personal-finance spreadsheet: a weekly
M/T/W/Th/F/Sat/Sun grid and a no-spend-day calendar.

## Data: one field, ONE merged query (getDashboardData)

Appended at the END of the existing Promise.all batch:

```ts
// ponytail: one query feeds the weekSpend buckets — fetch from week start
supabase.from("transactions")
  .select("type, amount, date")
  .eq("entity_id", entityId)
  .eq("type", "expense")
  .neq("status", "rejected")
  .gte("date", weekStart)
  .lte("date", todayStr)
```

Bucket in JS: `weekSpend` = 7 entries Mon..Sun, weekday label via
`format(new Date(t.date + "T00:00:00"), "EEE")` (last-7-days window always contains
exactly one of each weekday). Return object carries only `weekSpend` now.

## Widget structure (frozen design)

Both live in `src/features/dashboard/components/` (colocated, not `components/ui`),
are `'use client'`, and follow: flat `Card className="card-hover"`, mono eyebrow
(`font-mono text-[11px] uppercase tracking-[0.06em] text-muted-foreground`), serif
title (`font-display text-lg font-bold tracking-tight`), compact header (`pb-2`).

- **weekly-spend.tsx** — 7 flex-1 day cells (day letter + `text-xs tabular-nums`
  amount, `bg-accent-soft` on today's cell, `—` when total is 0) + right-aligned
  Week total column (`ml-auto border-l pl-3`, `font-mono text-base font-bold`).
- **nospend-calendar.tsx** — Sun-first `grid grid-cols-7 gap-1`, `h-7` day cells;
  spent>0 → `absolute right-1 top-1 h-1 w-1 rounded-full bg-red` dot; no spend →
  `bg-accent-soft/40 rounded-md`; future days → `text-muted-foreground/40`; today →
  `border border-accent`. Below: `Goal <b>10</b> · No-spend · Spend` mono text-xs
  row (`border-t pt-2.5`), goal hardcoded via `NO_SPEND_GOAL = 10` + ponytail
  comment. Counts only dates `<= today`. Returns null when `data.length === 0`.

## SSR date handling (hydration-safe "today")

`new Date()` in render disagrees between SSR (UTC) and client (local) — compute in
post-mount state instead:

```ts
const [today, setToday] = useState<string | null>(null)
useEffect(() => { setToday(format(new Date(), 'yyyy-MM-dd')) }, [])
```

Render neutral (no highlight/muting) until `today` is set. Same pattern as the
dashboard greeting.

## Grid placement (DashboardPage)

Rendered in a 2-col row (`grid gap-4 grid-cols-1 lg:grid-cols-2`) immediately after
the 4 stat cards, before Quick Add. Wired via new useState + applyData setters +
`initialData?.field ?? []` defaults; the DashboardData type is derived from
`ReturnType<typeof getDashboardData>` so new fields flow automatically.
