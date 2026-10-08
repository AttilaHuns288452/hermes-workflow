---
name: timezone-date-keys
description: Use when computing date keys or debugging windowed flakes.
---

# Timezone-safe date keys

A date key is a calendar date string ('YYYY-MM-DD') used as identity: today's
default, a seed's day offset, a per-day filter, a booking day. Mixing UTC and
local derivations of it produces failures that appear only during part of the
day and read as flaky tests.

## Rule 1: one local primitive for every date key

All local-calendar date keys in a codebase come from ONE helper:

```js
// dateKey(date) -> 'YYYY-MM-DD' from LOCAL calendar getters
const d = date ?? new Date()
const mm = String(d.getMonth() + 1).padStart(2, '0')
const dd = String(d.getDate()).padStart(2, '0')
return `${d.getFullYear()}-${mm}-${dd}`
```

Never compute a date key inline at a call site.

Why this shape: `new Date().toISOString().slice(0,10)` is the UTC date of the
instant. In any timezone ahead of UTC (e.g. UTC+8) it returns YESTERDAY between
local 00:00 and the offset (08:00 in UTC+8). One inline idiom poisons every
default, every `today+N` seed, and every day filter at once during that window
— seeded rows land a day early, defaults show yesterday, per-day capacity
rules misfire. The failure rate equals the window's fraction of the day, so it
reads as "intermittent".

## Procedure

1. Find every date-key site before changing anything: grep for `toISOString().slice(0,10)`, ad-hoc `toLocaleDateString` formats, and hand-built 'today' strings. Seeds, form defaults, list filters, and UI 'today' labels all count.
2. Put `dateKey()` where the date domain lives (a date/availability lib), not in a UI file.
3. Swap every site to the helper in ONE pass. Mixed idioms reproduce the bug in miniature: a UTC key in the seed and a local key in the UI still disagree during the window.
4. Date-key arithmetic (add N days) needs an anchor that survives the key round-trip: derive the next key from the key (parse as a calendar date, add days, re-format) or anchor at midday UTC before slicing. Midnight-anchored local Dates drift the key across DST and offset boundaries. Keep the anchor explicit, commented with WHY.
5. Barrel wiring: `export { dateKey } from './dates'` re-exports WITHOUT creating a local binding in the barrel. A module that both re-exports and uses the helper must also import it — the missing binding is a runtime ReferenceError far from the mistake, not a build error.
6. Do not "fix" helpers that intentionally convert a key to an instant (a booking's open timestamp): 'YYYY-MM-DD' to Date needs a deliberate time-of-day anchor (often noon UTC); local midnight is usually NOT what the caller wants there.

## QA and diagnosis

- A failure confined to a wall-clock window (green by day, red on after-midnight runs; a "flake" with a stable rate) is a date-identity bug until proven otherwise. Check test-side AND app-side 'today' computation for UTC keys BEFORE blaming fixtures, timing, or the product.
- Make the window reproducible on demand: run with TZ forced to the app's timezone (`TZ=Asia/Manila node ...`) or with the clock set inside the failure window. Fix the primitive, not the one assertion that caught it.
- Leave one runnable check behind the primitive: a unit test asserting the key at 00:01 and 23:59 local in a fixed TZ (TZ env or injected clock) — the boundary is the entire bug.
- Fixture rules for run-day and relative seed data (create your own 'today' state; derive expectations from seed offsets) live in `qa-suite-engineering`.

## Pitfalls

- The test runner's TZ differs from both the app's timezone and the developer's: a suite can pass in CI (UTC) and fail locally, or vice versa. Pin TZ in the suite's run command wherever date keys matter.
- Date-only strings are ambiguous input: `new Date('2026-10-07')` parses as UTC midnight while `new Date(2026, 9, 7)` is local — parsing a key with the wrong form shifts it back through the offset. Parse keys with explicit component constructors or a pure-key parser.
- A wrong idiom in a UI default (a form's initial date) is invisible until someone looks during the window; a QA assertion on it flakes at the same rate. Trust window-shaped flakiness as a detection signal even when no user has complained.
