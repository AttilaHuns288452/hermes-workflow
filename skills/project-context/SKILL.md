---
name: project-context
description: Use when the user says 'add to our context' or hands docs.
---

# Project Context Bundle

Assemble a project's scattered documents (proposals, studies, defense notes,
transcripts, mission briefs) into ONE durable, agent-readable context folder a
future session can load without re-discovery. "Add into our context" means
this — not merely reading files into the current conversation.

## Procedure

1. **Find the existing home first.** Probe project dirs for an established
   context doc set (PRODUCT.md/DESIGN.md-style doc roots, a context/ folder,
   a prior doc bundle) before creating anything. If a home exists, extend it.
   Otherwise create `~/Documents/Projects/<project>-<workstream>/context/` —
   one workspace per workstream (e.g. defense prep), not one per session.
2. **Convert every source document to markdown**, one file per source,
   lower-case hyphenated names (`defense.md`, `feasibility-study.md`). docx →
   the `docx` skill (markitdown first, `scripts/extract_docx_md.py` fallback).
   Keep extraction text-only; images/charts stay in the source originals.
3. **Verify before adopting** (see pitfalls): hash dedupe filename variants;
   anchor-check an existing markdown export against its source document.
4. **Write the README index at the workspace root**: a table
   `File | What it is | Source of truth (exact path)` — every markdown file
   maps to the exact original it came from. Add a short "headline facts"
   block (what the project is, who owns it, top open items) so a cold session
   orients in seconds.
5. **Save a compact memory pointer**: workspace path + headline facts only,
   never document contents. The folder is the content; memory just makes it
   findable.
6. **Report** the folder path, the file table, and a digest of the key facts
   in the reply — the user wants the material working for the task ahead, so
   the reply is part of the deliverable.

## Pitfalls

- **Sensitive material (grades, panel critique, transcripts, contact details)
  stays local.** Do not commit a context bundle into a public repo without
  explicit approval — a later `git add -A` there sweeps it in silently.
- **Sources of truth are the originals, not the extractions.** When a docx is
  revised, re-extract and replace the markdown; never hand-patch extracted
  text to fix a figure — the fix belongs in the source document.
- **"Our context" is durable, not in-chat.** Reading files into the
  conversation dies with the session; the folder + README + memory pointer is
  the deliverable.
- **Hash filename variants before converting** (`revised (1)`, `(2)`, `final`
  are usually copies): byte-identical inputs are one document.
