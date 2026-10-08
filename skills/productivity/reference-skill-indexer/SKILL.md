---
name: reference-skill-indexer
description: Index and search the external skill library.
triggers:
  - reference skills
  - external skill library
  - skillreferences
  - skill index
  - find skill in drive
  - skill discovery
  - rebuild skill index
---

# Reference Skill Indexer

Build and query a keyword-overlap index over the external skill library at `/home/attila/Documents/SkillReferences`. This library contains 2,194+ skills across 4 repos (ECC, external, hermes-workflow, hw-new) that are NOT indexed by the default LightRAG index.

## When to Use

- User asks to find a skill in the external library
- Rebuilding the index after drive imports or new repo additions
- Troubleshooting why external skills are not discoverable
- Auditing the skill library for coverage gaps

## Prerequisites

The external skill library requires TWO things to work:

### 1. Symlinks in ~/.hermes/skills/

```bash
cd ~/.hermes/skills && ln -sfn /home/attila/Documents/SkillReferences/ECC ECC && ln -sfn /home/attila/Documents/SkillReferences/external external && ln -sfn /home/attila/Documents/SkillReferences/hermes-workflow hermes-workflow && ln -sfn /home/attila/Documents/SkillReferences/hw-new hw-new
```

### 2. Config declaration in config.yaml

```yaml
skills:
  external_dirs:
    - ECC
    - external
    - hermes-workflow
    - hw-new
```

Without BOTH, the 2,194 skills are invisible to Hermes.

## Quick Start

```bash
# Build the reference index (run after any drive import)
python3 ~/.hermes/scripts/reference_build_index.py

# Query
python3 ~/.hermes/scripts/reference_find.py "github pull request"
python3 ~/.hermes/scripts/reference_find.py "code review security" --top 5
python3 ~/.hermes/scripts/reference_find.py "trading backtest" --repo ECC
```

## Index Location

- **Index file**: `~/.hermes/tmp/reference_search_index.json`
- **Scripts**: `~/.hermes/scripts/reference_build_index.py` and `reference_find.py`
- **Source**: All `SKILL.md` files under `/home/attila/Documents/SkillReferences/`

## Output Format

```
4	ECC/skills/project-flow-ops
3	ECC/skills/github-ops
3	hermes-workflow/skills/github
```

Score is keyword-overlap count (higher = more relevant). Names are relative to the reference root.

## Rebuild Triggers

- After importing new repos into `/home/attila/Documents/SkillReferences/`
- After `hermes skills tap add` (new GitHub skill sources)
- After major skill content changes in the drive
- After `hermes update` (may wipe symlinks)

## Verification

```bash
# Check symlinks exist
find ~/.hermes/skills -maxdepth 1 -type l | wc -l  # should be 4

# Check index health
python3 -c "import json; idx=json.load(open('/home/attila/.hermes/tmp/reference_search_index.json')); print(f'indexed={len(idx)}')"

# Test query
python3 ~/.hermes/scripts/reference_find.py "python testing" --top 3
```

## Pitfalls

1. **Symlinks lost on update** — `hermes update` wipes local modifications including symlinks. After every update, re-run the symlink command above.
2. **Config not set** — Symlinks alone don't make skills config-aware. Add `skills.external_dirs` to config.yaml.
3. **Stale index** — The index is a snapshot. Rebuild after any drive import.
4. **Windows paths** — Never copy an old index file from Windows. Rebuild from scratch on Linux.
5. **Deduplication** — Some skills appear in both local `skills/` and external dirs. Both will match; prefer the external version for domain-specific work.

## Relationship to LightRAG

The default LightRAG index (`~/.hermes/lightrag_index/skill_index.json`) only covers local `~/.hermes/skills/`. The reference index covers the external library. Use both for full coverage.