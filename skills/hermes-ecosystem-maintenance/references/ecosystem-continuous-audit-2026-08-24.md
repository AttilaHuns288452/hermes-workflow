# Ecosystem Continuous Audit — Light/Deep + Registry (2026-08-24)

Full-session pattern for the hermetic self-auditing loop that keeps SOUL/DECIDE/CAPABILITY_GRAPH in sync across 862 skills + 15 MCPs without LLM cost on every tick.

## Two-tier cron

| Tier | Schedule | Script | Mode | Purpose |
|------|----------|--------|------|---------|
| Light | `15 3 * * *` daily 03:15 | `ecosystem-audit-light.py` | `no-agent` | hash-compare only |
| Deep | `0 4 * * 0` Sun 04:00 | `ecosystem-audit-deep.py` | `no-agent` | full reconcile |
| Scout | `0 5 1 * *` monthly 01 05:00 | `github-scout.py` | `no-agent` | GitHub discovery (separate) |

Both light/deep are wrappers around `ecosystem-audit.py --light/--deep`. Wrappers are required because `hermes cron create --script X --no-agent` runs `X` verbatim with no arg forwarding — `ecosystem-audit.py` default is light, so deep needs its own wrapper.

## Registry + changelog

- `ecosystem-registry.json` — fingerprint: `skills.hermes_skills_list_lines`, `mcp_hash` (sha256 of `hermes mcp list`), `config_hash`/`soul_hash`/`decide_skill_hash`/`decide_home_hash`/`capability_graph_hash`, `scripts_hash`, `lightrag_index`, `model_default`, `cron_hash`, `graphify_projects`. Updated every run.
- `ecosystem-changelog.md` — only meaningful changes, not noise. First line `> Auto-maintained by scripts/...`.
- `ecosystem-discoveries.json` / `ecosystem-scout-report.md` — GitHub scout DB (see companion ref).

## Light: hash diff, idempotent

```python
diff_snap(old, new):
  for k in [config_hash, soul_hash, decide_skill_hash, decide_home_hash, capability_graph_hash, mcp_hash, scripts_hash, ...]:
    if old[k] != new[k]: diffs.append(...)
```

- No diffs → `save_registry(snap with last_checked)` + `[light] no changes` → **no changelog append** (anti-noise). Second run with identical env produces no writes except timestamp — verified `EXIT:0` twice.
- Diffs + significant (`mcp_hash`/`skills`/`config_hash`) → logs `[light] significant change — next deep will reconcile`.

## Deep: gated, not always

```python
if not force and not diffs and (now - last_deep).days < 7:
  skip  # use --force to override
```

When it runs:
1. Refresh `CAPABILITY_GRAPH.md` header `*Last audit: YYYY-MM-DD · N skills · mcp hash · model*` via regex.
2. Re-sync `$HERMES_HOME/DECIDE.md` pointer `Last sync: YYYY-MM-DD skill hash` if `decide_skill_hash` drifted (skill is canonical, home is pointer — see soul-md-enforcement.md).
3. Heuristics: clawlink routed? Drive backup 403 still failing?

## DECIDE merge pitfall (fixed this session)

`$HERMES_HOME/DECIDE.md` (378 lines) and `skills/decide/SKILL.md` (527 lines) were duplicates. Enforcement is `SOUL.md` Step 0 → `skill_view(name='decide')`, so the skill is the only auto-loaded canonical. Fix:

- Merge hierarchies (Tool Selection tiers, 7 chains, Verification matrix, Fallback matrix, Completion criteria) into skill as `## Decision Hierarchies & Operational Engine (from DECIDE.md — merged DATE)` inserted before `## MCP & Tool Routing`.
- Keep home `DECIDE.md` as pointer: header `Canonical: skills/decide/SKILL.md` + full copy for offline reading, backed up to `DECIDE.full.md.bak-DATE`.
- Result: 801-line skill, 389-line home pointer. `grep -n "14 servers enabled" skills/decide/SKILL.md DECIDE.md` both hit after merge.

## Verification

```bash
python scripts/ecosystem-audit-light.py  # → [light] no changes (idempotent)
python scripts/ecosystem-audit-deep.py   # → [deep] skip <7d or runs
hermes cron list | cat                    # 5 jobs: lending 23:00, hermes 02:00, light 03:15, deep Sun 04:00, scout 05:00 monthly
cat ecosystem-registry.json | head        # mcp_hash, decide_skill_hash present
```
