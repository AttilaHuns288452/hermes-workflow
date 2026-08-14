# Cashy explainability wave (2026-08-11)

P1 "explainable Cashy" workstream — landed in `src/features/ai/components/AIAssistant.tsx` (subagent-owned file; orb className line ~585 owned by a sibling agent — never touch).

## What shipped

1. **Live stats: already existed — no server change.** `getCashyContext()` (`src/features/ai/actions.ts`) already returns month income/expenses/net + top-5 spending lines, injected via `ensureContext()` before every send. Lesson: read the existing action before building the brief's assumed gap.
2. **Source footnotes:** `splitSource(content)` → `{ body, source }` — a trailing line matching `/^\*{0,2}Source:/` (after `trimStart()`) is split off and rendered as a footnote under the bubble (`mt-1.5 flex items-center gap-1 text-[10px] text-accent-bright` + `<Info size={10}/>`). Applied to ALL assistant bubble kinds; user bubbles untouched.
3. **Action chips:** under `insight`/`data` bubbles: `Log expense` → `/transactions?add=1`, `View transactions` → `/transactions`; class `inline-flex items-center gap-1 rounded-full border border-white/15 px-2.5 py-1 text-[11px] text-white/80 transition hover:bg-white/10 hover:text-white`. Chips are `<a href>` so the dialog's focus trap (`button, input, [href], ...`) covers them for free.

## Regex traps (both bit in this one parser)

- `/^\*\*?Source:/` = literal star + OPTIONAL star → **requires ≥1 star**; plain `Source:` never matches. Optional repeated literal char → use `{0,N}`: `/^\*{0,2}Source:/`.
- `**Source:** text` wraps only the LABEL, not the line — stripping line ends does nothing. Strip the label itself: `.replace(/^\*{1,2}Source:\*{1,2}/, 'Source:')`, and `.trim()` the captured line first (indented ` Source:` lines).
- `i <= 0` (not found, or `Source:` is the FIRST line) → return content unchanged; a first-line `**Source:**` is body, not footnote.

## Verification (final implementation + case table)

```js
const splitSource = (content) => {
  const lines = content.split('\n')
  const i = lines.findIndex((l) => /^\*{0,2}Source:/.test(l.trimStart()))
  if (i <= 0) return { body: content }
  return {
    body: lines.slice(0, i).join('\n').trim(),
    source: lines.slice(i).join('\n').trim().replace(/^\*{1,2}Source:\*{1,2}/, 'Source:'),
  }
}
// input → body, source
// 'Great month.\nSource: Transactions, Aug 2026'           → 'Great month.', 'Source: Transactions, Aug 2026'
// 'Great month.\n**Source:** Transactions, Aug 2026'       → 'Great month.', 'Source: Transactions, Aug 2026'
// 'No source here'                                         → unchanged, undefined
// '**Source:** first line only'                            → unchanged (first line is body)
// 'a\nb\n Source: x\nSource: y'                            → 'a\nb', 'Source: x\nSource: y'
// 'Great month.\n*Source:* Transactions'                   → 'Great month.', 'Source: Transactions'
```

Run this as a `node -e` case table BEFORE tsc — both regex bugs were caught there, not by tsc (tsc won't flag a wrong-but-typed regex).

## Pitfall: `&&`-chained verification

`node -e '...' && npx tsc --noEmit; echo "TSC_EXIT=$?"` — if the node check fails, `&&` skips tsc entirely and the echo prints the NODE exit code, masquerading as a tsc failure. Run tsc as its own call, or `;`-separate and echo each step's code.

## Status note

`/api/ai/chat/route.ts` SYSTEM_PROMPT does not instruct the model to emit `Source:` lines yet — footnote rendering is inert until a prompt tweak lands (out of component scope, prompt is server-owned). Chips' `?add=1` opens the expense dialog by default (matches QuickFAB behavior; `?add=1&type=income` preselects income).
