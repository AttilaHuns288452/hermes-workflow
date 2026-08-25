# Aux Latency Map — Muse Spark vs mimo-v2.5

Source: Hermes `config.yaml` before/after 2026-08-19, direct `hermes -z` timing.

| Auxiliary | Before | After | Saved |
|-----------|--------|-------|-------|
| `auxiliary.web_extract` | `meta/muse-spark-1.2-contributor` (10s, timeout 360) | `xiaomi/mimo-v2.5` (1-2s, timeout 60) | ~8s |
| `auxiliary.compression` | `auto` → Spark 10s (120) | `mimo-v2.5` (60) | ~8s |
| `auxiliary.skills_hub` | `auto` → Spark 10s | `mimo-v2.5` | ~8s |
| `auxiliary.approval` | `auto` → Spark 10s | `mimo-v2.5` | ~8s |
| `auxiliary.mcp` | `auto` → Spark 10s | `mimo-v2.5` | ~8s |
| `auxiliary.title_generation` | `auto` → Spark 10s | `mimo-v2.5` | ~8s |
| `auxiliary.triage_specifier` | `auto` → Spark 10s | `mimo-v2.5` | ~8s |
| `auxiliary.profile_describer` | `auto` → Spark 10s | `mimo-v2.5` | ~8s |
| `auxiliary.vision` | `mimo-v2.5` (kept) | `mimo-v2.5` | — |
| `auxiliary.curator` | `auto` → Spark (kept) | Spark (kept, 600s) | — |
| `auxiliary.kanban_decomposer` | `auto` → Spark (kept) | Spark (kept) | — |
| `model.default` | Spark (kept) | Spark (kept) | — |
| `delegation.model` | Spark (kept, reasoning_effort max) | Spark (kept) | — |

**Math:** 2-3 aux calls per turn × 8s = 16-24s/turn, 2-4 min per 10-turn session.
Warm gateway aux calls skip the 63s `hermes -z` cold boot; gains show mid-session, not in cold `-z` spawns.
