# Visual Audit Workflow (Firecrawl + MiMo + DeepSeek)

Pattern for "make this look premium" / "improve this site" tasks. Used on hermes-workflow overhaul 2026-07-27.

## Flow

```
1. Firecrawl screenshot of live site
   firecrawl_scrape(url, formats=["screenshot"], screenshotOptions={fullPage: true, viewport: {width: 1440, height: 900}})

2. MiMo vision analysis (vision_analyze with the screenshot)
   - Ask for brutal honest review: spacing, hierarchy, color, readability, premium feel
   - Request specific 1-10 scores per category
   - Ask "what needs the most improvement?"

3. Read source code (CodeGraph probe → read_file if needed)

4. Delegate fixes to DeepSeek V4 Flash via delegate_task
   - Include ALL specific issues from MiMo audit in the goal
   - Include exact CSS class changes, line numbers, color values

5. Build + deploy (also delegated to DeepSeek)

6. Firecrawl screenshot again → MiMo post-audit
   - Compare scores before/after
   - Report improvement delta to user
```

## Firecrawl Screenshot Pitfall

**Problem:** Firecrawl returns signed GCS URLs that expire (~5 min). Passing the raw signed URL to `vision_analyze` fails with 400/403 errors.

**Fix:** Download the screenshot locally first, then pass the local file path to `vision_analyze`:

```python
import subprocess, os
url = "<firecrawl signed screenshot URL>"
path = os.path.expanduser("~/Documents/screenshot.png")
subprocess.run(["curl", "-sL", "-o", path, url], timeout=30)
# Then: vision_analyze(image_url=path, question="...")
```

**Alternative:** Use `firecrawl_scrape` with `fullPage: false` for just the viewport (smaller, faster, but misses lower sections).

## MiMo Vision Prompt Template

```
This is [before/after] the [project name] site. Score 1-10:
(1) Visual quality, (2) Spacing/whitespace, (3) Hierarchy,
(4) Color consistency, (5) Text readability, (6) Premium feel.
Be brutally honest and specific. What improved? What still needs work?
```

## Delegation Briefing Template for Visual Overhauls

Include in `delegate_task` goal:
- Each specific issue from MiMo audit as a numbered fix
- Exact CSS values to change (e.g., `text-xs text-[#8895b8]` → `text-sm text-[#a0aec8]`)
- Line number hints (e.g., "Hero section is around line 265-339")
- Build + deploy instructions
- "Do NOT modify data files" constraint

## Ground-Truth Triage Before Fixing

Vision reviews over-report. Before patching anything one flags, verify each checkable claim against DOM measurement and classify it:

- **Measurable defect** (computed color, `getBoundingClientRect` widths, `scrollWidth > clientWidth` overflow, element width vs column width): fix at the owning layer.
- **Appearance claim** ("looks clipped", "superimposed", "orphan line"): confirm at full resolution or drop. Known false-positive classes: full-page screenshots stitch fixed bars mid-image, "occluded text" is usually the natural viewport fold, symmetric moving parts alias in sampled frames, currency glyphs OCR as bare letters (₱ reads as "P"), hairline progress-bar fill percentages are misread at any size, line-art SVG icons read as "broken image placeholders", and small pill/counter numbers get miscounted.

When a prose report asserts a state inconsistency (badge counts, which rows carry an accent), re-ask the SAME image with pointed per-element questions — then settle with a DOM probe. Prose counts drift; computed values do not. Probe recipes (computed-style, min-content clone): `frontend-patterns` → `references/tailwind-jsx-defect-pitfalls.md`.

## Local Dev-App Probe Harness (Playwright against localhost)

- Dev servers started as background jobs die between turns — restart and wait for readiness inside the SAME command that runs the probe.
- `waitUntil: 'networkidle'` flakes while HMR is recompiling (or another consumer hits the server) — use `domcontentloaded` plus a fixed settle wait, and retry once on timeout before treating navigation as broken.
- Set `localStorage` only AFTER a first navigation: evaluating on a fresh page targets `about:blank`, which throws `SecurityError` on storage access.
- Demo/mock builds that auto-inject a session on boot cannot reach their logged-out screens by clearing storage — they re-create the session on reload. Log out through the in-app flow first, then screenshot.
- Full-page screenshots of fixed bottom bars and FABs: see the stitching false-positive class above — verify clipping claims with a viewport-only screenshot at full scroll.

Keep the QA harness (screenshot + check scripts) in the repo (`qa/`, `scripts/`) — scratch dirs get pruned between turns, and a rebuilt harness silently drifts from the one that passed.

## Cross-Reference

For the full vision audit checklist with before/after scores, specific fixes that worked, and second-pass improvements, see `hermes-workflow-documentation` skill → `references/vision-audit-checklist.md`.
