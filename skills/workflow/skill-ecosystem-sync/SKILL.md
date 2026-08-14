---
name: skill-ecosystem-sync
description: >-
  Sync Hermes skills with external ecosystems (Open Design).
---

# Skill Ecosystem Sync

Bidirectional sync between Hermes skills and sibling ecosystems. Proven with
Open Design (desktop design app, plugin system) — 166 exported, 66 imported
in the first pass, zero collisions.

## Open Design ↔ Hermes (the reference implementation)

Two idempotent scripts in `~/AppData/Local/hermes/scripts/`:

- **`export-design-skills-to-opendesign.py`** — wraps Hermes design-skill
  collections (awesome-design-skills, design-skills-ihlamury, emilkowalski,
  ibelick) as Open Design plugin packs: `%APPDATA%/Open Design/.../data/plugins/design-<name>/{DESIGN.md, open-design.json}`
  + registers rows in `installed_plugins` (source_kind=user, sha256 digests).
- **`import-opendesign-skills-to-hermes.py`** — copies Open Design bundled
  `design-systems/` kits into `skills/opendesign/od-<slug>/` as Hermes skills
  (SKILL.md frontmatter + full DESIGN.md + manifest), **skipping any slug that
  collides with an existing skill name** (77 of 143 skipped first run — the
  collision-skip is the whole point; importing everything pollutes the index).

Rerun both after any design-skill change (they're idempotent — skip existing).
A weekly cron (`workflow-ecosystem-audit`, Mondays 07:00) reruns them
automatically and reports drift.

## Open Design plugin format (for hand-writing plugins)

A plugin folder = `open-design.json` manifest + content file:
- **Design systems:** `DESIGN.md` + manifest with `od: { kind: "scenario", taskKind: "new-generation", mode: "design-system", scenario: "design", surface: "web", useCase: { query: { en: "..." } } }` — `compat` is null.
- **Atoms (tool plugins):** `SKILL.md` + `compat: { agentSkills: [{ path: "./SKILL.md" }] }`.
- Manifest base: `$schema: https://open-design.ai/schemas/plugin.v1.json`, `specVersion: "1.0.0"`, name/title/version/description/tags (+ optional title_i18n/description_i18n).

## Pitfalls

- **Both the folder AND the DB row matter.** Open Design's app.sqlite
  `installed_plugins` table tracks `fs_path` + `manifest_json`; the user
  plugins dir is empty unless registered. Folders alone may not be picked up.
- **`source_kind` enum:** the app's own 460 rows are all `bundled`; exports use
  `user`. Verify in-app after the first export (app wasn't running during our
  first export — unverified until launch).
- **Write sqlite when the app is closed** (WAL conflict risk).
- **OpenDesign MCP is daemon-gated** — server only works when the app runs;
  fall back to the imported `od-*` skills directly.
- **Collision-skip strategy generalizes:** when importing any ecosystem's
  skills, diff against existing names first (`skills_list` / folder scan) and
  skip overlaps — flat imports create loader ambiguity errors (e.g.
  `skill_view(name)` → "Ambiguous skill name: 2 skills match").

## Generalizing to other ecosystems

Same shape applies to any platform that consumes skills as folders with a
manifest: enumerate source → map to target format (frontmatter/manifest +
body) → write to target dir → register in target's index/DB if it has one →
verify loadable via the target's own loader. The scripts are the template —
copy and adapt the manifest builder.
