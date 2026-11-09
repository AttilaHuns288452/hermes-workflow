---
name: google-forms-automation
description: Use when backfilling or verifying Google Form responses.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [google-forms, automation, surveys, data-backfill]
    related_skills: [google-workspace, browser-ui-automation]
---

# Google Forms automation

Bulk-submitting, replicating, or backfilling responses into a Google Form from a CSV/sheet, and verifying what the form has recorded.

## When to Use

- A CSV/sheet of form responses must be re-submitted into a Google Form (migration, restoration after data loss, consolidating responses into a revised form).
- You must verify what a Google Form actually recorded (count, per-response answers) without the linked spreadsheet.
- You need to know which entry fields a Google Form has and what values they accept.

## 0. Scope and integrity gate (every run)

- One form response = one claimed respondent. Before any mass submission, read the form's CURRENT response count and state the count arithmetic to the user (restoring into an empty form vs adding rows to a live dataset are different acts).
- If the user stages the request (asks a yes/no comprehension question like "do you understand, yes or no first"), answer only that question in that turn. Do not start work.
- Confirm and surface before firing: which rows, which questions get defaults, which source columns cannot be mapped. Revised forms always have drift (added/removed/renumbered questions).
- Defaults for questions with no source data: derive from correlated answers when honest, else the neutral option (e.g. "Not Sure"), and list every default rule in the final report. Defaults are the user's call — surface them even when the user said "go".
- Never delete, edit, or merge responses that already exist.

## 1. Get the field map (no auth needed)

```
curl -sL -A "<browser UA>" "https://docs.google.com/forms/d/e/<FORM_ID>/viewform" -o form.html
```

Parse the embedded `FB_PUBLIC_LOAD_DATA_ = ...;` array (it is JSON):

- `data[1][1]` = question items: `[qid, title, description, type, body, ...]`.
  - type 2/3/4 = choice (radio/dropdown/checkboxes), 7 = grid, 1 = paragraph, 11 = image, 6/8 = section headers (type 8 = page break).
- Choice question: entry id is the INNER group id `body[0][0]` (NOT the question's qid), options at `body[0][1][i][0]`, required flag at `body[0][2]`.
- Grid: one entry id PER ROW (`body[i][0]`), row label `body[i][3][0]`, shared column options `body[i][1][i][0]`.

Pitfall: `entry.N` names are not question IDs for choice questions, and grids submit one `entry.<rowid>` per row. The rendered DOM exposes `name="entry.*"` only for the current page of a multi-page form, so derive names from the blob, never from DOM scraping.

Pitfall: user-supplied filenames may contain invisible characters (narrow no-break space U+202F in dates). Locate files with a glob, not the literal path the user typed.

## 2. Map and validate before submitting

- Match source columns to fields by question text and row labels, not numbering — revisions renumber and drop questions. Prefix-match row labels against the source headers to prove column/row alignment.
- Validate EVERY value against its option list (exact text match, including case). Remap stray values to the nearest option explicitly and log the remap.
- Questions with no source column (added in a revision): default per section 0. Source columns whose question no longer exists: skip and report.

## 3. Submit

POST `application/x-www-form-urlencoded` to `https://docs.google.com/forms/d/e/<FORM_ID>/formResponse`:

- `entry.<id>=<option text>` per field (repeat the param for multi-value fields)
- `pageHistory=0,1,...,P-1` where P = page count = (number of type-8 section headers) + 1
- `fvv=1`, `submit=Submit`
- browser User-Agent header; sequential requests with a small delay

Pitfall: the POST response body is a content-agnostic JS shell — an empty rejected POST and a successful submission return the same embedded blob. HTTP 200 proves nothing. Never trust the body; verify by count (section 4).

Pitfall: a diagnostic probe submission is a real submission and may record silently. Assume it recorded, and include it in the count arithmetic and in the duplicate report.

## 4. Prove it landed

- Read the response count BEFORE the batch and again after: expected delta = rows submitted (+ earlier probes + any external arrivals during the run). The public viewform shows no count; the "Edit this form" pencil (aria-label) on the viewform means you have editor access — open it and read the `#responses` tab.
- Spot-check 2 submitted rows in the Individual response view. Extract answers from `[role="radio"][aria-checked="true"]` via `aria-label` ("answer, response for question") or `data-value`.

Pitfall: the editor canvas DOM and the response-view DOM coexist on the page, and grid answers render as radios with EMPTY innerText. Unselected grid cells look identical to "answers missing". Scope extraction to answer widgets (aria-label containing "response for"), not label text, before concluding anything failed.

## 5. Report

Include: rows submitted plus the count arithmetic that verifies them, every defaulted question and its value rule, every skipped source column and why, any value remaps, duplicates created (e.g. by probes), and the timestamp caveat — Google stamps submission time server-side, so backfilled rows carry the submission date, not the source dates.