---
name: session-history-mining
description: Recover past prompts and transcripts from Hermes' sessions.
---

# Session History Mining

Bulk-recover what was actually said across past Hermes sessions — complete
transcripts, prompt histories, development journals — from the local message
store (`~/.hermes/state.db`). Use `session_search` to find needles; use this
workflow whenever the request needs the whole haystack ("my exact messages",
"everything I asked about X", "a dev journal from our sessions").

Session management (rename/archive/prune) lives in `session-librarian`.

## Procedure

1. **Locate the store**: `~/.hermes/state.db`, table `messages`
   (`id`, `session_id`, `role`, `content`, `tool_*`, `timestamp` unixepoch — there is
   no conversation_id; session_id is the grouping key). Read-only queries only.
2. **Triage before extracting**: one query grouping `role='user'` messages by
   `session_id` with `min(timestamp)`, count, and a ~100-char first-message preview.
   Classify each session by what it actually contains — keyword hits leak unrelated
   projects into every candidate list.
3. **Extract in JSON mode**: `select json_object('id',id,'ts',datetime(timestamp,
   'unixepoch','localtime'),'sid',session_id,'c',content) from messages …` — one JSON
   object per row, `json.loads` per line. Never parse sqlite's delimited output.
4. **Filter system machinery** by content prefix: drop `[CONTEXT COMPACTION`,
   `[IMPORTANT:`, `[System:`, `[System note:`, `[ASYNC DELEGATION`. Marker-wrapped
   out-of-band user messages carry real user text — extract the inner text.
5. **Dedupe replays**: compaction handoffs replay earlier user messages verbatim
   (same timestamp + content appear multiple times) — dedupe on (timestamp, content
   prefix) before counting anything.
6. **Redact before the extract leaves the working directory**: `sb_secret_\S+`,
   `(sk|pk)_(live|test)_\S+`, provider API keys, `eyJ…` JWTs → `[REDACTED …]`.
   The final artifact passes a regex scan for these patterns or it does not ship.
7. **Preserve verbatim**: exact wording, typos included. The user wants to SEE their
   exact messages — complete coverage, visible inline, not curated to highlights and
   not hidden behind collapsed sections. Pair each message with its timestamp +
   session id; that metadata is the traceability.
8. **Verify**: extracted count vs source count, spot-check exact strings against the
   artifact, secret scan clean.

## Pitfalls

- **Multi-line `content` corrupts line-based parsing** of sqlite output — the
  separator and newlines both appear inside messages. JSON mode (step 3) is the
  only safe extraction shape.
- **Keyword matching finds sessions, not relevance.** Always read previews and
  classify per session; the topic's history spans many sessions and shares words
  with unrelated ones.
- **Replay duplicates inflate "N messages recovered"** — dedupe before reporting
  counts, and re-verify the reported count against the deduped list.
- **Secrets sit in historical prompts** (people paste keys into chat). Redaction is
  a gate, not a cleanup: scan the final artifact and refuse to ship on any hit.
