---
name: external-skill-import
description: "Use when importing external skill repos into Hermes."
---

# External Skill Import

Import skills from an external source (a GitHub skills repo, another agent runtime's skill cache, a curated pack) INTO `~/.hermes/skills/` as Hermes-native skills. The source is an external library to adapt, not a tree to copy. The deliverable is a per-skill decision map (imported / merged / skipped + why), not a copy count.

## Capability-gap gate (run before any import)

Provision capability, not novelty. An external skill is justified only by a **proven capability gap**, not by the existence of a candidate.

1. Name the missing capability precisely (what task cannot be done efficiently today, and why).
2. Search installed skills + LightRAG/reference index first. Most apparent gaps are a missing instruction, a tool flag, or an existing skill not being loaded — fix those before importing anything.
3. Only when the gap is real, search external sources (GitHub via `gh search repos "<capability> skill" --limit 10 --json fullName,description,stargazersCount,updatedAt,license`; note the valid JSON field is `license`, not `licenseInfo`).
4. Decide import vs local-fix vs reject on the **capability-to-complexity ratio**: a Markdown skill with no new state is cheap; a candidate that ships a binary, a database, or its own sync service is a much larger commitment than the gap warrants. Prefer a small Hermes-native skill + shared rules over adopting a new subsystem.
5. **Reject and record the rationale** (redundant with native features / license scope exceeds need / adds an unneeded state system / unmaintained / unsafe) in the handoff. A documented rejection stops a future session from re-litigating the same candidate; an undocumented one invites the same search again.

If the gap is coordination/alignment/traceability rather than a concrete tool, the answer is usually a small local skill plus shared charter rules — not an external orchestration framework.

## Hard rules (every import)

- **Adapt, don't copy.** Convert source-runtime assumptions (tool names, invocation style, install plumbing, frontmatter fields) to Hermes equivalents before anything lands. See `references/import-transforms.md` for the mechanical map.
- **Never duplicate an existing skill.** If a Hermes skill does essentially the same job: merge or skip. Install both and the user has every skill twice.
- **Never write to `skills.external_dirs` paths or `SkillReferences/`** — read-only live sources. All writes go to `~/.hermes/skills/`.
- **System terminology wins over upstream's.** When upstream renames a shared artifact mid-project, do not adopt the rename: the already-imported family stays on its terminology; translate new files at write time.
- **Rollback point first.** Tar the about-to-be-touched skill dirs before the first write.

## Procedure

### 1. Audit the source
Inventory every `SKILL.md`: purpose, cross-skill dependencies, support files, activation conditions, runtime-specific bits. Read the repo's own docs (agent instructions, glossary, plugin manifest) for its terminology and install plumbing — you need its vocabulary to translate it. Classify each skill: import-worthy method vs the repo's own in-progress/frozen bucket vs pure scaffolding.

### 2. Audit the target for prior work
Extract frontmatter `name:` from every SKILL.md across ALL skill roots (local `~/.hermes/skills/` + each `skills.external_dirs`). A previous partial import at older vintage is common — reconcile it (merge upstream's substantive hunks into our copy), never add a second copy. Grep existing skills for dangling references to the source's invocation names (`/skill-name`, "the Skill tool with", setup commands): those mark the glue skills the import set must supply.

### 3. Map and decide per skill
IMPORT / ADAPT / MERGE / SKIP / KEEP-BOTH with a rationale each. SKIP: skills duplicating Hermes coverage (record the equivalence), in-progress/frozen buckets, and repo scaffolding (`.claude-plugin/`, `.agents/`, installer scripts, per-runtime agent configs). Before deciding, weigh each candidate on:
- **License scope** — a repo root license is a starting point; copyleft (AGPL/CC-BY-SA) imposes obligations that must match the intended use, and per-file/NOTICE/third_party terms can narrow coverage further.
- **State and dependency cost** — what new binary, database, service, or runtime does it add? A self-contained skill is rarely a bad trade; a new persistence/sync system is.
- **Redundancy vs native features** — native Hermes profiles, Kanban, cron, backups, and the team charter already cover orchestration, routing, and recovery tooling; candidates in that space must beat them, not restate them.
- **Maintenance and safety** — recent activity, real docs, readable scripts, no surprise network/credential/install behavior. A repo shipping a runnable tool beside its skills splits deliverables: import the skills, register the tool through the MCP/CLI path in `hermes-cli-automation`, and SKIP the repo's own skill-authoring helpers (skill builders, changelog updaters, tool-design prompts). KEEP-BOTH only when scopes genuinely differ (e.g. general first-pass debugging vs stuck-bug methodology) — then state the trigger boundary in both.

### 4. Adapt on write
- Terminology canon: map upstream's core artifact names onto this system's (e.g. upstream `GLOSSARY.md` → our `CONTEXT.md`) with a mechanical transform over every file.
- Invocation: convert `Call the Skill tool with "X"` / slash commands to `load the \`X\` skill`; Claude Code tool names to Hermes tools (`Read`→`read_file`, `Write`→`write_file`, `Edit`→`patch`, `Bash`→`terminal`).
- Frontmatter: strip other-runtime-only fields (e.g. Codex `disable-model-invocation`, `argument-hint`); keep name + description.
- Rename upstream-branded skill names to descriptive class-level names, then grep-rename EVERY reference, including inside previously-imported skills.
- Keep per-repo contracts existing skills already consume (e.g. `docs/agents/issue-tracker.md`) and import the glue skill when imported cross-references need it.
- Keep provenance credits, remove runtime dependencies: an attribution line is not an assumption.
- Never import upstream's install/refresh commands (`claude plugins install`, `npx skills add`, updater CLIs) into skill bodies — use the system's own mechanism; record the upstream-refresh recipe in memory instead.

### 5. Validate (all must pass before reporting)
1. YAML frontmatter parses for every touched skill; name + description present.
2. Relative-link check: every referenced `.md`/`.sh` resolves. Example tree paths inside format templates are false positives.
3. Name-collision scan across all roots: extract **both** frontmatter `name:` **and each skill's directory basename**, then also check each new name against every existing *directory* name. Hermes resolves a skill by three aliases — declared name, directory name, and path relative to the root — so a skill whose name equals another skill's directory name is marked `ambiguous` and `skill_view` refuses it by that name. Renaming the directory (never the skill) is the fix. Confirmed live: `skills/creative/hyperframes` (declared `hyperframes-html-render`) vs a `skills/hyperframes` symlink made the HyperFrames entry point unloadable.
4. Residual-reference grep: upstream brand names, `Skill tool` phrasing, runtime flags, install commands.
5. Discovery: `hermes skills list` shows each new skill enabled. The name column truncates at ~14 chars + `…`, so full-name AND `name[:15]` greps falsely read "not discovered". Grep a prefix that fits INSIDE the visible window (e.g. `name[:13]`) or a distinctive substring from the first ~14 chars. Before concluding a skill is absent, confirm against the on-disk `SKILL.md` count and LightRAG — display truncation is not registration failure.
5b. **Dead-weight gate:** `python3 ~/.hermes/scripts/skills_health.py` must exit 0. It fails on unparseable frontmatter, empty descriptions, duplicate names inside one root, plugin skills registered without a description, and any skill Hermes' own resolver marks unloadable (no `load_name`). It walks with symlinks followed, so a skill dir symlinked in from another tool's tree is scanned exactly as Hermes scans it. Import scripts that join YAML keys onto one line (see the 2026-11 roblox repair) pass a file count but leave the skill unroutable — the gate is what catches that.
6. Rebuild the lightrag index (`python3 ~/.hermes/scripts/lightrag_build_index.py`) so reference discovery sees the new set.
7. Spot-check the synced content landed by asserting real body strings from the write plan — keyed per (file, needle) pair.
8. **Routing** — discoverable is not the same as fires. Put the trigger nouns in the first 60 chars of the description AND add a one-line pointer in each existing skill that is already open when the capability is needed; the domain skill the agent loaded mid-task beats a catalog row it stopped scanning. Record that wiring inside the new skill so a later rewrite of the pointed-from skills cannot silently kill the trigger. Prove it the way routing actually works: run a fresh single-query session with a natural request (no skill named), then read the session transcript for a `skill_view` of the new skill — a passing in-process load proves nothing about selection.

### 6. Acceptance and post-import evidence

- Treat delegated summaries, README claims, and generated manifests as leads, not proof. Read the persistent study report, inspect the actual target files after adaptation, and verify the pinned source commit and tree state before accepting a candidate.
- Maintain a correction map for every adopted candidate. Fix misleading examples in place before acceptance; adding a warning beside unsafe host execution or incorrect API guidance does not make the procedure safe or correct.
- Treat a repository root license as a starting point, not blanket coverage. Inspect per-file declarations, `NOTICE`, `third_party`, embedded datasets, fonts, model code, and runtime dependencies. Record the license boundary and add a per-skill `NOTICE.md` when mixed or incomplete provenance would otherwise be lost.
- Separate static guidance checks from runtime verification. Run a small stdlib-only regression checker against the installed text, then run examples only when their dependencies and safety boundary are available. Missing dependencies mean untested, not broken or verified, and do not justify automatic installation during import.
- After the final correction pass, rerun frontmatter, collision, residual-reference, and discovery checks against the live target, then rebuild LightRAG. Do not index an intermediate adaptation and call persistence verified.
- Record durable conventions in memory (refresh procedure, terminology map). Report per-skill decisions with reasons and distinguish static, runtime, blocked, and deferred evidence.

### 7. Final verification gate

- Do not call an import complete while an independent audit still has unresolved findings. First classify each finding as fixed, intentionally accepted, blocked by missing prerequisites, or unrelated; then re-run the narrow verification for every fixed item.
- Keep the final report aligned with the live tree. Re-read the manifest, audit output, index count, and discovery results after the last write; stale counts or stale status language are integration defects, not cosmetic issues.
- Verify both persistence layers separately: a fresh CLI process must discover the skills, and the retrieval index must return distinctive queries. A passing in-process `skill_view` alone does not prove restart persistence.
- Separate “capability exists” from “capability is runtime-proven.” Static guidance, dependency-absent, sandbox-blocked, and runtime-tested results must remain distinct in the handoff.

## Pitfalls
- A tree-preserving copy can silently wipe hand-authored replacement docs when regenerated from source: re-copying the source tree restores the originals over your rewrites. Re-author or re-apply replacements after every re-copy, and re-run the residual scan on the regenerated tree — a scrub applied to one copy does not survive regeneration.
- Upstream shared-reference dirs (e.g. `shared-references/`) defeat `references/` path rewrites whose regex carries a word-boundary lookbehind (`-` is a word char there): the paths pass the residual check yet resolve to nothing. Normalize every upstream path form explicitly, then run the link check with the files deleted so stale resolution cannot mask dangling refs.
- Symlinked `references/`/`tools/` inside a skill bundle read as critical findings in security scanners and break naive bundlers; prefer self-contained per-skill copies (disk is cheaper than a permanent critical flag).
- When a repo's reviewer/transport contract is platform-MCP plumbing, do not mechanically transform it — rewrite it short around the local delegation mechanism and keep the surrounding semantics (verdict schema, fresh-context rules, gate flags). Mechanical transforms of 100+ line transport docs leave mixed half-translated residue.
- A programmatic insert anchored on a trigger word can match the SKILL.md description line inside frontmatter and break YAML — anchor on body text or assert the insertion sits after the closing `---`. Description lines reuse body vocabulary.
- A dict-keyed batch of content checks silently drops every check after the first for a given file — key by (file, needle) tuples.
- Collision identity is the frontmatter `name:`, not the directory: loader scans match by name recursively, so renaming a dir does not resolve a collision.
- A shallow clone of the source is enough for reading; keep the checkout outside the skill tree so recon can never leak into the library.
- Never round-trip frontmatter through a YAML dumper: `yaml.dump` emits `...` document markers and re-quoted shapes that break the loader. Parse for values, then reconstruct the block textually (e.g. `json.dumps` per scalar) and assert the re-parsed key set is exactly {name, description}.
- In a tree-preserving copy, upstream links resolve from the REPO ROOT as well as the file's own directory — resolve each ref against both before calling it broken, or the link-fix pass rewrites healthy refs.
- `gh search repos --json` rejects unknown fields by name: `licenseInfo` is invalid, the correct field is `license` (and `stargazersCount`, `pushedAt`, `description`, `fullName`). A wrong field name fails the whole query, so pin the field list before scripting batch discovery.
- Do not import a candidate merely because a search returned it. A star count or recent commit is a maintenance signal, not a capability match — gate on the capability-gap decision first, or you adopt a subsystem for a gap that a one-line skill would have closed.
- A source skill may ship **no YAML frontmatter at all** (the file starts with `# Title`), or a description built by hand-joining fields onto one line. Authoring `name` + `description` is part of adaptation, not optional cleanup: validate every imported file with `yaml.safe_load` after the transform and re-scan the whole tree. Keep the trigger inside the first 60 chars — that is all the prompt index shows, so a long description whose subject appears later is invisible to routing.

## Related
- `workflow/external-skills-integration` — mounting whole external repos read-only via `skills.external_dirs` (different mechanism: no adaptation, no dedupe).
- `software-development/codex-skill-import` — raw copy of SKILL.md files from Codex plugin caches (copy-only).
- `software-development/repo-integration-reconciliation` — reconciling skills when onboarding a code repository.
- `skill-library-publication` — the inverse direction: syncing the public-safe subset back out to a shared repo (staleness diff, license holds, secret scan, branch push).
