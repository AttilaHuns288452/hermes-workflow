---
name: ai-gateway-research
description: Use when researching gateway models, plans, keys, or errors.
triggers:
  - which models can I use
  - xkiro
  - model catalog
  - api key disabled
  - plan comparison
  - price performance model
  - tool calling errors
---

# AI Gateway Research & Access Verification

Class: researching LLM API gateways (plans, catalogs, price-performance) and verifying what a given API key can actually call. Covers the user's own gateway accounts (xKiro is the primary one — provider notes in `references/xkiro.md`) and any OpenRouter-style service.

## Procedure

1. **Enumerate the catalog from the API, never the marketing site.** `GET /v1/models` (usually public, works without a key) is the source of truth for model IDs, access tiers, and per-token prices. Marketing tables lag and advertise retired IDs. Pull pricing fields from this response for any cost math.
2. **Verify access empirically per model class.** Catalog presence ≠ callable. Probe ONE model per provider/tier with a 5-max-token chat completion using the client's real key, and classify the result by the error taxonomy below. Never test all models — one per class is enough and keeps cost at zero.
3. **Read plan pages for what plans actually gate.** Gateway subscription tiers typically gate usage budget + concurrency, NOT the model catalog — verify before assuming. Find plans on the homepage (`#pricing` anchor); `/pricing`-style paths are often 404 routes, so grep fetched nav `href`s for the real location. Check the `/deals` (or equivalent) page for promos, then verify whether each promo is plan-billed or wallet-billed — "free" promos on the deals page are frequently wallet-only pay-as-you-go.
4. **Price-performance comparison method:** pick ONE benchmark all candidates report (a shared agentic/coding bench beats a Frankenstein average), compute `score ÷ blended $/Mtok` where blended = weighted input/output price at the workload's token ratio (3:1 for chat, 10:1 for agent loops). Recompute at each vendor's real discounts — gateway promos and off-peak half-price windows flip rankings. Treat vendor-reported benchmark numbers as unverified until an independent party measures them; say who reported what.
5. **Client-error complaints: reproduce the exact request with curl before touching client code.** For tool-calling loops that means BOTH rounds: round 1 with `tools` + `tool_choice:"auto"`, round 2 with the assistant `tool_calls` message AND the `role:"tool"` reply (matching `tool_call_id`, `content` as a STRING) appended. If both succeed via curl, the bug is in the client's message assembly, not the gateway.

## Error taxonomy (OpenAI-compatible gateways)

| Error | Meaning | Fix |
|---|---|---|
| `authentication_error` — "Invalid or disabled ClientApiKey" | key disabled/revoked server-side | dashboard → re-enable or mint a new key; check plan renewal too |
| `not_found_error` — "Model does not exist" | model ID retired/renamed | re-enumerate `/v1/models`, use the current suffixed ID |
| `permission_denied` — "requires real deposited balance" | wallet-only pay-as-you-go model; plan credits excluded by design | deposit to wallet or pick a plan-covered model |
| 200 but wrong/empty content | client parsing (SSE vs JSON) or prompt issue | inspect the raw JSON body before debugging code |

## Pitfalls

- **Test with the key the client actually uses.** Accounts commonly hold several keys — one active, one disabled — and the disabled one makes the whole provider look down.
- **A successful `GET /v1/models` says nothing about key validity.** Most gateways serve the catalog publicly; only a chat completion verifies auth.
- **Model IDs get suffixes on revisions** (`-0731`, `-beta`); the bare historical name 404s while marketing pages still show it. Always copy IDs from the live catalog response.
