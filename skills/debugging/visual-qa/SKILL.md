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

**Key pitfall: `screenshot` takes a POSITIONAL path, not `--path`.** `agent-browser screenshot --path foo.png` parses `--path` as a CSS selector → `✗ Element not found`. Correct: `agent-browser screenshot foo.png`.

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
