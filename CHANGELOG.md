# Changelog

Dated entries, newest first. Convention: `date — headline`, then bullets grouped by what changed and why.

## 2026-11-09 — Live-tree sync: skills refreshed, docs made honest

The repo was five days behind the live install and still claimed 1,367 skills.
This entry records what moved and, more importantly, what the numbers actually mean.

- **Skills: 1,367 → 1,482** (715 top-level directories). 195 published skills were older
  than their live copies and were refreshed; 115 skills that existed only in the live tree
  were published (including `ux-psychology` and `opensandbox`).
- **Held back, deliberately:** the `security-reverse` (46), `roblox` (43), `remotion` (12)
  and `aris` (7) packs remain unpublished until their upstream LICENSE/NOTICE is carried
  into this repo. They are third-party work; publishing them without attribution would be
  the wrong kind of convenient.
- **`SKILLS_CATALOG.md`:** the old sentence "Every skill below is installed and available
  in this Hermes Agent profile" was false for roughly 900 entries. It now states the true
  relationship: the catalog is the library; the maintainer's live profile injects a subset
  (~585) and the rest is adoptable breadth.
- **`README.md`, `SETUP.md`, site:** counts refreshed, duplicate-name claim corrected to
  "no duplicates inside a category, vendored copies excepted".
- **`team/SOUL.md`:** synced to the current operating contract (adds the "never stop with
  work still doable" rule and the tier-gated routing paragraph).
- **`docs/`:** rebuilt from `src/` after the copy changes.

Rationale: peers use this repo as the reference for the workflow. A stale count is a small
lie that compounds into wrong expectations; a public repo should say exactly what it holds.

## 2026-11-04 — Multi-agent specialist team published

The coordinated PM + 7-specialist organization, its shared governance, and the two skills that build and govern it are now first-class repo content.

- **`team/` — new.** `CHARTER.md` (operating model, role table, handoff contract, idea→launch lifecycle), `SOUL.md` (PM / Team Lead contract), and 7 specialist role contracts under `team/profiles/<role>/SOUL.md` (designer, engineering, research, marketing, sales, documents, qa). Collaboration runs through direct profile delegation + Kanban; the Desktop group chat is optional and never a blocker.
- **`skills/autonomous-ai-agents/hermes-multiagent-team/` — new.** How to build and verify the org: profile creation, role SOULs, the shared charter, structural + per-profile + behavioral test gates.
- **`skills/autonomous-ai-agents/team-alignment-traceability/` — new.** The cross-functional owner / dependency / acceptance-criteria contract, plus the provenance and security gate for future external-skill intake.
- **`skills/decide`:** tier-gated routing fixes (scope discipline, demand-driven skill composition).
- **README:** new "Multi-Agent Team" section (role table + `team/` layout); skill count 1365 → 1367.
- **SKILLS_CATALOG.md:** the two new skills listed under `autonomous-ai-agents`.
- **Site:** both skills added to the workflow catalog, counts refreshed, `docs/` rebuilt.

Rationale: the team org existed only in the live install. This publishes it as reusable, auditable repo content with the alignment contract that keeps cross-functional handoffs traceable.

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
