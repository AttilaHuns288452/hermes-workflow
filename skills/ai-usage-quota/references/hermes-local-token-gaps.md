# Hermes local token ledger — gaps (2026-08-20)

User asked: "how many tokens all-time in Hermes" and "has the cache hit rate improved for Muse Spark 1.2".

## Findings (this install)

Token-bearing files on disk:
- `~/AppData/Local/hermes/cron/usage_audit.jsonl` — cron-only. Observed 5 records, Σ prompt 51,507 / completion 3,930 / total 55,437. Fields: `prompt_tokens, completion_tokens, total_tokens, model, ts, duration_ms, error`. NO cache fields.
- `~/AppData/Local/hermes/sessions/session_*.json` — 1,254 files, message transcripts only. Recursive walk for `total_tokens` → 0 matches.
- No `cache_control` markers anywhere in the Hermes install (grep) → Muse Spark requests never set cache breakpoints → provider cache never exercised → effective 0% hit rate, full input price paid.

## Sum command (cron audit)
```bash
python3 - <<'PY'
import json
p=c=t=n=0
for line in open('cron/usage_audit.jsonl'):
    line=line.strip()
    if not line: continue
    d=json.loads(line); n+=1
    p+=d.get('prompt_tokens') or 0
    c+=d.get('completion_tokens') or 0
    t+=d.get('total_tokens') or 0
print('records',n,'prompt',p,'completion',c,'total',t)
PY
```

## Conclusion
- All-time Hermes tokens are NOT reconstructable from local files. Source of truth = provider billing console.
- Cache hit rate for muse-spark is unmeasurable locally (no breakpoints + logs drop cache fields). To measure: enable one `cache_control` breakpoint on system prefix + capture `cache_read_tokens`/`cache_creation_input_tokens` in the usage hook.

## Muse Spark 1.2 facts (commandcode)
- Default Hermes model (`config.yaml: default_model: meta/muse-spark-1.2-contributor`).
- 1M context, reasoning-capable, Meta model. Cached input billed $0.002/M (vs $0.10/M uncached) — caching matters economically.
