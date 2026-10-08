---
name: ui-replica
description: Use when the user wants a UI-only copy of an existing app — same stack (copy code) or restacked (rebuilt in a stack the user names). Same design, no backend, static fake data.
---
# UI Replica — same design, no backend

For client demos / static previews: same design, no backend, static demo data. Stubs the data client so the real frontend code copies verbatim.

## Rule 0: replicate means copy code, not reimplement
When the user says the UI must be "consistent with", "the same design as", or "replicate" an existing app or a demo video, screens merely *inspired by* the original fail the requirement — the user diffs them by eye and rejects them. Copy the source repo's actual frontend files verbatim; the design then matches by construction instead of by taste.

## Rule 0b: restack = port, not copy
When the user names a DIFFERENT target stack (e.g. "rebuild it in React + Tailwind"), verbatim copy is impossible — port with explicit fidelity mechanisms instead:
1. Extract the visual contract programmatically (CSS custom props, fonts, radii from the source stylesheet) into the new theming layer BEFORE writing components; screenshots are secondary evidence.
2. Convert the dataset MECHANICALLY (script the transform, keep field names), then inspect one full record and write renderers to the real shapes — field NAMES copy fine, shapes don't (a spec list may be `string[]`, not `{label,value}[]`; `model` may already contain the brand, so derive display names in one helper instead of concatenating brand + model).
3. Port formulas/data transforms 1:1 into one logic module — no "improvements" mid-port — and leave ONE runnable check (`node check.js`) asserting output ranges, identity sums, sort order, and money formatting against a fixed fixture.
4. Router: for a static deploy a ~5-line hash-route hook (useSyncExternalStore on `hashchange`) replaces a router dependency; links are `href="#/path"`.
5. QA = the step 7 route walk, but vision-check each route side-by-side against the SOURCE screens. Deploy per skill `static-site-github-pages-deploy`, then verify the LIVE URL with a cache-bust query (Pages CDN serves stale builds briefly).

## Rule 0c: clone from the product when no source code exists
When the target is a product the user names but you cannot copy code from ("literally copying X"), fidelity comes from extracting the real visual contract, not from taste:
1. **Research the product's own materials first**: search for interface/panel documentation (vendor help pages, university libguides often embed downloadable panel screenshots), and `curl` those screenshot PNGs locally.
2. **Vision-extract a spec from the screenshots**: per panel, get hex pairs (fill + accent per component), radii, component shapes, spacing, and IA order (which panel is where, what cards/chips exist). "Colors sampled from real product screenshots" is the fidelity claim the user checks.
3. **Lock the JS contract before rewriting chrome**: grep every `getElementById`/`querySelector`/`el('div','class')`/data-attribute usage across the JS, then rewrite HTML/CSS with all ids/classes preserved so behavior survives the reskin.
4. **Theme-safety audit before flipping the theme**: components whose styles are hardcoded (e.g. SVGs carrying their own palette) are self-contained embeds and stay as-is; only what consumes CSS custom properties must be retokened. Mixed-theme embeds are fine and often correct.
5. **QA = DOM assertions + side-by-side vision against the saved reference screenshots**, not against memory of the product.

## Procedure
1. **Survey the source frontend** (`pages/`, `components/`, `lib/`, `context/`): grep the import surface and the data-layer call shapes — query-builder calls, RPCs, function invokes, auth, realtime channels. This is the surface the fake must serve.
2. **Stub the data client, not the API layer.** Replace the ONE data-client module (e.g. `supabaseClient.js`) with an in-memory fake; every `pages/` + `lib/` file then copies verbatim. "No backend" becomes literally one file, and UI fidelity is guaranteed. Do NOT stub individual API functions — that reintroduces drift.
3. **Derive the fake's schema from the source's own seed scripts / data mappers** (`seed.mjs`, `seed_map.mjs`, scheduling helpers). Never invent columns or shapes; the seeds are the schema truth.
4. **Clean-copy the tree**: `rm -rf src && cp -r <source>/src src`, then verify file lists are identical (`find -type f | sort | diff` ignoring path prefixes). Incremental `cp` silently drops directories/files.
5. **Restore the fake client** (the copy overwrote it), then apply the fewest possible demo-only patches (e.g. role buttons always on). Keep each patch one line with a comment saying why — a diff against the source should show exactly one replaced file plus a handful of demo lines.
6. **Seed demo data covering every field any consumer reads** — grep the copied pages for field accesses on seeded rows (`.includes`, `?.name`, date/price reads). A missing field crashes screens (`undefined.includes`) or renders embarrassing placeholders ("Date to be assigned", ₱0, empty pills).
7. **Route-walk QA** (start from `templates/route-walk-qa.mjs`): every role × every route — pageerror + console-error capture, full-page screenshots. Zero errors before vision QA. Vision-check the key screens and require quoted card lines (real dates, names, prices) — that is what proves the projection layer returns real fields.
8. **Deploy, then verify the LIVE URL, not localhost**: poll the served bundle hash until it equals the local build's hash, then run the same role-walk via Playwright against production and vision-check the client-facing home.

## Pitfalls
- **Embeds contain commas**: a select-projection that splits on `,` shreds `services(name, price)` into garbage segments and returns undefined fields everywhere (all fallback copy shows at once). Split the column list at paren depth 0 and expand a bare `*` segment to all columns.
- **`.env` is gitignored, so `VITE_*` flags never reach CI builds** — the feature (dev buttons, QA panel) tree-shakes out of the production bundle while the build stays green. For demo builds hardcode the constant in source instead of trusting env; prove it by grepping `dist/assets/*.js` for a marker string of the feature BEFORE deploying.
- **Dev/role overlays render closed by default** (a floating badge). In E2E, click the overlay toggle (e.g. `[aria-label="Dev tools"]`) before asserting its labels; the panel also closes itself after a role switch — reopen it before the next switch.
- **SPA role/session setup must land before the route load**: context providers read localStorage at mount. Set the session key, then navigate (or reload); setting it after load has no effect.
- **Deployment API tokens often lack read scope for deployments.** Don't block on that: served-bundle-hash polling plus a live Playwright walk is sufficient proof of what production runs.
- **Tailwind v4 `@apply` cannot reference custom classes** defined in `@layer components` — expand the base utilities into each variant instead of `@apply base-class hover:other-class`; the reference silently fails or emits empty rules.
- **Cards nested in a themed band inherit the band's text color** — a light card inside a dark hero band paints its text in the band's light color (invisible). Set the card's text color explicitly and confirm with `getComputedStyle`; vision often can't see white-on-white.
- **Lazy images inside JS-hidden containers never fetch in Chromium** — eager-load anything the UI reveals later, and give hotlinked remote photos an `onError` fallback (inline SVG placeholder) so grids never show blank cells.
- **Before trusting QA screenshots, curl the app's index path and assert it is YOUR app** — a preview server whose workdir didn't exist at spawn silently serves a different root, producing confident wrong screenshots.
- **QA text assertions must be derived from disk content, not from remembered content** — even a verified file write can differ from what you recall composing (reworded prose, formatting hooks). Grep the file or assert structural anchors (ids, labels) instead of quoting paragraph text from memory.
- **Vision QA over-reports transient artifacts** — scroll-boundary clipping and in-flight toasts read as "broken" in stills. Confirm each complaint at DOM/code level (element bounding boxes, scroll state) before patching; patch only what reproduces.
- **A declared-but-unused element lookup in mount code masks a missing behavior** (the variable is fetched, never written). Grep for its usages when a UI field is visibly stale — the fix is one write at the mount site, not a CSS patch.

## Support files
- `references/fake-data-client.md` — the contract the in-memory data client must implement (builder surface, projection rules, RPC/auth/storage stubs).
- `templates/route-walk-qa.mjs` — role × route Playwright walk with error capture + screenshots; copy and edit CONFIG.
