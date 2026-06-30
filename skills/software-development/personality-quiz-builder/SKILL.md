---
name: personality-quiz-builder
description: "Build Akinator-like personality quizzes with character databases, archetype systems, multi-axis matching, and social sharing. Covers: archetype-driven character generation, 5-axis personality matching, AniList batch image fetching, quiz quiz flow, top-N results, share modals, and character libraries."
tags:
  - quiz
  - personality
  - matching
  - character-database
  - anime
platforms: [windows, linux, macos]
---

# Personality Quiz Builder

Build Akinator-style personality quiz sites: user answers questions → profile is matched against a character database → top-N ranked results displayed with share functionality.

## Architecture Overview

```
Questions (20+)
    ↓ User answers
Personality Profile (5-axis vector)
    ↓ Weighted Euclidean distance
Character Database (archetype-generated, N=300+)
    ↓ Sort by score
Top 10 Results + Character card + Share modal
```

## Components

### 1. Character Archetype System

Instead of hand-authoring every character, define **archetypes** with preset personality traits + description + match-reason templates:

```typescript
const ARCHETYPES = {
  gentle_flower: {
    traits: { e: -2, l: -2, v: -1, p: -1, n: 3 },
    gender: 'waifu',
    personality: 'INFP — The Gentle Healer',
    desc: 'Quiet, kind-hearted, {name} is shy but has incredible inner strength.',
    match: "You're gentle but strong when it counts.",
  },
  cold_captain: {
    traits: { e: -3, l: 2, v: -2, p: 2, n: 2 },
    gender: 'husbando',
    personality: 'ISTJ — The Cold Captain',
    desc: 'Cold, efficient, and the best. {name} hides deep care behind a stoic exterior.',
    match: "You show love through action, not words.",
  },
  // ... 30+ archetypes covering the full personality space
};
```

Each archetype maps to a point in the 5-axis space. Any character assigned that archetype gets those traits + a personalized description via `{name}` template substitution.

**Character list:** just name, series, archetype key, and emoji:

```typescript
['Hinata Hyuga', 'Naruto', 'gentle_flower', '💜'],
['Levi Ackerman', 'AOT', 'cold_captain', '🧹'],
['Gojo Satoru', 'JJK', 'unstoppable_jester', '🕶️'],
```

Then generate the full character file with a script. See `references/archetype-generator.md`.

### 2. Five Personality Axes

Each axis ranges from -3 to +3:

| Axis | -3 | 0 | +3 |
|------|-----|-----|-----|
| **E**nergy | Introvert | Balanced | Extrovert |
| **L**ogic | Heart/Feeling | Balanced | Head/Logic |
| **V**ibe | Serious | Measured | Playful |
| **P**ace | Relaxed | Steady | Driven |
| **N**ature | Independent | Flexible | Loyal |

### 3. Matching Algorithm

Use **weighted Euclidean distance** for accuracy:

```typescript
function weightedDistance(user, character) {
  const weights = { e: 1.2, l: 1.0, v: 1.3, p: 1.1, n: 1.4 };
  const squaredDiff =
    weights.e * Math.pow(user.e - character.e, 2) +
    weights.l * Math.pow(user.l - character.l, 2) +
    weights.v * Math.pow(user.v - character.v, 2) +
    weights.p * Math.pow(user.p - character.p, 2) +
    weights.n * Math.pow(user.n - character.n, 2);
  // ...
  return Math.round((1 - Math.sqrt(squaredDiff) / Math.sqrt(maxPossibleDist)) * 100);
}
```

Also add an **axis match bonus**: if user and character are within 0.8 on ≥3 axes, add a compatibility bonus. This improves differentiation between close matches.

### 4. Quiz Flow

1. **Gender selection screen** — choose waifu / husbando / both
2. **20 questions** — 4 answers each, each answer modifies the 5 axes
3. **Loading screen** — animated spinner + sparkles while "matching"
4. **Result screen** — character card with image, personality profile, match %, top-10 rankings
5. **Share modal** — WhatsApp / Twitter / Facebook / Copy Link

### 5. Social Sharing

Show a modal with platform-specific sharing:

```tsx
<a href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}`}>
  🐦 Twitter
</a>
<a href={`https://api.whatsapp.com/send?text=${encodeURIComponent(shareText)}`}>
  💬 WhatsApp
</a>
<a href={`https://www.facebook.com/sharer/sharer.php?u=...&quote=...`}>
  📘 Facebook
</a>
```

### 6. Character Library Page

A browsable grid of all characters with:
- **Filter tabs**: All / Waifus / Husbandos
- **Search bar**: by name or series
- **Click to expand** detail panel: image, personality chart, compatibility description

### 7. Anime Recommendations (downstream feature)

Use the same personality profile to recommend anime series. Create an anime database with `affinity` scores on the same 5 axes, then rank by distance:

```typescript
const ANIME_LIST = [
  { id: 'attack-on-titan', title: 'Attack on Titan', affinity: { e:0, l:2, v:-1, p:3, n:2 }, ... },
  // 50+ entries
];
```

Save the profile to **localStorage** after the quiz, then read it on the recommendations page.

### 8. Sound Effects for Tsundere Interactions

Add anime-style sound effects that play when users encounter tsundere characters (library clicks, quiz results). Two approaches, with the real-MP3-first pattern preferred.

#### Approach A: Real MP3 from MyInstants (Preferred)

Use an external MP3 URL with `new Audio()` and a synthesized fallback when the MP3 can't load:

```typescript
export function playBakaSound() {
  try {
    const audio = new Audio("https://www.myinstants.com/media/sounds/baka-m.mp3");
    audio.volume = 0.6;
    audio.play().catch(() => playBakaSynth());  // fallback if MP3 blocked
  } catch {
    playBakaSynth();
  }
}
```

Find the MP3 URL by curling the MyInstants page:
```bash
curl -sL "https://www.myinstants.com/en/instant/baka-m-86022/" | grep -oP 'https://[^"]*\.mp3' | head -1
```

#### Approach B: Synthesized with Web Audio API (Fallback)

Kept as backup when the MP3 can't load (CORS, slow network, ad-blockers). See `references/synthesized-sound-effects.md` for the full oscillator code.

#### Tsundere Detection

```typescript
export function isTsundere({ archetype?, name?, series? }): boolean {
  // Check archetype key: 'tsundere_soul', 'fearless_fighter', 'ice_fire_prince'
  // Check known tsundere series: Nisekoi, Toradora, Maid-Sama!, Kaguya-sama
  // Check known tsundere names: Taiga, Chitoge, Misaki, Asuka, Rin Tohsaka, Erza Scarlet
}
```

#### Integration Points

| Where | Trigger | Behavior |
|-------|---------|----------|
| Library card click | If char is tsundere → `playBakaSound()` | Instant on click |
| Quiz result page | If top match is tsundere → `setTimeout(playBakaSound, 500)` | 500ms delay after result appears |

#### Pitfalls
- **Audio blocked by browser autoplay policy** — Must be triggered by user gesture (click/tap). `setTimeout` from non-gesture events will fail silently. Wrap `new Audio().play()` in `.catch()`.
- **CORS / ad-blockers block MP3** — External MP3 URLs (MyInstants, etc.) may be blocked. Always have a synthesized fallback via `play().catch(fallback)`.
- **`useEffect` inside conditional render** — React hooks cannot be inside `if` blocks. Place the `useEffect` at the component top level with a conditional inside, guarded by `result && showResult`.
- **TypeScript type for cleanup** — When `setTimeout`/`setInterval` are used with TypeScript Node.js types, explicitly declare `NodeJS.Timeout | null` and assign before the callback.
- **`useEffect` dependency array** — Use `result?.character.name` not `result.character.name` (handle the null case) or the effect will error on first render.

### 9. Tenor GIF Sticker Integration (Auto-Cycling)

Add animated Tenor GIF stickers to quiz cards for engagement. The sticker auto-changes at random intervals while the user is on the page.

**Extracting GIF URLs from Tenor:** Given a Tenor embed code (`<div class="tenor-gif-embed" data-postid="...">`), extract the `data-postid`, fetch the Tenor view page, and grep for the direct CDN URL:

```bash
curl -sL "https://tenor.com/view/<slug>-gif-<postid>" | grep -oP 'https://media[^\"]*\.gif' | head -1
```

**State management with random rotation and auto-cycling (hydration-safe):**

```tsx
const stickerGifs = [
  "https://media.tenor.com/.../gif1.gif",
  // 6-10 GIFs for variety
];
// ⚠️ DO NOT use Math.random() in useState initializer — causes React Error #310
// Use a fixed initial value; randomize after client mount in useEffect
const [currentSticker, setCurrentSticker] = useState(stickerGifs[0]);

useEffect(() => {
  const switchSticker = () => {
    const next = Math.floor(Math.random() * stickerGifs.length);
    setCurrentSticker(stickerGifs[next]);
  };
  // Switch immediately on client mount (hydrate-safe: server already rendered stickerGifs[0])
  switchSticker();
  let cleanupInterval: NodeJS.Timeout | null = null;
  // Then auto-cycle every 4-9 seconds
  cleanupInterval = setInterval(switchSticker, 4000 + Math.random() * 5000);
  return () => {
    if (cleanupInterval) clearInterval(cleanupInterval);
  };
}, []);
```



### 10. CSS Animations for Quiz Engagement

Add to `globals.css`:

```css
/* Dance animation for sticker characters */
@keyframes dance { /* rhythmic bounce + wiggle + scale */ }
@keyframes floatUp { /* float up/down for hearts */ }
@keyframes glowPulse { /* pulsing shadow for sticker circle */ }
@keyframes sparkleFloat { /* upward + fade + rotate for sparkles */ }
@keyframes fadeInUp { /* 0.6s ease-out from translateY(30px) opacity(0) */ }
@keyframes fadeInScale { /* 0.5s ease-out from scale(0.8) */ }
@keyframes heartbeat { /* scale(1) -> scale(1.3) -> scale(1) for love emojis */ }
@keyframes gradientShift { /* 4s ease bg-position 0-100% for hero depth */ }
```

### 11. ErrorBoundary for Debugging Runtime Crashes

When a production Next.js page shows a blank screen or \"This page couldn't load,\" the root cause is typically a JavaScript runtime error during hydration. The fastest debug path is an ErrorBoundary:

```tsx
\"use client\";
import { Component, ReactNode } from \"react\";

interface State { hasError: boolean; errorMessage: string; }

export default class ErrorBoundary extends Component<{children: ReactNode}, State> {
  constructor(props: {children: ReactNode}) {
    super(props);
    this.state = { hasError: false, errorMessage: \"\" };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, errorMessage: error.message };
  }

  render() {
    if (this.state.hasError) {
      return <div>
        <h1>🚨 Oops! Something crashed</h1>
        <p>Error: <code>{this.state.errorMessage}</code></p>
        <button onClick={() => window.location.reload()}>Reload Page</button>
      </div>;
    }
    return this.props.children;
  }
}
```

Wrap the root page or layout:
```tsx
// app/page.tsx
import ErrorBoundary from \"@/components/ErrorBoundary\";
import AnimeQuiz from \"./services/AnimeQuiz\";

export default function Home() {
  return <ErrorBoundary><AnimeQuiz /></ErrorBoundary>;
}
```

**Common runtime crash causes in this class of app:**
- `Math.random()` in server-rendered component tree (hydration mismatch)
- `AudioContext` called outside user gesture (autoplay policy)
- `localStorage` in SSR (not available on server)
- Large character array rendering too many DOM nodes at once
- `setInterval` / `setTimeout` with stale closures (unreferenced cleanup variable)
- AdSense script interfering with React hydration (try removing the `<script>` tag temporarily)

**Debug workflow:**
1. Add ErrorBoundary → get the error message displayed in-browser
2. Check Vercel deploy logs for build-time warnings
3. Check browser DevTools console for hydration warnings
4. Remove one suspect feature at a time (AdSense, sound effects, sticker auto-cycle)

## Implementation Details

### File Structure
```
lib/
  characters.ts    — Generated character data (300+ entries)
  questions.ts     — 20 quiz questions with axis modifiers
  matching.ts      — Matching algorithm, personality types
  anime.ts         — Anime recommendation database
app/
  services/
    AnimeQuiz.tsx       — Main quiz component
    CharacterLibrary.tsx — Browseable character library
    AnimeRecommend.tsx   — Anime recommendations
  library/page.tsx      — Library route
  recommendations/page.tsx — Recommendations route
```

### Saving Quiz Results for Downstream Pages

```typescript
// In quiz component, after computing result:
localStorage.setItem("anime-personality-profile", JSON.stringify(res.profile));

// In recommendations page, on mount:
const saved = localStorage.getItem("anime-personality-profile");
if (saved) profile = JSON.parse(saved);
```
## Pitfalls

- **AniList API rate limiting**: 1 request = 1 character lookup. Rate limit kicks in at ~5 req/sec. Use 3 concurrent requests with 2.5s delays between batches for 371 characters (~8 min).
- **AniList search names**: Some characters require specific name formats (e.g., "Kamado Tanjiro" not "Tanjiro Kamado"). Search may fail for less popular characters — fall back to DiceBear or emoji.
- **AniList fuzzy match hazards**: The search frequently returns wrong characters (Shadow→Sonic, Obito→Parasyte's Obito, Pucci→Cappuccino). Always verify matches by looking up the character ID from the image URL. See `references/anilist-image-fetching.md` → "Fuzzy Matching Hazards" for the full list and defensive checks.
- **Game characters not on AniList**: Characters from Genshin Impact, Honkai, Arknights, etc. are often missing from AniList (it's anime-focused). Use `references/fandom-wiki-image-fetching.md` to search Fandom wikis for portrait PNGs instead.
- **Multi-pass strategy for image coverage**: Don't expect one pass to get everything. Run batch AniList → apply results → retry failed → media-first search → targeted wrong-match fix → Fandom wiki fallback → DiceBear SVG for last-resort. See `references/anilist-image-fetching.md` → "Multi-Pass Strategy".
- **Character ID verification**: After any automated match, extract the AniList character ID from the image URL (`b(\d+)` or `/(\d+).jpg`) and query the API to verify character name and media match expectations.
- **`];` pitfall in large arrays**: An accidental `];` inserted mid-list (e.g., after the waifu section) will silently DROP everything after it. Always verify `CHARACTER_LIST.length` after generation.
- **Character generation duplicates**: The archetype generator may produce duplicate entries with the SAME `id` but different `series` values (e.g. "My Hero Academia" vs "MHA", "Naruto" vs "Naruto Shippuden"). This causes **React key conflicts** — when `key={ch.id}` encounters duplicate keys, React's reconciliation breaks and search/filter components show stale characters that don't match the query.

  **Symptom:** Search "Bleach" returns 28 results (correct 17 Bleach + 11 non-Bleach like Momo, Nagisa, Ken Kaneki). The first result is correct but items 2-9 are always the same wrong characters regardless of search query.

  **Detection:** Scan for duplicate IDs with Python:
  ```python
  import re
  with open('lib/characters.ts') as f:
      content = f.read()
  ids = re.findall(r'id: "([^"]+)"', content)
  from collections import Counter
  dupes = {k: v for k, v in Counter(ids).items() if v > 1}
  print(f"Duplicate IDs: {dupes}")
  ```

  **Fix:** Remove duplicate entries (keeping the first occurrence). For entries with different series values (e.g. "Naruto" vs "Naruto Shippuden"), either pick one or create a unique ID like `naruto-uzumaki-shippuden`. After removal, always `npm run build` to verify no syntax errors, then `git push` to trigger Vercel auto-deploy.

  **The CharacterLibrary search component** is at `app/services/CharacterLibrary.tsx`. The filter logic:
  ```tsx
  if (search.trim()) {
    const q = search.toLowerCase();
    chars = chars.filter(c =>
      c.name.toLowerCase().includes(q) ||
      c.series.toLowerCase().includes(q)
    );
  }
  ```
  The grid renders `{filtered.map((ch) => (<button key={ch.id}>...))}`. Duplicate keys here break the reconciliation when the filter array changes size — React reuses DOM nodes by key and keeps stale ones visible.
- **NodeJS.Timeout type**: When using `setInterval`/`setTimeout` with TypeScript, declare cleanup variables as `NodeJS.Timeout | null` BEFORE the callback that assigns them.
- **Tenor GIF overflow**: GIF images may not be square. Use `object-cover` + `overflow-hidden` + `style={{ transform: 'scale(1.15)' }}`.
- **LocalStorage vs. SSR**: localStorage is only client-side. Wrap in `try/catch` inside `useEffect` or event handlers.
- **AudioContext autoplay policy**: Web Audio API sounds must be triggered by a user gesture. `setTimeout` from non-gesture events will fail silently. Wrap in `try/catch`.
- **`useEffect` inside conditional render**: Hooks cannot be inside `if` blocks. Place at component top level with conditional guards.
- **Image fallback updates**: When adding DiceBear fallback, replace ALL `if (imageUrl) ? img : emoji` patterns — library grid, detail panel, quiz results (main + top-10), featured grids.
- **`Math.random()` in SSR causes React Error #310**: Never use `Math.random()`, `Date.now()`, or any non-deterministic value in `useState` initializers or render functions in Next.js. The server renders with one set of random values, the client hydrates with different ones, and React crashes with "Minified React error #310" (hydration mismatch). Fix: use a fixed initial value (`useState(stickerGifs[0])`) and randomize after client mount in `useEffect()`. For structural containers with unavoidable random children (sakura petals), add `suppressHydrationWarning` to the container div.
- **Question count validation**: Ensure user answers ALL questions before computing results. Partial answers produce inaccurate profiles.
- **AdSense delay**: Takes 1-14 days to approve. `ads.txt` must be in `public/` root. Vercel serves `public/` files automatically.
- **Facebook blocks `.vercel.app`**: Buy a custom domain before heavy social promotion.

## Related

- `software-development/setup` — Vercel deployment, domain setup, SEO, monetization
- `software-development/setup/references/vercel-deployment-windows.md` — Full Vercel GitHub import workflow
