---
name: visual-qa
description: "Visually inspect and QA local or remote web pages when computer-use/cua-driver is unavailable. Screenshot capture + vision model analysis pipeline for Windows."
version: 1.1.0
platforms: [windows]
tags: [visual-qa, screenshot, vision, testing, windows]
triggers:
  - visual QA
  - screenshot the page
  - check the site
  - QA the design
  - look at the page
  - see how it renders
  - computer use (when cua-driver unavailable)
---

# Visual QA

When `computer_use` / cua-driver is NOT installed and you need to visually inspect a web page, use this fallback pipeline.

## Preferred: agent-browser CLI (if installed)

`agent-browser` (npm i -g agent-browser && agent-browser install) gives scriptable Chrome via CDP — faster and more reliable than Edge+CopyFromScreen. Pattern:

```bash
agent-browser open "http://localhost:3000/login"      # navigates; prints page title
agent-browser eval "document.querySelector(...).value = 'x'; ..."   # run JS, return JSON string
agent-browser screenshot "C:/path/shot.png"            # positional arg — see pitfall below
```

**Key pitfall: `screenshot` takes a POSITIONAL path, not `--path`.** `agent-browser screenshot --path foo.png` parses `--path` as a CSS selector → `✗ Element not found`. Correct: `agent-browser screenshot foo.png`. The `--output` flag ALSO lies — it prints `✓ Screenshot saved to --output` but the file lands nowhere findable. Working form is positional target + explicit dir:

```bash
agent-browser screenshot http://localhost:5174 "C:/Users/YOUR_USERNAME/Desktop/shot.png" --screenshot-dir "C:/Users/YOUR_USERNAME/Desktop"
```

**MSYS `/tmp` paths break `vision_analyze`.** On Windows the shell's `/tmp/foo.png` is not a path `vision_analyze` can resolve (`media file not found: '\tmp\foo.png'`). Always save screenshots to a real Windows path (`C:/Users/...`) before analyzing.

### Reveal-on-scroll animations → BLACK full-page screenshots

Landing pages with IntersectionObserver reveal animations (`opacity: 0` +
`.is-in` on intersect) produce misleading captures:

- `screenshot --full` expands the viewport AFTER load, so the observer never
  fires for below-fold sections → the "page" is a black rectangle with only
  the hero/footer visible. Vision then reports "massive empty middle section"
  — it's the capture, not the page.
- Two consecutive black frames with `--width/--height` flags is also a
  symptom: `agent-browser screenshot` has NO `--width/--height` options
  (they're not in `--help`) — extra flags after the path get parsed as the
  output filename (saved to a file literally named `--width`).
- Verify SSR content first (`curl -s <url> | grep '<distinctive headline>'`)
  to prove the page exists, then capture with the reveal-trigger recipe:

```bash
agent-browser open http://localhost:3000/
agent-browser wait 2000
for i in 1 2 3 4 5 6; do agent-browser scroll down 1200; agent-browser wait 500; done
agent-browser eval "window.scrollTo(0,0)"
agent-browser wait 800
agent-browser screenshot --full "C:/Users/YOUR_USERNAME/Desktop/shot.png"
```

The scroll loop fires the observers; scrolling back to top before the final
capture reproduces what a user sees. Save to a real Windows path (MSYS
`/tmp` breaks `vision_analyze`). If the no-JS fallback matters (crawlers),
confirm the CSS has `@media (scripting: none)` / reduced-motion overrides —
otherwise content stays `opacity: 0` without JS.

### Testing Radix/shadcn dialogs via eval

- Radix Select portals options OUTSIDE the dialog: after clicking the trigger, query `document.querySelectorAll('[role=option]')` on the document, not inside `[role=dialog]`.
- The hidden `<input name=category_id>` inside a Radix Select is not the trigger; click the button whose text contains the placeholder (e.g. 'Select category').
- Setting React-controlled inputs via eval: use the native setter (`Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set`) then dispatch `new Event('input',{bubbles:true})` — plain `.value=` won't register with React.
- End-to-end modal check: open → fill → submit → assert `[role=dialog]` gone + row/data present in page text → clean up test data (delete the row you created). This catches dead submit handlers and silent form rejections.

### Pixel-verify colors when vision is ambiguous

Vision models mislabel hues (blue `#2563eb` called "teal" twice in a row). When a color matters, sample the screenshot with PIL instead of trusting vision:

```python
from PIL import Image; from collections import Counter
img = Image.open("shot.png").convert("RGB"); w,h = img.size
cnt = Counter()
for y in range(int(h*.55), int(h*.75)):
    for x in range(int(w*.35), int(w*.65)):
        r,g,b = img.getpixel((x,y)); cnt[(r//16*16,g//16*16,b//16*16)] += 1
print(cnt.most_common(5))
```

Also confirm computed style via `agent-browser eval "getComputedStyle(document.documentElement).getPropertyValue('--primary')"` — DOM token + pixels together settle the argument.

### Vision route fallback: OpenRouter qwen-vl when vision_analyze rejects images (proven 2026-08-12)

`vision_analyze` can fail outright when the configured aux vision route (Console Go / opencode-zen) rejects image content — `Error code: 400 ... unknown variant 'image_url', expected 'text'` (upstream schema rejection, not a size problem) or `Connection error`. Don't burn time retrying; fall back to a direct OpenRouter call:

```python
# key: read in-process from HERMES_HOME .env — NEVER print it or write it to disk
for line in open(os.path.expanduser("~/AppData/Local/hermes/.env"), encoding='utf-8', errors='ignore'):
    if line.strip().startswith("OPENROUTER_API_KEY"):
        key = line.split("=", 1)[1].strip().strip('"').strip("'"); break
# POST https://openrouter.ai/api/v1/chat/completions
# model: qwen/qwen-2.5-vl-72b-instruct (free), messages content = [{type:text},{type:image_url, image_url:{url: f"data:image/png;base64,{b64}"}}]
```

Notes: the OpenRouter key lives ONLY in `~/AppData/Local/hermes/.env` (the opencode `auth.json` holds the opencode-go key, and the hermes `auth.json` credential pool stores fingerprints only — those are dead ends). If you must stage the key, overwrite the staging file with neutral text immediately after. The opencode CLI's remote routes may be down while Hermes' route works — `hermes -z "PONG"` is the quickest liveness probe for the opencode-go path.

### Verify vision flags geometrically — don't re-shoot on faith

Vision models flag issues on dimmed-overlay screens (scrims/bottom sheets) that are often hallucinated (a screen whose markup is identical to a PASSED sibling gets 5 flags), and they MISS the real bug. When a flag needs confirming, measure instead of trusting:

```js
// playwright: getBoundingClientRect overlap check (avatar box vs text box)
const a = avatar.getBoundingClientRect(), t = text.getBoundingClientRect();
overlapX = Math.max(0, Math.min(a.right, t.right) - Math.max(a.left, t.left)); // >0 = real overlap
```

Plus a tag-balance sanity check over the whole file — this caught the actual defect (a `<div>` closed with `</span>` nested the contact text inside a 32px avatar circle):

```bash
python -c "
import re; html = open(r'<file>', encoding='utf-8').read()
for tag in ('div','span','button','svg','a'):
    o = len(re.findall(r'<'+tag+r'[\s>]', html)); c = len(re.findall(r'</'+tag+r'>', html))
    print(tag, o, c, 'OK' if o==c else 'MISMATCH')"
```

Workflow: vision flags → geometry check each flag (overlap px / delta px) → fix only what measures wrong → re-shoot → re-QA. A flag that measures clean on an identical-to-passed-sibling screen is noise.

### Playwright frame capture: viewport must cover ALL frames

Capturing individual `.frame` divs from a multi-frame design doc fails with `page.screenshot: Clipped area is either empty or outside the resulting image` when the frame's y is below the viewport bottom. Fix: `browser.newPage({ viewport: { width: 500, height: 20000 } })` for a 13×844px doc, then clip each frame's `getBoundingClientRect()`. Also run a horizontal-overflow pass in the same evaluate (`el.getBoundingClientRect().right > frame.right`) — zero-cost layout QA.

## Edge + CopyFromScreen fallback pipeline

When agent-browser is unavailable:

## Step-by-step

### 1. Serve the file (local files only)

```bash
cd /path/to/site && npx serve -l 9876 -s &
# serve may bind to a random port — poll and check output
```

### 2. Open in Edge

Write a `.ps1` file (see `references/windows-powershell-screenshot.ps1`):

```powershell
# Kill Edge first to avoid session restore hijacking the URL
taskkill /f /im msedge.exe 2>$null; Start-Sleep 1
Start-Process "msedge" -ArgumentList "--new-window --no-first-run http://localhost:PORT"
Start-Sleep 4
```

Run: `powershell -ExecutionPolicy Bypass -File capture.ps1`

### 3. Screenshot

```powershell
Add-Type -AssemblyName System.Windows.Forms
$screen = [System.Windows.Forms.Screen]::PrimaryScreen
$bmp = New-Object System.Drawing.Bitmap($screen.Bounds.Width, $screen.Bounds.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0, $screen.Bounds.Size)
$bmp.Save('screenshot.png', [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
```

### 4. Analyze with vision

```python
vision_analyze(image_url="screenshot.png", question="QA this page. Report every visual problem...")
```

Model: `mimo-v2.5-free` for standard QA. `mimo-v2.5-pro` for complex analysis.

## Pitfalls

- **Bash eats `$` in inline PowerShell.** Always write `.ps1` files, never `-Command "..."` with dollar-sign variables.
- **Edge session restore overrides `file://` and `localhost` URLs.** Kill all `msedge.exe` processes first, use `--new-window --no-first-run`.
- **`npx serve` binds to random ports on conflict.** Check actual port in output — don't assume `-l 9876` worked.
- **`firecrawl_scrape` blocks `localhost`.** Use this PowerShell method for local files.
- **`web_extract` blocks private/non-routable IPs.** Same fallback applies.
- **Glassmorphism needs busy backgrounds.** A `backdrop-filter: blur()` on a flat dark `#0a0a0f` background renders as a solid box, not frosted glass. The blur effect is invisible without colorful/shaped content behind the card.
- **Source code drifts from screenshots.** If the app was edited between the screenshot and your analysis, data values, column headers, and card styling may differ. Always read the actual source files and note any divergence in the report.
- **Viewport clipping hides defects.** A screenshot may cut off footer, bottom charts, or monthly card values. Note what is below the fold and whether a full-page capture is needed.
- **Agent-browser sessions go STALE — screenshots can show old content.** agent-browser caches pages per session: after files change (or another dev server on the same port was screenshotted earlier), a bare `agent-browser screenshot <url> <path>` can render the OLD page while curl of the same URL proves the server serves the NEW code. Symptom: vision describes content that exists in a sibling folder / older build, not the current source. Fix: use a fresh session name and navigate explicitly:
  ```bash
  agent-browser open http://localhost:5174 --session verify-<ts>
  agent-browser screenshot --session verify-<ts> "C:/Users/YOUR_USERNAME/Desktop/shot.png" --screenshot-dir "C:/Users/YOUR_USERNAME/Desktop"
  ```
  Cross-check the served module with curl (`curl -s http://localhost:$PORT/src/App.jsx | grep 'distinctive string'`) BEFORE trusting the screenshot — if curl and screenshot disagree, the screenshot is stale, not the server.
- **Vision models hallucinate exact values.** Always cross-reference dollar amounts, percentages, labels, and badge text against seed data or source constants — never trust vision alone for precise numbers.

## Performing the analysis

After capturing the screenshot, the real QA happens through cross-referencing. Follow this sequence:

### 1. Read the source code
- Read `App.jsx` / main component — understand every card, chart, and table that should render
- Read `seed-data.json` or any mock data — note every value the UI should display
- Read `index.css` for CSS variables, theme colors, glassmorphism tokens
- Read `index.html` for meta tags (cache-busting), title, font loading

### 2. Verify data accuracy
For every displayed value in the screenshot, compute the expected value from source data:

- Net worth, income totals, expense totals, profit
- Percentage changes: `((current - previous) / previous * 100).toFixed(1)`
- Badge sign logic: profit >= 0 shows '+', profit < 0 shows '-' (or `Math.abs` for color-coded badges)

### 3. Check CSS properties against requirements
Use `grep` on source files to confirm specific CSS exists:

```bash
grep -n "backdrop-filter\|blur\|glass\|frost" src/App.jsx src/index.css
```

This catches missing glassmorphism, wrong color tokens, absent blur effects.

### 4. Verify the compiled bundle
Confirm all components exist in the production build:

```bash
grep -o "ComponentName\|section title\|unique string" dist/assets/index-*.js
```

For minified bundles, search for rendering strings (section headings, chart labels, footer text) rather than function names.

### 5. Run the dev server (when needed)
Start the app, curl the entry point to verify it serves, and catch runtime issues:

```bash
cd /path/to/app && npx vite --port PORT --strictPort &
sleep 4 && curl -s http://localhost:PORT | grep title
```

**Verify WHICH app owns the port before screenshotting.** `--strictPort` makes vite EXIT silently when the port is taken, and the port may be owned by a *different project or sibling folder copy* (this user keeps `project`, `project - Copy`, `project - Copy (2)` folders, each able to run its own dev server). Screenshotting a taken port QAs the WRONG app. Guard sequence before capturing:

```bash
netstat -ano | grep ":$PORT" | grep LISTEN                      # PID of the listener
wmic process where "ProcessId=PID" get CommandLine /value       # which project's vite?
curl -s http://localhost:$PORT/src/App.jsx | grep 'useState\|import'  # confirm it serves YOUR code (Vite serves compiled /src modules)
```

Also poll the background process (`process(action='poll')`) after starting vite — if `--strictPort` failed, the process already exited and `curl 200` came from the *other* app on the port.

### 6. Compile defect report
Structure the report with these sections:

```markdown
# QA Audit: [App Name] v[N] — [screenshot filename]

**Tested:** [what's visible] | **Not tested in screenshot:** [what's missing]

---

## Requirements Compliance

| Requirement | Status | Detail |
|---|---|---|
| [req name] | ✅ PASS / ⚠️ PARTIAL / ❌ FAIL / ❌ NOT VISIBLE | [one-line evidence] |

---

## 🛑 Critical Defects

### 1. [Title]
Evidence from screenshot + source cross-reference. Include actual vs expected values.
**Fix:** [one-line suggestion when obvious]

### 2. ...

## ⚠️ Moderate Defects

### 3. ...

## 🟡 Minor Issues

### 4. ...

## ✅ Passed Checks

| Check | Result |
|---|---|

---

## Verdict: **QA [PASS/FAIL]** ⛔ or ✅
One-line reason. Recommendation for recapture.
```

## Cross-reference techniques

| What to verify | How |
|---|---|
| Data values (net worth, profit, income) | Read seed-data.json → compare to vision output |
| Percentage changes | Recalculate with `((a-b)/b*100).toFixed(1)` |
| Profit badge sign (+/-) | Check the sign logic in source: `>= 0 ? '+' : ''` |
| Glassmorphism | `grep -rn "backdrop-filter"` on CSS/JSX — not just semi-transparent colors |
| Cache-busting | Check index.html for Cache-Control/Pragma/Expires meta tags |
| Nav bar active state | Code inspection — underline vs color vs bg change |
| Footer content | Read source, note if visible in screenshot |
| All tabs/components in bundle | grep for unique render strings in dist JS |
| Label truncation | Check chart width/height, `tick={{ fontSize }}`, and responsive container constraints |

## Model routing

| Step | Model | Why |
|------|-------|-----|
| 1-3 (serve, open, capture) | deepseek-v4-flash | Mechanical execution |
| 4 (analyze — standard QA) | mimo-v2.5-free | Multimodal vision |
| 5+ (cross-reference, report) | deepseek-v4-pro | Code reading + structured writing |

## Audit loop: MiMo audits → DeepSeek fixes → MiMo re-verifies (proven 2026-08-05)

User-directed pattern that caught real regressions: **MiMo 2.5 audits screenshots → DeepSeek V4 Flash implements the numbered findings → MiMo re-verifies the fixed screenshots.** Important pinning reality: `delegate_task` children inherit `delegation.model` (config.yaml, pinned to deepseek-v4-flash) — they are NOT MiMo. To run a real MiMo agent:

```bash
opencode run --model opencode-go/mimo-v2.5 "audit prompt with absolute image paths"
```

## Capture-timing pitfalls (cost two audit rounds, 2026-08-05)

- **Hydration race:** interacting with login forms right after `domcontentloaded` can fire BEFORE React hydrates → the form submits natively as GET and **credentials land in the URL query string**, navigation never happens. Always `waitForTimeout(1500–2000)` after page load before filling/clicking in playwright-style automation.
- **Dev-compile timing:** screenshots taken while Next dev is mid-compile (first hit after edits) show skeleton states + `Compiling…`/`Rendering…` badges — a vision audit then reports "page broken/stuck loading" (false FAIL). Warm the route once, wait 4–5s post-load, capture steady state only. The same compile was the cause of one inconclusive round.
- **Error-boundary false reading:** when a page crashes, the app-level `error.tsx` ("Something went wrong" + Reset) renders INSIDE the layout — the sidebar still shows, so a screenshot looks half-broken and vision can't tell boundary from page. Resolve with a DOM probe, not vision: check `h1` text, presence of a Reset button, and `pageerror` count (React render errors caught by a boundary do NOT fire `pageerror` — the boundary swallows them, so `pageerrors: none` does NOT mean the page rendered).
- **Verify post-fix with the same probe, not just vision:** after hoisting hooks/refixing, re-run the DOM probe (h1 = real heading, no Reset button, stat cards present) before declaring the fix landed.
