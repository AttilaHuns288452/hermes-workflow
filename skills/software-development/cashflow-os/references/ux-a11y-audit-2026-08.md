# UX / A11y / Responsive Audit — 2026-08-11 (read-only)

Audit of AppShell, forms, tables, dialogs, loading/empty/error states, mobile, and major routes. Screenshots: `screenshots/ui-batch`, `screenshots/sprint4`, `screenshots/sprint2`. Docs: `docs/DESIGN-SPEC.md`, `docs/UserGuide.md`.

## Method (repeatable)

1. **List screenshots + source tree** (terminal `ls`/`find` — search_files/rg fails on absolute Windows paths on this host).
2. **Batch `vision_analyze`** — 4–6 images per wave, one targeted audit question each (contrast, table structure, dialog, mobile, error states, empty states). Mobile shots may be skeleton/loading states — say so and don't over-read them.
3. **Read the governing source before trusting pixels**: AppShell.tsx, globals.css, ui/*.tsx, feature components.
4. **Verify contrast numerically** from tokens: light `--muted-foreground #575e6c` on white ≈ 6.5:1; dark `#8a8f98` on `#121315` ≈ 5.8:1; dark red `#f87171` ≈ 6.8:1. All pass AA — vision models over-report contrast failures.
5. **Cross-check every pixel finding against current source.** `screenshots/ui-batch` predates the #5e6ad2 rebase (shows #2563eb era) and predates the Cashy orb; dark-mode shots showed the old zinc palette. A stale screenshot finding (e.g. "inactive nav low contrast") is a false positive if tokens changed.
6. **External audit overlays**: the red "1 Issue" pill bottom-left in login screenshots is an external UI-audit tool overlay, NOT an app error. Don't report it.
7. **Report shape**: P0–P3 severity, findings tagged [UI] (pure styling/placement) vs [Functional] (feature/behavior), plus a "verified good" list so the parent knows coverage.

## Findings (live, unfixed at audit time)

### P0
- **QuickFAB covered by Cashy orb on mobile.** `QuickFAB.tsx:20` = `fixed bottom-6 right-6 z-50 md:hidden` (56px); `AIAssistant.tsx:585` orb = `fixed z-50 h-16 w-16 bottom-6 right-6`, no responsive hiding, rendered later in DOM → paints over the FAB. Mobile quick-add dead at default orb position. Fix: orb `bottom-24` on <md, or hide QuickFAB while orb undragged.

### P1
- **Notifications unreachable on mobile.** `NotificationBell` only in desktop header (`AppShell.tsx:823`, header `hidden md:flex`); `/notifications` absent from `navSections`. Add bell to mobile header or a nav entry.
- **No undo for transaction delete** (inline "Delete?" confirm, `TransactionList.tsx:796-817`, permanent). Finance app = data-loss risk; soft-delete + undo toast recommended (toast infra exists, 3.5s auto-dismiss).

### P2
- **Ledger table violates DESIGN-SPEC "no horizontal scroll at 360px"** — 6 columns in `overflow-x-auto`, no sticky header/first col. Mobile card-list variant (`md:` table) or sticky columns.
- **Small touch targets in mobile drawer**: theme/signout/close are `h-7 w-7` (28px) — under 44px rec (passes WCAG 2.5.8 24px min).
- **Custom dropdowns lack menu semantics** (EntitySwitcher, CurrencyDropdown in AppShell): plain button lists, no `role="menu"`/`aria-haspopup`/arrow keys; CurrencyDropdown trigger missing `aria-expanded`.
- **Filter popover not a dialog** (`TransactionList.tsx:650`): no `role="dialog"`/focus trap (has Escape + click-catcher + focus-return).
- **No focus/announcement on route change** — focus stays on sidebar link; no page-change signal for SR users.
- **`h-screen` → `h-dvh`** (`AppShell.tsx:539`) — 100vh clips under mobile browser chrome.
- **Import dialog dead-end error**: "Network error" (`ImportDialog.tsx:45`) no retry/guidance; no drag-drop, no file deselect, no progress indicator (double-submit risk near 5k rows).

### P3
- Inline delete-confirm cramped in `w-20` cell on mobile → dialog on <sm.
- Orb overlaps page content on desktop (calendar card) — draggable, acceptable; add `pb-24` to pages.
- Income metric empty state lacks CTA ("Nothing logged this month" vs weekly-spend's "Add a transaction").
- Business-guard CTA is bare entity name → "Switch to <name>".
- Info (ⓘ) icons on every metric label — wire tooltips or drop.
- Ambiguous flat trend icons when no prior data.
- Ledger: no sort controls, no total count ("showing N of M") — matters at 5k imported rows.

## Verified good (don't re-audit)
Skip link (`AuthShell.tsx:34` → `#main`); mobile drawer focus trap + inert + Escape; `role="alert"`/`aria-live` on all error paths (LoginForm, QuickAddForm, TransactionList, ImportDialog); password show/hide with aria-pressed; `aria-current` nav; reduced-motion block; per-feature skeleton/empty/error (shared `EmptyState` + one CTA); debounced search with stale-response guards; toast `role="status"` offset above FABs on mobile; empty state with CTA on budgets/accounts/transactions; business guard clear message + entity-switch CTA.

## Code-verified fix brief (second pass, same day — feeds the implementation wave)

Re-verified every finding against source with file:line, fix direction, and verification criteria. Screenshots for mobile/table findings are stale (see era trap below) — code is the source of truth.

- **P0 FAB/orb — CORRECTED FIX (earlier "orb bottom-24" suggestion is flawed):** QuickFAB's 4-action menu opens upward ~190px (`QuickFAB.tsx:25-36`), so an orb parked at `bottom-24` sits mid-menu → overlap returns when the menu opens. Verified fix: change the orb's DEFAULT className (`AIAssistant.tsx:585`) to `bottom-6 left-6 md:bottom-6 md:right-6` — dragged positions from `cashy-pos` localStorage already override defaults (`pos ? …`), so dragging is preserved. Do NOT touch QuickFAB (`QuickFAB.tsx:20`). Precedent: toasts already clear the corner via `bottom-24` on mobile (`toast.tsx:67`). Verify: 375px — both buttons visible/tappable, FAB menu opens unobstructed, dragged orb position restored after reload.
- **P1 "Add Income" mislabel [Functional]:** `QuickFAB.tsx:10-11` — both Add Expense and Add Income link `/transactions?add=1`; `TransactionList.tsx:270-274` reads only `add` and the dialog defaults `addType="expense"` (:114). Tapping "Add Income" opens an expense dialog. Fix: `?add=1&type=income` + read `type` in the existing `?add=1` effect to set `addType`. Verify: FAB → Add Income → dialog Type = Income preselected.
- **P1 mobile search gap:** CommandPalette is Ctrl+K-only (`CommandPalette.tsx:77`); mobile header (`AppShell.tsx:776-786`) has no search affordance. Fix: search icon in mobile header (pairs with the notification-bell fix).
- **P2 AppShell skip link:** AuthShell has one (`AuthShell.tsx:35`) but AppShell doesn't → 30+ nav links before main on desktop. Add "Skip to content" → `#main` alongside the route-focus fix.
- **P2 Cashy hardcoded colors:** `AIAssistant.tsx` uses raw `rgba(13,21,34,0.85)` dialog bg, `text-white`, `bg-white/10`, `text-gray-400/500`, `text-cyan-300`, `bg-blue-600` send button (:193-198, 210-216, 254-256, 489, 556, 562) — violates the never-hardcoded-colors rule and mismatches the `#5e6ad2` accent (blue-600/cyan-400 = second brand). Fix: keep the always-dark panel but map to CSS vars; minimum: send button → `var(--accent)`.
- **P2 dashboard mobile density:** 4 charts at fixed 280-300px (`charts.tsx:59,98,136,183`) stack to ~1,200px on mobile; briefing + momentum block wraps to multiple rows (`DashboardPage.tsx:314-350`). Fix: wrap each `ResponsiveContainer` in `h-52 md:h-[280px]` with `height="100%"`; `hidden md:flex` on the "vs last month" sub-block. Verify: 375px scroll length drops ≥30%, charts undistorted, momentum still visible on desktop.
- **P2 mode/entity clarity:** entity name appears only in the sidebar switcher (`AppShell.tsx:215-333`); breadcrumb is `CashFlow OS / <page>` (:799-807); only TransactionList shows mode ("Personal/Business Finance · month", :433-434). Fix: render current entity name (from `selectedEntity` localStorage, same source as :411) in the desktop breadcrumb and mobile header. Verify: business entity selected → name visible on every page header; personal → "Personal" or nothing.
- **P2 filter popover semantics (detail):** add `role="dialog"` + `aria-haspopup="dialog"` on Filter/MoreVertical triggers (`TransactionList.tsx:641, 446`); popover `w-72` (288px) → add `max-w-[calc(100vw-2rem)]` for 320px screens. Escape + focus-return already work (:96-110) — keep.
- **Screenshot-era trap (new instance):** `screenshots/ui-batch/final-transactions.png` shows the OLD inline filter row (FROM/TO/CATEGORY/TAG/RECURRING); current code has a Filter popover (`TransactionList.tsx:640-698`). Vision reports describing that layout are stale — verify against source before reporting. Same for `sprint2/mobile-*` (skeleton screenshots, no FAB visible → actually corroborates the orb covering the FAB).
