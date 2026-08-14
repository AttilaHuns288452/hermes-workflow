---
name: readability-refactor
description: Use when asked to make code simpler, readable, or organized.
---

# Readability Refactor

For this user: BSCS student, learning React. Wants comment-rich code and a plain-language walkthrough after ("what happens when I click X"). Treat "make it readable" as a teaching task, not just a formatting pass.

## Workflow

1. **Read every file first** (small app → batch full reads, they're cheap). Then plan.
2. **Plan before editing.** This user asks "report me what will you do first" — deliver a numbered before→after plan and let them approve. Use `clarify` when there's a real scope choice (backup? full refactor vs readability-only?).
3. **No git → offer a backup** (copy folder) before touching anything. If they decline, proceed carefully — verify with lint+build at the end.
4. **Zero behavior/visual change policy.** Preserve every className string verbatim unless it's a genuine typo fix. No redesign, no new features, no renaming exports. The exception: fix real typos (see pitfalls) and report them.
5. **Common simplifications** (only what's actually dead):
   - Remove unused `import React from 'react'` (Vite JSX transform doesn't need it)
   - Remove `useState` copies that shadow props and whose setters are never used — use props directly
   - De-duplicate repeated markup with an array + `.map()` (preserve the one special-cased item via a flag like `active: true`)
   - Extract hardcoded data out of the component into `src/data/<name>.js`
   - `cond ? <X/> : null` → `cond && <X/>`
   - Rename cryptic state (`page` → `view`) and add a comment-header explaining the state machine + one comment per JSX section
6. **Never delete files** (guardrail). Flag dead boilerplate (unused .css, unused assets in src/assets) for the user to delete manually — verify with grep that nothing references them.
7. **Verification** (user's bar: end-to-end):
   - `npm run lint && npm run build`
   - Dev-server smoke: `terminal(background=true)` → `npm run dev`, then separate call `curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/` (expect 200) and check `id="root"` in HTML, then kill the process.
   - Note: foreground `(npm run dev &)` is blocked by the terminal guard — use background=true.
8. **Deliver before/after summary** — per-file table, what changed, what was verified. Offer a preview/visual check.

## Pitfalls: invisible Tailwind class failures

This user's code has had these twice — grep className strings when a style "doesn't look right":
- **Typo'd utility names**: `transistion-all` (→ `transition-all`), `z50` (→ `z-50`). Invalid classes are silently dropped by Tailwind JIT — no build error.
- **Missing space before `${...}` interpolation**: `duration-200${active?'bg-blue-600...'}` glues into `duration-200bg-blue-600` — a dead class, so the active state never renders. Always a space before the `${`.
- `hover bg-slate-300` (space instead of colon) — modifier never applies.
- Same root-cause class as `bg-${color}-600` dynamic classes (see karpathy-guidelines): Tailwind only compiles complete literal class strings.

## Report format

Per-file table: file | before problem | after fix. Then verification results (lint/build/HTTP). Then the "for you to delete manually" list. Then a plain-language flow walkthrough if the user said they don't understand something.
