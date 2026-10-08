---
name: document-critique-response
description: Use when critique arrives on a finished document to fix.
---

# Responding to Critique on Finished Deliverables

Scope: analytical deliverables (CBA, proposal, feasibility study, graded document) that receive critique or audit findings and the user asks to respond, fix, or defend. Triage every criticism against the deliverable's own stated lens before editing; change content only on the five exception grounds below.

## The governing rule (standing user instruction, verbatim)

> "Do not change a methodology, assumption, number, or conclusion merely because it is an assumption or because an alternative methodology exists. Change it only when it is mathematically incorrect, methodologically inappropriate for a Project Resources CBA, unsupported to the point of being indefensible, internally inconsistent, or clearly misleading."

Generalized grounds for change (any one suffices, nothing else does):
1. Mathematically incorrect.
2. Methodologically inappropriate for the deliverable's chosen lens.
3. Unsupported to the point of being indefensible.
4. Internally inconsistent.
5. Clearly misleading.

An unsourced or labeled assumption may stand. Hardening, neutralizing, or hedging a standing assumption is a violation, even when an alternative methodology exists.

## Procedure

### 1. Fix the lens before anything else
The user's brief supplies the lens (e.g. "Project Resources CBA: resources consumed by the project vs economic benefits/resources gained"). When the brief says to keep a perspective throughout, that lens governs every judgment; the critique's implied methodology does not. A claim can be wrong under one lens and correct under another.

### 2. Triage first, edit second
Classify every criticism BEFORE touching the document: VALID / PARTIALLY VALID / NOT VALID / UNCERTAIN, each with one line of reasoning grounded in the deliverable's own stated methodology. When the user brief pre-rules on a criticism (keep X, justify Y, don't remove Z), record the ruling and follow it. The output of this phase is the edit list — nothing else gets edited.

### 3. Recompute independently
Recompute every headline number from the stated inputs with exact arithmetic (Python Decimal). When recomputation and the document disagree, the recomputation wins and the document gets fixed. Check both the sum of displayed rounded rows and the total computed from unrounded components — a rounding-convention footnote can make a small apparent discrepancy NOT an error.

### 4. Classify each edit against the five grounds
Map every candidate change to a ground number. Any change with no ground gets dropped. Watch for your own audit introducing stylistic rewrites of assumption descriptors (e.g. swapping "below-market student rate" for "internal rate-card assumption"): descriptor wording that characterizes an assumption is itself assumption content and only changes on the five grounds.

### 5. Edit the generator, never the artifact
When the document is built by a script, patch the script and rebuild. Hand-edits to the artifact are silently lost on the next build. See `references/docx-generator-verification.md` for the edit-and-verify mechanics.

### 6. Verify, then ship
- String gates on whitespace-flattened extracted text (old text gone, new text present, required disclosures present).
- Re-run the numeric recomputation against the rebuilt document's printed values.
- Vision QA the changed pages only.
- Ship to BOTH `~/Downloads` and the repo/project root; the root copy is what teammates find.
- Commit the generator + generated artifacts together.

### 7. Self-diff your own audit pass
After a change batch, diff your hunks against the governing rule and revert any that changed methodology, assumptions, numbers, or conclusions without one of the five grounds. This catches overcorrection introduced under pressure to "strengthen" the document.

## Pitfalls
- Verification text extraction of tables interleaves columns at line breaks — match with whitespace-flattened regex and row-anchored patterns, not literal substrings.
- Word/LibreOffice pagination is not deterministic across machines (distribution name, version, fonts). Gate on section presence and text, never on page numbers.
- Hyperlink URLs live in `w:hyperlink` runs that `p.text` neither shows nor edits — a duplicated URL is invisible to paragraph-level reads and unfixable there; scan and fix at XML `w:t` level.
- Curly quotes and multiplication signs (× vs x) normalize differently between the source script and extracted render text — compare on normalized forms.
- Hyphenation in rendered PDFs splits words across lines ("below-\nmarket") — extraction checks need `word-\s?word` tolerant patterns.
- Edits to a script through a REPL are invisible to `read_file` views of the file taken earlier in the session — verify against current source with `find`/regex before asserting a replacement target exists, and assert every replacement matched before writing.

## Support files
- `references/project-resources-cba-lens.md` — domain notes for defending a Project Resources CBA (donated labor, capacity vs cash, revenue vs net, scope, payback wording).
- `references/docx-generator-verification.md` — generator-edit and text-verification mechanics for python-docx pipelines.
