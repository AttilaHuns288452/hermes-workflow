# Windows → Linux Migration — Vinyl Desklet Session (2026-09-04)

Concrete migration session: imported skills from Windows backup on external drive (`/media/attila/SP PHD U3/MyOldOS/01_HERMES/data/`) to Linux Mint 22.3.

## Source Layout

- **Mount**: `/media/attila/SP PHD U3/MyOldOS` — `fuseblk (ro)`, dirname contains space, always quote
- **Hermes data**: `01_HERMES/data/` — full Windows Hermes installation copy
- **Key dirs**: `skills/`, `lightrag_index/`, `.codegraph/`, `memories/`, `profiles/`, `plugins/`, `scripts/`, `cron/`, `kanban/`, `sessions/`
- **Databases**: `state.db` (3.2 GB), `.codegraph/codegraph.db` (838.8 MB), `kanban.db`, `projects.db`, `response_store.db`

## What Was Migrated

| Artifact | Action | Result |
|----------|--------|--------|
| `memories/MEMORY.md` | Merge | 27 old + 14 current = 41 entries |
| `memories/USER.md` | Keep current | Already Linux-native |
| `skills/` (20 new) | Import | Source-only skills from Windows |
| `kanban/boards/` (8 boards) | Import | Full board data |
| `scripts/` (34) | Import | Skipped .ps1/.bat |
| `plugins/` | Existed | clawlink, achievements, ponytail |
| `lightrag_index/` | Rebuild | Old format incompatible |
| `.codegraph/codegraph.db` | Skip | 838.8 MB, couldn't open (permissions) |
| `sessions/` | Skip | 1.2 GB, historical only |
| `state.db` | Keep current | 3.2 GB, live DB |

## LightRAG Rebuild

Old Windows index used `~/AppData/Local/hermes/skills` — not compatible with Linux. Rebuilt from scratch:

```bash
# Linux build script (new)
python3 ~/.hermes/scripts/lightrag_build_index.py
# Output: Indexed 191 skills → ~/.hermes/lightrag_index/skill_index.json (891 KB)

# Query
python3 ~/.hermes/scripts/lightrag_find.py "desklet"
# → desktop/cinnamon-desklet-development (score 0.071)
```

## Windows Residue Found

- `decide/SKILL.md` — contained Windows paths (removed)
- `os-migration-restore/SKILL.md` — contained Windows paths (removed)
- `opendesign-direct-call.py` — contained Windows paths (removed)
- `config.yaml` — 307 lines of Windows paths (kept as comments, not active)

## Database Health

- `state.db`: integrity warning (cosmetic — FTS index, DB fully usable)
- `projects.db`: ok
- `kanban.db`: ok
- `response_store.db`: ok
- `codegraph.db`: not yet initialized (needs `codegraph init`)

## Score: 88/100

Deductions:
- -5: CodeGraph not initialized
- -3: state.db integrity warning (cosmetic)
- -4: Old codegraph.db not imported (couldn't open)
