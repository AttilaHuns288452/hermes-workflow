---
name: lightrag-skill-finder
description: Build and query a TF-IDF skill index for zero-API discovery.
triggers:
  - find skills
  - search skills
  - skill discovery
  - skill index
  - lightrag
  - tf-idf
  - what skill does X
---

# LightRAG Skill Finder

Build a TF-IDF index over all installed skills and query it for sub-second, zero-API-call skill discovery. This is the local fallback when the agent needs to find the right skill without hitting external APIs.

**Scope:** 4,439+ skills indexed. Linux paths.

## When to Use

- User asks "find a skill for X" or "what skill does Y"
- /decide routes to a TF-IDF lookup (per the decide skill's routing table)
- You need to discover capabilities without web search or API calls
- Validating that a skill exists before loading it

## How It Works

1. **Build**: Walk `~/.hermes/skills/`, tokenize every `SKILL.md`, compute TF-IDF vectors, write to `~/.hermes/lightrag_index/skill_index.json`
2. **Query**: Tokenize the query, compute cosine-like scores against all docs, return top-K matches
3. **Rebuild**: Run after any skill import, install, or significant change

## Quick Start

```bash
# Build the index (run once, or after skill changes)
python3 ~/.hermes/scripts/lightrag_build_index.py

# Query
python3 ~/.hermes/scripts/lightrag_find.py "create a github pull request"
python3 ~/.hermes/scripts/lightrag_find.py "vinyl record player desklet"
python3 ~/.hermes/scripts/lightrag_find.py "stock market analysis"
```

## Index Location

- **Index file**: `~/.hermes/lightrag_index/skill_index.json`
- **Scripts**: `~/.hermes/scripts/lightrag_build_index.py` and `lightrag_find.py`
- **Source**: All `SKILL.md` files under `~/.hermes/skills/`

## Output Format

```
0.0137	github/github-repo-management
0.0127	github/github-issues
0.0093	github/github-pr-workflow
```

Score is a TF-IDF weight (higher = more relevant). Names are relative to `~/.hermes/skills/`.

## Rebuild Triggers

- After importing skills from a backup or external source
- After `hermes skills install` or `hermes skills remove`
- After creating or deleting a skill manually
- After major skill content changes

## Limitations

- **TF-IDF only** — no semantic understanding. "create PR" won't match "pull request" unless both terms appear in a skill's SKILL.md.
- **First 4000 chars only** — long skills are truncated for indexing.
- **No descriptions** — only SKILL.md content is indexed, not frontmatter descriptions.
- **Local only** — only indexes installed skills, not remote catalogs.

## Pitfalls

1. **Windows paths in old versions** — The Windows Hermes installation used `~/AppData/Local/hermes/skills` as the source. On Linux, always use `~/.hermes/skills/`. If migrating from Windows, rebuild the index from scratch on Linux — do not copy the old index file.
2. **Stale index** — The index is a snapshot. If skills change, queries return stale results. Rebuild after any skill operation.
3. **Score threshold** — Scores below 0.001 are usually noise. Filter low-confidence results.
4. **Deduplication** — Some skills appear in both `skills/` and `backup-import/`. Both will match; prefer the non-backup version.

## Verification

```bash
# Test the index
python3 ~/.hermes/scripts/lightrag_find.py "desklet"
python3 ~/.hermes/scripts/lightrag_find.py "github"
python3 ~/.hermes/scripts/lightrag_find.py "finance"
```

Each should return relevant skills with scores > 0.