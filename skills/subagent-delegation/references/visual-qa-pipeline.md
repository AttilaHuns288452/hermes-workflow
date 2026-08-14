# Visual QA Pipeline (When You Can't Click Buttons)

## The problem

Firecrawl blocks localhost/private IPs. No puppeteer/playwright installed.
Need to visually QA a locally-built page. Can't programmatically click buttons.

## The pipeline

```
Orchestrator → plan the site
  ↓
DeepSeek V4 Flash → build it (delegate_task)
  ↓
Orchestrator → serve locally, capture screenshot
  ↓
MiMo V2.5 → visual QA analysis (delegate_task, pass screenshot path)
  ↓
Orchestrator → process findings, delegate fixes to DeepSeek
```

## Step-by-step

### 1. Serve the page locally

```bash
cd /path/to/site && npx serve -l PORT --no-clipboard -s &
```

Check which port it bound to (serve picks a random port if the requested one is in use):

```bash
# Poll the background process output
process(action="poll", session_id="<id>")
# Look for: "Accepting connections at http://localhost:XXXXX"
```

### 2. Capture screenshot (Windows PowerShell)

Write a .ps1 script (NOT inline — bash eats $ signs):

```powershell
Start-Process "msedge" -ArgumentList "--new-window --no-first-run http://localhost:PORT"
Start-Sleep -Seconds 4

Add-Type -AssemblyName System.Windows.Forms
$screen = [System.Windows.Forms.Screen]::PrimaryScreen
$bmp = New-Object System.Drawing.Bitmap($screen.Bounds.Width, $screen.Bounds.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0, $screen.Bounds.Size)
$bmp.Save('C:\Users\YOUR_USERNAME\Downloads\screenshot.png', [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
```

Run: `powershell -ExecutionPolicy Bypass -File capture.ps1`

### 3. Delegate visual QA to MiMo

```python
delegate_task(
    goal="QA this page screenshot — report EVERY visual defect, button alignment, spacing, contrast, glassmorphism rendering, font loading, layout issues",
    context="Screenshot at /path/to/screenshot.png. Page should have: dark theme, centered glassmorphism card, big counter, Increment/Reset buttons, total click tracker, footer with model attribution."
)
```

### 4. Process findings → fix

Orchestrator reads MiMo's QA report, identifies bugs, delegates fixes to DeepSeek.

### 5. Deduplicate results

After MiMo reports, verify each finding is real (not a hallucination). Cross-check against the source HTML. Keep only actionable defects.

## When screenshot is empty/wrong

Common causes:
- Edge restored previous session instead of opening the URL → kill Edge first (`taskkill /f /im msedge.exe`), use `--new-window --no-first-run`
- Script ran before page loaded → increase `Start-Sleep` to 5s
- Multiple monitors → `PrimaryScreen` may not be the one with the browser
- Edge not in focus → F11 fullscreen may not target the right window. Kill all Edge processes first, then open fresh.

## When you CAN'T take screenshots at all

Fall back to code-path analysis:
- Trace every handler, every branch, every edge case
- Verify state machine transitions (initial → click → reset → click → double-reset)
- Verify DOM resolution timing (script order, elements exist before handlers)
- Report findings as a table: test case → expected → actual → pass/fail

This is less thorough than visual QA but catches logic bugs (like the total++ in reset handler bug found in 2026-07 session).

## Pitfalls

- **`$` signs in bash**: PowerShell variables with `$` get eaten by bash. Always write scripts to .ps1 files, never inline.
- **Serve port mismatch**: `npx serve -l 9876` may bind to a different port if 9876 is taken. Always read the actual port from the process output.
- **Firecrawl blocks localhost**: Don't waste time retrying. Use the PowerShell screenshot approach instead.
- **vision_analyze directly from orchestrator**: Don't. Delegate to MiMo subagent. Follows the Vision Delegation Rule.
