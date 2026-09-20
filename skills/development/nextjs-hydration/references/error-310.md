# React Error #310 Reference

Error #310 is a **shared error code** in React's minified production bundle for two completely different errors. Always get the full message via an error boundary to know which one you're debugging.

## Type A: Hydration Mismatch
**Message:** `"Text content did not match. Server: "..." Client: "...""`

**Cause:** The HTML rendered on the server differs from what React renders on the client during hydration. Math.random(), Date.now(), browser-only APIs, or network-dependent data in the render path.

**Detection:**
- Check curl output for the component's HTML: `curl -sL site.com/page | grep -o 'key-text'`
- If key text is missing → SSR rendered the fallback/loading state, not the actual component
- Error appears on page LOAD (before any user interaction)

**Fix:**
1. **Dynamic import with ssr:false** — `next/dynamic(() => import('./X'), { ssr: false })`
2. **Client-only mount** — Loader pattern with `useEffect` + `useState` (see SKILL.md)
3. **suppressHydrationWarning** — for decorative random content only
4. **Stable initial state** — `useState(items[0])` then randomize in useEffect

## Type B: Hook Count Mismatch
**Message:** `"Rendered more hooks than during the previous render."`

**Cause:** A hook call (useState, useEffect, etc.) is **placed after an early return** (`if (x) return <UI />`). When the condition flips, the hooks below the return execute for the first time, changing the total hook count.

**Detection:**
- Error appears on USER INTERACTION (clicking a button, selecting an option), not on initial page load
- Clicking causes the entire page to blank out and show "This page couldn't load"
- The error is identical in static export AND SSR builds
- Search the component for `useEffect` or `useState` lines that appear BELOW any `if (...)` or `return` statement

**Debugging technique:**
1. Add a simple `error.tsx` to the app directory
2. Let the error boundary catch the crash and display: `{error.message}`
3. The full message says either "Text content did not match" (hydration) or "Rendered more hooks than during the previous render" (hook count)
4. If hook count → trace every hook call in the component and verify they all execute before any conditional return

**Fix:**
Move ALL hook calls to the top of the component, before any `if`/`return` statement:

```tsx
// BEFORE (broken) — useEffect AFTER early return
export default function Quiz() {
  const [gender, setGender] = useState(null);
  useEffect(() => { setMounted(true); }, []);   // hooks 1-11
  if (!gender) return <GenderSelector />;        // ← early return, hooks below NOT called
  useEffect(() => { /* tsundere */ }, [...]);   // ← hook 12 — called only when !gender is false!
  return <QuizQuestions />;
}

// AFTER (fixed) — all hooks before returns
export default function Quiz() {
  const [gender, setGender] = useState(null);
  useEffect(() => { setMounted(true); }, []);
  useEffect(() => { /* tsundere */ }, [...]);   // ← hook 12 — always called
  if (!gender) return <GenderSelector />;        // ← same 12 hooks regardless of path
  return <QuizQuestions />;
}
```

## Checking if fix is deployed

```bash
# Check for fix-specific markers
curl -sL site.com | grep -o 'uniqueFixMarker'

# Check if component crashed (hydration OR hook-count)
curl -sL site.com | grep -o '404\|_not-found\|couldn.t load'
# If found → crash still happening in production
```

## Live reproduction test (hook count variant)

```js
// Paste in browser console on the production page
let btn = document.querySelector('button');
btn?.click();
setTimeout(() => {
  console.log('crash:', document.body.innerHTML.includes('couldn\'t load'));
  console.log('error visible:', document.body.innerHTML.includes('Error:'));
}, 2000);
```

If `crash` or `error visible` is true → the hook-count bug is live.
