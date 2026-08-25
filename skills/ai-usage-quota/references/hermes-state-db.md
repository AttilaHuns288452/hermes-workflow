# Hermes state.db — the real Hermes token meter

Hermes desktop does **not** write to `opencode.db`. Its live meter is `state.db` table `session_model_usage`.

## Location
`C:\Users\Attila\AppData\Local\hermes\state.db` (also `sessions.db` is legacy; current is `state.db`)

## Schema
```sql
CREATE TABLE session_model_usage (
  session_id TEXT,
  model TEXT,
  billing_provider TEXT,   -- 'commandcode', 'opencode-go', 'auto', 'custom', 'local-ollama'
  billing_base_url TEXT,
  billing_mode TEXT,
  task TEXT,               -- 'title_generation', 'approval', '' for main
  api_call_count INTEGER,
  input_tokens INTEGER,
  output_tokens INTEGER,
  cache_read_tokens INTEGER,
  cache_write_tokens INTEGER,
  reasoning_tokens INTEGER,
  estimated_cost_usd REAL, -- always 0 for Hermes (shadow)
  actual_cost_usd REAL,
  first_seen REAL,         -- epoch seconds (float) — use this to filter by date
  last_seen REAL
);
PRIMARY KEY (session_id, model, billing_provider, billing_base_url, billing_mode, task)
```

## Today's query (2026-08-19 example)
```python
import sqlite3, datetime
DB=r'C:\Users\Attila\AppData\Local\hermes\state.db'
con=sqlite3.connect(DB)
today=datetime.date(2026,8,19)
rows=list(con.execute('SELECT model,billing_provider,api_call_count,input_tokens,output_tokens,cache_read_tokens,cache_write_tokens,reasoning_tokens,first_seen FROM session_model_usage'))
# filter by first_seen date
today_rows=[r for r in rows if r[8] and datetime.datetime.fromtimestamp(r[8]).date()==today]
# sum input/output/reason/cache_read per model
```

## Today's actual (2026-08-19)
- Total rows 70 across 48 sessions, 792 calls
- `input=12,985,324 output=535,185 cache_read=93,026,442 reasoning=166,224`
- Dominant: `meta/muse-spark-1.2-contributor::commandcode` 361 calls, 10.7M input

## Pitfalls
- `opencode.db` shows 0 today when running Hermes — different meter. Don't confuse them.
- `cache_read` is billed ~1% of input price — sum `input+output+reasoning` for billable, keep `cache_read` separate.
- `time_created` in opencode.db is **ms epoch**; `first_seen` in Hermes state.db is **seconds epoch (float)** — divide differently.
- `billing_provider` distinguishes `commandcode` (Hermes) vs `opencode-go` (OpenCode) — same model string can appear under both.
