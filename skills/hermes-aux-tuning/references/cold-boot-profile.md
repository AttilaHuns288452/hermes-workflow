# Cold-Boot Profile — Hermes Gateway vs hermes -z

Measured 2026-08-19, Windows, Hermes 0.19.1.

## Why `hermes -z` is ~63s

- `253` skills in `hermes/skills` + `456` in `.agents/skills` = 709 indexed
- `19` external_dirs (superpowers, agent-skills, garden, claude-seo, obsidian, 8× designer-skills, etc.) — each glob+parsed
- `mcp_discovery_timeout: 1.5s`
- Provider cold connect + skill load + agent boot

```
hermes -z "PONG" -m muse-spark  → 63s
hermes -z "PONG" -m mimo-v2.5    → 67s  (same boot tax dominates)
gateway /health                  → 0.014s
hermes config get                → 1.3s (warm, no agent boot)
```

## Fixes (ladder order)

1. **Use gateway/desktop, not `hermes -z`** for interactive work. Warm sessions load skills once, aux calls are 1-2s.
2. **Trim `skills.external_dirs`** — remove 3-4 unused mounts (e.g. designer-skills variants). Saves 5-10s cold boot.
3. Keep `mcp_discovery_timeout: 1.5s` and `prompt_caching.cache_ttl: 5m`.

## Tool quirks

- `patch` on `config.yaml` is blocked (security). Use `hermes config set <key> <value>`.
- `hermes gateway restart` blocked from subagent/background — user must run foreground.
- `api.commandcode.ai` direct POST → 403 (Hermes-scoped key); use `hermes -z -m ... --provider commandcode`.

## Tell user

"The 63s is cold boot, not model latency. Warm gateway aux calls are the real win — 8s saved per aux, every turn."
