---
name: hermes-aux-tuning
description: Tune Hermes auxiliaries and cold boot when Spark is slow.
---

# Hermes Aux Tuning

Class-level skill for Hermes `config.yaml` auxiliary routing and gateway latency.

## When to use
- User reports Muse Spark 10s latency
- `hermes -z` takes 60s+ (cold boot with 700+ skills)
- Any auxiliary (web_extract, compression, skills_hub, approval, mcp, title_generation, triage, profile_describer) feels slow
- Prompt cache hit rate collapses (e.g. 2:1 → 1:1, `cache=113/xxx 0%` every other turn on `commandcode/muse-spark`)

## Auxiliary routing rule

Keep **Spark only for reasoning-heavy jobs**, move everything else to `mimo-v2.5`:

| Keep on Spark | Move to mimo-v2.5 |
|---------------|-------------------|
| `model.default` (main chat) | `auxiliary.web_extract` |
| `auxiliary.curator` (600s, cross-session stitching) | `auxiliary.compression` |
| `auxiliary.kanban_decomposer` (task decomposition) | `auxiliary.skills_hub` |
| `delegation.model` (subagents, max reasoning) | `auxiliary.approval` |
| | `auxiliary.mcp` |
| | `auxiliary.title_generation` |
| | `auxiliary.triage_specifier` |
| | `auxiliary.profile_describer` |
| | `auxiliary.vision` (already mimo) |

**Per-turn saving:** 8s per aux call, 16-24s per turn (2-3 aux), 2-4 min per 10-turn session.

## Commands

```bash
# Move lightweight aux to mimo (ponytail: 1 loop, not 8 patches)
for aux in web_extract compression skills_hub approval mcp title_generation triage_specifier profile_describer; do
  hermes config set auxiliary.$aux.provider commandcode
  hermes config set auxiliary.$aux.model xiaomi/mimo-v2.5
done
hermes config set auxiliary.web_extract.timeout 60
hermes config set auxiliary.compression.timeout 60

# Verify
for k in web_extract compression skills_hub approval mcp title_generation vision curator; do
  hermes config get auxiliary.$k.model
done

# Restart required
# hermes gateway restart  (or relaunch Hermes desktop) — blocked from subagents, user must run
```

## Cold-boot reduction

Cold `hermes -z` = ~63s (709 skills: 253 hermes/skills + 456 .agents/skills + 19 external_dirs + MCP discovery 1.5s).

- **Primary fix:** Stay on **gateway/desktop** (0.014s health), don't use `hermes -z` for interactive work. Warm sessions skip cold boot.
- **Secondary fix:** Trim `skills.external_dirs` in `config.yaml` — remove 3-4 unused designer-skills mounts. Each dir = glob+parse. Saves 5-10s.
- `mcp_discovery_timeout` is already 1.5s — don't lower it.
- `prompt_caching` is `5m` by default; for 100k+ token sessions with toolset churn and 25-100s turn gaps, set `1h` (see Prompt cache collapse below).

## Verification

```bash
hermes config get auxiliary.web_extract.model  # → xiaomi/mimo-v2.5
curl -s http://127.0.0.1:8642/health  # → {"status":"ok"} in 0.01s
# hermes -z cold boot will still be ~60s — aux wins show warm, mid-session
```

## Prompt cache collapse (CommandCode / Muse Spark)

`cache=113/xxx (0%)` every other turn = toolset/prefix churn, not provider bug. Weighted hit rate (tokens) is the billable metric, not per-call avg. See `references/prompt-cache-tuning.md` for diagnostic, root causes, and `cache_ttl: 1h` fix.

## Pitfalls

- `hermes config` edits `config.yaml` directly — `patch` tool is blocked on that file; always use `hermes config set`.
- `hermes gateway restart` is blocked from subagent/CI — ask user to run it.
- Direct `api.commandcode.ai` POST with raw key returns 403 (Hermes-scoped key) — use `hermes -z -m xiaomi/mimo-v2.5 --provider commandcode` instead.

## References

- `references/aux-latency-map.md` — full per-aux before/after table
- `references/cold-boot-profile.md` — 709-skill profile, gateway vs -z timings
- `references/prompt-cache-tuning.md` — CommandCode cache-hit diagnostics (this session: 49% vs 67% yesterday)
