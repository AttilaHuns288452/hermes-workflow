---
name: prototype-to-app-transplant
description: Apply a design prototype (HTML exports + DESIGN-HANDOFF.md + DESIGN-MANIFEST.json, e.g. from Open Design) to an existing app, then polish beyond the prototype. Use when the user says "apply this design to our project", hands over a prototype folder with standalone HTML screens, or wants an existing app restyled to match exported screens. Covers token extraction, frozen design spec, parallel swarm dispatch, and pixel-level visual verification.
---

# Prototype → Existing App Transplant

When the user hands over a **design prototype** (standalone HTML files + `DESIGN-HANDOFF.md` + `DESIGN-MANIFEST.json`) and says "apply this to our project, polish it more": the prototype is a **visual contract**. Follow this pipeline.

## 1. Read the contracts first
- `DESIGN-HANDOFF.md` — fidelity/responsive/CJX contracts. Tells you the primary entry file and the viewport matrix to validate (360→1920, no horizontal scroll).
- `DESIGN-MANIFEST.json` — machine-readable screen map + required tokens + interactions.
- The bundled screenshot may be a *spreadsheet reference*, not the real design — trust the HTML files.

## 2. Extract tokens from the entry HTML
The HTML files are self-contained (`<style>` in head). Pull CSS vars + font stacks + type scale + radii. Typical finance-prototype set:
```
--bg #f8f9fb · --surface #fff · --fg #1a1d23 · --muted #6b7280 · --border #e5e7eb
--accent #2563eb · green #16a34a · red #dc2626 · orange #ea580c · purple #7c3aed
soft variants: color-mix(in oklch, <c> 10%, transparent)
font-display: 'Iowan Old Style'/'Charter'/Georgia serif (headings)
font-body: system sans · font-mono: meta/eyebrows 11px uppercase 0.06em
h1 clamp(28px,3vw,36px) · radius 8/12px · sidebar 240px
```
Also scan `class="..."` per screen for component vocabulary (stat-card, donut-center, goal-bar, health-ring, alert-item, empty-state...).

## 3. Freeze a DESIGN-SPEC.md into the project (`docs/`)
Token table + per-screen mapping (prototype file → target component) + project conventions + "polish beyond prototype" list (focus rings, hover lifts, tabular-nums, skeletons, viewport matrix). **Subagents work from this file**, not the raw prototype.

## 4. Dispatch the swarm (user preference: swarm subagents + kanban)
- **Kanban first**: one task per screen/area + a final ECC/build task. Assign to orchestrator.
- **Parallel subagents (max 3, deepseek-v4-flash) on DISJOINT file sets** (foundation/globals, dashboard, feature pages). Overlap = merge conflicts.
- Each agent: `npx tsc --noEmit` to typecheck; **exactly ONE agent runs `npm run build` at the end** (parallel builds collide on `.next`).
- Rule: visual classes only — data flow, server actions, loading/empty/error states byte-identical.
- Foundation agent must keep the existing dark-mode CSS vars working and flip the default theme if layout.tsx hardcodes `dark` and the prototype is light.

## 5. ECC review gate (if project AGENTS.md mandates)
Dispatch `code-reviewer` + `silent-failure-hunter` (or per-project roster) in parallel over `git diff`. Include pre-existing uncommitted fixes in scope — they may be the "already fixed" batch, not conflicts.

## 6. Verify visually — PIXEL-SAMPLE, don't trust vision alone
- `agent-browser open <url>` + `screenshot` → `vision_analyze` for layout/structure.
- **Vision models mislabel saturated blue as "teal"** and vice versa. When color fidelity matters, sample actual pixels with PIL:
  ```python
  from PIL import Image; from collections import Counter
  img = Image.open(p).convert("RGB"); w,h = img.size
  cnt = Counter(img.getpixel((x,y)) for y in range(int(h*.55),int(h*.75)) for x in range(int(w*.35),int(w*.65)))
  ```
  `#2563eb` ≈ rgb(37,99,235); rounded rgb(16,96,240) is fine; rgb(0,160,128) is REAL teal.
- Cross-check computed style in the live DOM: `agent-browser eval "getComputedStyle(document.documentElement).getPropertyValue('--primary').trim()"`.
- **Grep for legacy hardcoded colors** after transplant — auth forms and shells are the usual offenders (`bg-gradient-to-br from-emerald-400 to-teal-600`, `ring-emerald-500/50`, `text-emerald-500`). shadcn `bg-primary` components inherit the token system; hand-written pages don't.

## Pitfalls
- `DESIGN-HANDOFF.md` warns: don't introduce warm beige/cream washes unless in the export; don't flatten domain modules into generic cards; keep screens as separate routes.
- Probe CodeGraph first (`codegraph_explore`) — project is indexed, returns verbatim source, saves tokens.
- Pre-existing uncommitted changes from an earlier ECC cron run will show in `git status` — verify they're the expected error-check fixes before assuming conflict.

## Verification checklist
- [ ] `npm run build` passes (single run, after swarm)
- [ ] `tsc --noEmit` clean
- [ ] Pixel-verified accent colors match spec (login button + primary)
- [ ] No legacy emerald/teal classes remain in restyled surfaces
- [ ] Light default if prototype is light; dark toggle still works
- [ ] Kanban tasks completed; ECC review dispatched
