# Harvesting Source Content from Discord

Depth for template-filling step 1 when the source is a Discord channel
(read via the Hermes bot token from `~/.hermes/.env`).

## Forum channels keep messages in threads

A forum channel (type 15) GETs `[]` on `/channels/{id}/messages` even
with full permissions — its content lives in threads. Fetch:

1. `GET /channels/{id}/threads/archived/public?limit=100`
2. `GET /guilds/{guild_id}/threads/active` and filter
   `parent_id == channel id` — the active-threads endpoint is
   GUILD-level; `/channels/{id}/threads/active` returns 404.
3. `GET /channels/{thread_id}/messages?limit=100&before=<id>` per
   thread, paginating until empty; then reverse for chronological
   order.

Get `guild_id` from `GET /channels/{id}`. Persist the raw JSON dump to
the workspace before summarizing, so progress survives retries.

## Transport

Use curl with `Authorization: Bot <token>`. Plain urllib gets
Cloudflare-blocked (403) without a browser-like User-Agent — same class
of UA filtering as other APIs.

## Completeness check

Channel `last_message_id` should be accounted for by one of the fetched
threads — if the newest thread id is not in your set, you are missing
active threads and must query the guild-level endpoint before
concluding the harvest is complete.
