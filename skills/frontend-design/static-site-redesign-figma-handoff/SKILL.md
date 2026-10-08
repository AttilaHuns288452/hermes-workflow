---
name: static-site-redesign-figma-handoff
description: Use when redesigning a static site for Figma handoff.
---

# Static-site premium redesign → Figma handoff

Class: existing static HTML/CSS promo site (GitHub Pages / Vercel), user reproduces the design in Figma via html.to.design for a client-style defense. Generic design-audit checklists live in `redesign-existing-projects` (channel profile) and import markup rules in `figma-html-import` — this skill carries the end-to-end procedure and the pitfalls those don't.

## Always-on rules

- **Static and Figma-safe beats expressive.** No new animations, transitions, hover-dependent reveals, JS, or video. Flow layout (flex/grid); `position:absolute` only for small overlay status cards on an existing pattern.
- **Identity is a contract.** Read DESIGN.md / PRODUCT.md / messaging or claims docs before editing; if none exist, document the system after the build. New sections are system changes — use existing tokens/type roles; extend a shared stylesheet append-only (new classes only, never rename ones other pages use).
- **No kickers/eyebrows above headings** anywhere. No floating status pills/labels — a chip must carry data or it goes; hunt visually for survivors after removals (DOM checks alone miss them).
- **Palette directives are binding system changes.** When the user pins colors: put them in `:root` as named tokens, retire off-palette tokens by retinting every rule that references them (grep the hex across CSS *and* all pages, including inline SVG attributes), mark retired token definitions `RETIRED`, and update DESIGN.md to match built reality. Severity/risk states are communicated by typography, label, border weight, and background intensity inside the pinned palette — never by adding a new color.
- **Claims discipline:** demo numbers on mocks must be labeled illustrative; no availability/store claims that don't exist; keep disclaimers.

## Procedure

1. **Recon:** read the design-contract docs, the target page, the shared stylesheet's class inventory, and any board/generator scripts. Probe with CodeGraph/graphify before raw reads per token-saver rules.
2. **Plan → delegate:** write the full spec (section order, exact copy anchors, constraints) into ONE delegated build task; queue mid-flight steers (palette, craft-floor rules) via `delegate_task action=steer` when directives arrive while the child runs. Orchestrator hands-on only for small QA fixes.
3. **Verify the child's report independently** — self-reports are hypotheses: diff stats, structural DOM checks, fresh screenshots.
4. **QA sweep (every page × desktop 1280 + mobile 390):** `scrollWidth <= viewport` per page, zero console errors, anchors resolve, internal links exist, images load — **scroll through the page first**: below-fold `loading="lazy"` images report `naturalWidth: 0` until scrolled; don't call them broken.
5. **Vision pass on full-page screenshots** as the LAST check — it catches visual leftovers (orphaned pills, detached captions, dead space) DOM checks can't; adjudicate every vision flag against the DOM before fixing.
6. **Figma board:** regenerate the merged import file via the project's board script (see Pitfalls), Playwright-verify frames/images/zero console errors after rebuild.
7. **Commit + push + verify the LIVE URL** (Pages deploys in 1–3 min; curl for a marker of the new build before declaring done). Deliver a table of placeholders the user must replace.

## Pitfalls

- **Grid blowout from long unbroken strings** (emails, URLs, mono readouts): `break-word` does NOT shrink min-content. Root fix = `min-width: 0` on grid/flex children + `overflow-wrap: anywhere` on the string. Verify at 390px.
- **`place-items: center` centers items, not the stack**, in a stretched grid — a caption under a mock ends up detached with dead space. Add `align-content: center` + `gap` on the container.
- **Board generators:** extract bodies with `<body[^>]*>` — pages that scope overrides via a body class (e.g. `<body class="page-index">`) silently lose them otherwise; carry the class onto that page's frame wrapper. Base64-inline ALL local assets with correct MIME per extension (`.jpg`→image/jpeg, `.png`→image/png, `.svg`→image/svg+xml), including named root-level files (QR codes); one missed pattern = 404 inside the imported board. Flatten `:root` vars, strip comments BEFORE var-flattening, keyframes/animation/transition/sticky/backdrop-filter out, assert none remain.
- **Playwright `height="auto"` on SVG** is a console error — omit the attr, size via CSS/viewBox.
- **QR toolchain:** deps in a throwaway venv (`python3 -m venv /tmp/qrvenv && /tmp/qrvenv/bin/pip install 'qrcode[pil]' zxing-cpp`) — never into the system PEP-668 python. Generator: destination in ONE named constant; no published store listing → encode the live site URL as a documented smart-link placeholder and decode-assert the payload in the same script; ship a text fallback link beside the QR.
- **Store badges:** official artwork only — Apple badge API (`tools.applemediaservices.com/api/badges/download-on-the-app-store/black/en-us`) and Google's official badge PNG; keep official wording/alt text, unmodified; honest availability copy when listings don't exist. Off-palette colors INSIDE official badge artwork are expected, not a palette leak.
- **One vision defect per pass is normal** — fix it, re-screenshot, and stop; don't loop polish rounds.