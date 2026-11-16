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
  - new api key which provider
  - wire the app to a model
  - make it use the free model
---

# AI Gateway Research & Access Verification

Class: researching LLM API gateways (plans, catalogs, price-performance) and verifying what a given API key can actually call. Covers the user's own gateway accounts (xKiro is the primary one — provider notes in `references/xkiro.md`; OpenCode/OpenRouter-style services in `references/opencode.md`) and any OpenAI-compatible service. Also covers wiring an app to a chosen provider/model and verifying the runtime actually loads it.

## Procedure

0. **Identify the issuer before probing anything.** When handed an unfamiliar key: inventory the already-configured providers (base URL + key prefix each, values never echoed), and web-search the key's literal prefix plus "API key" — prefixes like `oc_sk_`, `sk-or-`, `gsk_` identify the service in one search. Stage the key ONCE in a scratch file and reference it via `$(cat …)` in every probe so it never lands in command lines or output.
1. **Enumerate the catalog from the API, never the marketing site.** `GET /v1/models` (usually public, works without a key) is the source of truth for model IDs, access tiers, and per-token prices — entries typically carry `access_tier` (free/paid/premium), `pricing` {input, output, cache_read, unit}, `context_length`, and `capabilities`, so cost math and tier filtering need no scraping. Marketing tables lag and advertise retired IDs.
2. **Verify access empirically per model class.** Catalog presence ≠ callable. Probe ONE model per provider/tier with a max_tokens=1 chat completion using the client's real key, and classify the result by the error taxonomy below. Never test all models for availability triage — one per class is enough and keeps cost at zero. Exception: when the deliverable is a per-model plan-coverage table, sweep the FULL catalog instead — parallel workers (~8), max_tokens=1, classify every result by the taxonomy. With an empty wallet that sweep doubles as the entitlement map: 200 OK = plan-covered, 403 permission_denied = wallet-only/PAYG.
3. **Read plan pages for what plans actually gate.** Gateway subscription tiers typically gate usage budget + concurrency, NOT the model catalog — verify before assuming. Find plans on the homepage (`#pricing` anchor); `/pricing`-style paths are often 404 routes, so grep fetched nav `href`s for the real location. Check the `/deals` (or equivalent) page for promos, then verify whether each promo is plan-billed or wallet-billed — "free" promos on the deals page are frequently wallet-only pay-as-you-go.
4. **Price-performance comparison method:** pick ONE benchmark all candidates report (a shared agentic/coding bench beats a Frankenstein average), compute `score ÷ blended $/Mtok` where blended = weighted input/output price at the workload's token ratio (3:1 for chat, 10:1 for agent loops). Recompute at each vendor's real discounts — gateway promos and off-peak half-price windows flip rankings. Treat vendor-reported benchmark numbers as unverified until an independent party measures them; say who reported what. **Read the baseline inside every vendor multiple** — speed/cost ratios are relative to whatever the vendor compared against, and a '200x cheaper' claim against reasoning models can collapse to ~1.5x against a cheap chat model; likewise 'accuracy' that means agreement-with-other-frontier-models is not ground-truth correctness. When an independent re-measurement exists, lead with it and note where it contradicts the vendor.

**When the question is real-world harness fit** ("why does X perform worse than Y here"), benchmark rank is not evidence — benchmarks never exercise this harness's tool schemas, verification habits, or retry behavior. Compare same-task session traces from `~/.hermes/state.db` instead: group `sessions` by `model` (filter `message_count > 0`; dead starts are zero-message rows), match the same task family across models by title keywords, compare per-completed-task cost plus message/tool-call counts, then read the `messages` rows (`active=1`) of the busiest sessions for failure classes: recovery turns after tool errors, data-model asserts that passed while the delivered artifact was broken, QA-script churn, guard bounce-backs. The strongest discriminator is what the model verified before claiming done. Report counts + trace evidence, never impressions; `session-history-mining` covers safe extraction.
5. **Client-error complaints: reproduce the exact request with curl before touching client code.** For tool-calling loops that means BOTH rounds: round 1 with `tools` + `tool_choice:"auto"`, round 2 with the assistant `tool_calls` message AND the `role:"tool"` reply (matching `tool_call_id`, `content` as a STRING) appended. If both succeed via curl, the bug is in the client's message assembly, not the gateway.

For suspected tool-ARG mangling (calls arrive with empty or truncated `arguments`), curl replay is not enough — the loss happens in the provider's function-call serialization after the request is accepted. Run `scripts/probe_tool_args_nesting.py --models <ids>`: one forced tool call per nesting shape (flat array-of-objects, object-valued property inside an array item, object-in-object, string-in-array) carrying a sentinel, then diff the returned arguments against it. A shape that reports DROP is destroyed provider-side and cannot be repaired downstream — mitigate at the schema layer by advertising that nested object as a JSON-encoded string and parsing it back at dispatch. Re-probe before citing a verdict; gateways fix these silently.
6. **Wire and verify end-to-end, locally AND in production.** The app's env file is the single source of truth; deployed platforms need the same vars set in their own env store plus a fresh deployment (env changes never retro-apply to a running deploy). Verify through the app's own health/config echo AND one real generation call whose result carries the provider's generated-by-model signal — a config echo proves the var loaded, not that generation works. Check both environments; local-vs-deployed config drift is the top cause of "it still uses the old model" reports.
7. **A dashboard full of models you never configured is an attribution question, not a mystery.** Work it in this order: (a) the harness's own ledger —
`select billing_provider, model, sum(api_call_count), sum(input_tokens+output_tokens) from session_model_usage group by 1,2 order by 3 desc`
against `~/.hermes/state.db` — grouping by `billing_provider` proves in one query whether the agent is even the source of that spend; (b) config: main model, `delegation.model`, any MoA preset, every profile config, and the fallback chain (a fallback pointing at the same provider under a different model is a legitimate source); (c) the clients. A local model bridge/proxy exposes dozens of provider-prefixed aliases to CLIs like Claude Code (`cmd-…` → provider A, `xk-…` → provider B), so every CLI run, benchmark sweep or spawned agent bills the provider under that alias's target model. Prove the path from the client's own records — a session log containing `"model":"<alias>"` is the evidence — instead of inferring from a config you already know.
Report request share and token share separately: a dashboard's single "share" column is usually **tokens**, so a model with 4% of tokens can be a tiny fraction of calls or the reverse, and quoting the wrong one changes the story.

## Error taxonomy (OpenAI-compatible gateways)

| Error | Meaning | Fix |
|---|---|---|
| `authentication_error` — "Invalid or disabled ClientApiKey" | key disabled/revoked server-side | dashboard → re-enable or mint a new key; check plan renewal too |
| `not_found_error` — "Model does not exist" | model ID retired/renamed | re-enumerate `/v1/models`, use the current suffixed ID |
| `permission_denied` — "requires real deposited balance" | wallet-only pay-as-you-go model; plan credits excluded by design | deposit to wallet or pick a plan-covered model |
| `429 rate_limit_exceeded` | upstream saturation, NOT entitlement | retry once with spacing; persistent 429s stay "unresolved" — never guess tier coverage from them |
| `410 internal_error` | model dead upstream (removed from routing) | exclude from recommendations; not a client bug |
| `402` "Insufficient account funds" | PAYG wallet empty — account-wide, not model-specific | deposit, or switch to a plan-covered/free route |
| `403` "active subscription required" | that model family is subscription-gated | activate the subscription or pick another family |
| `403` FreeTierError "can only be used from within \<app\>" | free tier is server-gated to the vendor's own client | use it from that client, or an external-app free host for the same model; never spoof client identity (see pitfalls) |
| `400` "MissingSessionID"-style protocol error | required routing/protocol header absent | supply the documented header — this is protocol, not auth; do not misread it as a bad key |
| 200 but wrong/empty content | client parsing (SSE vs JSON) or prompt issue | inspect the raw JSON body before debugging code |

## Pitfalls

- **Test with the key the client actually uses.** Accounts commonly hold several keys — one active, one disabled — and the disabled one makes the whole provider look down.
- **A successful `GET /v1/models` says nothing about key validity.** Most gateways serve the catalog publicly; only a chat completion verifies auth.
- **Model IDs get suffixes on revisions** (`-0731`, `-beta`); the bare historical name 404s while marketing pages still show it. Always copy IDs from the live catalog response.
- **Free-tier allowances are a separate meter from the plan window.** Using free-tier models does not extend plan usage — it protects it; when either meter runs out requests fall back to the wallet. Read the tier/allowance docs before telling the user what happens at exhaustion; the naive answer ("plan picks up free models after the free cap") is usually backwards.
- **Entitlement gates are not puzzles.** When a free tier is server-enforced to the vendor's own client (403 naming the client app), do not fabricate the client's identity headers (fake User-Agent/project/session-id shapes) to pass it — that is billing abuse, not integration. Report the gate and offer the legitimate routes: subscription, wallet top-up, or an external-app free host for the same model.
- **"Free" in a request is a money constraint with a literal meaning.** When the user says "free" and the catalog has literal free-tier IDs, wire the free-tier ID — never a plan-covered paid model that happens to cost nothing at the margin. Plan-covered ≠ free in the user's meaning; that substitution gets rejected even when the economics are identical. Never wire app traffic to a PAYG route just because it answers 200 — every request spends the user's money. If every working route bills per token, confirm before wiring.
- **Process env shadows `.env` files.** Node's `process.loadEnvFile()` and most dotenv loaders do NOT override variables already exported in the launching shell, so the server runs with the stale inherited value while `.env` says otherwise. Launch with `env -u VAR …` and confirm via the app's own health/config echo that the intended model id is the one actually loaded. The same asymmetry runs the other way for a long-lived daemon: writing a key into `.env` changes nothing for a process that started before the write, so the provider fails and silently falls back. Check `/proc/<pid>/environ` rather than only the file — a status command that reads `.env` will report healthy while the live process cannot see the key at all.
- **Benchmark rank does not predict harness fit.** High-benchmark models fail here on traits benchmarks never exercise (tool-arg serialization, verification discipline, retry loops) — answer "X feels worse than Y" questions from same-task session traces (step 4), never from the leaderboard.
