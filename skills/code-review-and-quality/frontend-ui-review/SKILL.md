---
name: frontend-ui-review
description: Use when reviewing UI/frontend diffs before merge.
---

# Frontend / UI Change Review

Review gate for UI-heavy diffs (design-system waves, token rebases, component refactors, empty-state sweeps). Verdict = APPROVE or REQUEST_CHANGES + numbered findings (severity | file:line | issue | one-line fix).

## Process

1. **Diff to file, tsc in parallel.** `git diff HEAD > /tmp/change.diff` and read it in chunks; kick `npx tsc --noEmit` off in the background at the same time. Review is blocked on nothing.
2. **Verify against current files, not just hunks.** Grep the live file for every claimed behavior. Dead code and missed call sites hide outside the diff.
3. **Check every named acceptance criterion** from the brief (e.g. "popover handles outside-click + Escape") — a failing named criterion is a MEDIUM at minimum and can justify REQUEST_CHANGES even when nothing else is broken.
4. **Report:** verdict first, then findings ordered by severity, one-line fix each. Say what was verified clean so the author doesn't re-check it.

## Bug classes to hunt (all caught in real reviews)

### Hooks rules
All new `useState`/`useRef`/`useMemo` must sit above every early return (loading/error gates). Grep the top of each touched component; a state added below a `if (loading) return` is a crash.

### Backdrop-only popovers
Custom (non-Radix) dropdowns/menus that close via a `fixed inset-0` backdrop usually **lack Escape-to-close and focus return** — keyboard users can't dismiss. Detection: grep for `keydown`/`Escape`/`onKeyDown` near the popover. Fix: one `useEffect` listening for Escape when open (mirror the codebase's existing drawer/palette pattern).

### Stale-response guards
`const f = filters; ... if (ref.current !== f) return;` — the early return still runs `finally { setLoading(false); setUpdating(false); }`, clearing the loading indicator while the NEWER fetch is still in flight. Fix: guard the finally with the same ref comparison. (Cosmetic only — list data stays correct — but flag it.)

### "Skeleton only before first load" refs
`loadedOnce`-style refs are usually set in only ONE fetch path; the mount path (`loadPage` etc.) forgets it, so the **first** filter change / post-mutation refetch still flashes the full skeleton — exactly the behavior the change claims to remove. Fix: set the ref at the end of every success path, including mount.

### `key={value}` remount-for-animation
Pattern: `<div key={card.val} className="stat-enter">` to replay an entrance animation on value change. **Safe** when the keyed element is a single child inside a per-item Card (no sibling collisions). **Unsafe** when list siblings can share the value (two cards both $0 → duplicate keys, animation breaks, console warnings). Fix: `key={`${label}-${val}`}`.

### Inline confirm replacing `window.confirm`
Verify: trigger keeps its `aria-label` (it usually gets dropped), buttons are keyboard-reachable, `confirmId` is cleared on success AND cancel, and no `window.confirm` remains in that flow. Check sibling files too — sweeps routinely miss 3-5 pages (flag as scope note, not blocker).

### Extracted helper never called
A `doDelete`-style helper is defined but the row handler inlines the same body instead of calling it. Detection: grep the function name for call sites. Fix: call it or delete it.

### Declared-but-unused tokens/utilities
`--ease-premium: cubic-bezier(...)` declared in globals.css, consumed nowhere. Grep the token name across `src/`. Fix: delete, or wire it into a utility.

### Non-reactive time displays
`Updated {Date.now() - updatedAt.getTime() < 60_000 ? "just now" : ...}` evaluated at render only — goes stale after 60s idle. Fix: capture the label at set time, or add a tick.

### Empty-state copy vs active filters
Refactored EmptyState shows first-run copy ("Add your first transaction…") even when filters match nothing. Fix: branch on `activeFilterCount > 0`.

### Component API consistency
Empty-state/stat-card refactors: keep legacy props (`description`) for back-compat, and grep all call sites for one consistent prop set. Mixed `copy`/`description`/`ctaLabel` usage across 17 files is the norm — call out stragglers.

## Verification

- `npx tsc --noEmit` must be clean; report the exit code.
- Filters/query semantics: verify the refactored controls write the same fields with identical sentinel handling (`"all"→""`, `"__all__"→""`, bool flags) — compare against the pre-change diff, don't assume.
- A11y: accent bars/indicators added for styling must be `aria-hidden`; active nav should keep `aria-current` semantics.
