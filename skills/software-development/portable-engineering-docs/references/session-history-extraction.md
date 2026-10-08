# Extracting conversation history from the local session DB

Needed only when documentation must quote REAL historical prompts/messages
(development journal, decision history, evidence pack) rather than summarize
from memory. Semantic search first; raw DB when you need many complete texts.

## Surfaces

| Need | Tool |
|---|---|
| Find/summarize sessions by topic | `session_search(query=…, limit=…)` (FTS5 over the message store) |
| Full verbatim text of many messages | sqlite3 on `~/.hermes/state.db`, `messages` table (`id`, `session_id`, `role`, `content`, `timestamp`) |
| Session metadata (age, source, cost) | `hermes sessions list` CLI |

## Extraction recipe

```sql
-- one JSON object per row; content is JSON-escaped so multi-line is safe
select json_object('k', id, 'c', content)
from messages where role='user' and session_id='…' order by id;
```

Parse line-by-line with `json.loads`. For cross-session sweeps, filter on
`content like '%keyword%'` but GROUP BY session and preview the first message
per session to confirm relevance — keywords over-select (shared words across
projects, coaching chats, other deliverables).

## Rules

1. `role='user'` = prompts. Exclude system notes, context-compaction handoffs,
   and tool-traffic messages — they are conversation machinery, not prompts.
2. Redact before the extract leaves the working file: historical prompts carry
   pasted secrets (service-role keys, live payment keys, third-party API keys)
   inside innocuous-looking text. Patterns: `sb_secret_\S+`, `(sk|pk)_(live|test)_\S+`,
   generic `sk-\S+`, `eyJ[A-Za-z0-9_-]{20,}` JWTs. Replace in place with
   `[REDACTED SECRET]` / `[REDACTED KEY]` and scan the FINAL artifact again.
3. Verbatim means verbatim: original wording and typos preserved; editorial
   commentary labeled as editorial.
4. Cite the session id + timestamp as metadata where useful; omit or humanize
   internal ids the reader cannot act on.

## Pitfalls

- **sqlite3 CLI output line-splits multi-line content.** Piping rows and
  splitting stdout by newline truncates every message to its first line — the
  extract looks like a set of suspiciously tiny prompts and the loss is silent.
  Use per-row `json_object()` and parse JSON per line; `-separator` custom
  delimiters still break under line-splitting.
- Multi-megabyte extracts: write to a working file and index first (id, date,
  length, first-N-chars), then pull full text only for curated ids — reading
  everything at once floods context without improving selection.
