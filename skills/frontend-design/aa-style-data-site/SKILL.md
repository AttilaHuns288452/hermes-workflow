---
name: aa-style-data-site
description: Use when building Artificial Analysis-style data sites.
---

# AA-style data site pattern (GadgetWise proven workflow)

## The pattern
Artificial Analysis-inspired 'test-lab' look: dark violet-ink (#231a3a) topbar/hero, light body, electric violet #7f4bf3 primary, signal orange #e85d04 RESERVED for the best-value/Pareto highlight only, blue-tinted neutrals (no beige). Mono font (ui-monospace stack) for numbers/data only.

## Core pieces
1. **CSS var swap trick**: keep original var names (--green, --line, etc.), just re-point them. 90% of a restyle in one :root patch.
2. **Index engine**: `ownIndex(g)` = weighted 0-100 from data fields; document weights in a visible footnote; compute, never hardcode — hero badges MUST match the formula output (caught a hardcoded 89 vs computed 78).
3. **Pareto scatter**: raw SVG, no chart lib. px()/py() mappers, `<title>` tooltips, click-to-detail. Frontier line = connect Pareto-optimal points sorted by price; needs ≥2 frontier points to draw. Verify with a python port of the formula before shipping.
4. **Compare table**: 'higher is better ↑ / lower is better ↓' row suffixes + ★ on best cell + Ownership Index row.

## Image sourcing (real names+photos, invented specs)
- Firecrawl scrape of vendor pages works but CDNs rate-limit hotlinking.
- **Best source: Wikimedia Commons API** — `commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=filetype:bitmap <q>&gsrnamespace=6&prop=imageinfo&iiurlwidth=960` → thumburl. Hotlinks reliably (upload/thumb.wikimedia.org), no rate limit, stable.
- Verify EVERY url with HEAD (image/*, status 200) before embedding.
- `loading="lazy"` + `onerror` fallback to category tile so no blank boxes.
- Honest-label footer: 'real products, illustrative specs and prices.'

## Verification loop (zero-error bar)
1. Static: html.parser tag balance, ends-with-</html>, view-id checklist, `node --check` on extracted <script>.
2. Python port of any math → verify indices/frontier.
3. Headless playwright (local http.server) — pageerror/console/requestfailed collectors MUST be empty; count rendered dots/cards/imgsLoaded.
4. Mobile 390px: `scrollWidth > clientWidth` = overflow bug; find culprit by walking getBoundingClientRect right>viewport.
5. vision_analyze QA on screenshots; DOM claims (dots exist) + visual claim (dots look right) are different checks.
6. After Pages deploy: playwright E2E against the LIVE url, same collectors.

## GitHub Pages deploy (new repo)
`git init -b main` → commit → `gh repo create <name> --public --source=. --push` → `gh api -X POST repos/<o>/<r>/pages -f 'source[branch]=main' -f 'source[path]=/'` → live at https://<o>.github.io/<r>/ in ~60s (curl-grep to confirm).

## Recommender UX pattern (v3, professor-proof)
- Centered single-column decision flow: quiz card ALONE in center (max-width 720px, margin auto), results REPLACE the quiz (quizCard hidden) — never side-by-side.
- Ask natural questions, never weight sliders: purpose (category-specific), priorities as chips (max 3), routine (charger/carry/annoyance) → weights inferred in code.
- Must-haves = hard filter BEFORE scoring (hardFilter returns exclusion reasons); budget is always hard; excluded items listed with reasons, can't be rescued by score.
- Requirements review step before results + "How GadgetWise chooses" transparency note ending in "No AI is used to choose the product."
- Results: best match (score bars ×weights, Why-ranked-first checkmarks derived from component thresholds, Trade-off from weaknesses+lowest component), "Why A ranked above B" (+N diffs both directions), other-options grid (deduped vs top/alt, hidden if empty), priority-adjust chips (boost one weight +4, rerank, report).
- JS splice gotcha: when replacing a function region by index, check what constants the removed region exported (LUX was cut → ReferenceError at runtime). Always node --check + browser smoke after splices.

## Pitfalls
- Duplicate CSS rules when patching near existing ones — dedupe before shipping.
- Hero/CTA overlap on mobile: collapse secondary buttons at ≤640px.
- Local http.server needs background=true in terminal tool; browser_exec blocks private URLs — use playwright directly.
- delegate_task: one tasks[] entry = ONE subagent. Splitting one job into 4 context entries spawns 4 agents fighting over one file. Flash-tier subagents die with '180s no response' writing huge files — prefer hands-on patching or write-in-sections instructions.