---
title: Next.js Hydration Fixes
name: nextjs-hydration
description: Fix SSR/hydration errors in Next.js apps — React error #310, client/server mismatch, dynamic content, browser-only APIs
---

# Next.js Hydration Fixes

## When to use
- User reports "This page couldn't load" on a Next.js site
- Error #310 (Minified React error #310) — "Text content did not match" OR "Rendered more hooks than during the previous render"
- Blank page or white screen after React hydration
- "404: This page could not be found" on a valid route (component crashed during SSR or hook-count crash)
- Quiz, form, or interactive component crashes when user clicks/interacts (hook-count variant)

## Root Cause

React error #310 covers TWO distinct problems depending on the underlying message. Always check the full message via an error boundary to know which one you're dealing with.

### Type 1: Hydration Mismatch ("Text content did not match")

Next.js pre-renders `"use client"` components on the server. If the server-rendered HTML differs from the client-rendered version, React throws #310 and stops. Common causes:

| Cause | Example |
|-------|---------|
| **Math.random()** | Sakura petals, random initial state, animation delays |
| **Browser-only APIs** | `window.AudioContext`, `localStorage`, `document` access |
| **Date/Time** | `new Date()`, `Date.now()` in render |
| **Network-dependent** | Fetched data that varies per request |
| **3rd-party scripts** | AdSense, analytics injecting different content |

### Type 2: Hook Count Mismatch ("Rendered more hooks than during the previous render")

A `useState`, `useEffect`, or other hook placed AFTER an early `return` statement. React tracks hooks by call ORDER and count. If render A calls 11 hooks and render B calls 12 hooks (because an early return was bypassed), React throws #310.

**Common cause:** A `useEffect` or `useState` line below an `if (condition) return <SomeUI />` block. When `condition` flips from true→false, the hooks below the return run for the first time, increasing the count.

**Fix:** Move ALL hooks before ANY early return. Never place hook calls after conditional JSX returns within the same component.

```tsx
// BAD: useEffect after early return ← hooks count changes between renders
export default function Quiz() {
  const [gender, setGender] = useState<Gender | null>(null);
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);

  if (!mounted) return null;
  if (!gender) return <GenderSelector />;   // ← returns here on render 2 (11 hooks)
                                              //   skips the useEffect below
  useEffect(() => { ... }, []);               // ← hook #12 — NEVER called on render 2!
  if (result && showResult) return <Result />;
  return <QuizQuestions />;                    // ← render 3 reaches here (12 hooks)
                                               //   React sees 11→12 → ERROR #310
}

// GOOD: all hooks before any conditional return
export default function Quiz() {
  const [gender, setGender] = useState<Gender | null>(null);
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);
  useEffect(() => { ... }, []);                // ← hook #12 — always called, even if !gender

  if (!mounted) return null;
  if (!gender) return <GenderSelector />;      // ← render 2 returns here (12 hooks)
  if (result && showResult) return <Result />; // ← render 3 same 12 hooks
  return <QuizQuestions />;
}
```

**Symptoms:** Clicking a button (e.g. gender select) wipes the entire page and shows "This page couldn't load". The page works initially but crashes on first interaction. The bug appears identically in `output: "export"` static builds AND SSR builds because it's a runtime hook-ordering issue, not a hydration issue.

### Type 3: Invalid DOM nesting ("In HTML, <div> cannot be a descendant of <p>")

Not error #310, but a hydration-fatal DOM structure error. Common in swarm-built card components: `<Badge>` (renders a `<div>`) placed inside `<p className="font-medium">{name}<Badge/></p>`. `<p>` may only contain phrasing content.

- Console (dev): `In HTML, %s cannot be a descendant of <%s>... This will cause a hydration error` — and the **Next.js dev error overlay opens** (a `[role="dialog"]` with `data-nextjs-dialog-sizer`; shows as a red "N Issues" badge in screenshots).
- **The overlay also blocks Playwright clicks** on the page behind it ("locator resolved to `<button>`" but never actionable) — a side effect that wastes E2E debugging time.
- Prod: the mismatch hits the app error boundary ("Something went wrong").
- **Fix:** wrap name + badges in a block container: `<div className="flex flex-wrap items-center gap-2"><p className="font-medium">{name}</p><Badge …/></div>`.
- **Hunt:** grep new/rewritten card components for `<Badge` (or any `<div>`-rendering child) nested inside a `<p>` before E2E; catch it live with `p.on("console", …)` error listener in Playwright.

**Detection via error boundary:** Add `app/error.tsx` that displays `error.message`:
```tsx
"use client";
export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return <div><h1>Error</h1><p>{error.message}</p>
    <button onClick={reset}>Try Again</button></div>;
}
```
The message will read: *"Minified React error #310; visit https://react.dev/errors/310 for the full message or use the non-minified dev environment..."* — clicking the URL confirms hook-count vs hydration. Without an error boundary, Next.js shows the generic "This page couldn't load" error page.

**Detection via browser console (faster):** After reproducing the crash:
```js
document.body.innerHTML.includes('could not load')  // true = Next.js error boundary triggered
document.querySelector('main')                       // null = main element vanished → React crash
document.body.innerHTML.length                       // 0 = catastrophic unmount
```

**Fix hierarchy for hook-count mismatch:**
1. **PRIMARY: Move hooks before all early returns** — Identify any `useState`/`useEffect`/`useMemo`/`useCallback` placed AFTER an `if (...) return <JSX />` block. Move them above ALL conditional returns. This ensures the same number of hooks on every render.
2. **ALTERNATIVE: `dynamic(() => import(...), { ssr: false })`** — Wrap the entire component in a loader that skips SSR. Works but adds a bundle-split point and loading flash. Prefer option 1.
3. **LAST RESORT: Restore `output: "export"`** — If the component is deeply entangled with conditional hooks and cannot be refactored easily, switch to static export. This doesn't fix the hook issue but may mask it in some cases (the SSR pass is eliminated entirely).

## 🔧 Fix: `next/dynamic` with `ssr: false`

Create a loader wrapper that uses `dynamic` import with SSR disabled:

```tsx
// app/QuizLoader.tsx
"use client";

import dynamic from "next/dynamic";

const Quiz = dynamic(() => import("./services/AnimeQuiz"), {
  ssr: false,
  loading: () => <div>Loading...</div>,
});

export default function QuizLoader() {
  return <Quiz />;
}
```

```tsx
// app/page.tsx
import QuizLoader from "./QuizLoader";

export default function Home() {
  return <QuizLoader />;
}
```

**How it works:**
- Server renders only the `loading` spinner (deterministic → no mismatch)
- Client hydrates the spinner (always matches)
- After mount, the real component loads dynamically and replaces the spinner
- **100% eliminates hydration errors** regardless of what the child component does

## 🩹 Partial Fix: `suppressHydrationWarning`

For minor random content (like animated positions), add to the parent element:

```tsx
<div className="container" suppressHydrationWarning>
  {petals.map(/* random positions inside won't trigger error */)}
</div>
```

This suppresses hydration comparison for the entire subtree. Use when:
- Only visual decorations (positions, sizes, delays)
- Content doesn't affect layout or user interaction
- Can't use `ssr: false` for architecture reasons

## 🚨 Detection
1. **Curl the live page** — `curl -sL site.com | grep -o '404\\|_not-found'` — if present, component crashed during SSR
2. **Check for hydration markers** — `curl -sL site.com | grep -o 'BAILOUT_TO_CLIENT_SIDE_RENDERING'` — confirms client-side rendering
3. **Page content check** — `curl -sL site.com/quiz | grep -c "Find Your Waifu"` — if 0, the static export didn't include the gender selection content (expected for `"use client"` mount-guard patterns)
4. **Verify Vercel deployment status** — `curl -sI site.com | grep "X-Vercel-Cache"` — HIT means you're seeing a cached version. Use `--token` CLI deploy if auto-deploy isn't working.
5. **Vercel build log indicator** — check the build output for `○ (Static)` vs `λ (Dynamic)` — all pages should be `○` for static export

## 📦 Fix Checklist
- [ ] Create loader wrapper with `dynamic(() => import(...), { ssr: false })`
- [ ] Update `app/page.tsx` to use loader instead of component directly
- [ ] Build: `npm run build` (verify all routes listed)
- [ ] Deploy: push to GitHub → verify Vercel build completes
- [ ] Verify: `curl -sL site.com | grep -o 'expected-text'` returns content

## Pitfalls
- `vercel.json` with `"framework": "nextjs"` may fix auto-deploy issues
- Vercel CLI may have stale token — run `vercel login` to refresh
- Multiple `package-lock.json` files cause Turbopack to pick wrong workspace root — delete extras
- Windows path issue: tool may resolve `/c/Users/...` as `C:\c\Users\...` — use native `C:\Users\...` or terminal sed instead
