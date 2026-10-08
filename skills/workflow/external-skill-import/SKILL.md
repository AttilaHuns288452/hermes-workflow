---
name: external-skill-import
description: "Use when importing external skill repos into Hermes."
---

# External Skill Import

Import skills from an external source (a GitHub skills repo, another agent runtime's skill cache, a curated pack) INTO `~/.hermes/skills/` as Hermes-native skills. The source is an external library to adapt, not a tree to copy. The deliverable is a per-skill decision map (imported / merged / skipped + why), not a copy count.

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
IMPORT / ADAPT / MERGE / SKIP / KEEP-BOTH with a rationale each. SKIP: skills duplicating Hermes coverage (record the equivalence), in-progress/frozen buckets, and repo scaffolding (`.claude-plugin/`, `.agents/`, installer scripts, per-runtime agent configs). KEEP-BOTH only when scopes genuinely differ (e.g. general first-pass debugging vs stuck-bug methodology) — then state the trigger boundary in both.

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
3. Name-collision scan: extract frontmatter `name:` (not directory names) across all roots; every new import must be unique.
4. Residual-reference grep: upstream brand names, `Skill tool` phrasing, runtime flags, install commands.
5. Discovery: `hermes skills list` shows each new skill enabled. Grep a distinctive PREFIX — the name column truncates around 20 chars, so a full-name grep falsely reads "not discovered".
6. Rebuild the lightrag index (`python3 ~/.hermes/scripts/lightrag_build_index.py`) so reference discovery sees the new set.
7. Spot-check the synced content landed by asserting real body strings from the write plan — keyed per (file, needle) pair.

### 6. Post
Record durable conventions in memory (refresh procedure, terminology map). Report per-skill decisions with reasons.

## Pitfalls
- A programmatic insert anchored on a trigger word can match the SKILL.md description line inside frontmatter and break YAML — anchor on body text or assert the insertion sits after the closing `---`. Description lines reuse body vocabulary.
- A dict-keyed batch of content checks silently drops every check after the first for a given file — key by (file, needle) tuples.
- Collision identity is the frontmatter `name:`, not the directory: loader scans match by name recursively, so renaming a dir does not resolve a collision.
- A shallow clone of the source is enough for reading; keep the checkout outside the skill tree so recon can never leak into the library.

## Related
- `workflow/external-skills-integration` — mounting whole external repos read-only via `skills.external_dirs` (different mechanism: no adaptation, no dedupe).
- `software-development/codex-skill-import` — raw copy of SKILL.md files from Codex plugin caches (copy-only).
- `software-development/repo-integration-reconciliation` — reconciling skills when onboarding a code repository.
