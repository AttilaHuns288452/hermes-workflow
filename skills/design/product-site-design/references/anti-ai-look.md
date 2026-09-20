# Anti-'AI look' direction — standing user preference for product/marketing sites

The user's bar: the site must read as **a real consumer product company** (Nest/Aqara-class clarity), never as an AI-generated concept page. Score sites on 'brand maturity', not cleverness. The single failure mode: **a chosen metaphor promoted to the whole visual personality.**

## The metaphor test (apply before styling)
- Human designers: product -> borrow 2-3 characteristics of a metaphor -> simplify.
- AI designers: product -> choose metaphor -> apply it to everything (mono readouts, signal dots, instrument panels, 'station log' rows, threshold rulers everywhere).
- If the metaphor itself is the personality, strip it. Keep precision; drop the costume.
- One signature concept per site max (e.g. a proprietary risk score). Everything else supports it; 10 micro-concepts competing = vocabulary overload.

## Palette dominance (roles, not narratives)
Target ~4 roles, then stop:
| Role | Use |
|---|---|
| Foundation (warm off-white) | majority of page |
| Primary dark | hero band, footer, headings authority, dark panels |
| Accent (one loud color) | primary CTA, key data, active states — nothing else |
| Border/muted gray | borders, secondary surfaces, muted text |

- A section's topic never earns it a new color (no 'beige = home warmth' logic — too literal).
- Dominance beats variety: users should perceive 2 dominant colors + 1 accent, not a careful 5-color system.
- Severity/risk states use typography, weight, and contrast — never extra hues.

## Fake-telemetry purge (the strongest AI tell)
Remove from ALL product mocks and page chrome:
- timestamps (20:41, 9:41), unit IDs (UNIT 01), AUTO · ON / LIVE lamps, window traffic dots
- status pills/chips, floating label cards, decorative dots, signal lamps that carry no data
- fake dashboard demos on download/contact pages

Keep at most ONE real measurement in the hero visual (e.g. 'Mold Risk Index 38/100'). Room/state lists render as plain quiet text, not pill badges. Dashboard mocks: title + one chart + plain-text states.

## Mono discipline
Monospace = measurements (38/100, 82% RH, 28°C) and row index numbers (01/02/03) ONLY. Labels, captions, tags, footers, eyebrows = normal text. A page full of mono readouts reads as a terminal, not a product.

## Copy
- Zero em dashes in visible copy — rewrite as two sentences or use commas. (Meta/OG tags exempt.)
- Benefit-first, natural product-team voice, no jargon, no 'clause — consequence' constructions.
- Never invent capabilities; keep honest prototype/disclaimer lines if the project requires them (trust beats polish).

## Structure (editorial flow)
Hero -> Problem -> Solution (product system rows) -> How it works (3 steps) -> Features (grouped list, not 6-7 equal cards) -> Where it lives -> CTA. Numbered hairline lists > card grids. Product-as-hero: device render + one clean screen, not UI chrome.

## Verification greps (run before shipping)
```bash
# visible-copy sweeps (strip comments first so review notes do not false-positive)
grep -n '—\|UNIT 0\|20:41\|9:41\|AUTO · ON\|LIVE' page.html
# class-level leftovers
grep -c 'chip\|lamp\|kicker\|hero-tag\|statline\|specline' page.html
```
Then one vision pass scoring ONLY 'brand maturity: looks like a real product company' and reporting defects with positions; fix and re-inspect once.

## Slop-copy and label discipline (de-slop passes)
When the user asks for a 'remove AI slop / vibe-coded feel' pass, sweep in this order and stop when the page reads edited, not empty:
- **Banned marketing vocabulary** (delete or replace with a plain sentence): smart, intelligent, cutting-edge, next-generation, revolutionary, seamless, effortless, powerful, comprehensive, advanced, personalized, tailored, unlock, elevate, discover, transform, optimize/optimized, sophisticated, robust, innovative, state-of-the-art, insights, 'scoring engine', 'black box'. 'Discover' as a section name becomes 'Browse'.
- **One label per meaning.** If a card says 'PER MONTH ≈ ₱783/mo' or repeats the score name twice around the number, delete the duplicate. De-slop audits flag 'Best match / Recommended for you / Your recommendation' triples — keep exactly one.
- **No badge without information.** A product card earns name + price + key value + rating; category chip + 'Student favorite' + score pill is already the ceiling. A 'Why it stands out:' label prefix before a strength sentence is slop — the sentence alone reads cleaner.
- **Repetition between sections is slop.** If two homepage sections list the same top-3 products in different formats, delete one. When a section was two-column and one column is removed, fix the copy that still says 'on the left / on the right'.
- **Open layout beats card-in-card.** 3-panel explainer sections become columns with a single top rule (no boxes); list rows become borderless rows; detail-page good/bad lists drop their panels; nested card footers collapse to one row.
- **Do NOT over-clean.** Keep the identity, the featured panel, the signature score — the target is 'distinctive + restrained', never 'plain white page + blue button'.
- **Recurring retheme requests need a standing project-retheme reference.** When the user repeatedly re-themes the same site, keep a per-project notes file (palette spec, contrast-checked tokens, category tint map, banned leftovers) so each pass starts from the current truth instead of re-deriving it; see `references/palette-swap.md` for the swap procedure and `references/gadgetwise-retheme.md` for the worked example.

## App-download handoff (badges + QR)
For app-download pages the composition is a single centered column: headline + one subline + QR + scan caption + store badges. No phone preview, perks band, or hardware CTA unless the user asks.
- **Badges: official artwork only.** Apple: `https://tools.applemediaservices.com/api/badges/download-on-the-app-store/black/en-us` (SVG). Google: `https://play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png` (PNG with built-in transparent padding — scale its CSS height ~1.3x the App Store badge's for equal visual height). Wording exactly "Get it on Google Play" / "Download on the App Store"; never redraw, recolor, or reword. Store-official colors inside badge artwork are not palette violations.
- **No availability claims** ("Available now", "Download today") unless listings exist. One honest availability line instead.
- **QR: real and decode-verified, never a decorative fake.** Encode a single documented constant (`APP_DOWNLOAD_URL` — the page itself is a legitimate smart-link placeholder until store URLs exist); self-check by rasterizing and decoding the render, asserting the payload. Provide a visible fallback link so the QR is never the only path. One place to change the destination.
- **Keep every mock in the same data story** (see SKILL.md rule 9): same rooms, same status words, same score across dashboard/app/hero surfaces.