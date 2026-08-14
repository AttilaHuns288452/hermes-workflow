# Hand-rolled toast system — module store + useSyncExternalStore (no deps)

Validated pattern from CashFlow OS (Next.js App Router + Tailwind v4, Aug 2026).
Replaces sonner/react-hot-toast when the constraint is "no new dependencies".

## Core shape

One file `src/components/ui/toast.tsx` (`'use client'`), no context at all:

```tsx
type ToastItem = { id: number; variant: 'default' | 'destructive'; title?: string; description?: string }

let toasts: ToastItem[] = []
let nextId = 1
const listeners = new Set<() => void>()

function emit() { for (const l of listeners) l() }

export function toast(opts: { title?: string; description?: string; variant?: 'default' | 'destructive' }) {
  const item: ToastItem = { id: nextId++, variant: opts.variant ?? 'default', title: opts.title, description: opts.description }
  toasts = [...toasts, item].slice(-4)   // max 4 — drop oldest
  emit()
  setTimeout(() => {                     // auto-dismiss ~3.5s
    toasts = toasts.filter((t) => t.id !== item.id)
    emit()
  }, 3500)
}

function subscribe(cb: () => void) { listeners.add(cb); return () => listeners.delete(cb) }
function getSnapshot() { return toasts }

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const items = useSyncExternalStore(subscribe, getSnapshot)
  return (
    <>
      {children}
      <div role="status" aria-live="polite" className="fixed right-4 bottom-24 z-[100] flex w-80 flex-col gap-2 md:bottom-4">
        {items.map((t) => (
          <div key={t.id} className="toast-in rounded-lg border bg-card p-3 shadow-sm">
            {t.title && <p className="text-sm font-medium">{t.title}</p>}
            {t.description && <p className="mt-0.5 text-sm text-muted-foreground">{t.description}</p>}
          </div>
        ))}
      </div>
    </>
  )
}

export function useToast() { return { toast } }  // module fn is stable — no memo needed
```

## The three tricks that make it work

1. **Immutable array replacement is the snapshot contract.** `useSyncExternalStore` re-renders
   only when `getSnapshot` returns a new reference. Never mutate `toasts` in place —
   always `toasts = [...toasts, item]` / `.filter(...)`. Module-level `[]` initial state
   also makes SSR/hydration consistent for free (empty on the server).
2. **No context.** The store is module-level; the provider is only a renderer. `useToast()`
   works even outside the provider tree, which makes testing trivial.
3. **Keyframes when you can't touch shared CSS** (e.g. `globals.css` is outside your file
   ownership in a parallel-agent task): inject them via a `<style>` tag inside the component:

```tsx
<style>{`@keyframes cf-toast-in{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}.toast-in{animation:cf-toast-in 180ms ease-out}`}</style>
```

Tailwind arbitrary `animate-[...]` won't work without keyframes existing somewhere —
the inline `<style>` is the self-contained escape hatch.

## Pitfalls

- **Never nest two providers of the same store** — each one renders its own stack, so a
  nested pair shows duplicate toasts. Wire providers into *mutually exclusive* layout
  branches instead (e.g. bare auth branch wraps its own, AppShell wraps app pages —
  `AuthShell` picks one branch per route, so exactly one provider is ever mounted).
- **Clear fixed FABs.** A bottom-right FAB (`fixed bottom-6 right-6 h-14`, mobile-only)
  collides with `bottom-4 right-4` toasts. Offset: `bottom-24 md:bottom-4` (~96px clears
  a 56px FAB at 24px).
- **Minimal-diff wrapping of an existing return:** wrap a large existing JSX return in a
  provider without re-indenting the inner block — `return (<ToastProvider>\n<div ...>` and
  close `</div>\n</ToastProvider>)`. JSX doesn't care about indent; the diff stays tiny.
- Dismiss-on-click was intentionally omitted (auto-dismiss covers it); add a close button
  only when users ask.
