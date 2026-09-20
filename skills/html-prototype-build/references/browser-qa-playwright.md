# Browser QA for HTML Prototypes — Playwright Recipe

Validated click-through QA for self-contained HTML prototypes: headless Chromium, no visible browser needed (playwright ships in the Hermes venv; a running Chrome/Brave is not required).

## Setup

```bash
# serve the artifact's directory (http catches more than file://)
python3 -m http.server 8743 --bind 127.0.0.1 &
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8743/index.html
```

The Hermes cloud browser_exec blocks private/internal addresses — use local Playwright for localhost QA.

Multi-page static sites: start the server with an EXPLICIT working directory (the terminal tool's `workdir` param) — a server started from a stale cwd serves the wrong tree and every page 404s. Verify liveness with `curl` against a real file URL, never `pgrep -f 'http.server <port>'` — the pattern matches the probe's own wrapper shell and reports phantom survivors. If Python playwright is unavailable, Node works identically: `npm init -y && npm i playwright` in a scratch dir, `npx playwright install chromium`, then `require('playwright')` from a `.js` script (use `page.waitForTimeout` after navigations for apps that render on DOMContentLoaded timers).

## Syntax gate (before the browser)

```python
import re, subprocess
c = open("index.html").read()
blocks = re.findall(r"<script>(.*?)</script>", c, re.S)
open("/tmp/check.js", "w").write("\n".join(blocks))
r = subprocess.run(["node", "--check", "/tmp/check.js"], capture_output=True, text=True)
print("JS:", "OK" if r.returncode == 0 else r.stderr[:1500])
```

Broken string literals and truncated tags produce zero visible symptoms — this gate is the only cheap detector.

## Assertion script skeleton

```python
from playwright.sync_api import sync_playwright

results, errors = [], []
def check(name, ok, extra=""):
    results.append((name, ok, extra))

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": 1366, "height": 900})
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errors.append(str(e)))   # attach BEFORE goto
    pg.goto("http://127.0.0.1:8743/index.html", wait_until="networkidle")

    # drive views via the page's own nav function (tests the real wiring)
    pg.evaluate("go('browse')")
    check("filter narrows", pg.locator("#browseGrid .gcard").count() == EXPECTED)

    # mobile pass
    pg.set_viewport_size({"width": 390, "height": 844})
    check("hamburger", pg.locator(".hamburger").is_visible())

    b.close()

for n, ok, x in results: print(("PASS" if ok else "FAIL"), n, x if not ok else "")
print(f"{sum(ok for _, ok, _ in results)}/{len(results)} passed")
print("CONSOLE ERRORS:", errors[:5] or "none")
```

## What to assert (interactive-prototype checklist)

- Every view renders its expected content — counts computed from the fixture data, never assumed.
- Search / filter / sort: one assertion per dimension, asserting narrowed counts.
- Modals: open, Escape closes, backdrop click closes.
- Auth gating: gated views bounce to the auth modal; register lands in the gated view; role badge renders.
- Role gating: admin-only view rejects non-admin with a toast.
- Core flows: select → tray → compare → verdict; review submit → pending badge; admin fetch → autofill → save → row count +1; approve review.
- Persistence flows (localStorage-overlay store): after each mutation RELOAD the page and assert the state survived, and assert the public page reflects the admin change (approved review visible on the detail page, deleted gadget gone from the catalog).
- Set expectations from the live DOM before clicking: read the current count/badge/value first. Tests authored from remembered fixture values fail on correct code; when an assertion fails, dump the actual DOM state (badges, counts, attributes) before touching app code — several "failures" are test bugs, not app bugs.
- Computed math: assert one known input/output pair (e.g. monthly cost = price / lifespan / 12).
- Mobile viewport: hamburger visible, nav opens, primary table usable.
- Console + pageerror clean at the end — passing assertions with console errors still means broken.

QA-script pitfall: opening a modal-bound input with page.fill fails on the hidden element — call the open function first, then fill.

## DOM adjudication of vision-QA flags

Vision flags are hypotheses. Measure before editing:

```python
# horizontal overflow?
pg.evaluate("() => ({s: document.documentElement.scrollWidth, c: document.documentElement.clientWidth})")
# element actually inside the viewport?
pg.evaluate("sel => { const r = document.querySelector(sel).getBoundingClientRect(); return {l: Math.round(r.left), r: Math.round(r.right)} }")
```

- "Clipped element" claims: scrollWidth == clientWidth plus complete corners in a zoomed crop ⇒ false positive; do not "fix" it.
- Sticky-bar overlap: `window.scrollTo({top: 999999, behavior: 'instant'})`, wait ~100 ms, then compare the last content row's bottom against the bar's top. Smooth-scroll mid-animation yields stale geometry and false overlaps.

## Visual evidence for the user

Screenshot the primary viewports (desktop home, a data-heavy view, admin, mobile 390px) into the project folder and deliver with MEDIA: paths — the user sees the result without opening anything.
