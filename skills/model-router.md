---
name: model-router
description: "5-layer free-model routing chain. Always default to free. Probe before commit. Layer 1: OpenCode. Layer 2: Freebuff. Layer 3: FreeLLMAPI (110+ models, 16 providers). Layer 4: OpenRouter (29+ free, 50 req/day). Layer 5: Paid BYOK (last resort)."
version: 1.0.0
author: Hermes Workflow
license: MIT
triggers:
  - model_selection
  - pre_query
---

# 🤖 Model Router — 5-Layer Fallback Chain

## Principle

**Always default to free. Probe before commit. Fall back gracefully.**

The model router tries the cheapest available model first, checks if it's appropriate for the task, and falls through to the next layer. Paid models are a last resort.

## The 5 Layers

### Layer 1 — OpenCode (Bundled Free)

| Provider | Models | Notes |
|----------|--------|-------|
| OpenCode Zen tier | Big Pickle, MiniMax M2.5 Free | Bundled with OpenCode CLI |
| Access | `opencode` CLI | No API key needed |

**Check:** Is OpenCode installed and responding?
```bash
opencode --version 2>/dev/null && echo "OpenCode available"
```

**Cost:** Free. Rate: Unmetered (Zen tier).

### Layer 2 — Freebuff (Cloud Free)

| Provider | Models | Notes |
|----------|--------|-------|
| Freebuff API | Kimi K2.6, MiniMax M3, MiMo 2.5 Pro | Free, ad-supported |
| Access | `npx freebuff` or direct API | May need signup |

**Check:** Is Freebuff responding?
```bash
# Test via CLI
npx freebuff --help 2>/dev/null && echo "Freebuff available"
```

**Cost:** Free (text ads). Rate: Generous free tier.

### Layer 3 — FreeLLMAPI (Local Proxy)

| Provider | Models | Notes |
|----------|--------|-------|
| 16 providers | 110+ free models behind one `/v1` endpoint | Self-hosted proxy |
| Access | `localhost:3001/v1` | Requires running the proxy server |
| Providers | Groq, Cerebras, Together AI, DeepInfra, Replicate, Fireworks AI, Lepton AI, etc. | Proxy stacks free tiers |

**Check:** Is FreeLLMAPI serving?
```bash
curl -s http://localhost:3001/v1/models | head -5
```

**Setup:**
```bash
git clone https://github.com/tashfeenahmed/freellmapi.git
cd freellmapi
pip install -r requirements.txt
python main.py  # starts on :3001
```

**Cost:** Free (each provider's free tier). Rate: Depends on individual provider limits.

### Layer 4 — OpenRouter (API Gateway Free Tier)

| Provider | Models | Notes |
|----------|--------|-------|
| OpenRouter free tier | 29+ free models | 50 req/day free |
| Standouts | DeepSeek V4, Qwen3.6-Plus, Llama 4 Maverick/Scout | SWE-bench capable |
| Access | `api.openrouter.ai/v1` | Free tier available |
| Catalog | [free-ai-tools catalog](https://github.com/ShaikhWarsi/free-ai-tools) | 238 models listed |

**Check:** Is OpenRouter accessible?
```bash
curl -s https://openrouter.ai/api/v1/models | python3 -c "import sys,json; [print(m['id']) for m in json.load(sys.stdin)['data'] if 'free' in m.get('id','').lower()]" 2>/dev/null | head -5
```

**Cost:** Free (50 req/day). No credit card needed.

**Recommended free models on OpenRouter:**
- `cognitivecomputations/dolphin3.0-mistral-24b:free`
- `microsoft/phi-4:free`
- `google/gemma-2-27b-it:free`
- `qwen/qwen-2.5-72b-instruct:free`
- `meta-llama/llama-3.2-90b-vision-instruct:free`

### Layer 5 — Paid Fallback (BYOK)

| Provider | Models | Notes |
|----------|--------|-------|
| Anthropic | Claude Opus 4.6, Sonnet 4.6 | Best for complex reasoning |
| OpenAI | GPT-5.4, GPT-5.1-Codex-Max | Best for coding |
| Google | Gemini 3.1 Pro | Best for long context |

**Check:** Are API keys configured?
```bash
echo "${ANTHROPIC_API_KEY:0:8}..." 2>/dev/null
echo "${OPENAI_API_KEY:0:8}..." 2>/dev/null
```

**Cost:** Paid per token. Use only when all free layers fail.

## Probe-Before-Commit Pattern

For every request, run this check:

```text
1. Can OpenCode handle this? (check OpenCode availability)
   → YES: route to OpenCode
   → NO: fall through

2. Can Freebuff handle this? (check Freebuff availability)
   → YES: route to Freebuff
   → NO: fall through

3. Is FreeLLMAPI running? (curl localhost:3001)
   → YES: route to FreeLLMAPI
   → NO: fall through

4. Can OpenRouter free tier handle this? (check free model availability)
   → YES: route to OpenRouter
   → NO: fall through

5. Route to paid model (last resort)
```

## Model Selection by Task Type

| Task Type | Recommended Free Model | Layer |
|-----------|----------------------|-------|
| Simple Q&A / chat | Big Pickle (OpenCode) | 1 |
| Code generation | Kimi K2.6 (Freebuff) or DeepSeek V4 (OpenRouter) | 2 / 4 |
| Code review / analysis | MiniMax M3 (Freebuff) or Qwen3.6-Plus (OpenRouter) | 2 / 4 |
| Creative writing | MiMo 2.5 Pro (Freebuff) | 2 |
| Long context (>100K) | Gemini Flash via FreeLLMAPI | 3 |
| Complex reasoning | Claude Sonnet 4 (OpenRouter) or GPT-4.1 (OpenRouter) | 4 / 5 |
| Vision / image analysis | Llama 3.2-90B (OpenRouter) or GPT-4o (FreeLLMAPI) | 3 / 4 |
| Quant finance | DeepSeek V4 (OpenRouter) or MiniMax M3 (Freebuff) | 2 / 4 |

## Provider-Specific Configuration

### OpenCode
```json
// ~/.opencode.json (or $XDG_CONFIG_HOME/opencode/config.json)
{
  "provider": "opencode-zen",
  "model": "big-pickle",
  "autoCompact": true
}
```

### FreeLLMAPI (Custom Hermes Provider)
```yaml
# ~/.hermes/config.yaml
custom_providers:
  freellmapi:
    type: openai
    api_base: http://localhost:3001/v1
    api_key: not-needed
    default_model: auto
```

### OpenRouter
```yaml
# ~/.hermes/config.yaml (or env var)
OPENROUTER_API_KEY: "sk-or-v1-..."
openrouter_base_url: https://openrouter.ai/api/v1
```

## Fallback Timeout

Each layer gets a timeout:
- Layer 1-2: 10 seconds
- Layer 3: 15 seconds
- Layer 4: 15 seconds
- Layer 5: 30 seconds

If a layer times out, fall through to the next layer immediately. Never retry the same layer more than once.

## Monitoring

Log which layer was used for each request so you can track:
- How often each layer is used
- Which models are most cost-effective
- When providers are down

```bash
echo "[$(date +%s)] model_router: layer=$LAYER model=$MODEL task_type=$TASK_TYPE" >> /tmp/model_router.log
```
