# Fixed prompt cost and state.db

How to measure what the agent pays on every API call, and how to compact the session store without
losing data. Both are "keep the instance lean" work; do the measurement before proposing a cut.

## Measure the always-on blocks

Four blocks are injected every turn, and every `delegate_task` child inherits the same ones:

| Block | Source |
|---|---|
| Memory | `~/.hermes/memories/MEMORY.md` |
| Skill catalog | `build_skills_system_prompt()` (agent.prompt_builder) |
| Operating contract | `~/.hermes/SOUL.md` |
| User model | `~/.hermes/memories/USER.md` |

```
python3 -c "import sys;sys.path.insert(0,'<hermes-agent>');from agent.prompt_builder import build_skills_system_prompt;print(len(build_skills_system_prompt()))"
wc -c ~/.hermes/memories/MEMORY.md ~/.hermes/memories/USER.md ~/.hermes/SOUL.md
```

`chars / 4` is a good token estimate. Report the total AND the per-block split, because the lever
is almost always the biggest block.

## What actually moves the number

- **Memory is usually the largest lever.** Keep environment facts, standing preferences, recurring
  pitfalls and integration recipes; drop completed-project narration, which `session_search` can
  recover. Compress oversized entries to their load-bearing facts instead of deleting the topic.
- Entries are `§`-separated — parse on that, not on blank lines. Archive before writing: plain copy,
  `.gz`, and a `.bak` beside the live file, then assert key facts still match after the rewrite.
- One pass of 20-30% is safer than a maximal cut, and it is measurable. A second pass later beats a
  single aggressive edit that nobody can review.
- **The skill catalog is mostly irreducible.** Each row is the name plus at most 60 description
  chars. Before pruning a category, count real loads per category from `state.db`; a few core
  categories carry most of the usage, and the long tail is the capability the user installed on
  purpose. Deleting it to save ~2K tokens is a bad trade — say so instead of doing it.
- **SOUL and USER are behavioural contracts, not padding.** Do not trim them to chase tokens.
- **Deferred tool listing is capped** (`build_catalog_listing_with_form(..., max_tokens=4000)`), so
  the number of MCP tools does not scale the prompt linearly. Prune redundant MCP servers for
  connect time and clutter — duplicate capability, or a credential this profile does not hold — and
  describe that honestly instead of claiming token savings.
- `skills.auto_load` pins full skill bodies into every session. Never use it for a domain skill just
  to make it fire; use a 60-char trigger description plus a pointer from the skill that loads first.

## `state.db` anatomy

```
sqlite3 -readonly ~/.hermes/state.db \
  "select name, round(sum(pgsize)/1048576.0,1) mb from dbstat group by name order by mb desc limit 12;"
sqlite3 -readonly ~/.hermes/state.db "pragma page_count; pragma freelist_count; pragma page_size;"
```

Typical blocks: `messages` (tool outputs dominate the bytes), `state_meta`, the FTS tables
(`messages_fts_*`, `messages_fts_trigram_*`), and `system_prompts`.

**`freelist_count` is the only honest reclaim estimate.** A DB with a few hundred free pages is
holding real data, not bloat — do not promise a large shrink before measuring.

**`state_meta` carries retained turn results.** Keys shaped `gateway.admission.result.v1.<hash>`
are per-turn result blobs kept for client replay; they have no retention policy and grow at roughly
1-2 MB per turn. Deleting old ones costs replay of that turn, not the transcript. Safe prune keeps
the newest N by rowid (rowid order is insertion order, a proxy for recency, not a timestamp):

```sql
DELETE FROM state_meta
WHERE key LIKE 'gateway.admission.result.v1.%'
  AND rowid NOT IN (SELECT rowid FROM state_meta
                    WHERE key LIKE 'gateway.admission.result.v1.%'
                    ORDER BY rowid DESC LIMIT 300);
```

Never run that while a turn is in flight — those rows are the settlement record. Offline only.

## Offline optimize recipe

`hermes sessions optimize-storage` refuses while anything holds the DB, and the gateway is always a
holder.

1. `hermes gateway stop` **refuses** while sessions are live and prints them; only `--yes` interrupts
   them deliberately. A script that calls plain `stop` waits, aborts, and changes nothing — read the
   log's tail, not just the fact that the script ran.
2. Launch detached so the job survives the app it kills:
   `systemd-run --user --collect --unit=<name> --on-active=30s /bin/bash <script>`, and let the
   script sleep a grace period so the user can read the last message.
3. Script order: stop gateway (`--yes`) → wait for `fuser <db>` to go empty (abort and relaunch if it
   does not) → `sqlite3 <db> ".backup '<snapshot path>'"` (mandatory before VACUUM) → prune stale
   admission blobs → `hermes sessions optimize-storage --yes` → **`sqlite3 <db> "PRAGMA
   busy_timeout=5000; VACUUM;"`** → `pragma integrity_check` → relaunch `hermes desktop
   --skip-build` with `DISPLAY` set.
   The VACUUM is not optional: `optimize-storage` only rebuilds the search index and reports "already
   on the compact layout — nothing to do" while the pruned pages sit on the freelist. Without it the
   file size is byte-identical before and after, which reads like the job failed.
4. Verify from the log: size BEFORE/AFTER, `integrity_check: ok`, and session/message counts
   unchanged apart from the pruned rows. A maintenance job that reports only "ran" is not evidence.

## Pitfalls

- A projected reclaim that was not measured is a promise you cannot keep. Quote `freelist_count` and
  the block breakdown, not a round number.
- **`optimize-storage` does not compact the file.** It prints "Search index is already on the compact
  layout — nothing to do" and leaves every pruned page allocated; the first offline run reported a
  size delta of exactly zero after deleting ~135 MB of blobs. Check `freelist_count` after the prune
  (it jumps by the pruned pages) and VACUUM while the DB is still offline. Measured result when the
  step was added: 1.36 GB → 1.20 GB, freelist 0.
- Deleting admission blobs from a live gateway races in-flight settlement; prune only with zero holders, which means the offline step.
- Optimize output can look successful while the gateway stop silently refused: check the log for the
  `ABORT`/`Refusing to stop` lines before believing the numbers.
- Session pruning (`sessions.auto_prune`, retention days) and storage optimization are different
  operations; a retention window that has not expired removes nothing, no matter how big the file is.
