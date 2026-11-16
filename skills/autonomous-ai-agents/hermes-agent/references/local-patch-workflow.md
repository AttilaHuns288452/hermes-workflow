# Local patch workflow + proving a patch is live

## Durable patch recipe

For each working-tree hotfix in `~/.hermes/hermes-agent/`:

1. **Guard test** in `tests/` asserting the end state of the touched function (schema type, gated branch, emitted string) — not the diff text.
2. **Re-apply script** (`~/.hermes/scripts/ensure_<topic>_patches.py`): per patch, `check signature -> exact old->new text swap -> re-check`; run the guard test at the end (inline import, falling back to a generation-venv python when the caller's interpreter lacks runtime deps); exit 0 clean, 1 with the failing patch names. Idempotent: a present patch is a no-op. When the patch set is a plain working-tree diff, skip hand-coded swaps: `git add -N` any new test files, save `git diff > ~/.hermes/scripts/local_patches.diff`, derive each patch's health marker from the diff itself (the longest added line per file), and re-apply with `git apply --3way` — markers regenerate with the diff and cannot drift from the patch text. Drive every per-topic ensure script from ONE entry point wired to an existing frequent cron so patch survival is checked continuously, not only after updates. Author multi-line anchor strings with `"""` + ONE backslash + newline (the line-continuation form the existing entries use): a doubled backslash bakes a literal backslash-plus-newline into the value, the repair arm reports "anchor text not found" forever, and the defect hides because the check (keyed on the new text) passes on a healthy tree. Assert every anchor occurs in the pre-patch text before trusting the script.
3. **Repair-path proof**: once, feed the script's swap functions the pre-patch file text (e.g. `git show HEAD:<path>`, or a text-level simulation of `hermes update`'s reset) and assert the check passes afterward, then diff the repaired file against the working patched copy (byte-identical) — otherwise the script only ever no-ops on a healthy tree and its repair arm has never run.

## Proving a patch is live (runtime evidence chain)

When a source fix lands but old behavior persists, distinguish STALE RUNTIME from MODEL behavior before re-patching anything:

1. **Process start vs patch mtime** — `stat -c '%y' <file>` vs `ps -eo lstart,cmd`. A process started before the edit holds pre-patch code; schemas/prompts materialize at process start.
2. **Assembly log lines** — `grep <component> ~/.hermes/logs/agent.log` shows timestamped rebuilds of the affected surface (tool-schema assembly, prompt build).
3. **Raw emitted payloads** — `messages.tool_calls` in `~/.hermes/state.db` stores what the model actually emitted. Inner-argument type distinguishes schema shapes (JSON string vs bare object), so turns before/after the fix show which schema the model was served.
4. **Fresh-context provider probe** — a model in a contaminated session replays its own old broken call shapes from history; that imitates the stale bug but isn't it. Probe the provider in a fresh conversation with both schema shapes to establish its true per-schema behavior.

Interpretation: patched source + post-patch processes + fresh-context probe passing = fix live; continued bad calls only in old sessions = history imitation, not staleness.

## Committing a durable patch set

A repo's pre-commit lint can run a STRICTER config than the project's own lint (e.g. a `ruff.pre-commit.toml` that enables rules `pyproject.toml`'s `[tool.ruff.lint]` deliberately disables). When committing durable local patches whose text must stay byte-identical to the re-apply anchors, never let an auto-fix (`ruff --fix`, formatter) rewrite them to satisfy that gate — it desyncs `local_patches.diff` and the exact-text swap anchors, so the re-apply arm mis-fires after the next `hermes update` and the working tree silently loses the fix. Either commit `--no-verify` (when the gate is style-only and the guard tests — the real correctness check — pass), or apply the fix, regenerate the diff (`git diff > local_patches.diff`), and re-prove the anchors. A cosmetic lint gate must not be allowed to rewrite a re-apply contract.
