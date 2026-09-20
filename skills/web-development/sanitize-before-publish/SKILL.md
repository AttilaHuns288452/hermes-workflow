---
name: sanitize-before-publish
description: "Strip internal annotations before going live."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [publish, deploy, content-review, sanitization, wireframe, web-development]
    category: web-development
---

# Sanitize Before Publish

Wireframe and internal-review sites contain developer-only annotations that must NOT go live: personal names in annotation notes, internal reviewer handles, proposal section references, draft markers, and internal todo notes. This skill defines how to find and strip them before deploying.

## When to Use

Load this skill when:

- Deploying a wireframe, prototype, or internal-review site to a public URL
- The user asks to "clean up" or "remove internal notes" from a site before publishing
- You're about to push a site that was built for internal review (fact-check annotations, reviewer callouts, draft markers)
- The user corrects you after a deploy because internal annotations leaked through

## The Rule

**Never deploy internal-review chrome to a public URL.** A single missed annotation is a public embarrassment. Wireframe review notes, reviewer names, proposal cross-references, and draft markers are for the working copy — not the live site.

## Patterns to Strip

### 1. Reviewer/Stakeholder Annotations

Internal reviewer names used as annotation callouts (not as proper attribution):

```html
<!-- STRIP these patterns -->
<div class="wf-note"><b>Palma:</b> hero treatment options...</div>
<div class="wf-note">pricing wording pending Palma (messaging.md Q2)</div>
<div class="wf-note"><b>Palma:</b> confirm you want individual names public...</div>
<div class="wf-note">imagery TBD with Palma</div>
<div class="wf-note">Palma/PM.</div>
<div class="wf-note">Palma's call — ...</div>
<div class="wf-note">with Palma ...</div>
```

**Key distinction:** A person's name in a **team grid** (proper attribution) stays. A person's name in an **annotation note** (`<b>Name:</b>`, `pending Name`, `Name's call`, `with Name`, `Name/PM`) goes. The annotation sentence usually becomes noise without the attribution — strip the whole annotation, not just the bold tag.

Regex patterns (case-insensitive):
- `<b>Name:</b>` at start of annotation
- `Name/PM.` or `pending Name` or `Name's call` or `with Name` or `Name:`
- `TBD with Name` or `TBD.*Name`

### 2. Proposal/Document Section References

Internal cross-references to proposal sections:

```html
<!-- STRIP these patterns -->
<div class="wf-note"><b>Fact-check:</b> the four cards below are lifted near-verbatim from
proposal §2 (Statement of the Problem)...</div>
<div class="wf-note">table is proposal §4 verbatim...</div>
<div class="wf-note">specs condensed from proposal §6 (Hardware) and §7 (Software)...</div>
```

Regex patterns:
- `proposal\s*§\d+` → remove the `§N` reference, keep the rest if it's real copy
- `§\d+\s*\([^)]*\)` → remove parenthetical section descriptions
- `proposal\s*` → clean up dangling "proposal" words after section removal

### 3. Draft Markers

```html
[DRAFT — confirm with Palma/PM.]
[TBD]
[FIXME]
[TODO]
```

### 4. Internal Review Chrome (optional)

Some wireframe sites have a `wf-pagelabel` bar at the top showing page name, version, and fact-check notes. This is review infrastructure, not site content. Strip it for production unless the user explicitly wants it.

## Procedure

### 1. Scan before committing

```bash
# Find all internal-annotation patterns
grep -rn -i -E '(palma|palma:|palma/|palma\'s|pending palma|with palma|proposal\s*§|§\d+|draft|todo|fixme|tbd.*palma|<b>palma:</b>|palma:</b>)' . --include='*.html' --include='*.css' --include='*.md' 2>/dev/null | grep -v node_modules | grep -v .git
```

### 2. Strip annotations

For each match, decide:
- **Is it a real content sentence that happens to mention a person?** → Remove just the person reference, keep the sentence.
- **Is it a pure annotation (reviewer note, fact-check callout, draft marker)?** → Remove the entire annotation block.

Use `patch` for targeted removal. For bulk removal across many files, use `execute_code` with regex replacement — but verify the regex doesn't over-match (e.g., don't strip "Jessica Mae T. Palma" from a team grid while stripping "Palma:" from annotations).

### 3. Verify

```bash
# Confirm no patterns remain (except legitimate team-member names)
grep -rn -i -E '(palma:|palma/|palma\'s|pending palma|with palma|proposal\s*§|§\d+)' . --include='*.html' 2>/dev/null | grep -v node_modules | grep -v .git
```

### 4. Commit the cleanup separately

```bash
git add *.html *.css
git commit -m "Remove internal annotations and proposal references before deploy"
git push
```

This keeps the cleanup distinct from content changes, so the user can see what was stripped.

## Pitfalls

- **Over-stripping team names.** "Jessica Mae T. Palma" in a team grid is attribution — keep it. "Palma:" in an annotation is a reviewer callout — strip it. The difference is context: grid vs. annotation, full name vs. handle, attribution vs. instruction.
- **Leaving dangling sentences.** Removing `<b>Palma:</b>` from "<b>Palma:</b> hero treatment options — (a) clean product shot..." leaves "hero treatment options — (a) clean product shot..." which reads as broken copy. Strip the whole annotation or rewrite it as neutral copy.
- **Missing proposal references.** `§5`, `§12`, `§1` etc. can appear in `proposal §5` or standalone. Check both patterns.
- **Assuming the user wants all notes stripped.** Some "wf-note" boxes contain real copy (e.g., "Own it, don't rent it" pricing explanation). Read before deleting.

## Verification

After cleanup, before reporting success:
1. `grep` confirms no annotation patterns remain (except legitimate full-name attributions)
2. The site still reads coherently — no dangling sentences where annotations were removed
3. The commit is pushed and the live URL returns 200
