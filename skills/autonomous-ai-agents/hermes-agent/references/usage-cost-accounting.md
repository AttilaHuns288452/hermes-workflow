# Usage & Cost Accounting: Diagnosis and Repair

When an insights/cost figure is wildly wrong, this is the procedure. The core discipline: costs are
derived values recomputable from recorded token counts, so repair them from that source of truth and
never invent a rate to make a number look plausible.

## Where costs live

- `sessions.estimated_cost_usd` / `actual_cost_usd` — per-session rollup, written at turn finalize.
- `session_model_usage` — per (session, model, task) detail rows with token counts
  (`input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_write_tokens`) plus
  `cost_status` / `cost_source` provenance.
- Pricing pipeline: `agent/usage_pricing.py` resolves a `BillingRoute`, then a `PricingEntry`
  (sources in order of trust: provider cost API → provider models API → official-docs snapshot →
  `user_override` → none). Internally all rates are normalized to **per-million**; token rates come
  in per-token and are multiplied by 1e6.
- Provider `/models` endpoints may declare their own pricing shape, including an explicit
  `unit` (e.g. `per_1m_tokens`) and key names like `input`/`output` instead of
  `prompt`/`completion`. `agent/model_metadata.py::_extract_pricing` maps the aliases and
  `_normalize_token_rates` rescales by the declared unit.

## The unit-mismatch class (the common catastrophic case)

A rate quoted per-million that is consumed as per-token inflates every estimate by exactly 1e6
(per-1k quotes inflate by 1e3). Symptom: `hermes insights` shows millions of dollars on a cheap or
subscription plan. Confirm by ratio, not by eyeballing:

1. Reproduce the figure from the store:
   `select model, cost_source, count(*), sum(estimated_cost_usd), sum(input_tokens),
   sum(output_tokens), sum(cache_read_tokens), sum(cache_write_tokens)
   from session_model_usage group by model, cost_source order by 4 desc;`
2. Recompute a suspect row independently: `tokens × rate_per_million / 1e6` per bucket, summed.
   Compute `stored / recomputed`. A tight cluster at exactly 1,000,000 (or 1,000) is the unit bug;
   a cluster at ~1 means those rows are fine. Rows at other ratios mean mixed rate cards over time —
   recompute each row at current rates rather than scaling by a factor.
3. Separate **history** from **live code** before patching anything: re-run the current pricing path
   on a sample usage and check its magnitude. If the live path is already dimensionally correct, the
   bad numbers are stale rows from an older build and the repair is data-only.

## Authoritative rates (never fabricate)

Order of trust for repair:
1. The serving endpoint's `/models` pricing, honoring its declared `unit` and `currency`.
2. The framework's models.dev snapshot (`agent/models_dev.get_model_info(provider, model)`).
3. Official-docs snapshot tables inside `usage_pricing.py`.

A model with no entry in any of these stays uncorrected and flagged in the report. Do not guess a
rate, and do not zero the row — an unpriced row is information.

## Repair procedure

1. **Manifest first.** Write every touched row to a CSV (`rowid, session_id, model, token counts,
   old_est, new_est`) before any UPDATE. This is the rollback.
2. **Recompute from tokens**, not by dividing stored values by a factor: `new = Σ tokens × rate / 1e6`
   per bucket. This also absorbs rate-card drift. Leave `estimated_cost_usd = 0` rows untouched
   (zero is a classification, not an error).
3. **Repair both tables.** After fixing detail rows, reconcile `sessions.estimated_cost_usd`.
   Pitfall: the rollup is NOT guaranteed to equal the sum of detail rows — rows whose
   `cost_source` is NULL can exist outside the rollup entirely, so a naive per-session delta
   (`rollup += new - old`) double-counts and can drive rollups negative. Measure first: for each
   session, compare rollup vs sum of detail rows *before* editing; if they diverge, rebuild the
   rollup from the detail sums (or reconcile via the manifest deltas), then assert both tables'
   grand totals agree with independent recomputation.
4. **Assert before committing the result as done:** every priced row must match the formula within
   tolerance, and the two tables must reconcile. Assert both sides — a repair that only verifies
   the detail table can leave the user-visible rollup wrong.
5. Verify end-to-end with the user-facing view (`hermes insights --days N`).

## Cache hit rate (same tables, different question)

Cache-hit questions ("what's the hit rate for model X on provider Y", "how much is caching saving") are
answerable from `state.db` alone — no API probe needed. Get the denominator right or the number is
nonsense.

**Prompt accounting.** `session_model_usage` stores the prompt as three disjoint buckets:
`input_tokens` (uncached) + `cache_read_tokens` (served from cache) + `cache_write_tokens`
(cache creation, Anthropic-style providers only; OpenAI-format routes record 0).

```
hit_rate = cache_read / (input_tokens + cache_read_tokens + cache_write_tokens)
```

Dividing by `input_tokens` alone yields >100% figures (seen: 6727%) because the cached bucket is 20-100x
larger than the uncached one on long agent sessions. `input_tokens` alone is the *uncached* portion, not
the prompt.

**Percentages beyond 100 are always a denominator bug**, never a provider anomaly — spot-check with
`cache_read <= input + cache_read + cache_write` before reporting.

Cost impact, priced per bucket from `models_dev_cache.json` (`cost.cache_read` per million; absent key
means that provider bills cached tokens at the full input rate):

```
actual      = uncached*input_rate + cached*cache_read_rate + output*output_rate   (all /1e6)
without_cache = (uncached+cached)*input_rate + output*output_rate
```

A row with `estimated_cost_usd = 0` and nonzero tokens means the route had no pricing entry — report
the token math and say the cost is unpriced, do not infer a rate.

**Cross-check against the live per-call log** before publishing: `agent.log` writes
`cache=91904/93027 (99%)` per API call (`in=X out=Y total=Z cache=…`). Per-call ratios sitting near the
aggregate prove the SQL is reading the same thing the provider reported; a large gap means the
aggregate is dominated by short/uncached sessions (a real distribution, worth saying out loud).

**Trend by day** (join `sessions` for `started_at`) is the useful second cut — a single aggregate hides
that one bad day was a batch of fresh cold sessions rather than a cache regression.

**SQL through the terminal tool:** multi-line SQL passed as a quoted shell argument mangles (`unrecognized
token: "`). Write the script with `write_file` (first line `.mode column`, second `.headers on`) and run
`sqlite3 ~/.hermes/state.db < /path/query.sql`. Reliable and re-readable, unlike a one-liner escape soup.

## API gotchas when driving the pricing code directly

- `estimate_usage_cost(model_name, usage, *, provider=None, base_url=None, api_key=None)` takes
  strings. `resolve_billing_route(model_name, provider, base_url)` also takes strings — passing a
  `BillingRoute` or `CanonicalUsage` where a name is expected raises `AttributeError: ... has no
  attribute 'strip'`.
- `get_pricing_entry(model_name, provider=..., base_url=...)`, not a route object.
- `CostResult` carries `status` (`actual` / `estimated` / `included` / `unknown`) and `source` —
  `included` means subscription-covered (no per-token invoice) and must not be "corrected" to a
  list-price estimate. Subscription plan usage whose per-token list price is known is still an
  estimate; labeling plan-covered models `included` needs the plan's coverage map, not the rate card.
