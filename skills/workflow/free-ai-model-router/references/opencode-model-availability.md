# OpenCode Model Availability (OpenCode Bundled + OpenRouter Free Tier)

> Last updated: June 10, 2026 (Probe round 3 — OpenCode bundled models found)
> Test: `opencode run '<simple prompt>' --model opencode/<model>` for bundled models
> Test: `opencode run '<simple prompt>' --model openrouter/<model>` for OpenRouter models

## OpenCode Bundled Free Models (Primary — Most Reliable)

These are **proxied by OpenCode** and accessed via the `opencode/` namespace. No API key needed — they come with the OpenCode CLI. Run `opencode models | grep 'opencode/'` to see the current list.

| Model | Status | Verified By |
|-------|--------|-------------|
| `opencode/deepseek-v4-flash-free` | ✅ Working | Wrote 16.4KB HTML unit converter (567 lines) |
| `opencode/mimo-v2.5-free` | ✅ Working | Wrote file with correct content |
| `opencode/nemotron-3-ultra-free` | ✅ Working | Wrote file with correct content |
| `opencode/north-mini-code-free` | ✅ Working | Wrote file with correct content |
| `opencode/big-pickle` | ✅ Working | Wrote file with correct content |

**All 5 confirmed working on June 10, 2026.** These are the go-to free models for OpenCode tasks.

## OpenRouter Working Free Models (Fallback)

| Model | Context | Status | Notes |
|-------|---------|--------|-------|
| `openai/gpt-oss-120b:free` | 131K | ✅ Working | Apache 2.0, wrote 12.5KB file |
| `nex-agi/nex-n2-pro:free` | 262K | ✅ Working | Qwen3.5 MoE, coding focused |

## Failing Free Models (OpenRouter :free tier)

All of these return `Unexpected server error` or timeout. Do not retry — move to the next model.

| Model | Error |
|-------|-------|
| `deepseek/deepseek-v4-flash:free` | Server error (now paid at $0.098/M) |
| `deepseek/deepseek-r1:free` | Server error |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | Server error |
| `google/gemma-4-31b-it:free` | Timeout |
| `mistralai/mistral-small-24b-instruct-2501:free` | Server error |
| `openrouter/owl-alpha:free` | Server error |
| `poolside/laguna-xs-2:free` | Server error |
| `poolside/laguna-m.1:free` | Server error |
| `openrouter/auto` | Server error (also not actually free) |
| `openrouter/free` | Server error |
| `google/gemma-4-26b-a4b-it:free` | Server error |

## Key Findings

- **OpenCode bundled models (`opencode/`) are the reliable free path.** All 5 work.
- **OpenRouter `:free` tier is mostly broken** — only 2 of 12+ models work.
- **DeepSeek V4 Flash is no longer free** on OpenRouter ($0.098/M input).
- **Default OpenCode without `--model`** may select image-only models — always use `--model`.
- **Run `opencode models`** to see the authoritative live list, not the OpenRouter website.
