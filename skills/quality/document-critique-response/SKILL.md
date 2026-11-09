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
Classify every criticism BEFORE touching the document: VALID / PARTIALLY VALID / NOT VALID / UNCERTAIN, each with one line of reasoning grounded in the deliverable's own stated methodology. When the user brief pre-rules on a criticism (keep X, justify Y, don't remove Z), record the ruling and follow it. Later reviewers do not reopen a ruling — the user's direct instruction outranks any critique, however well-argued. Log every such deliberate omission in the change log with its governing instruction, so the response can point at the ruling instead of silently dropping the item. The output of this phase is the edit list — nothing else gets edited.

### 3. Recompute independently
Recompute every headline number from the stated inputs with exact arithmetic (Python Decimal). When recomputation and the document disagree, the recomputation wins and the document gets fixed. Check both the sum of displayed rounded rows and the total computed from unrounded components — a rounding-convention footnote can make a small apparent discrepancy NOT an error. The critique's own claimed value is not evidence: when exact recomputation matches the document and contradicts the reviewer's number, the critique is the error — report the slip and change nothing. Never edit a correct figure to match a reviewer's arithmetic.

### 4. Classify each edit against the five grounds
Map every candidate change to a ground number. Any change with no ground gets dropped. Watch for your own audit introducing stylistic rewrites of assumption descriptors (e.g. swapping "below-market student rate" for "internal rate-card assumption"): descriptor wording that characterizes an assumption is itself assumption content and only changes on the five grounds.

### 5. Edit the generator, never the artifact
When the document is built by a script, patch the script and rebuild. Hand-edits to the artifact are silently lost on the next build. See `references/docx-generator-verification.md` for the edit-and-verify mechanics.

### 6. Verify, then ship
- String gates on whitespace-flattened extracted text (old text gone, new text present, required disclosures present).
- Re-run the numeric recomputation against the rebuilt document's printed values.
- Vision QA the changed pages only.
- Ship to BOTH `~/Downloads` and the repo/project root; the root copy is what teammates find.
- Completion reply shape: deliverable links first, then what was Fixed, then what was Deliberately not done with the governing instruction named. A critique item silently dropped reads as an unfixed defect in the next review round.
- Commit the generator + generated artifacts together.

### 7. Self-diff your own audit pass
After a change batch, diff your hunks against the governing rule and revert any that changed methodology, assumptions, numbers, or conclusions without one of the five grounds. This catches overcorrection introduced under pressure to "strengthen" the document.

## Multi-document set missions

When critique targets a SET of graded deliverables (proposal + CBA + feasibility
study + plans + sprint docs) and the ask is "make everything consistent and
apply every panelist note":

1. Inventory the package: list every file, `md5sum` against any older copies
   (same bytes = one document), extract each `.docx` to markdown (`docx` skill)
   into a working dir. Audit the extracted text; edit the real docx afterward.
2. Fan out parallel domain audits as subagents with disjoint read-only scope
   (financial recalculation, cross-document consistency, external evidence,
   architecture/claims), each writing findings to its own file; the parent
   consolidates. Give every child the requirement doc (panelist notes) and the
   project's verified fact base by absolute path.
3. Build ONE discrepancy matrix across all findings: ID | Topic | Document A
   says (exact quote + section) | Document B says (exact quote + section) |
   Verdict | Required correction | Documents to change. The exact quotes are
   load-bearing — the fixer locates edits by string match.
4. Audit-first gate (standing default for multi-fix responses): present the
   plan — finding register summary, classification, phasing with the REASON
   for each phase order, and what stays untouched without direction — then
   STOP until approved. This user routinely asks for exactly this on audit
   missions ("don't do anything yet, give me the plan first and why"); even
   when unasked, a multi-finding response gets plan-first. Correction-map
   form: current → problem → correct → required change.
5. Fix with one owner per document; verify by re-extracting each edited docx
   and string-gating old text gone / new text present, then layout-check the
   rendered pages of edited sections only.
6. Deliver one dated output directory copied to BOTH `~/Downloads` and the
   project root: audit report, change log, cited-sources file, remaining-
   issues file for anything only humans can do (new surveys, signatures,
   printing), and a verification/defense checklist.

## When the critique arrives as a formal audit report

An external audit (finding register with IDs, severities, evidence pointers
spanning many source documents) gets an intake pass before any edit:

1. Extract the finding register: ID, severity, status (confirmed vs open
   design), and which documents each finding cites; map every finding to the
   deliverables it can land on.
2. Confirm the audit matches the current file state. A finding quoting a
   figure that does not exist in the current deliverable means the file
   changed since the audit baseline (someone else edited it) — diff against
   your last known state first and never fix from assumed content.
3. Classify each finding: DOC-FIX (text/math/labels you can repair),
   TEAM-DECISION (a design fact only the project owners can settle: component
   choice, architecture route, threshold/envelope values), EVIDENCE-GAP
   (needs an external artifact: supplier quote, test result, signature), or
   CHALLENGABLE (arguable under the deliverable's lens — answer it with
   reasoning instead of silently complying).
4. Phase work so agreed baseline decisions come FIRST: prose edits made
   before the underlying facts are settled are guaranteed rework. For
   TEAM-DECISION items produce a one-page decision sheet with options and
   consequences — never pick a technical design fact yourself.
5. No silent number changes: every corrected figure carries a visible note
   (what it was, why it changed), per the user's "defensible and not
   questionable" rule.
6. Findings whose fix conflicts with a direct user instruction are answered,
   not applied: list them under "not done" with the governing instruction
   named, so the next review round sees a ruling instead of an unfixed defect.

## Pitfalls
- A finding that returns across review rounds and that character-level probes
  cannot reproduce is a counting artifact, not a hidden text defect. Reproduce the
  reviewer's count (which visible elements would yield those numbers?), eliminate
  the mechanism so the artifact cannot recur (glue split tables, name
  cross-reference targets), and report the reader artifact instead of renaming
  correct content to match a miscount.
- Verification text extraction of tables interleaves columns at line breaks — match with whitespace-flattened regex and row-anchored patterns, not literal substrings. Whitespace flattening does NOT rescue phrase probes when columns interleave word-by-word (a table row's label phrase never appears contiguous in pdftotext output even though the row is visibly painted). To verify a row landed: read its cells back via python-docx or vision-check the rendered page; treat zero PDF phrase matches on table content as inconclusive, never as absence.
- Word/LibreOffice pagination is not deterministic across machines (distribution name, version, fonts). Gate on section presence and text, never on page numbers.
- Hyperlink URLs live in `w:hyperlink` runs that `p.text` neither shows nor edits — a duplicated URL is invisible to paragraph-level reads and unfixable there; scan and fix at XML `w:t` level.
- Curly quotes and multiplication signs (× vs x) normalize differently between the source script and extracted render text — compare on normalized forms.
- Hyphenation in rendered PDFs splits words across lines ("below-\nmarket") — extraction checks need `word-\s?word` tolerant patterns.
- Edits to a script through a REPL are invisible to `read_file` views of the file taken earlier in the session — verify against current source with `find`/regex before asserting a replacement target exists, and assert every replacement matched before writing.
- Health, safety, or outcome benefits added at the user's request still get
  claim discipline: modal wording ("may reduce exposure"), an explicit
  non-guarantee clause, and a real citation. Absolute benefit claims are a
  panel's easiest target, and "defensible and not questionable" outranks
  enthusiasm in the request.
- A defense/Q&A prep sheet quotes the deliverable's live numbers. After any
  figure-changing batch, re-run the sheet's number gates — a prep sheet citing
  figures the panel can no longer find in the document is worse than no sheet.
- Recompute dataset claims (respondent counts, splits, percentages) from the raw data export before repeating them — documents quote numbers the data never showed.
- Transcribe scanned evidence before citing it: a signed letter may approve a PROCESS (e.g. permission to seek consultation) rather than validate the artifact it is filed under.
- Same-person name and title spellings drift across team-authored documents; normalize to one form everywhere — graders read the drift as sloppiness.
- A fix batch invalidates its own surroundings: renumbered captions make prose cross-references stale, and any rebuild shifts pagination (TOC pages, "see Table N" pointers). After every batch, re-run the whole-document numbering and cross-reference audit plus the string gates — auditing only the edited range lets the batch's side effects ship.

## Support files
- `references/project-resources-cba-lens.md` — domain notes for defending a Project Resources CBA (donated labor, capacity vs cash, revenue vs net, scope, payback wording).
- `references/docx-generator-verification.md` — generator-edit and text-verification mechanics for python-docx pipelines.
