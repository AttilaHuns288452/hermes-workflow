# useSyncExternalStore SSR crash ("Missing getServerSnapshot")

## Symptom
Hand-rolled store (module-level subscribe pattern — e.g. a toast system) wired into a provider
component crashes **prerendering of ANY static page** during `npm run build`:

```
Error occurred prerendering page "/about".
Error: Missing getServerSnapshot, which is required for server-rendered content.
```

`npx tsc --noEmit` does NOT catch it. Only a full build / prerender does.

## Root cause
The provider renders on the server during prerender of static routes. `useSyncExternalStore`
takes a third argument — the server snapshot — and crashes without it.

## Fix
```tsx
function getServerSnapshot() { return [] }   // stable empty initial state

const items = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)
```

## Pitfalls
- getServerSnapshot must return a STABLE value (empty array / initial state), never the live
  module store — the store is shared across requests and would leak one request's state into
  the next server render.
- Hydration: server snapshot must match the client's first render, or you trade this crash
  for a React #310 text-mismatch.
- This pattern ships inside the provider component; every page under the provider gets
  covered — one static route failing the build means the provider is rendered on all of them.

## Real case (2026-08-04, CashFlow OS)
Parallel-sprint subagent shipped a hand-rolled `ToastProvider` using
`useSyncExternalStore(subscribe, getSnapshot)` — two args. Build failed on `/about`
prerender. Fix: added `getServerSnapshot() { return [] }` (5 lines). tsc was clean the
whole time; only `npm run build` surfaced it. Lesson: after wiring ANY
`useSyncExternalStore` provider, run the full build before merging.
