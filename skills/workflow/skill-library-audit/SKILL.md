---
name: skill-library-audit
description: Audit skills libraries for broken frontmatter and refs.
---

# Skill Library Audit

## When to use
- "Audit all our skills / make sure skills work as intended"
- A specific skill won't load, or `skills list` shows it but linked files 404
- After copying skills between collections (e.g. Hermes ↔ Open Design plugins, or ZCode mirror sync)

## The known bug classes (all found in one real audit of 847 SKILL.md files)

1. **Unquoted colon in `description:`** — long descriptions with `word: word` sequences break YAML parsing (`mapping values are not allowed here`). Fix: fold the description (`description: >-`) or quote it. Some loaders tolerate it, some don't — always fix.
2. **Doubled `references/` prefix** — frontmatter lists `references: [references/auth-flow.md]` when the file lives at `<skill>/references/auth-flow.md`. The loader resolves relative to the references dir → every link 404s. Fix: strip the prefix.
3. **Dangling `../` references** — `references: [../../references/x.md]` escapes the skill dir to a file that doesn't exist. Fix: point at a real local file or delete the entry.
4. **Name collisions across dirs** — 175 of 847 were collisions in the audit; most were the by-design ZCode↔Hermes mirror (primary dir wins). Only act on collisions WITHIN one collection or where the primary copy is stale. **Collision loading quirk (2026-08):** when a bare-name skill exists in both `~/AppData/Local/hermes/skills` and `~/.agents/skills`, `skill_view` refuses with "Ambiguous skill name" — `file_path` does NOT bypass it (name resolution runs first). Categorized copies resolve as `category/name` (e.g. `software-development/cashflow-os`); a category-less local copy (e.g. `decide`, `subagent-delegation`) is only loadable via `read_file` on the local SKILL.md, which also blocks patching it (read-before-write guard needs a successful skill_view). Fix long-term: rename/absorb the mirror copy or give the local one a category.

## Procedure
1. Run the audit script (see `scripts/audit_skills.py`) over the primary dir + external dirs from `config.yaml` `skills.external_dirs`.
2. Fix parse errors first (they can shadow the whole skill), then dangling refs, then missing `required_commands`.
3. Re-run until 0 issues.
4. For Hermes: `hermes doctor` + `hermes skills list` (grep for `broken|disabled`) confirm loader-level health; `hermes mcp test <name>` for MCP servers (note: "enabled" ≠ working — test each; stdio servers fail on missing Python deps even when configured).
5. Cron jobs that run skills: read `cron/output/<job_id>/<latest>.md` for the real error — job failures often point back at skill/script bugs (see `hermes-cron-jobs`).

## Pitfalls
- The audit's own YAML parser can be stricter than Hermes's loader — a skill flagged PARSE ERR may still load. Fix it anyway; fragile frontmatter breaks other tools (LightRAG index, Open Design plugin import).
- Editing mirrored copies: fix BOTH the primary dir and the `~/.agents/skills` mirror (they're synced copies; one fix leaves the other broken).
- Check `required_environment_variables` / `missing_credential_files` via `skill_view` readiness fields — env-gated skills report `setup_needed` when creds are missing.
