# xKiro provider notes

User's primary gateway (Hermes runs on it). Verify everything live before relying on it — prices, tiers, and IDs drift. Tier snapshot below comes from the latest whole-catalog probe (method: SKILL.md step 2) — re-derive before any claim.

## Structure

- Base URL `https://api.xkiro.com/v1`, OpenAI Chat Completions + Anthropic Messages both supported. Model ID format `vendor/model`.
- `/v1/models` entries carry `access_tier` (free/paid/premium), `pricing` {input, output, cache_read, unit: per_1m_tokens}, `context_length`, `capabilities` — authoritative for cost math and tier filters; no scraping needed.
- No plan-status API: `/v1/plan`, `/v1/subscription`, `/v1/me` all 404. Plan state lives in the dashboard only; entitlement is proven empirically by probing.
- Plans gate usage, not the catalog: a plan covers free/paid/premium non-PAYG models within a sliding allowance window (refills gradually — no midnight reset). Free-tier models have their OWN daily token allowance, separate from the plan window: `:free` models never consume plan budget, and their daily ration is identical on every plan. When any allowance is exhausted, requests fall back to the wallet; at a $0 wallet they are refused.
- Docs are readable server-side via curl + HTML strip: docs.xkiro.com/guides/pricing and docs.xkiro.com/models/tiers.

## Tier semantics (from /models/tiers)

- `free`: callable on every plan within its daily token allowance.
- `paid`: needs an active plan or positive wallet balance (promo credit counts).
- `premium`: plan-covered or real deposit — promo/bonus credit does NOT unlock.
- A pay-as-you-go flag cuts across tiers: PAYG models skip the plan entirely and bill the wallet on every request.

## Wallet-only pay-as-you-go (403 permission_denied on plan; whole-catalog probe)

All DeepSeek, ALL Kimi (k2.5/k2.6/k2.7-code/k3), GPT-6 Astra, all Grok, Xiaomi MiMo, Tencent Hunyuan, MiniMax base tiers (m2.5/m2.7/m3 non-`:free`), Qwen base plus/max tiers (non-`:free`). Re-derive before claims: sweep `/v1/models` (8-way parallel, max_tokens=1) with the client's key — at $0 wallet, 200 OK = plan-covered, 403 permission_denied = wallet-only. Last sweep: 75 of 111 models plan-covered.

## Value ladder (recompute prices from /v1/models before cost claims)

- $0 — burn first, never touches the plan allowance: all `:free` variants (qwen3.7-flash:free and qwen3.6-plus:free at 1M ctx, minimax-m3:free at 1M ctx), ALL Mistral (mistral-large-2512 general, codestral-2508 for code), SenseNova flash-lite.
- Cheapest good paid: `z-ai/glm-4.7-flashx` (~0.07/0.40), `openai/gpt-5.6-luna` (~0.10/0.60, 1M ctx, vision), `z-ai/glm-5.3-flash` (~0.15/0.50, 1M ctx, vision — user's daily driver).
- Mid: `google/gemini-3.7-flash` (~0.375/1.875), `nvidia/nemotron-3-ultra` (~0.50/2.20, 1M ctx).
- Heavy: `google/gemini-3.8-flash` (~0.75/3.75), `openai/gpt-5.4-mini` (~0.75/4.50).
- Expensive: claude-sonnet-4.6 (~3/15), opus-4.x/5 (~5/25), claude-fable-5 (~10/50).
- Frontier leaders per independent indexes (Claude Fable 5.1, GPT-6 Astra) are NOT usable on the plan: fable-5.1 absent from the catalog, GPT-6 Astra PAYG-only.

## Quirks

- Send a browser-like User-Agent on every scripted xkiro call — Cloudflare rejects the default Python UA with 403 code 1010.
- `deepseek/deepseek-v4-flash` bare ID is retired; current IDs carry revision suffixes. Always copy IDs from the live catalog.
- 410 `internal_error` = dead upstream (seen on nemotron-3-nano and llama-3.3-nemotron-super-49b) — exclude from recommendations, don't debug.
- Persistent 429s across spaced retries (seen on glm-4.5, glm-4.5-x, glm-4.6) = upstream saturation, not entitlement — label unresolved instead of guessing coverage.
- Current active key(s) and their status are tracked in user memory — check there before asking the user for keys.
