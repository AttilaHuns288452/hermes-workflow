---
name: keyword-intent-matching
description: Use when classifying user text with keyword/regex rules.
---

# Keyword Intent Matching

Procedure for keyword/regex-based text routing (intent routers, topic tags, command matchers, topic chips) that does not silently misfire on substring traps. The core failure mode: a bad alternative is SILENT — it just never fires or over-fires — so the bug looks like a missing feature or a wrong tag, never like an error.

## Procedure

1. **Write the vocabulary table first:** keyword/alias list per intent, plus a trap battery — real strings that contain a keyword as substring or vice versa ("shortest" traps a `shor` prefix; "mainstream" traps `stream`; "constantly" traps `stant`). Order the table specific/long phrases BEFORE short general verbs: first-match-wins routing must hit "more simply" / "step by step" before the generic "explain".
2. **Decide match semantics per term before writing the regex:** whole-word vs prefix. Stem families ("stream"/"streaming") need explicit variants under whole-word semantics; prefix semantics must NOT carry a trailing `\b`.
3. **Escape literal non-word tokens** before insertion: `A\*`, `C\+\+`, `#include`, `.NET`.
4. **Compile and probe with a script** (`node -e` / `python3 -c`) running the REAL matcher over the vocabulary + trap battery, printing what each string routes to. Never verify intent regexes by reading them.
5. **Re-probe through the real entry point** (handler/HTTP call) once wired — surrounding scoring, ordering, or a catch-all above your pattern can change outcomes that the unit probe showed correct.

## Boundary mechanics (regex)

- `\b` exists only at a `\w`↔non-`\w` transition. `\b` placed AFTER `*`, `+`, `.`, `)`, `"`, or a space in the pattern can never match (both adjacent characters are non-word), so that alternative silently dies. Use a lookahead (`(?=\s|$|[.,!?])`) or drop the boundary.
- `\b` after an alternative turns a prefix into a whole word: `stream\b` misses "streaming". If you meant prefix semantics, omit the trailing boundary.
- Alternation is first-match-wins left to right: put the longest/most-specific alternative first.
- Match case-insensitively (`i` flag or lowercase both sides); mixed-case user input is the norm.

## Pitfalls

- The silent-failure shape above means the probe battery (procedure step 4) is the ONLY detection; adding more keywords without re-running it re-opens every earlier trap.
- When several intents match, the tie-break must be explicit (specific-before-general ordering, then score). Relying on object/array declaration order makes routing silently change when a new intent is appended.
- Negation and scope guards ("not X", "don't", "instead of") need their own early-check pattern — keyword hits inside negated sentences fire otherwise.
- Keyword anchors rendered into UI chips must use the same escaping as the matcher's literals, or the chip displays the pattern instead of the term (a chip labeled `A\*` instead of `A*`) — check chip labels in the UI, not just routing.
