# GitHub Ecosystem Scout — Scoring + Dedupe (2026-08-24)

Lightweight discovery for skills/MCPs/tools that does NOT auto-install. Runs monthly via `gh` CLI.

## Search

- Auth: `gh` 2.89 + `gho_` keyring token; `gh search repos "<query>" --limit 5 --json fullName,stargazersCount,updatedAt,pushedAt,description,isArchived,language,license`.
- 8 queries × 5 repos = 40 candidates, deduped to ~34 (see `QUERIES` in `scripts/github-scout.py`): `mcp server`, `agent skills`, `coding agent`, `browser automation playwright`, `visual regression testing`, `research agent citation`, `remotion video automation`, `deployment observability`.
- `gh` field is `stargazersCount`, not `stars` — wrong field returns `Unknown JSON field`.

## Scoring (heuristic, not ML)

```
if archived → 1, REJECT
if redundant_kw in name (EXISTING_KEYWORDS: 21st, codegraph, graphify, firecrawl, playwright, superpowers, opencode, codex, ...):
  if stars>5000 and updated<14d → 5, MONITOR ("overlaps X but high-signal")
  else → 3, REJECT ("redundant vs X")

stars: >=50k→4, >=10k→3, >=2k→2, >=500→1, else 0
recency: updated<7d +2, <30d +1, >180d -1; pushed>180d -1; updated>365d -2
awesome list penalty: if "awesome" in name and collection/curated in desc → -2
cap at 0..10 → >=7 RECOMMEND, >=5 MONITOR, else REJECT
```

Corrected in-session: `anomalyco/opencode` (200k) and `openai/codex` were 7→5 after adding `opencode`/`codex` to EXISTING_KEYWORDS; `punkpeye/awesome-mcp-servers` (92k) 7→5 after awesome penalty. Full scan result: 2 RECOMMEND (`anthropics/skills` 171k, `addyosmani/agent-skills` 89k), 12 MONITOR, 20 REJECT.

## DB + report

- `ecosystem-discoveries.json` — `{repos: {fullName: {url, category, query, stars, updatedAt, pushedAt, description, language, isArchived, score, tier, reason, lastChecked}}}` — survives across scans; re-scoring preserves `INTEGRATED`/`RECOMMENDED` tier.
- `ecosystem-scout-report.md` — grouped RECOMMEND/MONITOR/REJECT (REJECT truncated to 5), with `score`, `reason`, `updated` date.

## Modes

```bash
python scripts/github-scout.py           # full 8×5
python scripts/github-scout.py --quick   # 3×3 for testing (3 queries)
python scripts/github-scout.py --report-only  # re-render report from DB, no searches
```

`--report-only` currently does NOT re-score existing entries — to apply a scorer fix, delete `ecosystem-discoveries.json` and re-run. Light `hermes-ecosystem-maintenance` task: add live re-scoring if scorer evolves again.

## Cron

`0 5 1 * *` monthly 01 05:00 → `github-scout.py --no-agent` (default full scan). Next: 2026-09-01. Anti-noise: many scans legitimately produce 0 RECOMMEND — that's a valid outcome, not a failure.
