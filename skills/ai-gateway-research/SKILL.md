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

1. **Enumerate the catalog from the API, never the marketing site.** `GET /v1/models` (usually public, works without a key) is the source of truth for model IDs, access tiers, and per-token prices — entries typically carry `access_tier` (free/paid/premium), `pricing` {input, output, cache_read, unit}, `context_length`, and `capabilities`, so cost math and tier filtering need no scraping. Marketing tables lag and advertise retired IDs.
2. **Verify access empirically per model class.** Catalog presence ≠ callable. Probe ONE model per provider/tier with a max_tokens=1 chat completion using the client's real key, and classify the result by the error taxonomy below. Never test all models for availability triage — one per class is enough and keeps cost at zero. Exception: when the deliverable is a per-model plan-coverage table, sweep the FULL catalog instead — parallel workers (~8), max_tokens=1, classify every result by the taxonomy. With an empty wallet that sweep doubles as the entitlement map: 200 OK = plan-covered, 403 permission_denied = wallet-only/PAYG.
3. **Read plan pages for what plans actually gate.** Gateway subscription tiers typically gate usage budget + concurrency, NOT the model catalog — verify before assuming. Find plans on the homepage (`#pricing` anchor); `/pricing`-style paths are often 404 routes, so grep fetched nav `href`s for the real location. Check the `/deals` (or equivalent) page for promos, then verify whether each promo is plan-billed or wallet-billed — "free" promos on the deals page are frequently wallet-only pay-as-you-go.
4. **Price-performance comparison method:** pick ONE benchmark all candidates report (a shared agentic/coding bench beats a Frankenstein average), compute `score ÷ blended $/Mtok` where blended = weighted input/output price at the workload's token ratio (3:1 for chat, 10:1 for agent loops). Recompute at each vendor's real discounts — gateway promos and off-peak half-price windows flip rankings. Treat vendor-reported benchmark numbers as unverified until an independent party measures them; say who reported what. **Read the baseline inside every vendor multiple** — speed/cost ratios are relative to whatever the vendor compared against, and a '200x cheaper' claim against reasoning models can collapse to ~1.5x against a cheap chat model; likewise 'accuracy' that means agreement-with-other-frontier-models is not ground-truth correctness. When an independent re-measurement exists, lead with it and note where it contradicts the vendor.
5. **Client-error complaints: reproduce the exact request with curl before touching client code.** For tool-calling loops that means BOTH rounds: round 1 with `tools` + `tool_choice:"auto"`, round 2 with the assistant `tool_calls` message AND the `role:"tool"` reply (matching `tool_call_id`, `content` as a STRING) appended. If both succeed via curl, the bug is in the client's message assembly, not the gateway.

## Error taxonomy (OpenAI-compatible gateways)

| Error | Meaning | Fix |
|---|---|---|
| `authentication_error` — "Invalid or disabled ClientApiKey" | key disabled/revoked server-side | dashboard → re-enable or mint a new key; check plan renewal too |
| `not_found_error` — "Model does not exist" | model ID retired/renamed | re-enumerate `/v1/models`, use the current suffixed ID |
| `permission_denied` — "requires real deposited balance" | wallet-only pay-as-you-go model; plan credits excluded by design | deposit to wallet or pick a plan-covered model |
| `429 rate_limit_exceeded` | upstream saturation, NOT entitlement | retry once with spacing; persistent 429s stay "unresolved" — never guess tier coverage from them |
| `410 internal_error` | model dead upstream (removed from routing) | exclude from recommendations; not a client bug |
| 200 but wrong/empty content | client parsing (SSE vs JSON) or prompt issue | inspect the raw JSON body before debugging code |

## Pitfalls

- **Test with the key the client actually uses.** Accounts commonly hold several keys — one active, one disabled — and the disabled one makes the whole provider look down.
- **A successful `GET /v1/models` says nothing about key validity.** Most gateways serve the catalog publicly; only a chat completion verifies auth.
- **Model IDs get suffixes on revisions** (`-0731`, `-beta`); the bare historical name 404s while marketing pages still show it. Always copy IDs from the live catalog response.
- **Free-tier allowances are a separate meter from the plan window.** Using free-tier models does not extend plan usage — it protects it; when either meter runs out requests fall back to the wallet. Read the tier/allowance docs before telling the user what happens at exhaustion; the naive answer ("plan picks up free models after the free cap") is usually backwards.
