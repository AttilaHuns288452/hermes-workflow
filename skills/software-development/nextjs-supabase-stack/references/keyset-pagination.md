# Keyset (cursor) pagination — worked pattern (CashFlow OS transactions list)

Validated in a production edit session (Next.js 16 + Supabase, TS strict, `tsc --noEmit` clean).
Goal: cursor pagination on `(date, id) DESC`, limit 50, Load-more button with append
semantics, reset on filter change, delete still works after pages load. Ownership
constraint: only `src/features/transactions/` editable — `src/app/calendar/page.tsx`
calls `getTransactions` and could NOT be touched.

## Server action: overload to preserve legacy callers

```ts
export type TxFilters = { startDate?: string; endDate?: string; categoryId?: string; search?: string }
export type TxCursor = { date: string; id: string }
export type TxPage = { items: any[]; nextCursor: TxCursor | null }

const PAGE_SIZE = 50
const MAX_PAGE_SIZE = 200

// legacy callers (calendar page, page-stats action) get the plain array;
// pass cursor (null = first page) to opt into keyset pagination
export async function getTransactions(filters?: TxFilters): Promise<any[]>
export async function getTransactions(
  filters: TxFilters | undefined,
  cursor: TxCursor | null,
  limit?: number
): Promise<TxPage>
export async function getTransactions(
  filters?: TxFilters,
  cursor?: TxCursor | null,
  limit?: number
): Promise<any[] | TxPage> {
  const entity = await getEntity()
  if ("error" in entity) return cursor === undefined ? [] : { items: [], nextCursor: null }
  const { supabase, entityId } = entity

  let query = supabase.from("transactions").select("*, categories(name, type)").eq("entity_id", entityId)

  const size = Math.min(Math.max(limit ?? PAGE_SIZE, 1), MAX_PAGE_SIZE)

  if (cursor === undefined) {
    // legacy path: full list, created_at tiebreak (unchanged for existing callers)
    query = query.order("date", { ascending: false }).order("created_at", { ascending: false })
  } else {
    // fetch one extra row to know whether a next page exists
    query = query.order("date", { ascending: false }).order("id", { ascending: false }).limit(size + 1)
    if (cursor) {
      query = query.or(`date.lt.${cursor.date},and(date.eq.${cursor.date},id.lt.${cursor.id})`)
    }
  }

  if (filters?.startDate) query = query.gte("date", filters.startDate)
  if (filters?.endDate) query = query.lte("date", filters.endDate)
  if (filters?.categoryId) query = query.eq("category_id", filters.categoryId)
  if (filters?.search) query = query.ilike("description", `%${filters.search}%`)

  const { data, error } = await query
  if (error) return cursor === undefined ? [] : { items: [], nextCursor: null }

  if (cursor === undefined) return data
  const hasMore = data.length > size
  const items = hasMore ? data.slice(0, size) : data
  const last = items[items.length - 1]
  return { items, nextCursor: hasMore && last ? { date: last.date, id: last.id } : null }
}
```

## Why each piece is the way it is

- **`.or()` with nested `and()`** — the keyset predicate `(date, id) < (cursor.date, cursor.id)`
  is `date < X OR (date = X AND id < Y)`. PostgREST expresses this ONLY as
  `or(date.lt.X,and(date.eq.X,id.lt.Y))`. `date.lt.X` alone drops every same-date row.
  Safe for ISO dates and UUIDs (no commas/parens in values); escape values if they could
  contain those.
- **ORDER BY mirrors the keyset columns.** Tiebreaker `id` is mandatory — `date` alone has
  ties (many txns share a day) and rows would be skipped or duplicated across pages.
  Legacy path keeps its own `created_at` tiebreak so untouched callers see no ordering change.
- **limit + 1** detects `hasMore`; `nextCursor = last row's (date, id)` or `null`.
- **Overloads, not a union-only signature.** `getTxPage` (stats, needs ALL rows) and the
  calendar page keep calling with filters only → still get `Row[]`. The list passes
  `cursor = null` for page 1. Errors return whichever shape the caller opted into, so the
  client can always destructure `page.items`.
- **Gotcha:** `Awaited<ReturnType<typeof getTransactions>>` resolves to the LAST overload
  (`TxPage`), so component row types change from `[number]` to `["items"][number]`.

## Client component (TransactionList)

```tsx
const [transactions, setTransactions] = useState<Transaction[]>([])
const [nextCursor, setNextCursor] = useState<TxCursor | null>(null)
const [loadingMore, setLoadingMore] = useState(false)

// reset happens for free: the existing filters-change effect calls fetchData,
// which overwrites BOTH items and nextCursor (page 1)
const fetchData = async () => {
  setLoading(true)
  const page = await getTransactions(filters, null)
  setTransactions(page.items)
  setNextCursor(page.nextCursor)
  setLoading(false)
}

// stale in-flight load-more guard: filters changed while the fetch was in flight → drop it
const filtersRef = useRef(filters)
filtersRef.current = filters
const loadMore = async () => {
  if (!nextCursor || loadingMore) return
  const f = filtersRef.current
  setLoadingMore(true)
  const page = await getTransactions(f, nextCursor)
  if (filtersRef.current !== f) { setLoadingMore(false); return }
  setTransactions(prev => [...prev, ...page.items])
  setNextCursor(page.nextCursor)
  setLoadingMore(false)
}

// delete: filter locally (list + the stats copy). Keyset cursor is positional, so it
// stays valid — no refetch, loaded pages survive. Only refetch if you must revalidate.
const handleDelete = async (id: string) => {
  await deleteTransaction(id)
  setTransactions(prev => prev.filter(t => t.id !== id))
  setAllTxns(prev => prev.filter(t => t.id !== id))
}
```

Button: `{nextCursor && <Button variant="outline" onClick={loadMore} disabled={loadingMore}>{loadingMore ? "Loading..." : "Load more"}</Button>}`.

Edge cases accepted (documented with `ponytail:` comments in the real code):
- Filter reset + load-more race → guarded by `filtersRef` compare.
- Delete racing an in-flight load-more could re-append a deleted row — negligible, self-heals on next filter change.
- No test runner in repo → keyset string + overload behavior verified by `npx tsc --noEmit` only.
