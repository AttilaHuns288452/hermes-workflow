# Design-language sweep (frozen-rule class swaps)

Mechanical wave that turns audit line-refs into token-clean UI. The audit refs are a **FLOOR, not a ceiling** — after fixing flagged lines, grep the whole owned file set for the defect class and convert every instance (the audit will have missed same-class rows: extra `text-red-600 dark:text-red-400` lines, KpiCard icon chips, "Reminded" labels). Report beyond-ref extras explicitly.

## Class-swap table (tokens from src/app/globals.css)

| Violation | Replacement |
|---|---|
| `text-red-600 dark:text-red-400` | `text-red` |
| `text-green-600 dark:text-green-400` | `text-green` |
| `text-orange-600 dark:text-orange-400` | `text-orange` |
| `text-emerald-600 dark:text-emerald-400` / `border-emerald-500 …` | `text-green` |
| `text-blue-600 …` / `border-blue-500 …` | `text-accent` |
| `text-violet-600 …` | `text-purple` |
| `text-amber-*` (NO amber token) | `text-orange` |
| `text-[#c2410c]` | `text-orange` (--orange var IS #c2410c) |
| `text-[color:var(--green)]` / `var(--red)` | `text-green` / `text-red` |
| `text-red-500` / `text-green-500` | `text-red` / `text-green` |
| `bg-red-500` / `bg-red-500/20` | `bg-red` / `bg-red/20` |
| `bg-green-500` dot | `bg-green` |
| `bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300` | plain text `text-orange` |
| `accent-blue-600` (checkbox accent) | `accent-accent` |
| soft-bg icon chips (`bg-green-soft text-green` in stat cards) | plain icon, `text-muted-foreground` |
| pills (`rounded-full px-2.5 py-0.5 …` with text) | plain `text-xs font-medium text-<token>` span |
| `<Badge variant="outline" className="border-…">` pills | plain text span; REMOVE the now-unused Badge import |
| gradient (`bg-gradient-to-br from-green-soft to-card`) | `border border-green/30 bg-card` |

## Sweep workflow (proven: 9 files, 49 patches, one pass)

1. Read `src/app/globals.css` FIRST — token list is the source of truth (green/red/orange/purple/accent + `-soft`; NO amber → map amber→orange).
2. Apply via execute_code + `hermes_tools.patch` sequentially in ONE script: per-patch tag, print `OK/FAIL` per call (50-call budget covers ~45 patches). Use `replace_all=True` for repeated strings (`text-red-600 dark:text-red-400` ×8 etc.). Order-dependent pairs: replace `bg-red-500/20` BEFORE `bg-red-500`.
3. Verify with terminal `grep -nE '<palette|dark:|#[0-9a-fA-F]{3,8}|color:var|bg-gradient|Badge|alert\(' <files>` — must return nothing. Use terminal grep, NOT search_files: its pattern passthrough mangles `\b` and leading `-(` on this host (rg flag/regex errors); `grep -nE` is the reliable path.
4. `rounded-full` survivors are FINE if they're progress tracks (`overflow-hidden rounded-full h-1.5/h-2 bg-*` inside a bar, no text) — pills have px/py padding + text content.
5. `npx tsc --noEmit`; fix ONLY your files; report pre-existing errors in other agents' files as out of scope.

## Pitfalls (learned 2026-08-06 sweep)

- **alert()→setErr swap breaks tsc**: `setErr(r.error)` fails TS2345 when the action's error is `string | undefined` (alert() tolerated it). Always `setErr(r.error ?? "Something went wrong")`.
- **In-flight guards need one state + all buttons**: single `pending` value (`null | 'add' | id`), `disabled={pending !== null}` on every mutation button, early-return in each handler, `finally { setPending(null) }`. Guarding the flag but forgetting a button (or vice versa) is the common half-fix.
- **Inline error reuse**: the page usually already has `err`/`fetchErr` state — reuse it for row-action failures instead of adding a new state. Only refetch on SUCCESS; refetching after a failed action clobbers the list with stale data.
- **parseISO conversion**: `new Date(d.date)` → `parseISO(d.date)` requires updating the import line too (`import { format, parseISO } from 'date-fns'`).
- **Stat-card chip removal**: when the chip class is data-driven (`chip: net >= 0 ? "bg-green-soft…" : …`), remove the field entirely rather than leaving a dead conditional; the icon container keeps `rounded-lg` but goes `text-muted-foreground`.
