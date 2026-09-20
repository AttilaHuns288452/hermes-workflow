# GadgetWise retheme state (worked example of the palette-swap procedure)

Per-project state for the recurring GadgetWise visual passes (electric blue + dusty gray + deep blue-charcoal + warm orange, per the user's latest spec). Update this file whenever the identity changes again — it is the starting truth for the next pass.

## Current tokens (v4/v5, live in css/styles.css + css/identity.css)
- `--bg #F3F1EE` dusty gray · `--surface #FFFFFF` · `--surface-2 #ECEBE8`
- `--primary #2563EB` / `--primary-dark #1D4ED8` / `--primary-soft #E8F0FF` / `--primary-wash #F3F7FF`
- `--hero-1 #172033` / `--hero-2 #202B42` (deep blue-charcoal; hero, CTA, footer, compare tray, admin sidebar)
- `--accent-warm #F0A35B` / deep `#A05A1C` / soft `#FFF1E3` (coral is RETIRED — do not reintroduce)
- Stars `--gold #C77E1A` (rating semantics, ≥3:1 as icon); semantics: success `#3B8665`, warning `#96631F`, danger `#C6535B` (all AA on their softs)
- Shadows `0 1px 2px rgba(23,32,51,.04), 0 8px 24px rgba(23,32,51,.07)`; radii 6/10/14

## Composition rules that are now load-bearing (do not regress)
- ZERO CSS gradients on brand surfaces. Hero/CTA/footer are SOLID `--hero-1`; a gradient here is the #1 audit flag.
- Hero right side = showcase: large product image, name + price, ONE score metric (`79 Performance to Cost`), one orange flag. No spec rows, quote, formula — those live on gadget-detail.
- 'What students usually miss' is editorial typography (`.ed-big` display heads), not cards.
- One category family: all cat/g-card tints resolve to the indigo family (override block at the bottom of identity.css wins; per-key ink/line values in the data-cat rules were audited to match).
- Section order: hero → categories → editorial trio → Top rated (3 cards) → scatter (demoted: plain section, hairline top border, smaller heading) → cheapest-to-own (borderless rows) → flow (number + word only) → charcoal CTA 'Not sure which one?' + orange 'Find my gadget →'.
- Copy vocabulary fixed: 'Performance to Cost' (never 'Ownership Index' in UI strings), 'PER MONTH' on tags, 'Cost per month' rows, 'BEST MATCH' badge, 'Why it ranks here'. Zero AI/marketing words; scatter caption says 'Orange dots'.
- Recommendations stay deterministic: same breakdown tables, weights panel, honest under-budget wording. Never add AI prose.

## Known pitfalls already fixed (verify they stay fixed)
- Compare tray hidden with `display:none`/`.show{display:block}` — never `translateY(110%)` (full-page captures paint the sliver as a phantom dark band).
- Search input padding-left 38px covers the icon gutter.
- Hero h1 `#fff`, lede `--on-hero-2 #A9B4C9` (7.79:1); hero primary CTA is blue fill (5.17:1 on charcoal).
- Toast bottom 88px (clears the tray).
- All 21 catalog images on `upload.wikimedia.org` (thumb host 404s intermittently), zero duplicate URLs, per-product-name Commons searches.
- Data quirk: Anker model is 'PowerCore 20100' (brand field holds 'Anker'); iPad image is the 2024 file under `/e/ed/`.

## Verification commands
```bash
for f in js/*.js; do node -c "$f"; done
node test-catalog.js && node test-rec.js
node -e 'concat css; assert every var(--x) is defined'   # token coverage
# image health: curl HEAD every js/data.js URL, expect 200 image/*, no dups
# playwright: /tmp/shot.js pattern — 6 pages x 1440x900 + 390x844, then vision QA
```
Deploy: commit + push, sleep 100 (Pages lag), curl live URL with ?cb= cache-buster.

## Admin console state (post-scope-trim)
Fixed scope (user's product model: GadgetWise informs buyers, it does not fix products): admin = gadget CRUD + category CRUD + review moderation + view-only stats. NO issue management (issues are public-side info: detail-page tab + report form), no user suspend/activate (Users page is a read-only table), no data-quality page, no export/import page, no rec-engine log panel. Deleted pages: admin-issues.html, admin-quality.html, admin-data.html — do not rebuild them.

Architecture: `GWStore` (js/admin-store.js) = localStorage overlay `gw_admin_overlay_v1` applied over the mock dataset on load; admin.js router dispatches on `<body data-admin-page>` — a dead function in the router map kills EVERY admin page with a ReferenceError, so the router map must list only defined fns. Sidebar = `renderShell()` in admin.js (not per-page markup); NAV_ICONS entries become orphans when their nav link is removed.

Trim sweep checklist (any future scope cut): delete the page file; drop sidebar link; drop router case; drop the store function + its return export + any blank() fields; drop data.js structures feeding it; replace dashboard stats that referenced removed metrics (recompute from live data, never keep stale constants); drop test assertions; fix `colspan` in shared table markup; grep for orphaned icon entries and cross-page copy mentions. E2E note: intentionally visiting a deleted page to confirm 404 logs one 'Failed to load resource: 404' console error — filter that known line, do not count it as a page failure.

E2E invocation: `node` script requiring `/home/attila/.hermes/hermes-agent/node_modules/playwright` (local profile otherwise lacks it); always `addInitScript(() => localStorage.clear())` in a fresh context before asserting counts (overlay persistence). Tests: `node test-catalog.js && node test-rec.js && node test-admin-store.js` (admin-store test loads data.js + app.js + admin-store.js in a vm sandbox — new store methods are reachable as `Store.<fn>`, not `window.GWStore.<fn>`, and store functions must not touch `document` outside the sandbox mocks).