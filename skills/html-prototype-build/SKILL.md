---
name: html-prototype-build
author: Hermes background curator
description: Use when building an HTML prototype or mockup from a brief.
triggers:
  - html prototype
  - web prototype
  - interactive mockup
  - single-file web app
  - clickable prototype
---

# HTML Prototype Build & Verify

Class: produce a self-contained HTML prototype/artifact from a brief (spec, proposal, feature list) and verify it actually works before delivering. For design doctrine (taste, anti-slop, composition) load `frontend-design` and `creative/claude-design` alongside — this skill is the engineering loop those skills assume.

## Procedure

1. **Inventory the brief.** Extract every feature into a checklist row (feature → where it lives in the UI). Anything with both a user side and an admin side gets both. Nothing from the brief is silently dropped; nothing not in the brief is invented (prototype = visual contract, demo data is expected to be fake and made-up).
2. **Commit to an information architecture.** One top nav, one view per major feature group, modals for create/review/detail actions, demo data as a single flat JS array at the top of the script. Pick a palette and type scale up front (CSS variables); no framework, no CDN dependencies.
3. **Author in appended chunks.** For anything above ~15KB, write the first chunk with write_file, then append remaining chunks via execute_code (read file → `content + chunk` → write). Verify `"appended chunk N, total: X chars"` after each append. Tail markers (`</script>`, `</body>`, `</html>`) land in the final chunk.
4. **Syntax gate — before any browser test.** Extract every inline `<script>` block and run `node --check` on the concatenation. Fix until clean. The gate catches what rendered pages hide.
5. **Serve and click through.** `python3 -m http.server <port> --bind 127.0.0.1` in the project dir; run the headless Playwright QA per `references/browser-qa-playwright.md`. Attach console + pageerror listeners before `goto`. Assert every interactive surface with counts derived from the fixture data.
6. **Vision pass, flags adjudicated in the DOM.** Screenshot primary viewports (desktop, data-heavy view, admin, 390px mobile) into the project folder; run each through vision_analyze — for a review pass, prompt each as a "harsh design audit: concrete problems only" so it returns prioritized specific violations instead of descriptions. Treat every vision flag as a hypothesis — measure (scrollWidth vs clientWidth, getBoundingClientRect, zoomed crop) before editing, and record disproven flags as false positives rather than "fixing" them.
7. **Fix and re-run the full suite** — not just the failed check — then deliver: MEDIA: paths for the screenshots, feature-to-implementation table, QA pass count and console-error status, and the skipped/when-to-add line.

## Always-on rules

- Single self-contained file, zero remote JS/CSS dependencies — it must open by double-click as well as via http.server. Remote `<img>` URLs are allowed when the user explicitly asks for real product imagery, but always with `loading=lazy` plus an `onerror` fallback to a local category tile so the file still renders fully offline.
- Include the no-cache meta header; plain demo state is in-memory and resets on reload — say so in the UI and the delivery note rather than faking persistence. Exception: when the brief includes functional flows (admin CRUD, moderation queues, triage), implement real persistence per the localStorage-overlay pitfall below instead of "simulated" toasts.
- Demo credentials are never real: any email/password combination logs in, with the login modal stating it. Gate account/admin views behind the auth modal; role-gate admin with a visible toast on rejection.
- Accessibility floor: focus-visible styles, aria-labels on icon buttons, Escape closes modals, prefers-reduced-motion respected, responsive down to 390px with working hamburger nav.

## Real-data & site-reference upgrades

When the user asks to swap fictional demo data for real products (real name + real photo, invented specs/prices/reviews) or to "reference <site>" for design cues:

1. **Source product images by scraping official product pages, not search thumbnails.** Firecrawl v2 `scrape` with `formats:['markdown']`; take the page's og:image metadata plus the first `![](url)` images. Call the API directly (urllib/requests, `Authorization: Bearer <key>`) with `FIRECRAWL_API_KEY` from `~/.hermes/.env` — do this whenever the built-in web tools return 402/billing errors and the user has a key. For design-reference research the same curl + python tag-strip one-liner works: strip `<script>`/`<style>`, read visible text for structure and the repeated hex codes for the site's palette.
2. **GSMArena product pages are a reliable source of clean product shots**: the first image on a product page is `https://fdn2.gsmarena.com/vv/bigpic/<slug>.jpg`. Find pages via Firecrawl search `site:gsmarena.com <product>`. A wrong page ID loads a DIFFERENT product's page — the images scraped come from whatever actually loaded, so never trust a URL you didn't verify.
3. **Verify every image URL before embedding**: GET it with a browser User-Agent, require `Content-Type: image/*` and >5KB (small og:images are often site logos). Official CDNs (vendor image servers, Shopify, demandware) generally allow hotlinking.
4. **Vendor CDNs and GSMArena rate-limit (429) under batch verification — fall back to Wikimedia Commons.** Query the Commons API: `https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrsearch=filetype:bitmap <product name>&gsrlimit=8&gsrnamespace=6&prop=imageinfo&iiprop=url|size&iiurlwidth=960` (send a descriptive User-Agent); take `thumburl` from landscape results (width>height, width≥600) whose file title names the actual product. Commons thumbs hotlink reliably with no rate limiting — the better source whenever a catalog needs 10+ images verified in one pass; space same-CDN HEAD checks ~1s apart regardless.
4. **Wire in**: add an `img` field to the data array, render `<img loading=lazy ...>` with the onerror fallback (rule above), and keep the demo honest with a footer label like "Demo catalog: real products, illustrative specs and prices."

## Deterministic recommender UX

When the prototype includes a ranking/recommendation engine with a NO-AI requirement (no LLM picks, no generated prose), follow `references/deterministic-recommender-ux.md`: priority-slider pattern, template-only explanations, flip/gate verification.

## Pitfalls

- **Delegating a rebuild: one job = ONE `tasks[]` entry.** Each entry spawns an independent agent that cannot see the others — splitting one build into numbered "sections" dispatches duplicates racing on the same file. Stop extras via `delegate_task(action='stop', subagent_id=…)` and `steer` the survivor with the full brief.
- **Flash-class subagents die on the single big final write** — one model response emitting a ~80KB file exceeds their response budget, often after 40+ minutes of good research. Instruct them to author in appended chunks, or keep the final large write hands-on.
- **Delegation for READING works where delegation for WRITING dies**: a read-only copy/design auditor (deliverable = exact quoted strings + why + suggested replacement) pairs safely with hands-on patching — the write-death constraint is about concurrent authors on one file, not delegation itself.
- **Salvage dead subagents before redoing work.** Live transcripts persist at `~/.hermes/cache/delegation/live/<delegation_id>/task-N.log`; grep for verified artifacts (image URLs, research data, check results) — an agent that died at the final write usually leaves the whole research phase recoverable.
- **Restyling an existing prototype: remap token VALUES, keep token NAMES.** Swapping `--green`/`--orange` etc. to the new palette in `:root` restyles ~90% of the UI in one small diff (the var names are legacy, not semantic truth) — hunt only the hardcoded stragglers (topbar, hero, gradients) afterward.
- **Escape sequences through Python.** Never generate inline JS through a layer that processes escapes (writing the file from Python code): `\"` inside a JS string collapses to `"` and silently terminates the literal — the file renders but the script is dead. Write inch marks as `in.`, prefer single-quoted JS strings, and let `node --check` arbitrate.
- **Truncation still reports success.** A verified write can be cut mid-tag on large files — the syntax gate plus tail-marker check is the detector; a broken close tag (`</\nnav>`) renders fine and hides the bug.
- **Formatted strings are not numbers.** In ranking/best-value logic pass raw numeric values plus a separate formatter — `Math.min` over rendered strings ("₱24,999") returns NaN and every highlight silently disappears.
- **Sticky/fixed bottom bars need `main { padding-bottom }`** equal to their height — otherwise they cover the last rows of content at every scroll position, which vision QA will flag after the fact.
- **Functional flows need a store, not simulated toasts.** For admin CRUD/moderation/triage over demo data, write a localStorage-overlay module (one versioned key) applied over the base dataset on every load — stored copies of new/edited records, deleted-id arrays, per-id status maps. Rules that bite: load the store on EVERY page that renders the data, public pages included, or "approve → appears publicly" silently fails; rebuild derived lists INSIDE render() because the store mutates the dataset in place — a list captured at setup time is stale after the first action; default status is source-dependent (queue items pending, embedded records approved) so centralize the default instead of filtering mixed sources by status; deleting an item must also purge its per-id status/edit entries; validation guards (duplicate name, delete non-empty parent) go in the save path with the blocked button rendered `disabled`; recompute dashboard/metric numbers from the live dataset instead of hardcoded mocks.
- **QA-script traps:** opening a modal-bound input with `page.fill` fails on the hidden element — call the open function first. Assert counts recomputed from the fixture data, not assumed — a correct filter "fails" otherwise. After an in-page scroll use `behavior:'instant'` and wait before measuring geometry — smooth-scroll mid-animation gives stale rects and false overlaps.
- **Vision flags ≠ facts.** DOM measurement outranks the vision model: scrollWidth == clientWidth + complete corners in a zoomed crop ⇒ false positive, do not edit. Overlap claims need a post-scroll rect comparison, not a screenshot impression.
- **When renumbering multi-step wizard steps, grep every hardcoded gate** (`recStep===N`, `Step X of N`, loop bounds `i<=N`) — a stale high-N gate silently skips its render callback and the step renders blank: the code exists but never fires.
- **Before deleting or renaming a function, grep the module for dispatch maps that name it** (`{page: fn}[attr]` routers, event registries). A dead key throws ReferenceError inside the shared `init()` on EVERY page that loads the module while each page's static shell still renders — it reads as a data bug on one page. Attach pageerror listeners before `goto` and treat a silent page as unproven: rendering proves nothing.
- **Filter the count from the same array as the list.** Any "showing N of M" / tab badge computed from the unfiltered array while the list renders filtered contradicts itself on screen the moment moderation or deletion filters exist.
- **When deleting a step's inputs, grep each removed field name for dead readers** — leftover querySelector lines silently return defaults and template literals interpolate `undefined` into review/summary UI ("Routine undefined away from a charger").
- **Never offer a checkbox for a constraint the engine applies unconditionally** — a 'must stay below budget' chip on top of a hard budget filter is a no-op that erodes trust in every other option on the step.
- **Comparison-table ties are not wins**: best-cell highlighting must return 'no winner' when all values (or the only two compared) are equal, and the legend must state it — identical cells glowing as 'best' is a false statement rendered in the UI.
- **One concept, one name**: grep for synonym zoos ('monthly cost' / '₱/mo' / 'estimated ownership' / 'Cheapest monthly'; 'Index' / 'Ownership Index' / 'Intelligence Index') and standardize before shipping — the same figure under four labels reads as sloppy generation. Also fix invisible attributes (title/aria-label) that carry a stale full name.
- **Brand accent = interaction only; encode value semantics in green/amber/red** — score bars all in the accent color hide whether 38 differs from 100, and prices in accent read as links.
- **Transparent PNGs on tinted card backdrops render the product as black blobs** — put product images on a white backdrop, and verify each embedded image VISUALLY; HEAD 200 is not enough (a 200 PNG can still be unusable as a thumbnail).
- **Styled range sliders need explicit webkit track rules** — bare `accent-color` tracks fail 3:1 contrast; sync a `--fill` percentage custom property from JS for the filled gradient and give the thumb a white ring, or vision QA flags both.
- **Production QA on GitHub Pages must cache-bust (`?cb=<timestamp>`) for ~2–3 min after push** — the CDN serves the old build and false-fails bugs already fixed.
- **Write the prototype copy like a real product, not a school project** (user explicit: 'treat it like a website even though it's a prototype, no saying this is a placeholder'). Purge 'mock/placeholder/prototype' from user-facing strings and image alts; demo-state honesty lives in the footer/one line, not scattered labels. Editorial catalog copy (strengths, weaknesses, summaries) uses spec-based labels ('33W fast charging'), never voice ('rare in this class') — chatty asides read as AI-generated. A full-page screenshot with a 'Placeholder artwork' watermark undoes every polish pass.

skipped: backend/persistence/real APIs — prototypes are in-memory; wire to a real stack when the user moves to implementation.
