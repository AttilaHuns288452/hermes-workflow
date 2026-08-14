# Research round ECC gate + Emil motion baseline (2026-08-11)

Companion to the "Finance UI research round" section. Shipped as `39ba1b0`
(11 files, +325/−79; push → Vercel). Board: `cfos-research-sprint`
(t_e81c0cb8 / t_f0f0ceae / t_f7d2c3e3 / t_5ab72d0d — complete via
`env -u HERMES_DELEGATED_CHILD_CONTEXT hermes kanban complete <id>`).

## ECC gate findings (3 reviewers: code-reviewer + silent-failure-hunter + a11y-architect)

All P1s fixed before merge; every one was a REAL regression or crash:

| # | Finding | Fix |
|---|---------|-----|
| P1 | Count-up invisible: `key={card.val}` remounts the number div every rAF frame → `.stat-enter` (opacity 0) restarts each frame | Drop the key; enter animation plays once on mount, concurrently with the count |
| P1 | Sticky thead `top-12` leaves a 48px band of scrolling rows (app header is a flex SIBLING outside the scroll container; scrollport starts below it) | `sticky top-0 z-10 bg-[var(--card-layered)]` |
| P1 | Cashy tab TypeError: `.cashy-orb` matches MiniOrb DIVs too (dialog renders them before the real orb button in DOM) → `el.click is not a function` when dialog open | `document.querySelector("button.cashy-orb")` |
| P1 | MobileTabBar `z-40` == drawer scrim `z-40` → tab bar paints above the dimmed scrim, clickable behind the drawer | `z-30` on the tab bar |
| P1 | `shot-capture.js` (untracked scratch) contained plaintext login creds — one `git add .` from committed | Deleted |
| P2 | `pb-16`/`bottom-20` under-clear safe-area devices (bar = h-14 + env inset ≈ 90px) | `pb-[calc(theme(spacing.16)+env(safe-area-inset-bottom))]` on content; same calc pattern on FAB + orb `bottom` |
| P2 | Hover-reveal `md:opacity-0` → md–xl touch tablets get invisible actions (tap-hover jank) | `lg:` variants (hover-reveal only ≥1024px) |
| P2 | `splitSource` split at the FIRST `Source:` line (mid-message mention folded into footnote); `**Source: link**` bold-whole-line left trailing `**` | Only split when the match is the last non-empty line; strip leading AND trailing `*`; `content ?? ''` guard |
| P2 | ActionChips plain `<a href>` → full page reload, drops Cashy panel state | `next/link` |
| P2 | BudgetDashboard `shareTTL(getBudgetVsActual)().then(...)` no catch → unhandled rejection, loading stuck true forever | `.catch(() => setLoading(false))` |
| P3 | thead/tab-bar `bg-card` flatter than `--card-layered` cards in dark | `bg-[var(--card-layered)]` |

Also verified clean: useCountUp (SSR-safe, cleanup, reduced-motion, no NaN),
Sparkline (<2 points null, 0-range guarded), CategoryIcon (null → Tag),
z-stack (thead z-10 < popovers z-50 < palette z-[60] < toasts z-[100]).

## Emil motion baseline (emil-design-eng applied)

Repo: `C:/Users/YOUR_USERNAME/Documents/Repos/external-skills/emilkowalski-skills`
(git pull for new skills; `animate` collides with impeccable's reference file
— load via categorized path). Key facts for CashFlow OS:

- **Dialogs already compliant** (sprint-4): `--animate-dialog-in: dialog-in 200ms cubic-bezier(0.16,1,0.3,1)` (strong ease-out, 150–250ms band), `dialog-out 150ms ease-in forwards` (exit faster than enter), keyframes bake in the `-50%` centering, start `scale(0.96)` + opacity 0 (never scale(0)), modals keep centered origin. Same for overlay + `select-in` (scale 0.97 + translateY −4px).
- **Applied 2026-08-11:** `active:scale-[0.98]` on the shared Button base (the cva base already transitioned transform at 150ms — it just never used it); drawer `duration-300 ease-[cubic-bezier(0.32,0.72,0,1)]` (iOS drawer curve); origin-aware popover entrances: `origin-top-left animate-select-in` (Filter), `origin-top-right animate-select-in` (kebab) — entrance only, no exit (conditional render).
- **Rules to keep:** never animate keyboard-initiated / high-frequency actions (tab bar, palette — correctly static); `prefers-reduced-motion` global kill-switch in globals.css already handles reduced motion; no motion dependencies needed — CSS tokens cover everything so far.
- **Skills that map to future work:** `review-animations`/`improve-animations` = the missing MOTION gate for UI sprints (run alongside ECC); `pick-ui-library` validates choices (NumberFlow for numbers if the count-up ever needs digit transitions, Sonner if toasts need features, Virtuoso for table virtualization, cmdk for the palette); `prototype` matches the user's prototype-as-contract workflow (build N variants with a switcher before committing to a direction).
