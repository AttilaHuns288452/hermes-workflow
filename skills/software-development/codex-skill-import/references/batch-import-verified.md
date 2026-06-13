# Verified Codex Skill Import Recipe

## Scope
Copy all `SKILL.md` files from `~/.codex/plugins/cache/openai-curated/<hash>/skills/*/SKILL.md` into Hermes skills.

## Command
```bash
SRC_GLOB="$HOME/.codex/plugins/cache/openai-curated/*/skills/*/SKILL.md"
DEST_BASE="$HOME/AppData/Local/hermes/skills"
for f in $SRC_GLOB; do
  [[ -f "$f" ]] || continue
  skill_name="$(basename "$(dirname "$f")")"
  dest="$DEST_BASE/$skill_name"
  mkdir -p "$dest"
  cp "$f" "$dest/SKILL.md"
done
```

## Reproduce/verify
```bash
ls "$HOME/AppData/Local/hermes/skills/*/SKILL.md" | wc -l
```

## Notes
- `*` glob expands to any hash directory under `openai-curated`, so no hard-coded hash is needed.
- This is the recipe that worked on Windows with MSYS bash.
