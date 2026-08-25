# Hermes Prompt Cache Diagnosis — 2026-08-20

## Session that triggered this

- **Session ID:** `20260820_094322_168727`
- **Model:** `meta/muse-spark-1.2-contributor` @ `provider=commandcode` (`api.commandcode.ai`)
- **Config:** `prompt_caching.cache_ttl: 5m` (before fix)
- **Conversation:** 81 API calls, `in=47k → 283k`, `history=141 msgs`, `latency 5–111s`, gaps 78–197s
- **Fix:** `hermes config set prompt_caching.cache_ttl 1h` + `hermes gateway restart` → verified `1h`

## Measured hit rates (from agent.log, weighted by prompt tokens)

```
agent.log   (today, 2026-08-20): 303 calls  49.3% weighted  42.9% zero-hit  50.5% high-hit  ← user's "1:1"
agent.log.1 (yesterday):         834 calls  67.0% weighted  32.7% zero-hit                ← user's "1:2"
agent.log.2 (older):              39 calls  94.9% weighted   2.5% zero-hit
session 094322:                    81 calls  41.6% weighted  54% zero-hit (44/81)
```

Bimodal distribution: 130 calls at 0.0–0.1 and 140 at 0.9–1.0 — not a gradual decay.

## Log shape

```
INFO agent.conversation_loop: API call #N: model=... provider=commandcode in=<prompt> out=<completion> total=<sum> latency=<s> cache=<cached>/<prompt> (<pct>%)
# hit:   cache=253297/256146 (99%)
# miss:  cache=113/253292 (0%)   ← 113 = static system prefix only
```

Failed calls (no cache field) also appear — filter with `provider=commandcode.*cache=`:
```
WARNING API call failed ... BadRequestError ... Invalid option: expected one of "low"|"medium"|"high"|"xhigh"|"max"
WARNING API call failed ... 504 Upstream ... temporarily unavailable
```

## Root-cause checklist (in priority order)

1. **Toolset thrashing** — `tool_search activated (tier 1): 2 vs 6 vs 24 tools kept, 104–138 deferred` flips `tools[-1].cache_control` each turn. AGENTS.md: *Per-conversation prompt caching is sacred — swaps toolsets or rebuilds system prompt mid-conversation invalidates cache and multiplies cost.*
2. **Conversation bloat** — 4 breakpoints = `system-prefix + system-suffix + last 2 msgs`. At 283k prompt the stable prefix is evicted.
3. **TTL vs gap** — `5m` TTL with gaps 139s, 141s, 189s, 197s plus 27–111s latency + 504 retries → cache expires before next write. `1h` absorbs this.
4. **Subagent interleaving** — same session ID logs `API call #1..#8` for `skills_list` (223k chars) interleaved between main `#58→#59` with different tool lists.

## Code locations (where to verify)

- `agent/prompt_caching.py` — `build_prompt_cache_plan` / `apply_anthropic_cache_control` (4 breakpoints, `_can_carry_marker` skips empty tool/assistant turns)
- `agent/agent_runtime_helpers.py:anthropic_prompt_cache_policy` — `is_commandcode` branch:
  ```python
  is_commandcode = (
      provider_lower == "commandcode"
      or base_url_host_matches(eff_base_url, "api.commandcode.ai")
      or "commandcode" in eff_base_url.lower()
  )
  if is_commandcode:
      if is_anthropic_wire: return True, True
      return True, False  # envelope layout on chat_completions
  ```
  When hits reach 97–100% this branch is working — markers are sent, gateway honors ~98% hit rate when prefix stable.
- `config.yaml:prompt_caching.cache_ttl` — `5m` default, `1h` after fix.

## Diagnosis queries (copy-paste)

```powershell
# PowerShell — summary for all commandcode calls today
python -c "
import re; from pathlib import Path; import statistics
from collections import Counter
log=Path(r'C:\Users\Attila\AppData\Local\hermes\logs\agent.log').read_text(errors='ignore',encoding='utf-8')
pat=re.compile(r'provider=commandcode.*in=(\d+).*cache=(\d+)/(\d+)')
rows=pat.findall(log)
per=[int(c)/int(t) for _,c,t in rows]
tot_in=sum(int(i) for i,_,_ in rows); tot_c=sum(int(c) for _,c,_ in rows)
print(f'n={len(rows)} weighted={tot_c/tot_in:.1%} per-call avg={sum(per)/len(per):.1%} median={statistics.median(per):.1%}')
zeros=sum(1 for p in per if p<0.05); high=sum(1 for p in per if p>0.85)
print(f'zero-hit {zeros}/{len(rows)}={zeros/len(rows):.1%}  high-hit {high}/{len(rows)}={high/len(rows):.1%}')
print(Counter(int(p*10)/10 for p in per))
"
# History across rotated logs
# agent.log.1 = yesterday, agent.log.2 = older — repeat with Path(r'...\agent.log.1')
```

## Fix verification

```bash
hermes config set prompt_caching.cache_ttl 1h
hermes gateway restart
hermes config get prompt_caching.cache_ttl  # expect 1h
# start a NEW session — old 141-msg session stays busted; measure next 10+ turns
```

Direct `patch`/`write_file` on `config.yaml` is blocked (security-sensitive) — must use `hermes config set`.

## When to add more (next rung)

If weighted stays <65% after `1h` on similar workload: pin toolset tiers per session or trigger earlier compression/split — `1h TTL` only hides churn, stable toolset is the real fix.
# ponytail: global 1h TTL, per-session tool pinning if throughput matters
