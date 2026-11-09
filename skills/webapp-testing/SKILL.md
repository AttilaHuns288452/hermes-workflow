---
name: webapp-testing
description: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.
license: Complete terms in LICENSE.txt
---

# Web Application Testing

To test local web applications, write native Python Playwright scripts.

**Helper Scripts Available**:
- `scripts/with_server.py` - Manages server lifecycle (supports multiple servers)

**Always run scripts with `--help` first** to see usage. DO NOT read the source until you try running the script first and find that a customized solution is abslutely necessary. These scripts can be very large and thus pollute your context window. They exist to be called directly as black-box scripts rather than ingested into your context window.

## Decision Tree: Choosing Your Approach

```
User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │         ├─ Success → Write Playwright script using selectors
    │         └─ Fails/Incomplete → Treat as dynamic (below)
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Run: python scripts/with_server.py --help
        │        Then use the helper + write simplified Playwright script
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

## Example: Using with_server.py

To start a server, run `--help` first, then use the helper:

**Single server:**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**Multiple servers (e.g., backend + frontend):**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

To create an automation script, include only Playwright logic (servers are managed automatically):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Always launch chromium in headless mode
    page = browser.new_page()
    page.goto('http://localhost:5173') # Server already running and ready
    page.wait_for_load_state('networkidle') # CRITICAL: Wait for JS to execute
    # ... your automation logic
    browser.close()
```

## Reconnaissance-Then-Action Pattern

1. **Inspect rendered DOM**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **Identify selectors** from inspection results

3. **Execute actions** using discovered selectors

## Common Pitfall

❌ **Don't** inspect the DOM before the app has rendered on dynamic apps
✅ **Do** wait for render before inspection — but prefer `domcontentloaded` + `page.wait_for_selector(...)` for the element you need over `networkidle`. Against dev servers with HMR churn (Vite/webpack), `networkidle` may never settle, and the resulting goto/wait timeout looks like a code failure. A networkidle timeout with zero `pageerror`/console-error entries is server churn: restart the dev server and re-run once before suspecting the code.

## Best Practices

- **Use bundled scripts as black boxes** - To accomplish a task, consider whether one of the scripts available in `scripts/` can help. These scripts handle common, complex workflows reliably without cluttering the context window. Use `--help` to see usage, then invoke directly. 
- Use `sync_playwright()` for synchronous scripts
- Always close the browser when done
- Use descriptive selectors: `text=`, `role=`, CSS selectors, or IDs
- Add appropriate waits: `page.wait_for_selector()` or `page.wait_for_timeout()`

## Node ESM scripts against the bundled Playwright

When a QA script must be `.mjs`, import from the package export entry, not a deep library path:

```js
import { chromium } from '/home/attila/.hermes/hermes-agent/node_modules/playwright/index.mjs';
```

Deep paths such as `playwright/lib/mjs/playwright.mjs` fail with `ERR_MODULE_NOT_FOUND` — the package's `exports` map only exposes `index.mjs` / `index.js`. Read `node_modules/playwright/package.json` `exports` before inventing a path; a plausible-looking directory layout is not evidence of an importable module.

## Suite-authoring pitfalls (app flows)

- Native `confirm()`/`alert()` in a flow: Playwright auto-dismisses any dialog with no registered handler, so `confirm()` returns false and the flow silently aborts — the suite then false-fails a working feature. Register `page.on('dialog', d => d.accept().catch(() => {}))` (or the exact answer the flow needs) before entering any code path with native dialogs, including warning confirms the product added for safety.
- `innerText` returns `text-transform`-rendered text: a heading styled `uppercase` reads back uppercase. Assert labels/headings with case-insensitive regex (`/availability/i`), never `.includes('Availability')`.
- Toasts and transient feedback usually render through a PORTAL appended to `document.body`, OUTSIDE the app root. Asserting them against `#root`/`main` innerText false-fails a working feature ("no error message shown" while the toast is right there on screen). Read `document.body.innerText` — or the portal node — for any assertion about transient feedback, and remember input VALUES never appear in innerText at all (check `input.value`).
- When regression asserts fail after a deliberate behavior change, diff each failing assert against the current spec first: a stale assert encodes the superseded behavior and gets updated to the new specified behavior (then re-run the whole suite). A genuinely broken feature and a stale assert look identical in the summary line — confirm which one you have before editing either side.
- Node test scripts importing app source with bundler-style extension-less imports (`from './availability'`) fail under plain node. Bundle a tiny entry with esbuild at run time (`build({ stdin: { contents, resolveDir }, bundle: true, format: 'esm', write: false })`) and import the `data:text/javascript;base64,...` result — works for any Vite/React source tree without adding a test framework.
- When a suite assertion contradicts a clean manual probe (suite says +28px overflow, probe says clean), replicate the suite's EXACT preceding UI actions before trusting either side — defects often live only in a state the probe never reached (a row added, a dialog open). Reading the suite's check code first to learn its state costs one call; re-probing blind costs many.
- Suite probes bind to more than accessible names: element counts ("the only combobox"), attribute substrings (`img[src*="..."]` asset filenames, class/testid hooks), and substring regexes on visible copy all break silently when a polish pass changes them. Before renaming a visible label, swapping an asset filename, or introducing another element of the same role into a screen, grep the suite tree for the old string/selector and update the probe in the same change — or bridge with `aria-label` so the visible copy can move freely.
- A form screen often has several controls sharing text — a `Sign In` tab toggle AND a `Sign In` submit, or a `Register` tab plus a `Register` button. `button:has-text('Sign In')` matches the first (usually the tab), so the click flips the mode instead of submitting and the flow silently never authenticates. The same collision breaks accessible-name lookups: a global header search and a page-level search both carrying `aria-label="Search gadgets"` make `getByLabel('Search gadgets')` throw a strict-mode violation (resolved to 2 elements) while `input[type=search]` silently drives the FIRST one (usually the header), so the page feature never triggers and the suite reports a dead UI. Disambiguate with a unique `id`/placeholder or scope to the page region (`locator('main').getByLabel(...)`), and before writing ANY name- or role-based lookup check whether a second same-role control exists on the screen. Submit via Enter in a field (`locator('input[type=password]').press('Enter')`) or an explicit `button[type=submit]` selector, then assert the post-submit state (URL/heading changed, an authenticated element appeared) before driving the logged-in UI — a login that silently failed surfaces later as a 'broken' downstream screen.
- A plain static file server (`python3 -m http.server`) cannot serve `/api/*` serverless functions: every such request returns `index.html`, so the SPA's `res.json()` throws `Unexpected token '<', "<!DOCTYPE"` and the UI renders its error state. That is a test-environment mismatch, not a code bug. Test API-calling UI against the DEPLOYED URL (where the functions actually run) or a dev server that boots the function runtime; reserve the static server for pure-static pages. Tell: `Unexpected token '<'` from a JSON parse is always HTML where JSON was expected — check WHICH server you are on before reading it as a code defect.
- In an edge-case matrix, isolate each case (try/catch or a guarded run) and print its result as it is decided. An unhandled locator timeout or a missing fixture aborts the whole script and discards the cases that already passed; one skip/fail recorded and continued beats a red run that loses its earlier green evidence.
- Interacting with an SVG chart's dot/label link fails Playwright's actionability check even though the feature works: an `<a>` wrapping a `<circle>` + `<text>` has a bounding-box CENTER in the empty gap between the dot and its label, so `.hover()`/`.click()` reports "... intercepts pointer events" and times out while real users (who hit the dot or the label) are fine. Drive SVG marks by COORDINATE: `scrollIntoView({ block: 'center' })`, pick a mark whose `getBoundingClientRect()` sits INSIDE the viewport (a box below the fold returns unreachable coords and `mouse.move` there hits nothing), then `p.mouse.move(cx, cy)` / `p.mouse.click(cx, cy)` at the circle's center. A directly-dispatched `mouseenter` will NOT fire React's `onMouseEnter`/`onMouseLeave` — React synthesizes those from `mouseover`/`mouseout`, so exercise hover handlers with `dispatchEvent('mouseover', { bubbles: true })` or a real `mouse.move`, never a bare `mouseenter`. A cursor-following tooltip must be `pointer-events-none` or it swallows the very hover that shows it and flickers between shown/hidden.
- A suite's pass/fail summary must come from the COMMAND'S exit code, never from grepping its output. `node build | tail -1` returns tail's exit 0 even when the build failed — the failure then reads only as an odd stack-trace line while the chain continues and a broken tree ships. Write output to a log and check `BUILD_EXIT=$?` (or run unpiped) before treating anything as green; a masked failure already shipped a blank-page crash once. Conversely, a run that prints zero pass AND zero fail lines crashed before its checks — empty counts are a crash signal, not a clean run; read the log tail for the stack trace before reporting.
- A script's module imports resolve against the FILE while `readFileSync('.env.local')`-style config reads resolve against the CWD — a suite can import cleanly from any directory yet crash `ENOENT` on a config file that plainly exists. When a run dies on a missing file, read the script's own read paths to learn the CWD it assumes and re-run from there before moving or recreating anything.
- Export the app's business timezone for date-sensitive QA (`TZ=Asia/Manila` for a UTC+8 clinic). A UTC runner silently flips date-keyed fixtures to yesterday during the local 00:00–08:00 window, so day-scoped asserts pass in the afternoon and flake in the morning — the suite is not intermittently wrong; its clock is.
- QA failure triage before condemning code: a FAIL line is identical whether it is a real regression or a test artifact, so rule out the test first. (1) Wrong tab/panel targeted — a score, badge, or detail that lives on a non-default tab reads as "missing" from the default view; click through the surface's tabs/panels and re-assert before calling it absent. (2) Fixture state drifted from the run's assumptions in EITHER direction: a fixture it depends on was cleaned up by an earlier step (a test user deleted, a /tmp script pruned) — recreate it and re-run; or a stray row a prior run LEFT BEHIND breaks a precondition assertion (a "seed is Mon–Sat"-style premise fails on one leftover row whose updated_at is fresh while the authoritative config still says otherwise). Cross-check the failing precondition against the live config before believing it, and remove the litter through the owning role's write path — never relax the assertion to accept drifted state. (3) A stale bundle/CDN served the old build — grep the live bundle for a new-code marker; on lazy/chunked apps the HTML lists only the entry + preloads, so extract the chunk names from the ENTRY bundle's text and grep each chunk too, or the check false-fails "not shipped". Vite entries reference chunks as bare strings like `"./patient-CV-kOMSA.js"` (grep `"[^"]*\.js"`), not `assets/...` paths — fetch each as `assets/<that name>`; an `assets/*.js` pattern on the entry text matches ZERO chunks and the verification silently checks nothing. Confirm which cause you have before editing either the code or the assertion.
- Cache-busting a HASH-ROUTED SPA (HashRouter, `#/route`) needs the cache-buster OUTSIDE the hash: `https://host/?cb=123#/g/product-id`. Appending it inside the route (`#/g/id&cb=123`) makes `&cb=123` part of the route param, so the lookup misses and the page renders "not found" — a harness bug indistinguishable from a real broken product. The route parser reads only what is after `#/`; keep `?cb=` in the real query string before the `#`.
- A list/catalog that fills via N parallel fetches (per-category searches, lazy pagination) shows 0 items and a "0 tracked" stats strip for several seconds after `goto`. That is a timing artifact, not empty data — settle longer (8-13s) and re-read the count before concluding the data is missing or the API is down. The same artifact poisons filter tests: a baseline row count taken mid-fetch reads 0, so both "the filter empties the list" and "clearing restores it" assert against a moving target — capture baselines only after `wait_for_selector` on the first row.
- When a name/role lookup misses an element you can SEE rendered, fall back to text-filtering before concluding it is absent: `locator('button').filter({ hasText: /X/i })` finds what `getByRole('button', { name: /X/i })` misses, because role/name matching is strict-singleton and substring-based and tab/segmented controls often carry ambiguous or text-transformed accessible names.
- `getByLabel`/name matching is SUBSTRING-based and also matches `aria-label` on elements that are not labels at all: a checkbox labeled `Compare` next to a header icon link `aria-label="Compare gadgets"` makes `getByLabel('Compare').nth(0)` click the NAVIGATION LINK, and the run then reports "the checkbox list vanished" when it actually navigated away. Use `{ exact: true }` for exact-label targets, and when a click produces an unexpected NAVIGATION, dump the outerHTML of the first few matches before suspecting the app, a re-render, or a vanished element.
- Entrance-animation waves (staggered reveals) make clicks actionability-unstable: Playwright retries "element is not stable", then force-clicks whatever is at the coordinates mid-flight - often a card link underneath the intended checkbox. For state toggles (checkboxes, icon buttons, small controls) prefer a DOM-level `el.click()` via `evaluate`, which is deterministic and immune to motion; reserve real coordinate clicks for interactions that must prove pointer behavior, and let entrance waves settle before those.
- Accessible names swallow an element's descriptions: a category chip whose visible label is `Laptops` with subtext "Heavy work, code, thesis" has the accessible name "Laptops Heavy work, code, thesis", so an anchored `getByRole('button', { name: /^laptops$/i })` never matches and the click times out like a missing element. Use UNANCHORED regexes (`/laptops/i`) for name lookups, and before scripting a multi-step wizard, walk it ONCE dumping each step's visible buttons/inputs — later steps do not exist yet, and inputs hide behind secondary buttons ("Set a custom budget instead") that the flow must click first.
- `innerText` inserts newlines at inline element boundaries, so a copy assertion for "marketplace reviews" false-fails against "marketplace\nreviews" on the very page that is correct. Collapse whitespace (`text.replace(/\s+/g, ' ')`) before any multi-word phrase regex.
- The first `select` on a page is usually the sort dropdown, not the filter you mean: pick selects by their option content (e.g. the one whose options include "All" plus category names), never by position.
- An admin/settings screen that configures a data-driven surface (categories, catalog queries, feature flags) can be purely DECORATIVE: the CRUD writes a table the public site never reads, because the real config is hardcoded elsewhere. Isolated tests pass — both sides exist in their own silo. Verify END-TO-END: add/rename/delete a record through the admin, then assert the public surface (nav, filters, tiles, fetched results) reflects it AND that a hardcoded fallback does not shadow the DB value. Wire the DB rows to MERGE OVER the defaults (defaults fill gaps, DB wins) instead of choosing one source. WHY: a settings table that feeds nothing is invisible to every isolated test and surfaces only as the user's "I don't see any difference."
- Stacked dialogs break `.first()`/`.last()` assumptions: when a confirm dialog opens OVER a modal (a discard prompt over an edit dialog), DOM order, not z-order, decides `.last()`, so the locator grabs the wrong dialog and the run false-fails a working feature. Scope by content (`.filter({ hasText: 'Discard unsaved changes' })`) instead of position, and remember the reverse case too: a confirm rendered EARLIER in the tree still paints on top only if its z-index wins — if the flow looks like the prompt never appeared, the prompt may be buried under the modal's backdrop (fix the stacking or move the dialog after the modal in JSX).
- Don't replace an entire page with an error card during a data outage when that page owns navigation or filters (catalog sidebars, category chips, tabs). Keep the chrome usable and render the error INSIDE the results region. Assert during the outage state that nav/filters stay clickable — an all-or-nothing error card strands the user on a dead screen exactly when they most want to browse elsewhere. Navigation is not product data; it should survive a product-data failure.
- A clickable list row's status badge and action buttons are often SIBLINGS of the row button, not children — filtering the row with a second `.filter({ hasText: 'Pending' })` (status or action copy) resolves to 0 elements while the row is plainly visible, and the click times out like a missing row. Filter the clickable by ONE distinctive content string (title, service name) and assert status/actions from the opened detail surface; dump the region's textContent once to see which text actually lives inside the button.
- An SPA storing its session in localStorage keeps the previous account logged in after `context.clearCookies()`: role-login flows then silently drive the wrong user and role asserts pass against the wrong account. Before each role login, clear `localStorage` AND `sessionStorage` and RELOAD (clearing storage mid-page does not reset the in-memory auth client), then assert the login form is present before typing.

## Measurement pitfalls (probe targeting & scroll math)

- **A verification probe measures whatever its selector resolves to, which is often NOT the element you mean.** `document.querySelector('svg')` returns the page's first SVG (usually an icon), `pane.querySelector('h4')` returns the first section's heading, not the section you just navigated to. A value read from the wrong node is a PHANTOM defect ("labels render at 0.5px", "the jump overshoots by 2352px") that sends you patching working code. Scope every probe to its target (role/aria-label/active class, or match the state you set — e.g. the active TOC entry's heading), and print the measured node's identity (tag + text + size) next to the value. When a probe number looks absurd, check WHICH element it measured before believing it.
- **"It moves / it jumps / it changes position on toggle" claims need ink-extent
  proof, not bounding boxes.** A button and its SVG can keep identical rects
  across states while the glyph's ink extent changes (e.g. a hidden state's
  corner-to-corner slash vs a small oval — same box, ink band 54-63 rows vs
  43-63 — the icon reads as jumping). Measure in two layers: rect equality
  (both states) proves the BOX is stable; a deviceScaleFactor-2 crop of the
  control compared min/max dark-pixel rows (PIL) across states proves the INK
  is stable. Fix at the SVG (draw variant-state marks inside the base glyph's
  band), never with layout nudges.
- **A probe's own TypeError is not a page defect.** An unguarded element dereference inside `p.evaluate()` (or a `node -e` one-liner) — `{}.textContent.slice(...)`, `el.textContent` on a null lookup — throws in the PROBE, and the run's output reads "CRASH: Cannot read properties of undefined" indistinguishably from an app failure. Guard every dereference (`(el || {})`, `?.`), and when a probe crashes, fix the probe and re-run before diagnosing the app. For multi-step probe scripts, print each step's result as it completes: a probe that dies at step 3 otherwise reports only its final line (or nothing), and the missing log reads like a broken feature instead of a dead probe.
- **`el.offsetTop` is relative to the offsetParent (usually the document BODY), not the scroll container.** A "scroll to section" computed inside a static-positioned scroller overshoots by the container's own page offset. Compute from rects instead: `el.getBoundingClientRect().top - scroller.getBoundingClientRect().top + scroller.scrollTop`. Verify jump accuracy by measuring the target's delta from the scroller top AFTER the scroll settles - for `behavior: 'smooth'` waits, or drive probes with `behavior: 'instant'` so the measurement cannot race the animation.
- **Parse display values keeping the decimal separator.** `s.replace(/[^\d]/g, '')` turns `₱2,856.36` into `285636` and the probe reports a phantom 100x outlier (an "over budget"/"over limit" defect that never existed). Strip with `[^\d.]` and parseFloat, and sanity-check parsed magnitudes against the domain before believing an outlier.
- **Name probe booleans after the condition being asserted, so `true` means the check passed** (`noOverflow: scrollWidth === innerWidth`, not a field named `overflow` computed as `scrollWidth <= innerWidth` where true means the opposite of the name). A summary line like `overflow: true` reading as PASS forces a debug pass just to re-derive the author's polarity; name the field so no derivation is needed.

## Screenshot & vision-audit pitfalls

- A `full_page: true` screenshot stitches by scrolling: fixed bottom navs, tab bars, and FABs get painted at EVERY scroll seam, so they appear mid-image over content they never overlap. Never report "element X is clipped/hidden behind the nav" from a full-page shot — verify with a viewport-only screenshot scrolled to that position plus bounding-box math (element bottom vs nav top). The stitching artifact and a real overlap are indistinguishable in the stitched image.
- A user-supplied screenshot is often a COMPOSED mockup or a mid-scroll/stitched capture (phone-frame overlay, floating chrome painted mid-image, a modal caught mid-scroll): its reported "defects" are frequently capture artifacts, not real. Reproduce the exact complaint against your OWN render (fresh Playwright capture at the reported width/state) before editing anything, and fix only what reproduces. Fixing toward a mockup inserts bugs into working code.
- Vision audits over-report: a decorative SVG misreads as a broken image, an arrow button reads as a stray chip, and numeric reads (progress bars, percentages) wobble between calls. Confirm every vision-flagged defect against source code (does the alleged element even exist?) and a full-res crop BEFORE patching; for numeric claims read the code that computes the value instead of re-asking the vision model. Frame each audit question as "concrete visible defects only, do not invent issues that are not visible" — an open-ended "any problems?" invites invented defects that cost a triage pass each. Patching an over-read inserts real bugs into working code.
- Vision reads whatever bytes are on disk AT CALL TIME — if a screenshot write and a vision call race, the model can describe the PREVIOUS file and flag a defect your fresh state already disproves. Sequence them (screenshot → short wait → analyze), never fire them near-simultaneously. When a vision verdict contradicts your own live DOM/geometry measurement, trust the measurement, re-shoot + re-analyze before concluding; do not "fix" toward a stale image.
- For SIZE / WIDTH / ALIGNMENT / OVERFLOW claims, measure the rendered rects (`getBoundingClientRect`, `documentElement.scrollWidth` vs `window.innerWidth`, `elementFromPoint`) at each target width. Vision is for legibility and polish; it cannot be trusted for pixel dimensions (a 48×52 tile reads as "portrait/stretched" and a centered pill reads as "left-aligned" when it is not).
- Some genuine defects are visible only at narrow widths (320px) or only in one state — capture the audit matrix at both mobile (~390) and desktop (~1440) widths, and probe overflow with `document.documentElement.scrollWidth` vs `window.innerWidth` at 320px too. For diagnosing horizontal overflow, see `references/mobile-overflow-debugging.md`.
- A vision-flagged stray text fragment ("a half-buried word under the card") may be PHOTO pixels or OCR noise, not UI. Attribute it before patching: grep the UI source for the fragment, hit-test the DOM at the fragment's coordinates; if neither yields it, re-shoot with the suspect image layer hidden — a fragment that vanishes with the image is image content. Tiny badge/pill text (10px caps) misreads routinely ('CONFIRMED' reads as a broken word): verify small text against the source string, never patch toward an OCR misread.

## Paint-level verification (clipped-but-present content)

CSS clipping (`overflow: hidden`, transforms, off-track layout) keeps DOM text, layout rects, and visibility predicates fully alive while NOTHING renders: `innerText`, `textContent`, `getBoundingClientRect`, and visibility checks all report a completely blank carousel/tab strip as healthy. For multi-state content (carousels/sliders, tab panels, drawers, horizontal strips) verify that each state PAINTS:

- Hit-test the visible center of the clip viewport: `document.elementFromPoint(x, y)`, then read `el.textContent` — only painted content is hit-testable. Pair with a screenshot of that state.
- `elementFromPoint` takes VIEWPORT coordinates: an element scrolled below the fold hit-tests `null`, a false "blank". `scrollIntoViewIfNeeded()` before hit-testing.
- A rect intersecting the viewport is not evidence of paint — a clipped slide still intersects. A health check written at the layout layer can never see a paint failure; assert at the layer that can fail.
- State-switch suite asserts ("dot click advances the carousel") reading `innerText` pass on clipped-but-present text. Add one paint-level check per stateful surface so the suite can catch clipping regressions.
- After every navigation (dot, tab, open, autoplay tick), hit-test the NEW state before declaring it renders.

## Visual polish loop (user expectation)

For visual/UI work, a green suite is NOT the finish line: iterate screenshot → vision review → fix confirmed defects at the owning layer → re-shoot and confirm, until no real defects remain. Judge the rendered result, not just the passing checks.

Full-app sweeps ("visual QA everything on mobile and desktop, loop until no more bugs") run as a matrix, not page by page:

1. Capture ONCE: every role × route at ~390 AND ~1440 (plus 320 for overflow), each shot paired with a machine overflow check (`documentElement.scrollWidth` vs `innerWidth`). One batch script; a long capture in the foreground times out, and half a matrix is worse than none.
2. Audit in batches of ~3 captures per vision call, tagging each surface CLEAN or defect-list.
3. Filter the known artifact classes BEFORE believing any flag (stitched fixed nav, marquee mid-glide partial cards, tiny-text OCR noise), then confirm every remaining defect against source or geometry before patching.
4. Fix root causes only, then re-shoot the fixed surfaces PLUS any surface sharing the fixed component — a shared-row fix changes other screens.
5. Re-run the label-coupled suites before shipping; a suite assert broken by a deliberate label change is updated in the same change.
6. **Fan out the audit, serialize the fixes.** A broad polish mission across many surfaces can be dispatched as parallel READ-ONLY visual-audit subagents (one per surface group — public pages vs admin/auth), each rendering at the target widths and returning a severity-tagged concrete-defect list. Verify every reported defect against the LIVE render before fixing — a child's report is a self-reproduction that can cite a stale bundle or over-read vision — then fix at the owning layer and re-verify. Never relay a subagent's "looks fine" or "fixed" as proof.

## Canvas / WebGL artifacts (Three.js, p5, raw canvas)

DOM text cannot verify a canvas page, and pixel assertions are flaky. Make the artifact assertable instead:

1. In the artifact itself, expose a tiny state hook covering exactly what interaction changes: `window.__pageState = () => ({ ready, autoRotate, distance, rotationY })`.
2. Assert initialization: the hook reports `ready: true` AND the canvas has nonzero backing size (`[canvas.width, canvas.height]` — viewport-sized, not 0x0).
3. Assert each control by DELTA, not by appearance: read state, act (click the button, or `page.locator('canvas').dispatchEvent('wheel', { deltaY: 300 })` for zoom), read state again, require the relevant field changed. For reset controls, assert only fields the animation cannot move (camera distance, pitch, mode flags), or pause the animation before comparing: a continuously-running loop mutates rotation state between the click and the read, so an assert like `yaw equals its reset literal` false-fails a working reset on the very next frame.
4. Attach `page.on('console')` (type=error) and `page.on('pageerror')` collectors and fail the run on any entry — a WebGL page can render while silently throwing.

**Pixel readback pitfall:** `canvas.toDataURL()` / `getImageData` on a WebGL canvas returns BLANK unless the context was created with `preserveDrawingBuffer: true` — a 0-pixel readback is not a render failure. Measure rendered pixels from `page.screenshot()` (compositor output) plus PIL stats or vision instead.

Serve the artifact over a local HTTP server (`python3 -m http.server` in its directory, navigate to `http://127.0.0.1:PORT`) so CDN importmaps and cross-origin texture loads behave as in production; do not assume `file://` matches that behavior.

Before the first browser run, syntax-gate the inline script: extract the `<script>` contents to a temp `.js` and run `node --check` on it — or run `~/.hermes/skills/html-prototype-build/scripts/check_inline_js.js <file>`, which checks each block separately (modules as `.mjs`) and skips `src=`/JSON/importmap blocks. An HTML file passes every HTML lint while an inline script carries a syntax error that renders as a blank canvas, and the browser run then reads as a WebGL failure instead of a typo.

## Reference Files

- **examples/** - Examples showing common patterns:
  - `element_discovery.py` - Discovering buttons, links, and inputs on a page
  - `static_html_automation.py` - Using file:// URLs for local HTML
  - `console_logging.py` - Capturing console logs during automation