---
name: patch-hygiene
description: Use when batch-patching files or claiming an edit landed.
---

# Patch Hygiene

Batched patch-based edits fail silently more often than loudly. This skill governs the edit step itself: where anchors come from, how results are checked, and what proves an edit landed. When the edit's landing surface is a deployed site, `references/verify-shipped-change.md` extends that proof to the live bundle.

## Rules

1. **Anchors come from a fresh read in this turn, and are long enough to be unique.** old_string text must come from a read_file/search_files result produced in the current turn — never from remembered file content or a context-compaction summary. Summaries can carry excerpts from a SIBLING project with the same file names, and those read exactly like your target while matching nothing. This includes files you wrote earlier in the SAME session: the on-disk formatting (wrapped attributes, indentation, quote style) is not what you remember writing. If an anchor feels familiar, re-read the file first. Anchor on the full statement plus distinctive context: a short fragment next to a lookalike statement lets the fuzzy matcher rewrite the NEIGHBOR line and still report success.
2. **Every edit call's result is checked — `success: true` is not `did the right thing`.** `hermes_tools.patch` returns `{success: False, ...}` instead of raising. A script that fires N patches and prints a closing line reports fiction. Assert every result (or collect them and fail on any `success: false`) inside the batch, AND read the returned diff: every hunk must sit where you intended. A hunk at an unexpected line means the fuzzy matcher hit a lookalike — repair it before doing anything else; never build later steps on a corrupted file.
3. **The diff is proof the edit landed.** After a batch, `git diff --stat` (or a re-read of the touched spans) must show the expected files/hunks BEFORE any "patched" / "updated" claim. Narrating the intent of an edit is not evidence it applied.
4. **Multi-file mechanical batches are transactional: verify everything before the first write.** Build all replacements from disk reads in one script, count-verify every anchor, and abort before the first write if any count misses. A half-applied batch is harder to fix than the original state, and a lone `patch` call per edit cannot roll back what already landed.

## Pitfalls

- A fire-and-forget patch loop "succeeds" N times while writing nothing; the failure only surfaces later when dependent steps read stale code and every symptom points somewhere else, so the debug trail starts from the wrong end.
- Never chain sequential find→replace rules whose output can match a later rule's input (remap 11→13, then 13→16, and every original 11 silently becomes 16). Remap many values (sizes, ids, names) in ONE pass with a mapping table (`perl -pi -e 's/pat/map{$1}/ge'` style) so each source value is replaced exactly once; count matches and diff before building.
- Git-untracked or freshly written files produce empty `git diff` output — prove those with a re-read or `git status`, not diff.
- When a patch is refused with a "similar but different text" error, the error's quoted section IS the file's live state and may contradict your earlier read. The "Did you mean" hint lines quote the exact live text: copy one verbatim as the new old_string (old + suggested line) instead of re-guessing whitespace or wrapping, and diff-check the result.
- A patch that replaces only part of a line must keep the line's closing delimiter in BOTH strings. When old_string covers a JSX/attribute span but the line ends in `>` or `/>`, dropping that trailing token from new_string leaves a stray `>` in the file and the build breaks on a line that "looks patched"; include the full line in both strings, or run the build/lint immediately after the batch.
- Two failed anchors on text you are sure is present is a wrong-content signal, not fuzzy-matcher flakiness: stop varying the anchor, re-read the whole file, and if it is small, switch to ONE verified full rewrite (`write_file`) after that fresh full read instead of a third anchor guess. Anchors reconstructed from a context-compaction summary or from your own earlier prose routinely diverge from disk (sibling projects, drifted versions, formatting you misremember), and each retry against phantom content wastes a turn.

- Do not patch the control the user's word suggests when the code shows something else: before patching a described UI difference ("page X lacks the Y that page Z has"), diff the compared views in source first. User widget vocabulary is approximate (a segmented tab pill may be called a "slider"), and patching the imagined control leaves the real gap in place; extract a shared component both views use rather than re-creating the control in one place.

## Key pattern

```
✅ read → patch with anchors from that read → check each result → git diff --stat matches expected files → claim
❌ batch-fire patches with a hardcoded success message
```
