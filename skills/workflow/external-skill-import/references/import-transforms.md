# Import transforms (mechanical, run per skill dir on write)

Apply as one pass per skill directory during the Adapt-on-write step. These are string-level translations from the source runtime's conventions to Hermes conventions. After the pass, the residual assertions at the bottom must come back empty.

## Terminology canon

Translate upstream's core artifact names to this system's established ones at write time. Consistency inside the system beats matching upstream. Example: upstream `GLOSSARY.md` (their terminology file) → our `CONTEXT.md`, and every pointer to it (`GLOSSARY-FORMAT.md` → `CONTEXT-FORMAT.md`, cross-refs "see GLOSSARY" → "see CONTEXT"). Exception: an artifact whose filename is the teaching subject itself (e.g. a template for writing glossaries) keeps its name.

## Invocation and tool references

| Source-runtime form | Hermes form |
|---|---|
| `Call the Skill tool with "X"` / `Skill tool` | `load the \`X\` skill` |
| Slash commands `/x` as run instructions | `load the \`x\` skill` / prose (skills are not slash commands here) |
| Claude Code tools `Read`, `Write`, `Edit`, `Bash` | `read_file`, `write_file`, `patch`, `terminal` |
| `skill_view(name=...)`-style already correct | leave as-is |

## Frontmatter

- Keep: `name`, `description` (description ≤ 60 chars, trigger first, ends with period).
- Strip runtime-only fields: Codex `disable-model-invocation`, `argument-hint`, and any `agents/*.yaml` companion configs.
- Drop or translate `metadata.hermes.category` per the local category layout.

## Skipped entirely (never copied)

`.claude-plugin/`, `.agents/`, installer/update scripts, `claude plugins install` / `plugin install` / `npx skills add` / updater CLI instructions. The refresh recipe goes in memory, not in the skill body.

## Naming

Upstream-branded skill names (`setup-<author>-skills`, `<author>-foo`) get descriptive class-level names (`engineering-skills-setup`, `grilling`). After renaming, grep EVERY file in the import set AND previously-imported siblings for the old name and rewrite the reference.

## Residual assertions (must be zero after the pass)

```
'Skill tool', 'disable-model-invocation', 'argument-hint',
'claude plugins install', 'npx skills add', 'openai.yaml',
upstream brand names, upstream install command names
```

Acceptable non-zero hits: provenance attribution lines ("Source: ... skill by ...") — they document origin and are not runtime dependencies.
