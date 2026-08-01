# Next.js Hydration Mismatch / React Production Crash — Reference

This document covers both hydration mismatch errors (debug/dev mode) and React production crashes ("This page couldn't load") on Vercel.

## Understanding the Two Error Surfaces

### Development / Debug mode — React Error #418 / #423

When a component's server-rendered HTML doesn't match client-side output, React logs to console:
```
Warning: Expected server HTML to contain a matching <div> in <div>.
```
or
```
Error: Hydration failed because the initial UI does not match what was rendered on the server.
```
Link: https://react.dev/errors/418 / https://react.dev/errors/423

**Build output has NO errors** — it's a pure runtime hydration issue that only shows in browser devtools.

### Production — "This page couldn't load" crash

When a React component **throws during rendering** (not hydration mismatch, but a genuine JS exception), Next.js's built-in error boundary catches it and replaces the ENTIRE page with:

```html
<div style="font-family: system-ui, ...; height: 100vh; display: flex; align-items: center; justify-content: center;">
  <h1>This page couldn't load</h1>
  <p>Reload to try again, or go back.</p>
</div>
```

**Detection:** After triggering the interaction, check:
```js
document.querySelector('main') !== null  // false = main element vanished
document.body.innerHTML.length            // may be ~14KB (error page HTML + scripts)
document.body.innerHTML.includes('could not load')  // true = Next.js error boundary
```

The error page has an empty `js_errors` message in browser_console but the error is real.

## The QuizLoader→AnimeQuiz Pattern (How It Breaks)

This application uses a double-nested client-only mount guard:
```
QuizLoader ("use client")
  → if !mounted → render spinner
  → if mounted → render AnimeQuiz
    
AnimeQuiz ("use client")
  → if !mounted → return null
  → if !gender → render gender selection
  → else → render quiz questions
```

Under SSR (without `output: "export"`):
1. Server renders QuizLoader → spinner (mounted=false)
2. Client hydrates QuizLoader → useEffect fires → mounted=true → AnimeQuiz renders
3. AnimeQuiz runs its first client render → `mounted` is false initially → returns null
4. On next tick, AnimeQuiz's useEffect fires → mounted=true → renders gender selection

The cascade of deferred renders creates timing issues with React 19's concurrent features. The component can throw during step 3 if it tries to access data that hasn't been initialized yet (e.g., accessing `QUESTIONS[currentQ]` while `currentQ` is 0 but `QUESTIONS` hasn't resolved).

**Fix:** Add `output: "export"` to next.config.ts. This eliminates SSR entirely — every page is pre-rendered as static HTML, and all client components mount fresh with no hydration constraints. This is the nuclear option but is correct for fully static sites.

## SSR Crash Signal via Curl

```bash
# Detect if the page crashed on the server (hydration never starts)
curl -sL "https://www.animewaifucompatibility.xyz/" | grep -o '_not-found'
# If found → the component crashed during SSR

# Detect bailout to client-side rendering
curl -sL "https://www.animewaifucompatibility.xyz/" | grep -o 'BAILOUT_TO_CLIENT_SIDE_RENDERING'
# If found → Next.js kicked it to the client; the client must complete hydration

# Detect static HTML size (small = likely just spinner/fallback)
curl -sL "https://www.animewaifucompatibility.xyz/" | wc -c
# ~15KB = spinner HTML + Flight data (client component not yet hydrated)
# ~15KB but with "could not load" = production error state

# Check if page has both the fallback AND error content
curl -sL "https://www.animewaifucompatibility.xyz/" | grep -c "Loading quiz\|could not load"
# 2 = both spinner and error content (page crashed after SSR rendered fallback)
```

## Vercel Deployment Debugging

### Fix not reflecting on live site
```bash
# Check Vercel cache hit vs miss
curl -sI https://www.animewaifucompatibility.xyz/ | grep X-Vercel-Cache
# HIT = cached old version, deploy may not have pushed

# Check if GitHub webhook exists (auto-deploy pipeline)
gh api repos/AttilaHuns288452/anime-waifu-quiz/hooks --jq '.[].config.url'
# Empty = no webhook = GitHub integration not set up

# Force redeploy
# Go to Vercel Dashboard → Deployments → last checkmark → "Redeploy"
```

### Common build-time errors
| Error | Cause | Fix |
|-------|-------|-----|
| `/vercel/path0/out/routes-manifest.json` not found | `outputDirectory: "out"` in vercel.json | Change to `outputDirectory: ".next"` |
| `BAILOUT_TO_CLIENT_SIDE_RENDERING` in HTML | Next.js detected client-only component | Normal for `"use client"` with `useEffect` - not an error |
| Turbopack build warning | Invalid config key like `turbopack: { root: process.cwd() }` | Remove the `turbopack` key if not using valid options |

## Quick Diagnosis Flowchart

```
Site loads but buttons/quiz don't work?
  ↓
Check browser console → js_errors present?
  → Yes → Check body.innerHTML for "could not load"
    → Found → React crashed during re-render → Keep/restore output:"export"
  → No → Check if main element exists after clicking
    → Vanished → Same: React crash → Keep/restore output:"export"
  
Site doesn't load at all (curl gets 404/500)?
  ↓
Check Vercel build logs
  → routes-manifest error → Fix outputDirectory in vercel.json
  → Other build error → Fix locally and push

Git push but site unchanged?
  ↓
Check GitHub webhooks → empty?
  → Reconnect Vercel Settings → Git → "Configure Git Provider"
  → Or manually redeploy from Vercel dashboard
```
