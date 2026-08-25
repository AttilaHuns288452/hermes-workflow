---
name: ai-usage-quota
description: Use when asking token usage, spend, or monthly quota.
---

# AI Usage & Quota Measurement

Answering "what did I use / what did it cost / why is the meter at X%" for Attila's
providers (OpenCode Go, Zen, OpenRouter, CommandCode). The user cares about spend
economics — plan decisions get judged against measured usage.

## Data sources (know which meter answers which question)

| Question | Source | How |
|---|---|---|
| Token/cost totals, per month, per model | Local opencode DB | `opencode stats` CLI or SQLite on `~/.local/share/opencode/opencode.db` |
| Hermes (commandcode) tokens today / per-model | Hermes `state.db` | SQLite `state.db` table `session_model_usage` (columns: `model`, `billing_provider`, `input_tokens`, `output_tokens`, `cache_read_tokens`, `reasoning_tokens`, `first_seen`) — filter by `first_seen` epoch. See `references/hermes-state-db.md` |
| Monthly allowance meter ("76% used") | Web console ONLY | app.opencode.ai / console.opencode.ai (Go plan dashboard) |
| Per-token pricing | https://opencode.ai/docs/zen | per-1M-token table incl. cache-read fractions (~1–10% of input price) |

**The Go/Zen quota meter is NOT exposed via API key.** Probing `api.opencode.ai`
with the Bearer key returns 404 for /quota, /usage, /account, /limits, /benefits
— the CLI client only calls `/chat/completions` and `/models` (base URLs found by
binary string-grep: `https://opencode.ai/zen/go/v1`, `/zen/v1`). Don't burn time
probe-farming endpoint lists.

## Quick path

```bash
opencode stats                 # all-time: Input/Output/Cache Read/Cache Write + cost
opencode stats --days 30       # rolling window
opencode stats --models        # per-model token + cost table
```

## Per-calendar-month / per-model breakdown

Aggregate Python-side from SQLite — the `session` table has exactly the needed
columns: `time_created` (ms epoch), `tokens_input`, `tokens_output`,
`tokens_reasoning`, `tokens_cache_read`, `tokens_cache_write`, `cost`, `model`
(model is JSON like `{"id":"meta/muse-spark-1.2-contributor","providerID":"opencode-go","variant":"default"}`).

Run `scripts/usage_by_month.py` (monthly table; pass a `YYYY-MM` arg for a
per-model breakdown of that month). Key snippet:

```python
datetime.datetime.fromtimestamp(time_created / 1000).strftime("%Y-%m")  # month key
```

## Explaining the numbers to the user (the recurring confusion)

- Local `cost`/`$` figures are a **shadow price**: per-token rate × tokens. Free
  models (`*-free`) show $0.0000. Cache reads bill at ~1¢/M so 20M+ cache reads add
  almost nothing to the $ figure.
- The plan's "% of monthly usage" meter counts **ALL tokens** — free models and
  cache reads included — against the flat-fee monthly allowance. Flat subscription
  means the % does not correspond to a dollar bill.
- So "why only $2.74 if I'm at 76%?" is almost always: two different meters, and the
  answer is "$ is a shadow estimate of paid-model tokens; X% is your allowance meter."

## Credential & config locations

- `~/.local/share/opencode/auth.json` — `{"<provider>": {"type": "api", "key": ...}}`
  (OpenCode Go key lives here, service id `opencode-go`).
- `~/.local/share/opencode/account.json` — account/serviceID mapping.
- Hermes `config.yaml` (`~/AppData/Local/hermes/`) `providers:` sections + hermes
  `auth.json` (`credential_pool`). Redact keys in any output; extract via python and
  keep them out of chat.

## Pitfalls

- `time_created` is ms epoch — divide by 1000 before `fromtimestamp`.
- Group by month in **Python**, not SQL `strftime` compare — the SQL version
  returned zero rows in practice.
- f-string `:d` format crashes on float counters from `defaultdict` lambdas with
  mixed-type inits — init all ints, let `+=` promote the cost column to float.
- Skip sessions with all-zero tokens when aggregating (empty/aborted sessions
  pollute totals).
- Hermes vs opencode: `opencode.db` = OpenCode/Go/Zen only; `state.db:session_model_usage` = Hermes/commandcode. If today shows 0 in opencode but you used Hermes, check `references/hermes-state-db.md`.
- Hermes `first_seen` is seconds epoch (float), not ms — do NOT divide by 1000.

## Prompt cache hit-rate diagnosis (Hermes / commandcode)

When `cache=113/xxx (0%)` alternates with `cache=97-100%` on `muse-spark-1.2@commandcode`:

### Measure (from `agent.log`, not the quota %)

```bash
# per-call cache line shape: cache=<cached>/<prompt> (<pct>%)
grep "provider=commandcode.*cache=" ~/AppData/Local/hermes/logs/agent.log | tail -n 40
```

Python summary (weighted vs per-call, zero-hit vs high-hit):
- `weighted = sum(cached)/sum(prompt)` — answers "what % of billed tokens were cached"
- `per-call avg = mean(cached/prompt)` + `median` — reveals bimodal `0%` vs `~99%`
- `zero-hit (<5%)` vs `high-hit (>85%)` counts — >40% zero-hit = busted prefix

`113` = static system prefix only — history/tools didn't hit. `97-100%` = healthy prefix reuse.

### Root causes (check in order)

0. **Caching not enabled at all** — `grep -rn "cache_control" ~/AppData/Local/hermes` returning nothing means no `cache_control` markers are ever sent, so the provider can't cache and hit rate is **0 / undefined** (every token recomputed at full input price). Precedes every other cause — verify first. Fix: pin one `cache_control: {type:"ephemeral"}` on the system-prefix message.
1. **Toolset thrashing** — `tool_search activated (tier 1): 2 vs 6 vs 24 tools kept` mid-conversation moves `tools[-1].cache_control`. DOCS: *swaps toolsets → invalidates cache*.
2. **Monster conversation** — `in=47k→283k` over 80+ turns, `history=141`. 4 breakpoints only cover `system-prefix + system-suffix + last 2 msgs`; growth pushes prefix out.
3. **5m TTL + slow turns** — `prompt_caching.cache_ttl: 5m` + gaps `70-190s` + `latency 25-111s` + `504 retries` → expires before next write.
4. **Subagent interleaving** — `skills_list` (223k chars) calls interleaved on same session ID poison prefix.

`is_commandcode` (`provider=commandcode` + `api.commandcode.ai` → envelope layout) is correct when hits reach `97-100%` — markers are sent.

### Fix (lazy rung)

```bash
hermes config set prompt_caching.cache_ttl 1h   # NOT direct yaml edit (blocked: security-sensitive)
hermes gateway restart
hermes config get prompt_caching.cache_ttl      # verify: 1h
# next session: check agent.log — weighted should recover toward 65-70%+ if workload allows
```

See `references/hermes-prompt-cache-diagnosis.md` for the 2026-08-20 session transcript (303 calls: 49.3% weighted vs 834 calls: 67% prior day) and the full diagnosis query.

### Pitfall

Do NOT `patch`/`write_file` `config.yaml` directly — agent is blocked. Always use `hermes config set`. After TTL change, the old 141-msg session stays busted; start a fresh session to measure.

## Hermes lifetime tokens — what's actually on disk

The "Hermes `state.db`" path answers per-model/day for commandcode, but it is NOT a lifetime ledger and is easy to over-trust. Verified 2026-08-20 on this install:

- `cron/usage_audit.jsonl` (only source with token counts) holds **cron-only** fires — observed 5 records, Σ 55,437 tokens. It records `prompt_tokens/completion_tokens/total_tokens` and **drops all cache fields** (`cache_read`, `cache_creation`), so cache hit rate is uncomputable from it.
- `sessions/session_*.json` (1,254 files) are transcripts — **zero per-message token counts**. A recursive walk for `total_tokens` yields 0 hits. They cannot answer "all-time tokens."
- Therefore a true **all-time Hermes token total is NOT on disk** — it lives only at the provider billing console (commandcode.ai for `muse-spark-1.2-contributor`, opencode.ai/zen for `*-free` sessions). Don't claim a disk total from these two sources.

### One-line fix to make "all-time" answerable

Append to a usage hook on every chat completion (same shape as the cron audit):

```python
usage_audit.append({
  "ts": now, "model": model,
  "prompt_tokens": u.prompt_tokens,
  "completion_tokens": u.completion_tokens,
  "total_tokens": u.total_tokens,
  "cache_read_tokens": getattr(u, "cache_read_tokens", 0),   # was dropped
  "cache_write_tokens": getattr(u, "cache_creation_input_tokens", 0),
})
# hit rate = cache_read_tokens / (cache_read_tokens + prompt_tokens - cache_write_tokens)
```

Then all-time = `sum(total_tokens)`; hit rate = `sum(cache_read) / (sum(cache_read)+sum(prompt)-sum(cache_write))`. See `references/hermes-local-token-gaps.md` for the commands + observed output.