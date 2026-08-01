---
name: prototype-transplant
description: Apply an exported HTML design prototype (Open Design exports, Figma HTML drops, financeprototypeapp-style archives with DESIGN-HANDOFF.md/DESIGN-MANIFEST.json) onto an existing production app without breaking logic. Covers token extraction, frozen design spec, parallel swarm execution on disjoint files, ECC review, and visual verification before deploy.
triggers:
  - apply this prototype to our project
  - transplant this design
  - make it look like this design
  - prototype design handoff
---

# Prototype → Production Transplant

When the user drops a design-prototype folder (exported HTML screens + handoff
manifest) and says "apply it to our project, polish it": the design is a
**visual contract** — match pixels/behavior first, refactor internals later.

## 1. Extract the design contract (before any code)

- Read `DESIGN-HANDOFF.md` / `DESIGN-MANIFEST.json` if present — they define
  tokens, viewport matrix, and the screen-file-first policy.
- Extract tokens programmatically, don't eyeball:
  ```python
  import re
  txt = open('business-mode.html', encoding='utf-8').read()
  vars_ = re.findall(r'--[\w-]+\s*:\s*[^;]+;', txt)   # CSS custom props
  fonts = re.findall(r'font-family:\s*([^;]+)', txt)
  ```
- Screenshot the reference with vision_analyze for a design-language read, but
  treat the HTML/CSS as truth — the screenshot may be a spreadsheet mock, not
  the real design.
- **Freeze tokens into `docs/DESIGN-SPEC.md`**: colors + soft variants, font
  stacks, clamp type scale, spacing, radius, sidebar width, per-screen mapping
  (prototype file → app component), and the polish bar (focus rings, hover
  lifts, tabular-nums, no horizontal scroll at all 9 viewports). This file is
  the single source of truth all swarm agents share.

## 2. Execute with a parallel swarm (3 agents, disjoint files)

- Split by **file ownership**, never by concern: agent 1 = globals.css +
  layout + AppShell; agent 2 = dashboard feature dir; agent 3 = investments +
  transactions. Disjoint files ⇒ zero merge conflicts.
- Each agent gets: DESIGN-SPEC path, prototype HTML path, project AGENTS.md
  conventions, explicit "**visual classes only — logic/actions/states
  untouched**", and `tsc --noEmit` to typecheck. NOT `npm run build` —
  parallel builds fight over `.next`; one agent (or the orchestrator) runs the
  single build after all land.
- Use the user's configured delegation model (e.g. deepseek-v4-flash) for all
  agents.

## 3. Review + harden (mandatory per project AGENTS.md)

- Run 2 ECC review agents in parallel: code-reviewer (logic regressions in the
  restyle) + silent-failure-hunter (unchecked awaits, swallowed errors).
- Triage findings; fix the real ones with minimal diffs (raw-value flags for
  % cards, stats from unfiltered fetch, negative-stock guards). Skip app-wide
  refactors (e.g. no toast system exists = a project, not a fix — say so).
- Rebuild, then verify changed routes visually (see `visual-qa` skill).

## 4. Verify before deploy

- Live browser check per changed page (agent-browser): screenshot + pixel
  sampling + `getComputedStyle` for token colors — vision models mislabel hues
  (blue called "teal"), pixels don't lie.
- Test every dialog end-to-end: open → fill → select → submit → assert closed
  + data landed → clean up the test row. Radix Select portals options OUTSIDE
  the dialog; query `[role=option]` on document, click the trigger button by
  its placeholder text, and use the native value setter + input event for
  React-controlled fields.

## Pitfalls

- **Default theme flip**: prototype is light, app defaults `dark` in
  `layout.tsx` — remove the hardcoded `dark` class or the prototype look never
  shows. Then the theme toggle must READ localStorage on mount, not just write
  it, or preference resets every reload.
- **Leftover brand colors**: old app's emerald/teal lives in login forms,
  AuthShell blobs, focus rings, brand gradients. `grep -rn "emerald\|teal" src/`
  after the main pass.
- **shadcn token mapping**: components use `bg-primary`, not `--accent` — remap
  BOTH `--primary` and the new `--accent` in globals.css or buttons keep the old
  color while the design system says otherwise. Verify with
  `getComputedStyle(document.documentElement).getPropertyValue('--primary')`.
- **Data-dense spreadsheet-style prototypes** (finance trackers): cards with
  mono uppercase eyebrows + tabular-nums values + colored icon chips translate
  well; don't flatten into generic cards.
- **Windows orphaned `next dev`**: Next.js refuses to start on port 3000 with a
  stale PID and falls back to 3001. Kill with
  `powershell -Command "Stop-Process -Id <pid> -Force"` — `taskkill` from
  git-bash may fail (`//F` mangles) or hang. Always check which port the new
  server bound.
