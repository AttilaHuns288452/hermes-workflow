---
name: design-token-qa
description: Use when UI must match a client's existing design system.
---

# Design Token QA

Companion to `design-handoff-boards` / `figma-html-import` — frame generation and Figma merging live there (they are external/read-only; this skill is the editable half they lack): decoding the CLIENT's real design system, and proving the generated frames actually carry it.

## Rule 1 — Never invent the palette

When the deliverable must match an existing design (client/team app, "so they can speed up their progress"), the palette, nav variant, and component language come from THEIR artifacts — not agent taste, not a promo site, and not the wireframe's annotation ink.

Source artifacts, best first:
1. **Figma progress screenshots** — authoritative: real tokens, nav variants, component states, what exists and what doesn't. Ask for these when the client has a live file.
2. **UI-kit / style-guide exports** — token names + swatches.
3. **Wireframe PDFs** — layout structure and flow only; their colored annotation elements are spec-callout ink, NOT the design system.
4. **Promo site / prior deliverables** — fallback only; brands drift between marketing site and app.

For every ambiguous element, use BOTH methods:
- **Deterministic (values):** PIL pixel scan — saturated-cluster sweep to locate elements, then sample centroids for exact hex. Also read `pdfinfo` page sizes for component specs (e.g. 390x61pt strips = navbar variants) and scan tall columns for gradient stop values.
- **Vision (construction):** one image + one targeted prompt — ring or callout frame? pill or tint? which element floats? Vision guesses values; pixels confirm them.

Pin before generating: accent(s), gradient stops + direction, text/surface/line colors, status colors, nav variant + active treatment, icon stroke style, radius language, progress-indicator construction — and what does NOT exist (e.g. no progress rings in their system = don't add ring chrome they never drew).

## Rule 2 — Verify the render, not the HTML

Palette present in the HTML proves nothing. Gate every build/restyle:
1. Screenshot QA must save the **RGB copy** — never the `.convert("L")` copy, which grayscale-ifies the file and poisons every later color check.
2. Pixel-verify each token in the saved PNG (tolerance ~30/channel): brand, both gradient stops, status colors, text navy.
3. Adjudicate vision flags with pixels + computed style BEFORE editing code: `getComputedStyle` on the flagged element, fresh screenshot, pixel scan. Stale captures and grayscale saves impersonate "missing color" bugs.
4. Vision pass last, for layout truth only (overlap/clip/alignment); Playwright geometry runs first.

## Vision calls without a vision tool

The configured chat model accepts images natively via its OpenAI-compatible endpoint — call it directly from execute_code; don't hunt for a standalone vision tool. Use `scripts/vlm_query.py` from this skill. Rules it encodes:
- A browser-like **User-Agent header is required** — without it the gateway's WAF rejects with 403 code 1010 even with a valid key.
- **One image per request.** Multi-image requests can return 200 with empty content; retry single.
- **Downscale screenshots to ≤1100px** — full-res PNGs can also return empty content.
- Never print the key; load from env, fall back to the Hermes secrets file.
- 402 = wallet empty → fall back to pixel-scan-only QA and say so; don't fake a vision verdict.

## Verification scripts (this skill's scripts/, copy into the project's design/ dir)

- `scripts/vlm_query.py` — vision calls to the chat model (one image/request, UA header, 402 fallback).
- `scripts/qa_frames.py` — static import-safety + Playwright geometry (`.frame` scrollHeight, overflow, fill ratio).
- `scripts/qa_render.py` — per-frame screenshots, non-blank assert, saves COLOR PNGs for token pixel checks + contact sheet.

## User contract for handoff deliverables

Deliver merged single-file board + per-frame files + wireframe variant, all 390x844, import-safe (no var()/absolute/transform/rgba/<a>/sprite refs), verified by geometry + pixel + vision gates before delivery. Include a contact-sheet PNG inline in chat as the at-a-glance proof.