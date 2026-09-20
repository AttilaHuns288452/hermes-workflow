# CommandCode Model Identifiers (as of 2026-09-03)

## Free Models (no credit cost)

| Full ID | Short Name | Notes |
|---------|-----------|-------|
| `meituan/longcat-2.0:free` | longcat-2.0 | 1M context, agentic coding |
| `poolside/laguna-s-2.1-free` | laguna-s21 | Long-horizon, open-weight |
| `deepseek/deepseek-v4-flash` | — | Requires credits |

## Models Requiring Credits

| Full ID | Short Name | Notes |
|---------|-----------|-------|
| `deepseek/deepseek-v4-pro` | — | Hybrid-attention long-context |
| `deepseek/deepseek-v4-flash` | — | Fast reasoning (default) |
| `deepseek/deepseek-v4-flash-vision-exp` | — | Flash + vision |
| `deepseek/deepseek-v4-flash-fast` | — | Low-latency flash |
| `meta/muse-spark-1.2-contributor` | — | Coding-optimized |
| `meta/muse-spark-1.2` | — | Agentic coding |
| `meta/muse-spark-1.3` | — | Multimodal reasoning |

## Incorrect Names (DO NOT USE)

| Wrong | Correct |
|-------|---------|
| `laguna-s21-free` | `poolside/laguna-s-2.1-free` |
| `deepseek-v4-flash` | `deepseek/deepseek-v4-flash` |
| `longcat-2.0` | `meituan/longcat-2.0:free` |

## Exit Codes Reference

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Config/unknown model error |
| 2 | Argument parsing error |
| 10 | Credit exhausted |
| 124 | Timeout (from `timeout` command) |
| other | Network/provider error |

Run `commandcode --list-models` for the full current catalog.