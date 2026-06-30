---
name: personality-quiz-engine
description: "Build 'which X are you' personality quizzes with a cosine-similarity matching engine, multi-axis personality vectors, large character/outcome databases, and shareable results pages. Covers quiz question design, personality axis scoring, character matching, runner-up calculation, and go-to-market for viral personality quizzes."
triggers:
  - personality quiz
  - which character are you
  - personality test
  - matching engine
  - cosine similarity quiz
  - waifu quiz
  - personality assessment
  - quiz app
  - viral quiz
platforms: [windows, linux, macos]
---

# Personality Quiz Engine

## When to Use

- User wants to build a "which X are you" personality quiz (anime characters, pets, cars, etc.)
- User wants a personality matching engine with scoring and ranking
- User needs help designing quiz questions that map to personality axes
- User wants a viral shareable quiz with results page
- User wants to monetize a quiz (affiliates, ads)

## Core Architecture

### Personality Axis System

Use **5 axes** for the matching system. Each axis runs from -3 to +3:

| Axis | Range (-3 to +3) | Description |
|------|------------------|-------------|
| **E** (Energy) | Introvert → Extrovert | How you recharge and socialize |
| **L** (Logic) | Heart → Head | Emotion vs logic in decisions |
| **V** (Vibe) | Serious → Playful | Overall tone and energy |
| **P** (Pace) | Relaxed → Driven | Intensity and ambition |
| **N** (Nature) | Independent → Loyal | Relationship style and devotion |

### Character/Outcome Database

Each outcome (character, animal, car, etc.) gets a trait vector:

```typescript
interface Character {
  id: string;
  name: string;
  series: string;        // Category/source
  gender?: "waifu" | "husbando";  // Optional gender filter
  traits: { e: number; l: number; v: number; p: number; n: number };  // -3 to +3
  personality: string;   // Short label like "INFP — The Gentle Healer"
  description: string;   // About the character
  matchReason: string;   // Why the user matched — shown on result page
  emoji: string;         // Single emoji for visual identity
}
```

**Database size guidelines:**
- Minimum viable: 12-15 outcomes
- Good: 30-40 outcomes
- Rich: 60+ outcomes (covers more personality types, reduces repeat matches)

### Question Design

Each question has 4 answers. Each answer modifies the 5 personality axes:

```typescript
interface Answer {
  text: string;
  modifier: { e: number; l: number; v: number; p: number; n: number };
}
```

**Question design rules:**
- **15-20 questions** (15 for quick engagement, 20 for Akinator-like accuracy)
- Each question should probe 1-2 axes primarily
- Answer modifiers should be -3 to +3 per axis
- Avoid questions where all answers modify the same axis (prevents stacking)
- Questions should feel fun and relevant to the theme (anime, jobs, animals, etc.)

**Question bank examples by axis:**
- **Energy (E):** "How do you recharge?" "Choose your ideal weekend"
- **Logic (L):** "What matters more in decisions?" "How do you react to plot twists?"
- **Vibe (V):** "What describes your vibe?" "What's your ideal vacation?"
- **Pace (P):** "How do you handle conflict?" "What's your approach to life?"
- **Nature (N):** "What's your ideal relationship?" "What trait do you value most?"

### Matching Algorithm

Two approaches, from simplest to most accurate (Akinator-like):

**Option A — Cosine Similarity (simple):**

```typescript
function calculateUserProfile(answers: QuizAnswer[]) {
  const profile = { e: 0, l: 0, v: 0, p: 0, n: 0 };
  for (const answer of answers) {
    profile.e += answer.modifier.e;
    profile.l += answer.modifier.l;
    profile.v += answer.modifier.v;
    profile.p += answer.modifier.p;
    profile.n += answer.modifier.n;
  }
  const maxPerAxis = questionCount * 3;
  const normalize = (val: number) => 
    Math.round(Math.max(-3, Math.min(3, (val / maxPerAxis) * 3)) * 10) / 10;
  return { 
    e: normalize(profile.e), l: normalize(profile.l),
    v: normalize(profile.v), p: normalize(profile.p), n: normalize(profile.n) 
  };
}

function cosineSimilarity(a, b) {
  const dot = a.e*b.e + a.l*b.l + a.v*b.v + a.p*b.p + a.n*b.n;
  const magA = Math.sqrt(a.e**2 + a.l**2 + a.v**2 + a.p**2 + a.n**2);
  const magB = Math.sqrt(b.e**2 + b.l**2 + b.v**2 + b.p**2 + b.n**2);
  return (dot / (magA * magB)) * 100;
}
```

**Option B — Weighted Euclidean Distance (recommended, more Akinator-like):**

```typescript
// Each axis can be weighted differently based on how well it differentiates characters
function weightedDistance(user, character) {
  const weights = { e: 1.2, l: 1.0, v: 1.3, p: 1.1, n: 1.4 }; // Loyalty and Vibe have higher weight
  
  const squaredDiff = 
    weights.e * Math.pow(user.e - character.e, 2) +
    weights.l * Math.pow(user.l - character.l, 2) +
    weights.v * Math.pow(user.v - character.v, 2) +
    weights.p * Math.pow(user.p - character.p, 2) +
    weights.n * Math.pow(user.n - character.n, 2);
  
  const maxPossibleDist = Object.values(weights).reduce((s, w) => s + w * 36, 0);
  return Math.round((1 - Math.sqrt(squaredDiff) / Math.sqrt(maxPossibleDist)) * 100);
}
```

**Step 3 — Axis match bonus:** Boost characters that match on multiple axes:

```typescript
function axisMatchCount(user, character) {
  let count = 0;
  if (Math.abs(user.e - character.e) <= 0.8) count++;
  if (Math.abs(user.l - character.l) <= 0.8) count++;
  if (Math.abs(user.v - character.v) <= 0.8) count++;
  if (Math.abs(user.p - character.p) <= 0.8) count++;
  if (Math.abs(user.n - character.n) <= 0.8) count++;
  return count;
}

// Final score = weightedDistance + (axisMatches / 5) * 15
const finalCompatibility = Math.min(99, weightedDistance + (axisMatches / 5) * 15);
```

**Step 4 — Certainty score:** Shows confidence in the top match based on gap to runner-up:

```typescript
function calculateCertainty(scored) {
  if (scored.length < 2) return 100;
  const gap = scored[0].compatibility - scored[1].compatibility;
  return Math.min(100, Math.round((gap / 25) * 100));
}
// Display labels: >70 = "🎯 High Confidence", 40-70 = "📊 Good Match", <40 = "🔄 Close call"
```

Sort all candidates by `finalCompatibility` descending. The top result is the primary match. The second result is the runner-up (show this for engagement).

### Gender/Gating

If the quiz has gender-specific outcomes (waifus vs husbandos, male vs female), add a gender selection screen before the quiz:

```typescript
type Gender = "waifu" | "husbando" | "both";
```

Filter the character database by gender before matching. "Both" uses all characters.

### Results Page Layout

1. **Hero section** — Gradient background, character image (circle) or emoji fallback, name, series, personality type, compatibility %, certainty badge
2. **"Why {Name}?"** — Personalized match reason  
3. **About {Name}** — Character description
4. **Personality Profile** — Show the user's 5-axis scores with labels
5. **Runner-up** — Second closest match card (drives retakes and sharing). Use amber background (`bg-amber-50 border-amber-200`).
6. **Top 10 Rankings** — Full ranked list showing rank icon/medal (🥇🥈🥉 for top 3), character thumbnail (40x40 circle), name, series, compatibility % with color-coded progress bar (green >=80%, blue 60-79%, gray <60%). #1 row gets gold background (`bg-gradient-to-r from-yellow-50 to-amber-50`). This drives retakes and comparison-sharing.
7. **Share button** — Opens a share modal popup that shows the character emoji, name, compatibility %, and a 2x2 grid of share options: Copy Link, Twitter/X, Facebook, WhatsApp. Uses fixed overlay (`fixed inset-0 bg-black/40 backdrop-blur-sm`) with centered card. Do NOT use `navigator.share()` (unreliable on desktop). Use direct platform URLs (Twitter intent, FB sharer, WhatsApp API) plus clipboard fallback.
8. **Retake button** — "Take Again" to restart
9. **Feedback form** — localStorage-based (same pattern as `saas-launch` skill) OR Google Forms POST for real email delivery. To use Google Forms: create a form with matching fields, inspect the HTML for `entry.XXXXXX` IDs, then POST with `mode: "no-cors"` to `https://docs.google.com/forms/d/e/{FORM_ID}/formResponse`.
10. **Affiliate links** — Place themed affiliate links after results (e.g., Crunchyroll for anime quizzes)
   - Gold/silver/bronze medals for top 3
   - Each row: rank, thumbnail (40x40 circle), name, series, compatibility % with color-coded progress bar (green >80%, blue 60-80%, gray <60%)
   - Gold #1 row: bg-yellow-50/amber-50, border-yellow-300
7. **Share button** — Opens a share modal popup (not inline alert):
   - Modal: `fixed inset-0 bg-black/40 backdrop-blur-sm`, card: `max-w-sm rounded-2xl`
   - Shows character emoji, name, compatibility %
   - 2x2 grid: Copy Link, Twitter/X, Facebook, WhatsApp
   - Native share (`navigator.share()`) is NOT used — the modal works everywhere
8. **Retake button** — "Take Again" to restart
9. **Feedback form** — localStorage-based (same pattern as `saas-launch` skill) OR Google Forms POST for real email delivery. To use Google Forms: create a form with matching fields, inspect the HTML for `entry.XXXXXX` IDs, then POST with `mode: "no-cors"` to `https://docs.google.com/forms/d/e/{FORM_ID}/formResponse`.
10. **Affiliate links** — Place themed affiliate links after results (e.g., Crunchyroll for anime quizzes)

### Character Images

Add an optional `imageUrl` field to the Character interface:

```typescript
interface Character {
  id: string;
  name: string;
  series: string;
  // ... other fields
  imageUrl?: string;  // Publicly available character image URL
}
```

**Source: AniList public API** (no auth needed, rate limit 1 req/sec):
```bash
# Fetch character image URL
curl -s 'https://graphql.anilist.co' \
  -H 'Content-Type: application/json' \
  -d '{"query":"query ($search: String) { Character(search: $search) { image { large } } }","variables":{"search":"Character Name"}}'
# Response: "https://s4.anilist.co/file/anilistcdn/character/large/b<id>-<hash>.png"
```

The URL returned is publicly accessible for embedding in `<img>` tags.

**Display pattern (preferred):**
```tsx
<div className="w-40 h-40 rounded-full border-4 border-white/30 shadow-2xl overflow-hidden bg-white/10">
  {character.imageUrl ? (
    <img src={character.imageUrl} alt={character.name} 
         className="w-full h-full object-cover" loading="lazy"
         onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
  ) : (
    <span className="text-7xl heartbeat">{character.emoji}</span>
  )}
</div>
```

Always provide an emoji fallback for characters without images. Use `onError` to hide broken image links gracefully.

### Loading Screen

After the last question, show a brief loading animation while computing results:

```tsx
function LoadingScreen({ onFinish }: { onFinish: () => void }) {
  const [dots, setDots] = useState("");
  useEffect(() => {
    const interval = setInterval(() => setDots(p => p.length >= 3 ? "" : p + "."), 400);
    const timer = setTimeout(onFinish, 2000);
    return () => { clearInterval(interval); clearTimeout(timer); };
  }, [onFinish]);

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-gradient-to-br from-purple-900 via-pink-800 to-blue-900">
      <div className="loading-spinner mb-8" />
      <p className="text-xl text-white/80">Finding your match{dots}</p>
    </div>
  );
}
```

### Sharing Strategy

Share text format:
```
I got {name} ({compatibility}% match)! Find your own: https://yourdomain.xyz
```

## Quiz UI Structure

### Gender Selection Screen
- 3 buttons in a card layout: "Show Me [Gender 1]", "Show Me [Gender 2]", "Surprise Me"
- Each button has an emoji, title, and subtitle
- Background: gradient matching the theme

**Featured characters showcase:** Below the gender buttons, show 12-16 character name badges to build excitement. Each is a pill badge showing emoji + name + series. This also serves as social proof and helps users understand the scope of characters available.

### Character Library Page

Create a `/library` route with a browseable gallery of all characters:

- **Filter tabs**: All / Waifus / Husbandos (styled as pill buttons)
- **Search bar**: Filter by character name or series
- **Grid**: 2-4 column responsive grid of character cards
- Each card = circular image (or emoji fallback) + name + series + gender badge
- **Click to expand**: Detail panel slides in on the right (lg screens) or below (mobile)
- Detail panel shows: large image, name, series, personality type, description, compatibility explanation, 5-axis profile
- Detail panel is sticky on desktop for smooth browsing

### Quiz Screen
- **Progress bar** — Shows question N of total + percentage
- **Question card** — White card with the question text and 4 answer buttons
- **Answer buttons** — Full-width, hover effect, gray-50 background
- **Transitions** — Use `transition-all duration-500` for smooth progress bar animation

### Results Screen
- Gradient hero with emoji, name, series tag, compatibility badge
- "Why {Name}?" and "About {Name}" sections
- Personality profile with 5-axis score display
- Runner-up card (amber/amber-50 background)
- Share + Retake buttons

## Deployment

- Same as `saas-launch` Phase 3: Next.js static export → GitHub → Vercel import
- Buy a themed domain (e.g., `animewaifuquiz.xyz`, `whichpet.xyz`, `yourspirit.xyz`)
- Update the domain in 3 places: sitemap BASE_URL, layout metadata, JSON-LD schema

## Monetization

| Method | Best For | Notes |
|--------|----------|-------|
| Themed affiliate links | High-volume quizzes | Crunchyroll (anime), Amazon (general), Chewy (pets) |
| AdSense | All quizzes | Add to results page |
| Share-to-earn | Viral growth | More shares = more traffic = more ad/clicks |

## Pitfalls

- **Cosine similarity can return negative values** if profiles are opposite — clamp display score to 0-100
- **Gender filtering must happen BEFORE matching** — otherwise waifu/husbando selection doesn't work
- **Share functionality needs fallback** — `navigator.share()` only works on HTTPS + mobile. Always provide `navigator.clipboard.writeText()` as backup
- **Question count validation** — ensure user answers ALL questions before showing results
- **Character database balance** — if one personality type has 10 characters and another has 1, users may feel "stuck" getting the same type. Aim for roughly even distribution across personality archetypes
- **Runner-up should be from a different personality cluster** — if the primary and runner-up are nearly identical, it feels like a bug. If possible, skip the next N closest if they're within 5% of each other on all axes
- **The `onBlur` + `setTimeout` for help tooltips** is needed to allow click events to register before the tooltip hides

## Related Skills

- `saas-launch` — build, deploy, and monetize the full site around the quiz
- `software-development/setup` — initial project scaffolding
- `productivity/ai-marketing-skills` — ongoing promotion and growth

## Supporting Files

- **`references/character-database-example.md`** — Full 70+ character database with personality vectors, match reasons, and distribution guidance. Copy and customize for your own quiz.
- **`templates/15-question-set.md`** — Production-ready 15-question quiz with full modifier table for each answer. Adapt theme and answer text to your subject.
