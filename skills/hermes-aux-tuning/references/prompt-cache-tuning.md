# Prompt Cache Tuning — CommandCode / Muse Spark

Condensed from session 20260820_094322 (1:2 → 1:1 collapse, 303 calls).

## Diagnostic (weighted > per-call avg)

```python
import re
from pathlib import Path
log = Path(r'C:\Users\Attila\AppData\Local\hermes\logs\agent.log').read_text(encoding='utf-8', errors='ignore')
pat = re.compile(r'provider=commandcode.*in=(\d+).*cache=(\d+)/(\d+)')
rows = pat.findall(log)
tot_in = sum(int(i) for i,_,_ in rows)
tot_c  = sum(int(c) for _,c,_ in rows)
per    = [int(c)/int(t) for _,c,t in rows]
print(f'weighted {tot_c/tot_in:.1%}  per-call {sum(per)/len(per):.1%}  zero-hit {sum(1 for p in per if p<0.05)}/{len(rows)}')
# Per-session breakdown:
pat2 = re.compile(r'\[([^\]]+)\].*provider=commandcode.*in=(\d+).*cache=(\d+)/(\d+)')
from collections import defaultdict
g=defaultdict(list)
for m in pat2.finditer(log):
    g[m.group(1)].append(int(m.group(3))/int(m.group(4)) if int(m.group(4)) else 0)
for sess, vals in sorted(g.items()):
    if len(vals)>=5:
        print(sess, f'n={len(vals)} avg={sum(vals)/len(vals):.1%} zeros={sum(1 for v in vals if v<0.05)}/{len(vals)}')
```

Scale: agent.log (today, 49.3% weighted, 42.9% zero-hit) vs agent.log.1 (67% / 32.7% zero-hit) vs agent.log.2 (94.9% / 2.5%).

## Root causes (ranked)

| Signal | Log clue | Fix rung |
|--------|----------|----------|
| Toolset thrashing | `tool_search activated (tier 1): 2 vs 6 vs 24 kept / 104-138 deferred` mid-session — `tools[-1].cache_control` moves, next turn only 113-token system prefix hits (`cache=113/xxx 0%`) | Pin toolset or split session |
| Monster conversation | `in=47k → 283k` over 81 turns, 4 breakpoints only cover system-prefix + suffix + last 2 msgs | Compress/split earlier |
| 5m TTL + slow turns | `cache_ttl: 5m` + gaps 78-197s + latency 27-111s + 504 retries → expiry before next write | `cache_ttl: 1h` |
| Subagent interleaving | `API call #1..#8` (skills_list 223k) interleaved between `#58→#59` on same session ID | Isolate delegate sessions |

`is_commandcode` (provider==commandcode / host api.commandcode.ai → envelope layout `True, False`) is correctly wired — hits show 97-100% when prefix stable.

## One-line fix

```bash
hermes config set prompt_caching.cache_ttl 1h
hermes gateway restart  # user runs — blocked from subagents
```

`prompt_caching.cache_ttl: 5m` → `1h` in `C:\Users\Attila\AppData\Local\hermes\config.yaml`.

## Verification

After fix, same workload should return to ~65%+ weighted. If still <50%, stable toolset is next rung (avoid tier churn mid-chat).

## References

- `agent/agent_runtime_helpers.py:anthropic_prompt_cache_policy` — CommandCode branch (envelope layout, native on anthropic_messages)
- `agent/prompt_caching.py:apply_anthropic_cache_control` — 4 breakpoints, static prefix split
- `agent/conversation_loop.py` — `cache=113/xxx` log line (113 = static system prefix)
