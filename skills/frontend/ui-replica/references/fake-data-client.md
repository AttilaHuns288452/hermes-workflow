# Fake data-client contract (supabase-style)

One module stands in for the whole backend. Implement exactly the surface the source app's `lib/` actually calls (survey first), as a thenable builder returning `{ data, error }` envelopes:

## Query builder
- `from(table)` → builder supporting the chain shapes the app uses: `select(cols, opts)` (incl. `{ count: 'exact'|'head' }` and `head: true`), `insert(rows)`, `update(patch)`, `upsert(rows)`, `delete()`.
- Filters as chainables returning the builder: `.eq .neq .gt .gte .lt .lte .in .is .ilike .like`.
- Modifiers: `.order(col, { ascending }) .limit(n) .range(a, b) .single() .maybeSingle() .abortSignal()` (no-op is fine for the last).
- The builder itself must be awaitable/thenable resolving `{ data, error }`.

## Projection rules (the bug-prone part)
- Split `select` column lists at **paren depth 0** — `services(name, price)` embeds contain commas.
- Segment `*` inside a larger list (`select('*, services(name)')`) expands to all columns.
- Embedded relation segment `parent(cols)`: resolve via the FK column on the row (`row.service_id` → `services` table), attach projected child as `row.parent_name = {...}`.
- Respect `count` and `head` options; return row arrays (or a row object for `single/maybeSingle`) exactly as the real client does.

## Other surface (stub to shape only)
- `rpc(name, args)` → route to small in-memory implementations for the fns the app calls.
- `functions.invoke(name, { body })` → canned `{ data, error }` per function name.
- `auth`: `getSession/setSession/signOut/onAuthStateChange` — session stored in a localStorage key so the demo's role buttons can set it.
- `channel()/removeChannel()` → no-op objects (`on().subscribe()` shape) if the app wires realtime.
- `storage.from()` → throw a clear error if reached (demo data has no uploads), never crash silently.

## Schema truth
Read shapes from the source's own `seed.mjs` / `seed_map.mjs` / scheduling helpers, not from the pages. Seed rows must include every field any page reads (dates, times, prices, nested names, status enums) — placeholder copy in rendered cards means a missing field, not a UI bug.
