# Static / Figma-safe build + fixed-palette tokens

Depth for the procedure's step 3 and the palette pitfalls. Load only when the target is a Figma-bound static build or a pinned palette.

## Static, import-safe rules

- No new `transition:`, `animation:`, `@keyframes`, JS, video, or hover-dependent reveals. Existing legacy hover rules in the shared stylesheet stay untouched; add nothing new.
- Flow layout only (flex/grid). `position:absolute` reserved for small overlay status cards (the float-card pattern).
- Never rename or delete CSS classes used by other pages of the same site; append new classes instead.
- Reuse the site's existing tokens and type roles (display face for headings, text face for body, mono ONLY for data readouts — never as a kicker above headings).
- Figma import board (if the repo has a board builder script): inline CSS, flatten every `var()` to literals, base64-inline images, strip sticky/animation chrome, one labeled frame per page at 1280px; grep-level asserts in the builder (no `position:absolute|fixed`, `rgba(`, `<use`, `var(`, bare `transform:`) catch drift.

## Severity within a pinned palette (no red/amber/green)

Severity ladder using only the brand colors (navy / teal / sky / white / beige):

| State | Treatment |
|---|---|
| LOW / healthy | teal chip or teal label (system operating) |
| MODERATE / info | sky-blue chip |
| HIGH / CRITICAL | white-on-navy chip, heavier border, bolder label, higher background intensity |

Carry the rest through typography (weight/size), border weight, contrast, and label text — never off-palette hues. The active/action state (e.g. "Dehumidifier ON") is the teal accent moment.

## Section rhythm from balance targets

Treat color balance as a repeating rhythm, not per-section free choice. Separation is TONAL, not seamed: once adjacent bands are tonally distinct, drop `border-top/bottom` between light sections — border plus tone together reads as clutter. Four-tier ladder that holds up: near-white hero (`#FBFBF9`) → paper (`#F7F8F6`) → alternate band 2–3 steps visibly deeper than paper (e.g. `#E9EEEC`; a one-step shift reads as no rhythm at all) → ONE warm beige band (`#F2EBDF`) reserved for the page's human/emotional moment → deep navy CTA + footer. Assign semantics: cool tones explain the system, the single warm band carries the ownership/human promise, dark closes the page. Within bands: dark ink for headings and body on light/warm surfaces; bright accents (teal) for graphics, chips, key numbers, and large/bold text only.
