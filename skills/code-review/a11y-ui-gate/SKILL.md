---
name: a11y-ui-gate
description: Use when reviewing UI changes for accessibility.
---

# A11y UI Gate Review

Run when dispatched as the a11y reviewer for a UI change wave (e.g. ECC `a11y-architect` gate), or when asked to check contrast/keyboard access/reduced-motion on a frontend diff. Verdict format: `APPROVE` / `REQUEST_CHANGES` + numbered findings `(severity | file:line | issue | one-line fix)`, always backed by computed ratios and read code — never assumptions.

## Workflow

1. **Scope the diff correctly.** `git status --short` shows staged AND unstaged; `git diff --stat` shows ONLY unstaged, `git diff --cached --stat` ONLY staged. A "wave" split across index + worktree hides half the changes if you check one diff. Read both, plus untracked files.
2. **Run the type check** the gate asks for (`npx tsc --noEmit`) — report exit code as baseline.
3. **Contrast: compute, don't eyeball.** Run `scripts/contrast.py` (ships with this skill) — it computes WCAG ratios AND simulates Tailwind `color-mix(in oklch, X%, transparent)` soft-token blends over their base background, which are otherwise unknowable by inspection. Add any palette pairs the diff introduces.
4. **Check the asked pairs, then the real usage sites.** The gate names specific pairs (e.g. accent on white) — verify those, but ALSO grep where the token is actually used as text vs fill. Classic miss: pair passes on white but fails on the page bg (`#f8f9fb`-style) or on soft blends, or as small text in dark mode.
5. **Keyboard-interaction checklist** (the patterns that recur in every wave):
   - Popover/menu trigger: `aria-expanded` present? `aria-haspopup`? Escape closes? Focus moves into panel on open and RETURNS to trigger on close? If no focus mgmt → finding (Major).
   - Backdrop `fixed inset-0` click-catcher: NOT focusable is CORRECT — don't flag it. The finding is missing Escape + focus return.
   - Inline confirm (Delete?/Cancel/Delete): buttons real `<button>`s? Activating the trash unmounts the focused button → focus drops to body (Major, fix: ref + effect focusing the Cancel button when confirm state changes). Confirm text and the resulting row removal need `aria-live`/`role="status"`.
   - Dialog: if it wraps Radix/shadcn `Dialog` (Radix Root), focus trap + Escape + focus return + `aria-labelledby`/`aria-describedby` come free — verify the wrapper renders `DialogTitle`/`DialogDescription` and don't re-litigate the trap. Real findings are usually inside: placeholder-only inputs (no label/id pair), error `<p>` without `role="alert"` or `aria-describedby`.
   - Icon-only buttons: every one needs `aria-label` or `title` (title works as accessible name; nothing on the button does not).
   - `aria-label` on a plain `<div>` with no role is DROPPED by AT — add `role="dialog"`/`role="group"` or delete the label.
   - Nav active state: `aria-current={active ? "page" : undefined}` (or `aria-pressed` for toggle groups).
6. **Reduced motion.** A global `@media (prefers-reduced-motion: reduce) { *, ::before, ::after { animation-duration:0.01ms !important; ... } }` block covers ALL CSS animation/transition — verify it exists, then hunt JS animation: `requestAnimationFrame`/`setInterval` counters must be gated on `matchMedia("(prefers-reduced-motion: reduce)")`. CSS-only entrance animations (fade/slide, `stat-enter`) are covered by the CSS block — no finding.
7. **Semantic utilities.** Font-swap utilities (`.num`: font-family + `tabular-nums`) can't break reading order — only `direction`/`unicode-bidi`/content reordering can. Don't invent findings.
8. **Decorative icons.** lucide-react SVGs ship `aria-hidden="true"` by default (verify once per project in `node_modules/lucide-react/dist/cjs/lucide-react.js`) — icon-only decorative SVGs in non-focusable wrappers need nothing. Empty-state CTAs: confirm the component renders a real `<button>` (check for `asChild`).

## Severity

- Critical — blocks access entirely
- Major — significant difficulty (missing keyboard path, focus loss, contrast < 4.5 on small text)
- Minor — workaround exists (missing aria-expanded, unannounced error, unnamed icon button)
- Enhancement — beyond compliance (title should be a heading, aria-live on empty-state swap)

## Pitfalls

- Contrast thresholds: 4.5:1 normal text, 3:1 large text (≥18.66px bold or ≥24px) and UI graphics. Borderline passes (4.5–4.8) should be reported as PASS with the margin noted — they're one anti-aliasing tweak from failing.
- Accent-on-accent-soft (text on `color-mix` 10–14% tint) is the most common hidden failure — always simulate the blend.
- When a token serves BOTH text and fill (e.g. accent text AND white-on-accent badges), the fix is a separate text token (`--accent-text`), not lightening the shared token — lightening it breaks the badge.
- Don't flag `aria-busy` skeletons replacing `role="status"` loading text unless the wave also removed the sr-only fallback — skeleton-only loading can lose the completion announcement, but verify before reporting.
