# Client-component fix classes (ECC silent-failure + a11y + perf)

2026-08-05 sprint, TransactionList.tsx (758 lines). Recurring ECC finding classes on client
components and the fixes that passed review. Check these BEFORE shipping any feature component.

## Data-fetch hardening (CRITICAL class)

- Any `async` fetch without try/catch: network error → unhandled rejection AND `setLoading(true)`
  never reset → permanent "Loading..." screen. Canonical pattern:

```tsx
const fetchData = async () => {
  setLoading(true);
  const f = filters;                       // snapshot BEFORE await
  try {
    const page = await getTransactions(f, null);
    if (filtersRef.current !== f) return;  // stale-response guard (mirror loadMore)
    setTransactions(page.items);
    setNextCursor(page.nextCursor);
  } catch {
    setPageErr("Failed to load transactions");
  } finally {
    setLoading(false);                     // ALWAYS reset loading in finally
  }
};
```

- Put the stale-guard in the SHARED fetch function, not the effect: fetchData is called by the
  filters effect AND post-add/review/delete refreshes — one guard covers every call site
  (root-cause fix; an effect-only guard leaves sibling callers racy).
- `filtersRef.current = filters` in the RENDER body is a React anti-pattern (ref write during
  render). Move the sync into the filters effect; the effect's first run may skip the fetch but
  must still update the ref.
- Invalid input that silently `return`s: set the error state first
  (`setAddErr("Enter a valid amount")` before returning).

## Derived-data perf (recomputed per render/keystroke)

- Maps/Sets/filter+reduce built inline in the render body run on EVERY render, including each
  search keystroke. Wrap in useMemo:
  - `staffNameById` Map (deps: staffList)
  - month stats as ONE combined useMemo returning `{ income, expense, net, savingsRate }`
    (deps: allTxns, monthKey)
  - `allTags` Set+sort (deps: allTxns, transactions)
  - `txDate` Map: `format(parseISO(t.date), "MMM d, yyyy")` keyed by transaction id — the old
    code formatted the same date 3× per row per render (cell + delete aria-label + confirm text)
- `parseISO(t.date)` (date-fns) instead of `new Date(t.date)`: `YYYY-MM-DD` parses as UTC
  midnight → off-by-one display in non-UTC timezones. (Server-action side prefers
  `new Date(d + "T00:00:00")` — either avoids the UTC-midnight trap.)
- Month stats must exclude `pending` too, not just `rejected` (pending money double-counts).

## shadcn/Radix a11y specifics

- `SelectTrigger` spreads `...props` → `id`/`aria-label` pass through to the Radix button. A
  Label's `htmlFor` needs the matching `id` on the TRIGGER (the focusable element), not the
  Select root.
- This repo's `CardTitle` renders a plain `<div>` — no heading semantics. When `src/components/
  ui/**` is frozen (parallel-agent ownership), replace with a real
  `<h2 className="font-display text-lg font-bold">` in the component instead of CardTitle.
  Keep h1→h2→h3 order.
- `aria-live="polite"` on a whole action container (Approve/Reject row) makes screen readers
  announce everything inside it; move it onto the error span only. Use `role="alert"` for
  page-level/add-form errors.
- Contrast: `text-orange` (#ea580c) fails WCAG AA at 12px → local `text-[#c2410c]` on that
  badge only. Tradeoff vs the "no hardcoded hex" rule: acceptable when globals.css is frozen;
  flag it in the review notes.

## Touch targets + table polish

- Icon buttons (`size="icon"`) → `h-10 w-10`; dialog primary CTA → `h-11`; inline clear button
  `p-0.5` → `p-2`. Filter row `gap-3` → `gap-x-4 gap-y-3`; `whitespace-nowrap` on date/amount
  cells; `tracking-tight` on big stat numbers (tabular-nums already there).

## Patch-tool pitfalls on this host (CRLF + template literals)

- Repo files are CRLF: patch diffs show whole-line rewrites (line-ending normalization) —
  harmless, but read the diff for real content changes.
- EASY TO BREAK: converting a JSX className into a template literal via patch — keep the
  BACKTICKS (`className={`...`}`). One dropped backtick silently yields `className="...${...}"`
  and only tsc catches it. After multi-hunk patches, grep for leftover old patterns
  (`new Date(t.date)`, `CardTitle`) and run `npx tsc --noEmit`.
- search_files (ripgrep) can throw `IO error` on absolute Windows paths — fall back to
  `terminal` grep (same host quirk family as the TS6053 inline-lint false positive).
- Verification: subagent runs `npx tsc --noEmit` only (parent owns `npm run build` per sprint
  pipeline); here both passed.
