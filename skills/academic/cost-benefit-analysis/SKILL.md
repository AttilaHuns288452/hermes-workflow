---
name: cost-benefit-analysis
description: Use when building a Cost-Benefit Analysis from estimates.
---

# Cost-Benefit Analysis

## When to use
User provides hour/rate estimates (or cost items) plus a CBA template (often a Google Docs link) and wants the analysis filled in. Common for school capstone/business docs (Attila's SF/SE group).

## Workflow
1. **Extract numbers first.** hours × rate = development cost. Then verify the stated total: SUM the row items — a stated total can disagree with its rows (real case: rows summed 185h, stated total 180h). Flag it, use the stated total by default, tell the user which to fix.
2. **Follow the template structure exactly** (section headings, order, table columns). Standard CBA skeleton:
   1. Executive Summary — purpose, costs vs benefits, net benefit, payback, verdict.
   2. Objectives — measurable, numbered.
   3. Cost Analysis — 3.1 Initial (one-time): development, hardware/infrastructure, training, deployment. 3.2 Ongoing (recurring annual): licensing (₱0 for custom-built), maintenance (~15% of dev cost/yr), hosting/ops. Total over N years (3 yrs for small systems; state why).
   4. Benefit Analysis — 4.1 Tangible (monetized, backed by an ASSUMPTIONS TABLE: volumes, rates, prices, with a research basis per row), 4.2 Intangible (qualitative: High/Medium impact).
   5. Cost-Benefit Comparison — costs, benefits, net benefit + ROI, payback period, break-even benefit level.
   6. Sensitivity Analysis — costs +10%, benefits at 80%, both (worst case). Proves margin of safety.
   7. Recommendations — proceed/not + concrete conditions (e.g. which module to prioritize).
   8. Approval — blank signature table.
   Optionally append References — strengthens school submissions.
3. **Ground benefits in research** (web_search). For healthcare: no-show rates, reminder effectiveness, admin-time costs — see references/clinic-cba-research.md. Cite sources inline + in the reference list. Use CONSERVATIVE mid-range values; the sensitivity section is the safety net.
4. **Never fabricate unknowns.** Names, decision-makers, client-specific facts stay as placeholders ([Your Name], [Decision-Maker 1]) unless the user supplies them. "Fill the template, don't touch what's not clear yet" = leave those.
5. **Deliverables**: when a Google Docs template exists, DOWNLOAD it (`/document/d/<ID>/export?format=docx`) and fill it IN PLACE with python-docx (preserves template formatting, fonts, dividers — markdown-exporter output loses them). When no template exists, write markdown and use `markdown-exporter md_to_docx`. Full recipe, python-docx pitfalls, and the Word-COM → PyMuPDF → vision_analyze QA loop: `references/python-docx-template-pipeline.md`. Verify the docx via read_file (auto-extracts docx text) — check sections, tables, and ₱ symbols survived.
6. **Vision-model readability QA (this user REQUIRES it)**: render the filled docx → PDF (attach to the running Word instance via GetActiveObject, ExportAsFixedFormat format 17) → PyMuPDF PNGs → `vision_analyze` every page → fix → re-render until clean. Vision reliably catches: header duplication from multi-run edits, wall-of-text paragraphs, monthly-vs-annual math confusion, tables split at page breaks, orphaned reference lines, blank trailing pages.
7. **Number changes ripple everywhere**: when the user changes ANY input (time period 3-yr → 1-yr, or a single cost item like deployment 4k → 3.6k), recompute EVERYTHING: initial total, grand total, net benefit, ROI, payback, ALL sensitivity scenarios (costs+10%, benefits 80%, worst case), break-even %, exec summary, comparison table, recommendation. Then verify by asserting every OLD value is ABSENT from the final text ("Php71,400" not in doc) — presence of the new value is not proof the old one is gone. Split-paragraph trap: a paragraph previously split into 3 (exec summary P1/P2/P3) means paragraph-match updates catch only the first fragment — old numbers survive in the others. Match each fragment, or sweep by old-value absence.
7b. **Citation ↔ reference 1:1 check**: after any citation/bullet edit, verify every reference list entry is cited in-text and vice versa (uncited ref = APA violation). Watch for malformed multi-source citations: ";" before ")" like "(A, 2021; B, n.d.;)".
8. **Google Docs template delivery**: uploading the filled .docx to Drive opens it as a Google Doc (instant path when no Google auth). For direct template editing, see routing below.

## Google Docs routing (important)
- From Hermes, editing Google Docs = `productivity/google-workspace` skill (google_api.py / gws CLI). `setup.py --check` first; `--install-deps` if a ModuleNotFoundError appears.
- The `google-docs` skill (google-drive/ dir) is Codex-plugin-only — it calls mcp__codex_apps tools that do NOT exist in Hermes. Do not load it for Hermes work.
- NOT_AUTHENTICATED → OAuth setup flow is in the google-workspace skill: user creates a Desktop OAuth client in Google Cloud Console (enable Drive + Docs APIs, add self as test user), then `--client-secret <path>` → `--auth-url --services docs,drive` → user approves in browser and pastes the redirect → `--auth-code`. Dependencies already installed on this PC.

## Pitfalls
- Stated total vs row-sum mismatch — always check before building the cost tables.
- Inflated benefits: keep assumptions conservative and visible; sensitivity analysis must stay strongly positive even at costs +10% AND benefits 80%.
- Currency: use ₱ consistently (template may mix $ and Php); verify it survives docx conversion.
- Don't invent clinic/hospital-specific facts; mark them as assumptions and let sensitivity carry the risk.
- Template fillers: multi-run paragraphs (must clear runs[1:]), red template example text (force black), tables found by header text not index, non-idempotent insert scripts, "[6]" substring matching hijacking paragraphs that contain "[6]–[11]" — details in references/python-docx-template-pipeline.md.
- Windows cleanup: the filesystem is case-insensitive — `rm -f Name-Final.docx` deletes `Name-FINAL.docx`, `cp x FINAL.docx` overwrites `Final.docx`. Intermediates go in build/; always `ls` after cleanup.
- User reports "numbers not updated" but the file verifies clean → STALE VIEW, not stale file. Prime suspects: the Google Docs original (never edited — still the blank template; the filled version only exists in the downloaded docx) and old PDF/docx tabs in a viewer. Verify the file first (arithmetic assertions), then point at the exact path — don't re-edit.
- Row-sum vs stated-total mismatch fix: keep the user's stated total as the anchor and REBALANCE rows to sum to it (185h→180h: Requirements 10→8, Patient records 25→20), and keep table rows consistent with bullet details (deployment bullet 12h ↔ table row 12h, ₱3,600).
- User edits in Word are live: the approval table can gain real names between sessions. Edit the CURRENT docx in place (never rebuild from an earlier version once the user has touched the file — rebuilds lose their edits). On PermissionError (locked by Word), save to a temp name, then two-step rename when unlocked.

## This user's document style (Attila)
- NO em dashes — commas/words instead. En dashes in numeric ranges are fine.
- In-text APA citations (Author, Year) at every sourced claim; full APA list at the end.
- Assumptions as bold intro + bulleted list with bold labels; short paragraphs, never walls of text.
- No red/colored text; placeholders stay; ₱ throughout; plain English.
