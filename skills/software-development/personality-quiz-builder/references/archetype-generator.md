# Archetype Generator & Database Design

## Why Archetypes

Hand-authoring 300+ characters with unique personality traits, descriptions, and match reasons is infeasible. Instead, define **~30 archetypes** that cover the full personality space, then assign each character to an archetype.

## Archetype Template

```typescript
const ARCHETYPES = {
  archetype_key: {
    traits: { e: -2, l: -2, v: -1, p: -1, n: 3 },  // 5-axis profile
    gender: 'waifu' | 'husbando',
    personality: 'INFP — The Gentle Healer',             // Display label
    desc: 'Quiet, kind-hearted, {name}...',               // {name} = char name
    match: "You're gentle on the outside...",              // Compatibility reason
  },
};
```

## Character List Format

Keep it minimal — just name, series, archetype, emoji:

```typescript
const CHARACTER_LIST = [
  ['Hinata Hyuga', 'Naruto', 'gentle_flower', '💜'],
  ['Levi Ackerman', 'Attack on Titan', 'cold_captain', '🧹'],
  // ... 300+ entries
];
```

## Generator Script Pattern

```javascript
// generate_chars.js — run once to build characters.ts
const fs = require('fs');

// 1. Define ARCHETYPES (30+ entries)
// 2. Define CHARACTER_LIST (300+ entries of [name, series, archetype, emoji])
let output = 'export const CHARACTERS: Character[] = [\n';
for (const [name, series, archKey, emoji] of CHARACTER_LIST) {
  const arch = ARCHETYPES[archKey];
  const id = name.toLowerCase().replace(/[^a-z0-9\s-]/g, '').replace(/\s+/g, '-');
  output += `  {
    id: "${id}",
    name: "${name}",
    series: "${series}",
    gender: "${arch.gender}",
    traits: { e: ${arch.traits.e}, l: ${arch.traits.l}, v: ${arch.traits.v}, p: ${arch.traits.p}, n: ${arch.traits.n} },
    personality: "${arch.personality}",
    description: "${arch.desc.replace('{name}', name)}",
    matchReason: "${arch.match}",
    emoji: "${emoji}",
  },\n`;
}
output += '];\n';
fs.writeFileSync('lib/characters.ts', output);
```

## Deduplication

The generator can produce duplicate entries if the same character appears twice under different names. Add a build-time dedup step:

```javascript
const seen = new Set();
characters = characters.filter(c => {
  const key = c.name.toLowerCase();
  if (seen.has(key)) return false;
  seen.add(key);
  return true;
});
```

## Personality Types (display labels)

Map axis scores to readable labels on the result screen:

```typescript
export function getPersonalityDescription(profile) {
  const parts = [];
  if (profile.e < -1) parts.push("🎭 Introverted");
  else if (profile.e > 1) parts.push("🌟 Extroverted");
  else parts.push("⚖️ Balanced");

  if (profile.l < -1) parts.push("💖 Heart-Driven");
  else if (profile.l > 1) parts.push("🧠 Logic-Driven");
  else parts.push("🤝 Balanced Thinker");

  if (profile.v < -1) parts.push("📚 Serious-minded");
  else if (profile.v > 1) parts.push("🎉 Playful");
  else parts.push("😌 Measured");

  if (profile.p < -1) parts.push("🌊 Relaxed");
  else if (profile.p > 1) parts.push("🔥 Driven");
  else parts.push("⏸️ Steady");

  if (profile.n < -1) parts.push("🦅 Independent");
  else if (profile.n > 1) parts.push("🤝 Loyal");
  else parts.push("🔄 Flexible");

  return parts.join(" · ");
}
```
