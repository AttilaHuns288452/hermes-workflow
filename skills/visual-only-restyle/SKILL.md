---
name: visual-only-restyle
description: Restyle an existing feature page to match a prototype/design while keeping ALL logic, data fetching, and server actions identical. Use when the user says "visual classes only", "keep logic untouched", or assigns one screen of a multi-screen prototype transplant. Covers parallel-agent file ownership, composing existing server actions for new sections, and token-based styling. Proven on CashFlow OS (investments + transactions screens).
---

# Visual-Only Restyle

Restyle an existing app page to match a reference design (HTML prototype, mockup, design spec) WITHOUT touching behavior. Proven on CashFlow OS (Next.js App Router + Tailwind v4 + shadcn + Supabase) across the investments + transactions screens.

## When to Use
- "Restyle X to match <prototype>" / "visual classes only" / "keep ALL logic, data fetching, server actions, states identical"
- You're one dispatched agent in a multi-screen prototype transplant (`design-prototype-transplant` covers the orchestrator side; this is the executor side)
- Design tokens already exist in globals.css — you apply them, you don't create them

## Workflow

### 1. Survey ownership before editing
- `git status --short`: uncommitted changes in shared files (globals.css, layout, sibling feature dirs) = another agent's in-flight work. Do NOT edit those; build on them.
- Re-read shared files FRESH even if you read them earlier — stale reads are real (a globals.css read showed no tokens; a re-read showed the full system, landed mid-session by the foundation agent).
- Read the target component fully; keep every state/fetch/action verbatim. Route pages are thin wrappers — the restyle lives in the feature component.

### 2. Apply the token system, don't reinvent it
- Surfaces: `bg-background` (page), `bg-card` + `border` (cards), `rounded-xl` for large cards, small chips `rounded-lg`.
- Status colors via Tailwind v4 `@theme`-mapped utilities: `text-green/red/orange/purple/accent`, soft chips `bg-green-soft` etc. (`color-mix` ~10% tints).
- Serif display headings: `font-display` (add explicitly on CardTitle divs — the global `h1/h2/h3` serif rule doesn't reach them). Eyebrows/meta: `font-mono text-[11px] uppercase tracking-[0.06em] text-muted-foreground`. All money: `font-mono tabular-nums`.
- Pill badges: `inline-block rounded-full bg-*-soft px-2.5 py-0.5 text-xs font-semibold text-*`.
- Derived severity tiers (e.g. budget fill colors green ≤50% / orange ≤100% / blue over) keep the visual meaningful without new data.

### 3. New sections under a freeze = derive or compose, never query
- Derive client-side from data already fetched in your component (alerts from holdings, allocation-by-type, month-to-date stat cards from the loaded list).
- Compose EXISTING server actions from other features — they're just async functions (e.g. `getGoals`, `getBudgetVsActual`, `getHealthScore`, `getDebts`). Importing one across features is not a logic change.
- Type results: `type X = Awaited<ReturnType<typeof action>>[number]` (or `NonNullable<...>` for nullable returns).
- If no existing action anywhere returns the data, DROP the section (render nothing) — never add a query/action/table under a freeze. Say so in the summary.

### 4. App-wide polish pass (many pages, one pattern)

When the task is "make every page consistent" (headers, hover, focus rings) rather than restyle one screen:

- Read the spec's polish section FIRST — it usually names the non-compliant components and the reference pages that already have the pattern (e.g. "pattern exists in Dashboard/PortfolioView/TransactionList — apply to Accounts, budgets, calendar…"). That list IS the audit.
- Read the named reference pages to extract the EXACT canonical markup, then `grep -rn "<h1" src` (terminal grep — see pitfalls) to find every non-compliant header. The task's prose description of the pattern is a paraphrase; the reference pages are ground truth. Normalize the references too — a "pattern" cited in the spec often has drifted variants (mono line below h1 instead of eyebrow above, missing `font-display`).
- Canonical header block (eyebrow ABOVE, serif h1, muted subtitle below):
  ```tsx
  <p className="font-mono text-[11px] uppercase tracking-[0.06em] text-muted-foreground">EYEBROW</p>
  <h1 className="mt-1 font-display text-2xl font-bold md:text-3xl tracking-tight">TITLE</h1>
  <p className="mt-1 text-sm text-muted-foreground">SUBTITLE</p>
  ```
  The global `h1/h2/h3 { font-family: var(--font-display) }` rule already makes h1 serif — add `font-display` anyway so the markup self-documents. Headers with action buttons keep `flex items-start justify-between gap-4` (pattern block left, buttons right). Centered report headers keep `text-center` but still get eyebrow + h1 + subtitle.
- The task may describe an effect with literal utilities (e.g. "hover:-translate-y-0.5 hover:shadow-md transition"). Check globals.css for an existing mechanism (`.card-hover` global class) BEFORE inlining — reuse it, don't add both (double transform/shadow = visual conflict). The parenthetical describes the effect, not the required implementation.
- Focus rings: change the BASE component once, not every call site. shadcn `button.tsx`/`input.tsx` `focus-visible:ring-1 ring-ring` → `ring-2 ring-primary/50` covers the whole app. Add explicit rings ONLY on raw (non-shadcn) elements at their call sites (plain `<button>`, bare `<input>`). Radix-based triggers (Select) already get `focus:ring` — leave them.
- Dropping an icon from a header orphans its import. Project AGENTS.md often has "No unused imports" as a quality bar — clean imports by hand; `tsc --noEmit` may NOT flag them (noUnusedLocals may be off).
- Verify: `npx tsc --noEmit` PLUS a negative grep — re-run the audit pattern and confirm only non-header hits remain (e.g. `text-2xl font-bold` still matches stat values; headers should be zero).

### 5. Verify
- `npx tsc --noEmit` → exit 0 is the done signal. Never `npm run build` in a shared repo (parallel builds fight over `.next`).
- Unused imports fail typecheck under `noUnusedLocals` — drop imports your restyle orphans (e.g. Badge replaced by pill spans).

## Pitfalls
- Editing a file another agent has uncommitted changes in = silent conflict for the orchestrator. Git status first, always.
- Duplicating tokens another agent already landed in globals.css = drift. Read the file fresh; use what's there.
- "Visual classes only" does NOT mean "don't touch the component file" — it means don't change behavior. Rewriting JSX is expected; keep handlers/actions byte-identical.
- `search_files` fails on this Windows host with absolute `C:/...` paths (rg errors "IO error … /c/Users/…: The system cannot find the path specified" — it resolves the path MSYS-style and misses). Fall back to terminal `grep -rn`/`find`/`ls` after `cd` into the project — and prefer it outright for audit greps. Relative paths may work in search_files but don't burn a call discovering it.

## References
- `references/cashflow-os-restyle-recipe.md` — concrete tokens + section recipes (donut center label, SVG health ring, bar charts, budget fills) proven on CashFlow OS.
- `references/cashflow-os-polish-pass-recipe.md` — canonical page-header block, per-page eyebrow/subtitle map, `.card-hover` reuse, central focus-ring bump, negative-grep verification.
