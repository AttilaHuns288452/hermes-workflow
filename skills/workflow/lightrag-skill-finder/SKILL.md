---
name: lightrag-skill-finder
description: TF-IDF semantic skill search over 665+ skills — sub-second, zero API calls, daily auto-rebuild.
triggers:
  - "find skill"
  - "skill search"
  - "what skill"
  - "which skill"
  - "skill finder"
  - "lightrag"
---

# LightRAG Skill Finder

TF-IDF search over 665+ skills. Sub-second. Zero API calls.

## Query

```bash
python "C:/Users/Attila/AppData/Local/hermes/lightrag_index/find.py" "<query>"
```

Returns top 5 matches with scores + descriptions.

## Rebuild

```bash
python "C:/Users/Attila/AppData/Local/hermes/lightrag_index/build_index.py"
```

Scans all 19 external skill dirs + bundled skills. ~3 seconds. Output: `skill_index.json` (3MB).

## Cron

Job `e3529912964e` — daily 4am rebuild. Silence = healthy.

## Routing

`/decide` static table (~40 entries) has no match → fallback: `find.py "<user prompt>"`.

## Path

`C:\Users\Attila\AppData\Local\hermes\lightrag_index\`
