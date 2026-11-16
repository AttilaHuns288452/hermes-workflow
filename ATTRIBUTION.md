# Third-Party Attribution

Skills in this repository that were imported from external projects, with their
upstream source and license. Original authoring remains with those projects; this
file records provenance so redistribution terms are respected.

The skills authored by Attila are licensed CC BY-NC 4.0 (see `LICENSE`). Imported
skills keep their own upstream license, which is noted below. Where an upstream
license permits redistribution (MIT, Apache-2.0, BSD), inclusion here does not
relicense the original work.

| Pack / skill | Upstream | License | Notes |
|---|---|---|---|
| `skills/security-reverse/**` (47 skills) | [zhaoxuya520/reverse-skill](https://github.com/zhaoxuya520/reverse-skill) | MIT | Imported at commit `cab634b`. Frontmatter trimmed to `name` + `description`; tree structure preserved. |
| `skills/craft-anything/**` | [storytold/craft-anything](https://github.com/storytold/craft-anything) | Apache-2.0 | Vendor-installed skill via `setup --client hermes`. |
| `skills/capacitor-mobile/**` | [Cap-go/capgo-skills](https://github.com/Cap-go/capgo-skills) | MIT | 19 upstream Capgo skills consolidated into one skill with references. Capgo Cloud / organization / release-management material excluded (paid-service only). |
| `skills/expo-mobile/**` | [expo/skills](https://github.com/expo/skills) | MIT | 16 open-source Expo framework skills; the 7 EAS (paid service) skills excluded. |
| `skills/expo-mobile/references/react-native-performance/**` | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | MIT | `react-native-skills` rule set, 38 single-topic files. |
| `skills/productivity/supabase/references/security-trap-checklist.md` | [supabase/agent-skills](https://github.com/supabase/agent-skills) | MIT | Condensed from the official `supabase` skill; the rest of that skill was not imported. |
| `skills/remotion/**` (12 skills) | [remotion-dev/remotion](https://github.com/remotion-dev/remotion) | Remotion License (SPDX: NOASSERTION) | Official plugin skills pinned at `b486861` (v4.0.519). Remotion's license is not an OSI license; usage of the Remotion framework itself is governed by its own terms. |
| `skills/roblox/**` (43 skills) | Multiple community packs (EL4CTEO, MSayib `roblox-dev-skill`, greedychipmunk, TabooHarmony) | Per-skill; see each `SKILL.md` `source` field | Frontmatter normalized during import. |
| `skills/aris/**` (7 skills) | ARIS bundles | Per-skill | See each `SKILL.md`. |
| `skills/media/**`, `skills/development/**` | Mixed (video-shotcraft, ai-skills-blender, cinematic-pipeline, internal) | Per-skill | See each `SKILL.md`. |
| `skills/tinyfish-*/**` (7 skills) | TinyFish vendor CLI | Per-skill | Installed by `tinyfish connect`. |
| `skills/9-somboon/**` | 9-somboon prompt pack | Per-skill | See `SKILL.md`. |

## Removal requests

If you own one of these projects and want your material removed from this
repository, open an issue and it will be removed promptly.

## What is deliberately not published

- Credentials, tokens, API keys (the audit gate `scripts/audit_skills.py` blocks
  these patterns before commit).
- Machine-specific state: MCP server definitions, cron jobs, session data,
  `config.yaml` values, personal memory files.
- Skills whose upstream carries no license permitting redistribution.
