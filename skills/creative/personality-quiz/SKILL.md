---
name: personality-quiz
description: Build "which X are you" personality quizzes with a character/type database, personality axes, cosine similarity matching, and shareable results. Works for waifu/husbando, Hogwarts houses, MBTI types, Marvel characters, etc.
triggers:
  - personality quiz
  - which ___ are you
  - waifu quiz
  - character match quiz
  - personality matching
  - anime quiz
  - compatibility quiz
platforms: [windows, linux, macos]
---

# Personality Quiz Builder

## Architecture

A personality quiz has three layers:

```
characters.ts          →  Character database with trait vectors
questions.ts           →  Quiz questions with answer modifiers  
matching.ts            →  Cosine similarity matching engine
```

## 1. Character/Type Database (`lib/characters.ts`)

Define a **Character** interface with vector traits across 5 axes:

```typescript
interface Character {
  id: string;
  name: string;
  series: string;        // franchise/category
  gender: "waifu" | "husbando"; // or your type categories
  traits: { e: number; l: number; v: number; p: number; n: number };
  // Each axis is -3 to +3
  personality: string;   // e.g. "INFP — The Gentle Healer"
  description: string;   // 1-2 sentence character bio
  matchReason: string;   // Why the user matched this character
  emoji: string;         // Display emoji
  imageUrl?: string;     // Real AniList photo or DiceBear fallback
}
```

**5 Personality Axes** (each scored -3 to +3):

| Axis | -3 | +3 |
|------|----|-----|
| **E** Energy | Introvert | Extrovert |
| **L** Logic | Heart/Feeling | Head/Logic |
| **V** Vibe | Serious | Playful |
| **P** Pace | Relaxed | Driven/Intense |
| **N** Nature | Independent | Loyal/Devoted |

### Archetype-Based Generation (for 200+ characters)

Instead of hand-writing 300+ characters, use an **archetype system** with 35+ predefined profiles. Each archetype has preset traits, a description template, and a match reason template:

```typescript
const ARCHETYPES = {
  gentle_flower: {
    traits: { e: -2, l: -2, v: -1, p: -1, n: 2 },
    personality: "INFP — The Gentle Healer",
    desc: "Gentle, kind, and fiercely protective...",
    match: "You're gentle and caring...",
  },
  tsundere_soul: {
    traits: { e: -1, l: -1, v: 2, p: 2, n: 2 },
    personality: "ENFP — The Fiery Heart",
    desc: "Brash on the outside but soft inside...",
    match: "You act tough but care deeply...",
  },
  cold_captain: { /* Levi, Kakashi, Byakuya */ },
  chaotic_fun: { /* Power, Aqua, Chika */ },
  quiet_power: { /* Tanjiro, Izuku, Gon */ },
  // 30+ more archetypes
};
```

Then define each character in a compact array:
```typescript
['Hinata Hyuga', 'Naruto', 'gentle_flower', '💜'],
['Taiga Aisaka', 'Toradora!', 'tsundere_soul', '🐯'],
['Levi Ackerman', 'AOT', 'cold_captain', '🧹'],
// 200-400 entries
```

Generate the full TypeScript file from this array by expanding each entry with the archetype's data. This keeps the source manageable (50KB for 420 characters) while producing full personality profiles.

**Pitfall:** If using a generator script, make sure the full array isn't prematurely closed with `];` when splitting waifu/husbando sections. All entries must be in ONE array before the final closing bracket.

**Filter function** to narrow by gender/type:
```typescript
export function getCharactersByGender(gender: "waifu" | "husbando" | "both"): Character[] {
  if (gender === "both") return CHARACTERS;
  return CHARACTERS.filter(c => c.gender === gender);
}
```

## 2. Quiz Questions (`lib/questions.ts`)

Each question has 4 answers. Each answer shifts the 5 axes:

```typescript
interface Answer {
  text: string;          // Display text with emoji
  modifier: { e: number; l: number; v: number; p: number; n: number };
}

interface Question {
  id: number;
  question: string;
  answers: Answer[];
}
```

**Design rules for good questions:**
- 15-20 questions ideal (enough for accuracy, short enough to finish)
- Each answer should probe 1-2 axes strongly (values -2 to +3)
- Vary which axis each question targets — don't hammer one axis
- Use relatable scenarios (recharging, conflict, ideal weekend, motto, past experiences)
- Every answer gets an emoji for visual appeal
- Include anime/manga-specific questions for themed quizzes (e.g., "what power would you want?", "what kind of protagonist are you?")

## 3. Matching Engine (`lib/matching.ts`)

Two approaches, ranked by accuracy:

### Approach A: Cosine Similarity (simpler)
```typescript
function cosineSimilarity(a, b) {
  const dot = a.e*b.e + a.l*b.l + a.v*b.v + a.p*b.p + a.n*b.n;
  const magA = Math.sqrt(a.e*a.e + a.l*a.l + a.v*a.v + a.p*a.p + a.n*a.n);
  const magB = Math.sqrt(b.e*b.e + b.l*b.l + b.v*b.v + b.p*b.p + b.n*b.n);
  return (dot / (magA * magB)) * 100;
}
```

### Approach B: Weighted Euclidean Distance + Axis Match Bonus (Akinator-like, more accurate)
For better differentiation between similar characters:

**Step 1 — Calculate user profile:**
```typescript
function calculateUserProfile(answers) {
  // Sum modifiers across all answers
  // Normalize: (value / (numQuestions * 3)) * 3 to -3/+3 range
}
```

**Step 2 — Weighted distance with axis match bonus:**
```typescript
const WEIGHTS = { e: 1.2, l: 1.0, v: 1.3, p: 1.1, n: 1.4 };
// Loyalty (n) and Vibe (v) weighted highest — they differentiate best

function weightedDistance(user, character) {
  const sqDiff = 
    WEIGHTS.e * Math.pow(user.e - character.e, 2) +
    WEIGHTS.l * Math.pow(user.l - character.l, 2) +
    WEIGHTS.v * Math.pow(user.v - character.v, 2) +
    WEIGHTS.p * Math.pow(user.p - character.p, 2) +
    WEIGHTS.n * Math.pow(user.n - character.n, 2);
  const maxDist = Object.values(WEIGHTS).reduce((s, w) => s + w * 36, 0);
  return Math.round((1 - Math.sqrt(sqDiff) / Math.sqrt(maxDist)) * 100);
}
```

**Step 3 — Compute final score with certainty:**
```typescript
function findMatches(answers, preferredGender) {
  const userProfile = calculateUserProfile(answers);
  const scored = candidates.map(character => {
    const distScore = weightedDistance(userProfile, character.traits);
    // Count axes within 0.8 of character — gives up to +15%
    const axisMatches = countCloseAxes(userProfile, character.traits);
    const axisBonus = (axisMatches / 5) * 15;
    return { character, compatibility: Math.min(99, distScore + axisBonus) };
  });
  scored.sort((a, b) => b.compatibility - a.compatibility);
  // Certainty score based on gap between #1 and #2
  const certainty = Math.min(100, ((scored[0].compatibility - scored[1].compatibility) / 25) * 100);
  return { character: scored[0], compatibility, certainty, runnerUp: scored[1], profile: userProfile };
}
```

### Certainty Score
Show users how confident the match is based on the gap between top-2 matches:
- **High confidence** (gap > 17%): "🎯 High Confidence Match"
- **Medium confidence** (gap 10-17%): "📊 Good Match"
- **Low confidence** (gap < 10%): "🔄 Close call! Retake for more accuracy"

### Personality Axis Descriptions
For the results display, map each axis to readable labels:
```typescript
if (e < -1) "Introverted — you recharge alone"
if (e > 1)  "Extroverted — you thrive with others"
// etc for l, v, p, n
```

## Character Image Pipeline

Achieve 100% image coverage by combining multiple sources:

### Source 1: AniList API (primary, ~50% coverage)
Batch-fetch character images from AniList's GraphQL API. Rate limit: ~90 req/min.

```bash
curl -s 'https://graphql.anilist.co' -H 'Content-Type: application/json' \
  -d '{"query":"query ($search: String) { Character(search: $search) { image { large } } }","variables":{"search":"Character Name"}}'
```

**Batch fetch strategy (Node.js):**
```javascript
// Fetch 3 at a time with 1.5-2s delay between batches
const CHUNK = 3;
const DELAY = 2000;

async function processBatch() {
  const chunk = characters.slice(idx * CHUNK, (idx + 1) * CHUNK);
  const results = await Promise.all(chunk.map(fetchFromAnilist));
  for (const url of results) if (url) addImageToFile(url);
  // Wait, then recurse
  await new Promise(r => setTimeout(r, DELAY));
  await processBatch();
}
```

Use name variations for better coverage:
```javascript
function getNameVariations(name) {
  const vars = [name];
  // Remove parentheticals: "L (Ryuzaki)" → "L"
  vars.push(name.replace(/\s*\([^)]*\)\s*/g, '').trim());
  // Try first name: "Nagisa Shiota" → "Nagisa Shiota" then simplified
  return [...new Set(vars)];
}
```

### Source 2: Jikan/MyAnimeList API (backup, <5% coverage)
```bash
curl -s "https://api.jikan.moe/v4/characters?q=Character%20Name&limit=1&order_by=favorites&sort=desc"
# Returns images.images.jpg.image_url
```
Rate limit: 30 req/10s. Lower coverage than AniList but catches some gaps.

### Source 3: DiceBear Fallback (100% guaranteed)
For characters no API has, generate unique avatars from their name:
```typescript
export function getCharacterImage(name: string, realImageUrl?: string): string {
  if (realImageUrl) return realImageUrl;
  const prefix = "https://api.dicebear.com/9.x/lorelei/svg?seed=";
  return prefix + encodeURIComponent(name.replace(/\s+/g, '_'));
}
```
DiceBear generates deterministic, unique SVGs per seed (character name). Use `lorelei` for waifu-friendly, `adventurer` for husbando. Add `backgroundColor=b6e3f4,c0aede,ffd5dc` for pastel backgrounds.

### Component Integration
Replace all `{ch.imageUrl ? <img src={real} /> : <span>{emoji}</span>}` with a single helper:
```tsx
import { getCharacterImageWithGender } from "@/lib/images";

// Always renders something:
const src = getCharacterImageWithGender(ch.name, ch.gender, ch.imageUrl);
<img src={src} alt={ch.name} onError={(e) => e.target.style.display = 'none'} />
```
This guarantees every character card renders an image.

## Tenor GIF Stickers (Easter Eggs)

Add animated Tenor GIF stickers to quiz cards for engagement.

### Getting GIF URLs from Tenor Embeds

Given a Tenor embed like:
```html
<div class="tenor-gif-embed" data-postid="10797314150976249328" ...>
```

Extract the direct CDN GIF URL:
```bash
# Replace <postid> with the data-postid value
curl -sL "https://tenor.com/view/<slug>-gif-<postid>" \
  | grep -oP 'https://media[^"]*\\.gif' | head -1
```

### Auto-Cycling Stickers (Random Timer)

Make stickers automatically rotate at random intervals to keep the page feeling alive:

```tsx
const stickerGifs = [
  "https://media.tenor.com/.../yao-yi-yao-yao-guang.gif",
  "https://media.tenor.com/.../menhera-chan-chibi.gif",
  "https://media.tenor.com/.../honkai-star-rail-anime.gif",
  "https://media.tenor.com/.../chibi-anime-boy.gif",
  "https://media.tenor.com/.../dance-chibi.gif",
  // 6-10 GIFs for good variety
];

const [currentSticker, setCurrentSticker] = useState(
  () => stickerGifs[Math.floor(Math.random() * stickerGifs.length)]
);

// Auto-switch at random intervals (first at 3-5s, then every 4-9s)
useEffect(() => {
  const switchSticker = () => {
    const next = Math.floor(Math.random() * stickerGifs.length);
    setCurrentSticker(stickerGifs[next]);
  };
  let interval: NodeJS.Timeout | null = null;
  const initialDelay = setTimeout(() => {
    switchSticker();
    interval = setInterval(switchSticker, 4000 + Math.random() * 5000);
  }, 3000 + Math.random() * 2000);
  return () => {
    clearTimeout(initialDelay);
    if (interval) clearInterval(interval);
  };
}, []);
```

### Sticker Display Pattern

Surround the GIF with animated decorations for a "cute sticker" feel:

```tsx
<div className="flex flex-col items-center justify-center mb-6">
  {/* Glowing circle behind */}
  <div className="sticker-glow w-40 h-40 rounded-full bg-gradient-to-br from-pink-200 via-purple-200 to-blue-200" />
  
  {/* Floating hearts above */}
  <span className="text-lg sticker-float" style={{ position: 'absolute', top: '-8px' }}>💕💖</span>
  
  {/* The GIF itself */}
  <img src={currentSticker} alt="dancing" className="w-36 h-36 object-cover rounded-full"
    style={{ transform: 'scale(1.15)' }} />
  
  {/* Sparkles floating around */}
  <span className="text-sm sticker-sparkle" style={{ position: 'absolute', top: '20%', right: '-10px' }}>✨</span>
  <span className="text-sm sticker-sparkle2" style={{ position: 'absolute', bottom: '20%', left: '-10px' }}>⭐</span>
  
  {/* Caption */}
  <p className="text-xs text-purple-400 mt-3 sticker-float font-medium">
    ✨ Let's find your perfect match! ✨
  </p>
</div>
```

CSS for the animations:
```css
@keyframes glowPulse {
  0%, 100% { box-shadow: 0 0 15px rgba(236,72,153,0.3), 0 0 30px rgba(168,85,247,0.1); }
  50% { box-shadow: 0 0 25px rgba(236,72,153,0.5), 0 0 50px rgba(168,85,247,0.2); }
}
@keyframes floatUp {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}
@keyframes sparkleFloat {
  0% { opacity: 0; transform: translateY(0) rotate(0deg); }
  50% { opacity: 1; transform: translateY(-20px) rotate(180deg); }
  100% { opacity: 0; transform: translateY(-40px) rotate(360deg); }
}
```

## Sound Effects (BAKA! for Tsundere Characters)

Add anime-style sound effects triggered by certain character types.

### The BAKA! Sound

Use a **real MP3** from MyInstants with a synthesized Web Audio fallback:

```typescript
// lib/sound-effects.ts
export function playBakaSound() {
  try {
    const audio = new Audio("https://www.myinstants.com/media/sounds/baka-m.mp3");
    audio.volume = 0.6;
    audio.play().catch(() => playBakaSynth()); // fallback
  } catch {
    playBakaSynth();
  }
}

function playBakaSynth() {
  // Web Audio API oscillator-based "BA-KA!"
  // Play lower tone (180→220Hz) for "BAH" then higher (350→400Hz) for "KAH!"
  // Add noise burst for the percussive 'K' sound
}
```

### Detecting Tsundere Characters

Detect by character name, series, or archetype:

```typescript
export function isTsundere({ name, series, archetype }: {
  name?: string; series?: string; archetype?: string;
}): boolean {
  // Known tsundere archetypes
  const archSet = ['tsundere_soul', 'fearless_fighter', 'ice_fire_prince'];
  if (archetype && archSet.includes(archetype)) return true;
  
  // Known tsundere series
  const seriesSet = ['Toradora!', 'Nisekoi', 'Kaguya-sama', 'Maid-Sama!'];
  if (series && seriesSet.includes(series)) return true;
  
  // Named characters
  const nameSet = ['Taiga Aisaka', 'Chitoge Kirisaki', 'Misaki Ayuzawa', 
                   'Asuka Langley Soryu', 'Rin Tohsaka'];
  if (name && nameSet.includes(name)) return true;
  
  return false;
}
```

### Integration Points

| Where | Trigger | Code |
|-------|---------|------|
| Library card click | On click, if tsundere → play | `onClick={() => { if (isTsundere({name, series})) playBakaSound(); }}` |
| Quiz result load | On result show, if tsundere → play after 500ms | `useEffect` with 500ms timeout |

**Pitfall:** `useEffect` must be at the component top level, not inside a conditional return block. Use a dependency on `result?.character.name`.

## Anime Recommendations Page

Add a `/recommendations` route that uses the user's quiz persona profile (stored in localStorage) to recommend anime series.

### Anime Database

Each anime entry has personality affinity scores (-3 to +3 per axis):
```typescript
interface AnimeEntry {
  id: string;
  title: string;
  altTitle: string;
  genres: string[];
  tags: string[];
  year: number;
  episodes: number;
  description: string;
  // Personality affinity: which profiles would like this show
  affinity: { e: number; l: number; v: number; p: number; n: number };
  score: number;      // MAL/AniList score (1-10)
  malUrl: string;     // MyAnimeList link
  watchUrl: string;   // Crunchyroll/netflix link
}
```

50+ anime entries covering major series (AOT, Frieren, Steins;Gate, Cowboy Bebop, Violet Evergarden, Kaguya-sama, etc.)

### Personality-to-Anime Mapping

Map each axis to genres:
| Axis (-) | Genre | Axis (+) | Genre |
|----------|-------|----------|-------|
| Introvert (E-) | Psychological, Seinen | Extrovert (E+) | Action, Shonen |
| Heart (L-) | Romance, Slice of Life | Logic (L+) | Sci-Fi, Thriller |
| Serious (V-) | Dark Fantasy, Mystery | Playful (V+) | Comedy, Romance |
| Relaxed (P-) | Iyashikei, Comedy | Driven (P+) | Action, Adventure |
| Independent (N-) | Seinen, Psychological | Loyal (N+) | Fantasy, Adventure |

### Recommendation Algorithm

```typescript
function getAnimeByPersonality(profile: PersonaProfile): AnimeEntry[] {
  return ANIME_DB
    .map(anime => {
      const diff = Math.sqrt(
        Math.pow(profile.e - anime.affinity.e, 2) * 0.8 +
        Math.pow(profile.l - anime.affinity.l, 2) * 0.7 +
        Math.pow(profile.v - anime.affinity.v, 2) * 0.9 +
        Math.pow(profile.p - anime.affinity.p, 2) * 0.6 +
        Math.pow(profile.n - anime.affinity.n, 2) * 1.0
      );
      const maxDist = Math.sqrt(5 * 36);
      const match = Math.round((1 - diff / maxDist) * 100);
      return { ...anime, match: Math.min(99, match) };
    })
    .sort((a, b) => b.match - a.match)
    .slice(0, 10);
}
```

### Storage & Display
- Quiz results stored in `localStorage.setItem('quizResult', JSON.stringify(result))`
- Recommendations page reads from localStorage
- If no quiz taken, show "⚠️ Take the quiz first!" with link
- Each recommendation card shows: match %, genre tags, year, episodes, click-to-expand for description + external links

## 4. Quiz UI Components

### Landing Page
- **Featured characters** — Show 6 sample characters as pill badges (emoji + name + series) so users see what they might get
- **Gradient text title** — `bg-gradient-to-r from-purple-600 via-pink-500 to-blue-500 bg-clip-text text-transparent`
- **Question count** — Prominently display (e.g., "Answer 20 questions to find your match")

### Gender/Type Picker
Three gradient-background cards: Type A (pink tones), Type B (blue tones), Surprise Me (purple tones). Each card has emoji + bold title + subtitle + subtle floating decoration emoji.

### Loading Screen (the "Akinator moment")
Full-screen overlay shown while matching:
- Spinning gradient loader (purple/pink)
- Animated heart emoji
- "Finding your match..." + animated dots
- "Analyzing across 20 dimensions..."
- Floating sparkle emojis (✨🌟💫⭐)

### Question Screen
- **Emoji progress indicator** — each question number gets a unique emoji (e.g., 🌸🌺💮🏵️🌷🌹🌻🌼💐)
- Progress bar with purple-pink-blue gradient and smooth `duration-700` transition
- Question card with `fadeInUp` animation on each new question
- 4 answer buttons with gradient hover effect (shifts to purple/pink on hover)

### Results Screen
- **Pulsing glow hero** — gradient background (`from-purple-600 via-pink-500 to-blue-500`) with `.animate-pulse-glow` CSS box-shadow animation
- **Animated gradient** — background-size 200% with gradient shift animation for hero depth
- **Certainty badge** — show high/medium/low confidence indicator
- **Character info** — personalized match reason + description + personality type
- **Personality profile** — visual 5-axis bar chart with colored bars per axis
- **Runner-up** — second best match card with character name, series, and compatibility %
- **Top 10 rankings** — ranked list with medal emojis (🥇🥈🥉), circular character thumbnails, compatibility bars (green/blue/gray), and series names
- **Share button** — `navigator.share()` on mobile, `navigator.clipboard.writeText()` fallback on desktop
- **Share modal** — popup with 4 options: Copy Link, Twitter/X, Facebook, WhatsApp. Each opens the platform's native share dialog with pre-filled result text.
- **Share text** — "I got [Character Name] ([X]% match)! Find your match: [URL]"
- **\"Take Again\"** button to restart
- **Anime Recommendations link** — navigates to /recommendations page with personality-based anime suggestions

### Animated GIF Stickers (Tenor Integration)
Add animated Tenor GIF stickers to quiz cards for engagement:

```tsx
const stickerGifs = [
  "https://media.tenor.com/.../yao-yi-yao-yao-guang.gif",    // Yao Yi Yao dance
  "https://media.tenor.com/.../menhera-chan-chibi.gif",         // Menhera Chan
  "https://media.tenor.com/.../honkai-star-rail-anime.gif",     // Honkai sticker
  "https://media.tenor.com/.../chibi-anime-boy.gif",            // Chibi boy dance
  "https://media.tenor.com/.../dance-chibi.gif",                // Kaoruko dance
  // Add 6-10 GIFs for variety
];

// Pick random on each page load
const [currentSticker] = useState(
  () => stickerGifs[Math.floor(Math.random() * stickerGifs.length)]
);
```

**Getting GIF URLs from Tenor:** Given a Tenor embed (`<div class="tenor-gif-embed" data-postid="...">`), extract the `data-postid`, fetch the view page, and grep for the direct CDN URL:
```bash
curl -sL "https://tenor.com/view/<slug>-gif-<postid>" | grep -oP 'https://media[^"]*\\.gif' | head -1
```

**Display pattern:** Place GIF in a circular container with `sticker-glow` class (pulsing shadow), add floating hearts (💕💖) above, sparkles (✨⭐💫🌟) around the card, and a caption like `"✨ Yao yi yao ~ Let's find your match! ✨"`. Show on both the landing page and each question card.

### Character Library Page
A browsable grid of all characters with:
- **Filter tabs**: All / Waifus / Husbandos
@keyframes sakuraFall {
  0% { transform: translateY(-10vh) rotate(0deg); opacity: 0.8; }
  100% { transform: translateY(110vh) rotate(360deg); opacity: 0; }
}

/* Fade-in-up for screen transitions */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Pulsing glow for result card */
@keyframes pulseGlow {
  0%, 100% { box-shadow: 0 0 20px rgba(168, 85, 247, 0.3); }
  50% { box-shadow: 0 0 40px rgba(236, 72, 153, 0.5); }
}

/* Heartbeat for love emojis */
@keyframes heartbeat {
  0%, 100% { transform: scale(1); }
  14% { transform: scale(1.3); }
  42% { transform: scale(1); }
}

/* Sticker dance animation — rhythmic bounce + wiggle + scale */
@keyframes dance {
  0%, 100% { transform: translateY(0) rotate(0deg) scale(1); }
  10% { transform: translateY(-18px) rotate(-10deg) scale(1.05); }
  20% { transform: translateY(-5px) rotate(5deg) scale(1); }
  30% { transform: translateY(-18px) rotate(10deg) scale(1.05); }
  40% { transform: translateY(-5px) rotate(-5deg) scale(1); }
  50% { transform: translateY(-18px) rotate(-10deg) scale(1.05); }
  60% { transform: translateY(-5px) rotate(5deg) scale(1); }
}

/* Faster partner dance */
@keyframes danceFast {
  0%, 100% { transform: translateY(0) rotate(0deg) scale(1); }
  12% { transform: translateY(-14px) rotate(-12deg) scale(1.1); }
  37% { transform: translateY(-14px) rotate(12deg) scale(1.1); }
  62% { transform: translateY(-14px) rotate(-12deg) scale(1.1); }
  87% { transform: translateY(-10px) rotate(-8deg) scale(1.05); }
}

/* Sparkle float — upward + fade + rotate */
@keyframes sparkleFloat {
  0% { opacity: 0; transform: translateY(0) scale(0) rotate(0deg); }
  50% { opacity: 1; transform: translateY(-20px) scale(1.2) rotate(180deg); }
  100% { opacity: 0; transform: translateY(-40px) scale(0) rotate(360deg); }
}

/* Float up/down for hearts and text */
@keyframes floatUp {
  0% { transform: translateY(0) scale(1); opacity: 0.8; }
  50% { transform: translateY(-15px) scale(1.05); opacity: 1; }
  100% { transform: translateY(0) scale(1); opacity: 0.8; }
}

/* Glow pulse for sticker background circle */
@keyframes glowPulse {
  0%, 100% { box-shadow: 0 0 15px rgba(236,72,153,0.3), 0 0 30px rgba(168,85,247,0.1); }
  50% { box-shadow: 0 0 25px rgba(236,72,153,0.5), 0 0 50px rgba(168,85,247,0.2); }
}

/* Flower sway for decorative flowers */
@keyframes flowerSway {
  0%, 100% { transform: rotate(-8deg) scale(1); }
  25% { transform: rotate(8deg) scale(1.1); }
  50% { transform: rotate(-5deg) scale(1); }
  75% { transform: rotate(5deg) scale(1.05); }
}

/* Gradient shift for result hero depth */
@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
```

### CSS Pitfall: Dark Mode Override
The default Next.js CSS includes `@media (prefers-color-scheme: dark)` setting `--background: #0a0a0a`. This OVERRIDES Tailwind gradient background classes on the body. **Delete the dark mode CSS custom properties and the `body { background: var(--background) }` rule** — let Tailwind's gradient classes control the background instead. The site should always show the gradient regardless of OS dark mode preference.

## 5. Monetization

| Method | Integration |
|--------|------------|
| Affiliate links | Crunchyroll, anime merch, streaming services |
| AdSense | Display ads on quiz and results pages |
| Social sharing | navigator.share → viral loop |
| Feedback form | localStorage-based feedback collection |

## 6. Next.js Setup

Use `create-next-app` with TypeScript + Tailwind + static export:

```bash
npx create-next-app@latest . --typescript --tailwind --eslint --app --use-npm
```

Configure `next.config.ts`:
```typescript
const nextConfig = {
  output: "export",
  images: { unoptimized: true },
};
```

## Pitfalls

- **Cosine similarity returns negative values for opposite personalities.** Clamp result to 0-100 range with `Math.max(0, Math.min(100, 50 + raw * 0.5))`.
- **Large character pools (70+) make the ts file big.** This is fine — it's static data that gets tree-shaken. Character data is ~30KB for 70 characters.
- **Next.js + Tailwind generates large CSS.** Acceptable for a static export. The render-blocking CSS warning from Lighthouse is cosmetic for real users.
- **navigator.share only works on HTTPS + mobile.** On desktop, fall back to `navigator.clipboard.writeText()`.
- **Font loading delays FCP.** Add `display: "swap"` to Google Font config (`next/font/google`).

## Verification

```bash
cd quiz-project
npm run build
npx serve out -p 3000
# Test all paths: /, gender selection, all questions, results, share, feedback
```
