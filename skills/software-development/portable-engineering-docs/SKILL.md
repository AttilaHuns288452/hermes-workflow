---
name: portable-engineering-docs
description: Use when building or syncing project documentation systems.
---

# Portable Engineering Documentation

Documentation-as-code that produces ONE self-contained artifact a teammate can
open anywhere: `docs/*.md` sources → generator → single-file HTML handbook →
verifier. No hosted site, no docs framework, no CDN. Works for private repos and
`file://`.

## Always-on rules (the documentation invariant)

**Code · database · tests · docs sources · generated artifact are ONE
synchronized system.** A meaningful change (code, architecture, database,
security, QA, dependencies, file structure, workflows, env vars, business rules)
is NOT complete until the relevant `docs/*.md` are updated in the SAME change
set, the artifact is regenerated, and the verification passes. Never hand-edit
the generated file. Never merge while docs describe the previous architecture.

- **Code is authoritative.** Docs contradicting the implementation get fixed;
  code that contradicts its own docs gets flagged as a defect, not silently
  documented.
- **Never document from memory or design files.** Extract every file path,
  symbol, migration number, version, and test count from the current tree.
  Plausible-sounding names invented from memory (a function that "must exist")
  are the top source of fake docs — a symbol-existence verifier catches them.
- **No fabricated claims.** Test counts = what actually ran. Features = what
  exists in code, not in Figma/plan docs. Unverified physical checks are labeled
  as unverified. Secrets and personal/clinical data never appear — placeholders
  only.
- **Quoted historical material is verbatim or it is not quoted.** When the
  brief says preserve original wording (session prompts, transcripts, email):
  full text in a fenced block inside `<details>`, never paraphrased, never
  truncated to be tidy — the fence preserves exact wording and gains the copy
  button, the collapsible keeps the page navigable. Label editorial summary
  lines (result / evidence / verification) as editorial so a reader can tell
  the two apart.
- **Release/audit documents distinguish historical evidence from current
  state** ("audited at commit X" vs "current HEAD") — never present an old
  commit's results as the present state, and never erase the history.

## Procedure

1. **Audit current HEAD first.** Tree, manifests, migrations, functions, QA
   files, existing docs, recent git history. Build the fact table BEFORE writing
   prose. Decide what is actually present; do not redo already-fixed work.
2. **Shape the system** (justify any deviation):
   ```text
   README.md            → concise orientation, points at the artifact
   docs/*.md            → documentation sources (edit these)
   build script         → compiler: merges sources + REAL source-code slices
   DEDICATED_ARTIFACT.html → generated handbook (never hand-edit)
   verify script        → asserts docs match the tree
   ```
   One file the user can copy: embed everything (inline CSS/JS), navigation via
   `#anchors`, client-side search over rendered DOM text, copy buttons with an
   `execCommand` fallback (clipboard API is unavailable on `file://`).
3. **Content architecture** (the knowledge-base standard — a reader must answer
   "where is this implemented / which rule protects it / what breaks if I change
   it" for every module): start-here → architecture (layer diagram + what each
   layer does) → system map (concrete action→state traces) → file map → module
   map (purpose, invariants, failure modes) → concept index
   (WHAT/WHY/WHERE/HOW/DEPENDS ON/PROTECTED BY/TESTED BY/IF MODIFIED) → domain
   pages (DB, security, payments, scheduling, storage, notifications, recovery,
   QA) → "if you change this, read this first" map → development history (when
   the session record exists: verbatim prompts grouped by phase + prompt→code
   traceability table) → glossary → limitations &
   release state. Every major section carries an **Implementation table**
   (layer | exact path | what it does) and the top carries a **master
   traceability table** (feature × frontend/server/database/external/QA).
4. **Code snippets are extracted at build time** from real files (path + line
   range), with what/concept/why/depends/tested/source on each. They cannot go
   stale silently because the verifier re-checks them.
5. **Verify** (scripted, not eyeballed): every referenced file path exists;
   every cited symbol/migration/QA-file exists in source; internal links resolve;
   then a **stale-claim scan of the generated artifact** for the categories of
   claim that were corrected during the work (architecture wording, versions,
   counts, removed subsystems) plus secrets/PHI patterns.
6. **Browser-verify the artifact**: open via `file://` with ALL network
   requests blocked; check nav order, deep anchors, search hits, copy buttons,
   responsive widths (390/768/1024/1440, drawer on mobile), zero console
   errors.
7. **Report** the sync explicitly: regenerated YES/NO · synchronized with HEAD
   YES/NO (verified, not assumed) · stale claims remaining N · broken links N.
   Update the project's CANONICAL release/audit document in place — do not spawn
   a new report file per pass.

## Pitfalls

- Line-based markdown converters escape inline HTML: `<details>`/`<summary>`/
  `<div>` block tags need an explicit passthrough branch (baked into
  `templates/build_docs.py`) or collapsible content renders as literal tags.
- Registering a new section in the generator via scripted `str.replace` fails
  SILENTLY when the anchor text drifted (Python replace is a no-op) — assert
  the change landed (the build output's section count/registry) instead of
  trusting the write.
- Content distilled from chat/session history carries pasted secrets (service-
  role keys, live payment keys, third-party API keys) inside otherwise
  innocuous prompts — regex-scan the extracted material AND the generated
  artifact (`sb_secret_`, `sk_live`/`pk_live`, `sk-*` key shapes, `eyJ` JWTs)
  and replace in place with `[REDACTED …]`; a clean source with one unscanned
  quote is still a leak. The extraction recipe (raw session-DB mining) is in
  `references/session-history-extraction.md`.
- `file://` blocks `fetch()`/XHR — never design docs around loading local
  markdown/JSON at runtime; embed content at build time. External `<a>` links
  are fine (they degrade gracefully offline).
- Mermaid/CDN renderers break offline — use ASCII/`<pre>` diagrams or inline
  SVG. ASCII ER/flow diagrams satisfy "visual diagram" requirements.
- Python f-strings holding CSS/JS: double every brace (`{{ }}`); a backslash
  inside an f-expression is a SyntaxError (py3.11) — hoist the expression to a
  variable first.
- **Line-number references rot on ANY edit above them.** After refactors,
  re-derive them with grep and re-pin in the same change set; have the verifier
  check them or quote ranges sparingly.
- Stale-claim scans: `.` does not cross newlines (use DOTALL for context
  extraction), and phrase matches need a legitimacy check — "every query is
  filtered by RLS" is a true security claim, "api.js holds every query" is a
  false architecture claim. Inspect each hit; fix only the wrong ones.
- Do not duplicate dependency versions in prose — cite the manifest as
  authoritative; if a version must appear in text, generate it at build time.
- The generator reads documentation sources that OTHER tasks edit: treat the
  generator's embedded diagram/label text as documentation too — stale wording
  hides inside the generator when only `docs/*.md` are grepped for fixes.
- Repo-side hosted docs (GitHub Pages) do not exist on private repos (free
  plan); removing a docs site means deleting workflows + site config + hosted-URL
  references in ONE pass, then regenerating.
- Large single-file generation: direct writes are fine for ~100KB+ markdown, but
  delegated subagent children time out on one huge write — sectioned writes
  through a sentinel. Prefer direct writing when the content is already in
  context.
- Smooth-scroll + screenshot timing: capture with reduced-motion and
  wait-for-content, never blind sleeps — mid-flight captures read as layout
  bugs and waste a debugging cycle.

`templates/build_docs.py` is a working generator skeleton (markdown subset
converter + nav + search + copy buttons + build-time code slices);
`templates/verify_docs.py` is the reference-existence verifier. Reproduce with
modifications.