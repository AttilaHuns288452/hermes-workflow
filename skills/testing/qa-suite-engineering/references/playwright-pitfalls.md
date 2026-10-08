# Playwright Selector, Timing & Flow Pitfalls

Each rule: the trap, then the mechanism.

- **Never extract data with a regex over `page.textContent()`** — textContent
  joins adjacent elements with NO whitespace, so a value parsed "up to the next
  word" eats the next element's text (e.g. a password captured as
  `Pass123This`). Read the specific element instead (`locator('div:has(> b)')`
  .filter({ hasText: 'label' })).
- **`:has-text()` is case-insensitive substring** — `button:has-text("Active")`
  also matches "Inactive" and clicks the wrong toggle. Use `:text-is()` for
  exact label matching on toggles and state-bearing buttons.
- **Same-labelled buttons in one form resolve by DOM order.** A suite clicking `form button:has-text("LABEL")` with `.last()` to reach the submit is silently redirected when another same-labelled button is inserted ABOVE the submit. DOM order inside the form is part of the test contract — grep the suite tree for the label before adding or moving form buttons.
- **Apps render duplicate navs (desktop sidebar + mobile bar); one is hidden at
  any viewport.** `locator('nav').first()` may pick the hidden one and time out
  waiting for visibility. Use `allTextContents()` joined, or scope to the
  visible element.
- **Positional selectors (`:first()`, `nth(0)`) are nondeterministic whenever
  list order can tie** (equal prices, equal timestamps). Select by a stable
  name/id inside the row, not by position.
- **Broad text regexes over a whole page false-pass**: wrong pages contain
  common words. Pin assertions to a state string unique to the expected screen.
- **Fixed waits race async settles** (webhooks, provider round-trips): poll with
  a budget (e.g. 24 × 1.5s) until the expected text appears. Do NOT reload
  inside the poll loop — each reload restarts the fetch you are polling and
  starves it.
- **A failing check must carry evidence in its output** (the relevant page text
  slice or state dump) — otherwise every diagnosis costs a reproduction run.
- **Chrome cannot be told to duplicate a tab** (Playwright/CDP has no clone).
  Verify per-tab session isolation with two pages in one context + refresh,
  and assert the new-tab case separately (fresh tab starts signed out).
- **Expression-bodied arrow helpers break when patched with two statements**:
  `() => a.clear(); b.clear()` is a syntax error. When a sed-style edit adds a
  statement to a one-liner callback, wrap the body in braces and re-run a parse
  check over every edited file.
- **A loading-state assert after a blind sleep races SPA boot** — a skeleton
  check that samples at a fixed 700ms fails on cold contexts even when the app
  is correct. Wait for the indicator itself (`.animate-pulse`-style locator
  with a bounded `waitFor`), then assert its presence.
- **Anchor screenshots of smooth-scrolling pages capture mid-flight renders**
  (half blank, stale nav highlight). Load with `reducedMotion: 'reduce'` in the
  context (or emulate it) and a short settle before `screenshot()`.
- **Horizontal page overflow: find the culprit, don't mask it.** Detect with
  `document.documentElement.scrollWidth - clientWidth` first — rect scans
  MISSED trailing-margin overflow (a full-width element with `mr-N` extends
  the page while every `getBoundingClientRect()` stays inside the viewport).
  Then scan every element's rect to LIST what extends past the viewport width
  (and know the list can come up empty when the culprit is pure margin): long
  unbroken inline `code` tokens need `overflow-wrap: anywhere`, flex rows need
  `min-w-0` on the flex-1 child (an input's `min-width: auto` floor is its
  intrinsic width, the classic 320px overflow culprit), grid tracks need
  `minmax(0, 1fr)` — a bare `1fr` is `minmax(auto, 1fr)`, whose auto min floors
  the track at its items' max min-content contribution, and an `overflow: auto`
  scroll container zeros its own min-size as a grid/flex ITEM but does NOT zero
  its intrinsic contribution up the ancestor chain, so a closed in-flow
  dropdown or long chip row silently floors the track (fix at the track, plus
  `min-width: 0` on the suspect child). When the rect scan comes up empty,
  bisect: hide candidates one at a time (`display: none`) and watch
  `document.documentElement.scrollWidth` drop. Wide tables belong in an
  `overflow-x: auto` wrapper (their scroll rect is NOT page overflow).
  Never `body { overflow-x: hidden }` — it hides the defect from the test too.
- **Flow assertions must follow the real route chain from source.** Grep the
  submit handlers' `navigate()` targets and the real CTA labels before writing
  URL/click assertions — a harness expecting the "obvious" URL gets click/URL
  timeouts that look like product flakiness but are harness errors (a
  multi-step flow often routes through an intermediate confirm screen before
  the result screen, which is a separate refresh-safe route).
- **Instant-settling mocks auto-advance past transient screens.** When demo/mock
  state resolves immediately (a mock payment flips to "paid"), the app's effect
  redirects before you can assert the intermediate screen (payment/QR display).
  Freeze that ONE redirect test-side with `page.addInitScript` stubbing
  `history.pushState`/`replaceState` to a no-op, assert the screen, then follow
  the real CTA — no app changes, and a fresh context per test means no restore.
- **Conditionally rendered forms (`{open && <Form/>}`) are absent from the DOM
  until toggled** — a flow check that loads the page and looks for the form
  passes vacuously or times out; click the toggle trigger first and assert the
  form appeared before filling it.
- **Fixture ground truth is the seed data's machine values, not the UI's
  display labels** ('approved' vs "Confirmed") — assert the machine value, then
  the label separately; a conflated assert breaks when either side changes.
- **Click timeouts on short pages are usually coverage, not bugs.** Fixed bottom
  tab bars, sticky headers, and floating action buttons overlay targets at
  natural scroll; `scrollIntoView({ block: 'center' })` before clicking.
  Investigate the app only when the target genuinely has no handler.
- **Form values are invisible to text assertions.** `textContent`/`innerText`
  never include input VALUES or placeholders — assert typed state via
  `locator.inputValue()` (or `input.value`); routed through textContent, a
  value check silently passes over the wrong value.
- **`page.evaluate()` accepts NO timeout option** — passing `timeout:` is
  silently ignored and a hung page renderer blocks the call forever. Treat an
  evaluate that never returns as evidence of a page-side hang or recursion
  (guard with a Node-side `Promise.race` timer) — not of a slow network — and
  follow the crash-triage rule below.
- **A click that kills or hangs the tab: check mutual callback recursion
  FIRST.** When two modules each wire the other's full flow (A's open() renders
  content and calls B's show(); B's show() renders and calls A's open()), one
  click enters an async render cycle that OOMs the tab ("browser has been
  closed") — grep the click path for handlers that call each other and make
  the lower layer show-only BEFORE hunting regexes or loops (both look
  innocent). Bisect with a micro-probe (step markers + hard timeout +
  `page.on('crash')`) that calls the suspect handler directly, with and
  without its argument.
- **A TypeError reading a property of undefined far from the action usually
  traces to a 404'd `<script src>`.** A wrong path (e.g. `demos/x.js` vs
  `js/demos/x.js`) leaves that module's globals undefined and the crash lands
  wherever one is first dereferenced. Log `response` 404s in EVERY probe; when
  a global is unexpectedly undefined, grep the HTML's script srcs against the
  served tree.
