# Changelog

Dated entries, newest first. Convention: `date — headline`, then bullets grouped by what changed and why.

## 2026-10-16 — Workflow docs aligned with verified behavior

Gap audit of the documented workflow against live Hermes behavior (verified 2026-10-16). Small additive diffs only — no rewrites.

- **INTEGRATION.md → new "Workflow Operations" section.** Fills five documented gaps:
  - *Delegation & concurrency:* when to delegate (parallel independent workstreams, review separation, long mechanical batches) vs. the anti-pattern of spawning agents for show; disjoint file ownership; evidence-required-from-children read-back; concurrency limits referenced from `config.yaml` keys.
  - *Model selection & escalation:* `config.yaml` declared the single source of truth; escalation on concrete failure evidence only, never preemptively. No model IDs in the new text — config keys and provider names only.
  - *Independent verification & review:* per-output-type gates with real tool output, author ≠ verifier, findings-with-evidence over verdict words, guard tests as the regression contract.
  - *Failure handling:* bounded retry (`kanban.failure_limit`), per-integration timeouts, checkpoints, rollback (git + timestamped config `.bak` + Drive/state backups with restore script), and the self-healing local-patch mechanism (`ensure_patches.py` health markers → `git apply --3way`, `ensure_agent_patches.py`, guard tests).
  - *Skill & integration maintenance:* how a skill becomes usable (land → audit → reload → probe), the daily 06:00 profile drift check (`drift_check.py`; `local` Ollama profile exempt from MCP comparison **by design**), and skill name-collision pitfalls (rename on import, never delete).
- **INTEGRATION.md → Step 8 caveat:** model-chain tables marked as dated snapshots; `config.yaml` is authoritative, docs must not be copied model IDs from.
- **README.md:** `CHANGELOG.md` added to the project-structure tree.

Rationale: the previous docs described the pipeline shape but not its operating rules — delegation was one line, verification was a slogan, and failure handling was unrecorded. All added behavior was re-verified against the live install (cron jobs, guard tests, patch scripts, config keys) before documenting; nothing here is aspirational.
