# Model Probe Methodology

> Last used: June 10, 2026 — discovered OpenCode bundled free models
> Context: OpenRouter `:free` models kept failing; user pointed at OpenCode's own model list

## The Correction

I was probing OpenRouter `:free` models (e.g., `nvidia/nemotron-3-ultra-550b-a55b:free`), all of which returned server errors. The user pointed out they could see free models in their OpenCode app. Running `opencode models` revealed 5 models under the `opencode/` namespace — all working, all free.

**Lesson**: OpenCode bundles its own proxied free models. These are the authoritative free list. The OpenRouter website shows many `:free` models that don't actually work through OpenCode's CLI.

## Three-Step Probe Pattern

### Step 1: Discover
```bash
# Get ALL models
opencode models

# Filter to free / OpenCode-bundled models
opencode models | grep -E ':free|opencode/'

# Count them
opencode models | grep -c -E ':free|opencode/'
```

### Step 2: Smoke Test
```bash
# Each model should complete with exit code 0 and show "> build · <model>"
opencode run 'Respond with exactly: OK' --model opencode/<model> --timeout 60
```

Expected success output: `> build · <model>` followed by exit code 0.
Expected failure: `Error: { "name": "UnknownError", ... "Unexpected server error" }`

### Step 3: File Write Verification (Gold Standard)
```bash
# Create a real file to confirm the model can actually produce output
mkdir -p /tmp/probe
opencode run 'Create a file at /tmp/probe/<model>-test.txt with content: "<model> WORKS"' --model opencode/<model>
# Verify
cat /tmp/probe/<model>-test.txt
```

## Known Working Models (as of June 10, 2026)

### OpenCode Bundled (most reliable — try first)
| Name | Type | Verified By |
|------|------|-------------|
| `opencode/deepseek-v4-flash-free` | Coding, general | Wrote 16.4KB HTML file |
| `opencode/mimo-v2.5-free` | Coding, agentic | Wrote file |
| `opencode/nemotron-3-ultra-free` | Reasoning, heavy | Wrote file |
| `opencode/north-mini-code-free` | Fast, light | Wrote file |
| `opencode/big-pickle` | General | Wrote file |

### OpenRouter :free (fallback only — most fail)
| Name | Context | Status |
|------|---------|--------|
| `openai/gpt-oss-120b:free` | 131K | ✅ Working |
| `nex-agi/nex-n2-pro:free` | 262K | ✅ Working |

## Pitfalls

- The OpenRouter website shows many `:free` models that return server errors through OpenCode CLI. The `opencode models` list is the only authoritative source.
- Models without `:free` suffix (e.g., `openrouter/auto`) route to paid models — you'll be charged.
- Always do a smoke test before committing to a model for a big task. Free models come and go without notice.
- Cache probe results per session but re-probe each new session — model availability changes daily.
