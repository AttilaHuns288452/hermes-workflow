---
name: documentation-as-code
description: "Use when code changes must regenerate synced documentation."
tags: [documentation, handbook, docs-sync, generated-artifact, verification, maintainability]
triggers: [update the documentation, regenerate the handbook, docs out of sync, documentation HTML, generated docs, docs consistency, stale documentation, documentation synchronization, engineering guide]
---

# Documentation As Code

A documentation set is a build artifact like a binary: **sources + generator + output +
verifier**, updated in the SAME change set as the code it describes. A code change without
regenerated docs is an incomplete change; a docs change without regenerated output is an
incomplete change.

## The pipeline (know which file is which)

```text
README            → concise orientation only (links, quick start, one overview diagram)
docs/*.md         → documentation SOURCES (edit these)
<generator>       → compiler (merges sources + real source-code slices)
GENERATED.html    → the artifact (never hand-edit)
verify script     → proves the docs still match reality
```

Establish this chain explicitly in the repo's change guide so every future change follows it.

## Procedure per change

1. **Classify the change**: does it touch routing, architecture, data access, DB behavior,
   migrations, security, payments, scheduling, storage, notifications, deployment,
   dependencies, QA, env vars, file structure, or business rules? If yes, docs update is
   mandatory in this change set. If no, say explicitly that no doc content change was needed
   — but still re-run the generator when the generator embeds source-code slices.
2. **Update the affected `docs/*.md` sources** — the pages that describe the changed area,
   not a blanket rewrite. The code is authoritative: when docs and code disagree, fix docs
   (unless the code has a real defect).
3. **Regenerate**: run the generator. Never patch the generated file to "save time" — the
   next regeneration erases it and the source stays wrong.
4. **Verify** (this is the step people skip):
   - run the repo's verify script;
   - scan the GENERATED output for stale-claim classes: old version strings, old counts
     (migrations/files/suites), names of deleted files, retired subsystem names, secrets;
   - open it in a browser: navigation, anchors, search, mobile width, console errors.
5. **QA**: run the affected suites plus the full matrix before declaring done.

## The verify script (build one per repo, run it every change)

A ~50-line script that FAILS when docs drift from reality:

- every `` `path/like/this` `` reference in the docs exists in the repo;
- every named symbol (functions, triggers, components) occurs in the real source/migrations;
- every referenced migration/QA file exists;
- numeric claims (counts, versions) match the manifest/filesystem.

Pitfall: it catches exactly the drift that review misses — invented paths, renamed symbols,
and copy-pasted trigger names. Wire it into the change routine, not CI theater.

## Pitfalls

- **Line-number references rot with every edit.** Docs that cite `file.jsx (L345)` go stale
  on ANY unrelated insertion above. Re-pin them at the end of the change: grep the symbol,
  replace the numbers, then regenerate. Prefer symbol names over line numbers when the
  reader does not need an exact line.
- **The generator itself can hold stale content** (embedded diagram text, section list,
  snippet ranges). When a referenced file moves or shrinks, re-check the generator's slices
  — a snippet range pointing past the file silently truncates the excerpt.
- **Version/count claims belong in ONE place.** If a doc must state a version, make the
  generator read it from the manifest at build time; otherwise every upgrade becomes N
  stale claims. Until then, grep ALL docs for the old value when it changes.
- **Retired subsystems leave prose behind.** Deleting a service/workflow/page requires a
  sweep for its NAME across docs and generator text — deployment sections and architecture
  diagrams keep describing deleted machinery for months.
- **Do not describe aspirational architecture.** Document the router/service layer that
  EXISTS (e.g. "hand-rolled switch inside BrowserRouter", not "React Router <Routes>").
  A docs pass that makes the architecture SOUND cleaner than the code is a defect factory.
- **Docs QA claims must match actual runs.** Copy counts from the real suite output in the
  same session; never carry forward old numbers because a previous report said so.
- **Generated output is verified, not trusted.** "Regenerated" is not "synchronized" — the
  stale-claim scan + browser pass is what earns the word.

## Report convention

End doc tasks with explicit statements: the generated artifact **regenerated: YES/NO** and
**Documentation synchronized with current HEAD: YES/NO**, backed by the checks actually run.