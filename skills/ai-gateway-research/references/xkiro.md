# xKiro provider notes

User's primary gateway (Hermes runs on it). Verify everything live before relying on it — prices, tiers, and IDs drift.

## Structure

- Base URL `https://api.xkiro.com/v1`, OpenAI Chat Completions + Anthropic Messages both supported. Model ID format `vendor/model`.
- Plans gate **usage budget + concurrency only**; the model catalog is identical across tiers (Free → Power). Pro ≈ $5/mo with a weekly usage budget; higher tiers multiply budget, add concurrent-request headroom and peak-hour priority. Docs: xkiro.com/docs → "How routing works".
- "Smart routing + automatic fallback" is infrastructure, not a model: the gateway resolves the requested model to an upstream route and retries the next route on failure; billing and the response's `model` field always report the requested model. There is NO `auto`/`router`/`smart` model ID — probed and confirmed not_found.
- Site layout: plans live at homepage `#pricing` anchor; `/pricing` is a 404 route; `/deals` lists promos and new models. Readable server-side — plain `curl` + HTML strip works.

## Wallet-only pay-as-you-go (plan credits NEVER cover — needs deposited balance)

All DeepSeek, Xiaomi MiMo, MiniMax paid tier, Tencent Hunyuan, plus other premium-tier providers. Re-derive the current set: pull `/v1/models`, filter `access_tier == "premium"`, probe one per provider with the client's key. The rejection message is the definitive test: "requires real deposited balance ... not covered by a plan".

## Plan-covered highlights (prices last audit — recompute from /v1/models)

- Free on plan: `openai/gpt-5.3-codex-spark`, all Mistral models, SenseNova flash-lite.
- Cheap/value tier: `z-ai/glm-4.6v-flash` (~0.04), `nvidia/nemotron-3-nano` (~0.05), `meta/muse-spark-1.2-contributor` (~0.065), `z-ai/glm-4.7-flash` (~0.07), `openai/gpt-5.6-luna` (~0.10/0.60), `z-ai/glm-5.3-flash` (~0.15/0.50).
- Premium: `anthropic/claude-sonnet-5`, `moonshotai/kimi-k3`, `anthropic/claude-opus-5` (~4.50), `openai/gpt-6-astra` (~10/50).
- Deals page periodically runs 50%-off promos (Grok/Kimi/GPT-5.6 family) — recheck before cost claims.

## Quirks

- `deepseek/deepseek-v4-flash` bare ID is retired; current IDs carry revision suffixes (e.g. `deepseek/deepseek-v4-flash-0731`). DeepSeek direct API also bills off-peak at half price — xKiro pass-through pricing may not, so cheapest-DeepSeek routing is vendor-direct off-peak.
- `/v1/models` is served without authentication — never treat a catalog fetch as a key test.
- Current active key(s) and their status are tracked in user memory — check there before asking the user for keys.
