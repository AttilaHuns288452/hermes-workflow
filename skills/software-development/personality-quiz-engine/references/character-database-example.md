# Example Character Database — Anime Waifu/Husbando Quiz

This is a production-ready character database from a deployed quiz (70+ characters).
Use it as a reference when building your own personality quiz. Replace characters,
adjust trait vectors, and adapt match reasons to your theme.

## Personality Axis Guide

Each axis runs -3 to +3:

| Axis | -3 | 0 | +3 |
|------|----|---|----|
| **E** (Energy) | Introvert | Ambivert | Extrovert |
| **L** (Logic) | Heart-driven | Balanced | Logic-driven |
| **V** (Vibe) | Serious | Neutral | Playful |
| **P** (Pace) | Relaxed | Steady | Driven/Intense |
| **N** (Nature) | Independent | Flexible | Loyal/Devoted |

## Schema

```typescript
interface Character {
  id: string;
  name: string;
  series: string;
  gender: "waifu" | "husbando";
  traits: { e: number; l: number; v: number; p: number; n: number };
  personality: string;   // Short label like "INTJ — The Strategist"
  description: string;   // Character bio (2-3 sentences)
  matchReason: string;   // Second-person hook shown on results
  emoji: string;         // Single visual emoji
}
```

## Example Entries (Full 70+ database available in session history)

### Waifus (Female Characters)

| Character | Series | E | L | V | P | N | Personality |
|-----------|--------|---|---|---|---|---|-------------|
| Hinata Hyuga | Naruto | -2 | -2 | -1 | -1 | +3 | INFP — The Gentle Healer |
| Mikasa Ackerman | AOT | -2 | +2 | -2 | +2 | +3 | ISTJ — The Silent Guardian |
| Rem | Re:Zero | -1 | -2 | -1 | +2 | +3 | ISFJ — The Devoted Heart |
| Yor Forger | Spy×Family | 0 | -1 | 0 | +1 | +2 | ESFP — The Secret Sweetheart |
| Nobara Kugisaki | JJK | +2 | +1 | +2 | +2 | +1 | ESTP — The Fearless Fighter |
| Shinobu Kocho | Demon Slayer | 0 | +2 | -1 | +2 | +2 | INTJ — The Elegant Strategist |
| Marin Kitagawa | My Dress-Up Darling | +3 | -2 | +3 | +1 | +1 | ESFP — The Vibrant Creator |
| Frieren | Frieren | -3 | 0 | +1 | -1 | +1 | INTP — The Timeless Philosopher |
| Boa Hancock | One Piece | +2 | -1 | +2 | +2 | +3 | ENFJ — The Pirate Empress |
| Rukia Kuchiki | Bleach | -1 | +1 | 0 | +1 | +3 | ISTJ — The Steadfast Soul Reaper |
| Erza Scarlet | Fairy Tail | +2 | +1 | -1 | +3 | +3 | ESTJ — The Unwavering Knight |
| Makima | Chainsaw Man | +1 | +3 | -2 | +3 | -2 | ENTJ — The Master Manipulator |
| Kaguya Shinomiya | Kaguya-sama | -1 | +2 | 0 | +2 | +1 | INTJ — The Ice Princess |
| Zero Two | Darling in the Franxx | +2 | 0 | +2 | +3 | +2 | ENFP — The Rebel Partner |
| Kurisu Makise | Steins;Gate | -1 | +3 | 0 | +2 | +1 | INTJ — The Reluctant Genius |
| Violet Evergarden | Violet Evergarden | -3 | +1 | -3 | -1 | +3 | INFJ — The Doll Who Learned |
| Mitsuri Kanroji | Demon Slayer | +2 | -3 | +2 | +1 | +1 | ENFP — The Love-Filled Warrior |

### Husbandos (Male Characters)

| Character | Series | E | L | V | P | N | Personality |
|-----------|--------|---|---|---|---|---|-------------|
| Levi Ackerman | AOT | -3 | +2 | -2 | +2 | +2 | ISTJ — The Cold Captain |
| Satoru Gojo | JJK | +2 | +2 | +3 | +2 | -1 | ENTP — The Unstoppable Jester |
| Tanjiro Kamado | Demon Slayer | 0 | -3 | -1 | +2 | +3 | ENFJ — The Kind-Hearted Slayer |
| Kakashi Hatake | Naruto | -2 | +2 | +1 | 0 | +2 | ISTP — The Laid-Back Genius |
| Itachi Uchiha | Naruto | -3 | +2 | -3 | -1 | +3 | INFJ — The Tragic Hero |
| Lelouch vi Britannia | Code Geass | +1 | +3 | 0 | +3 | -1 | ENTJ — The Mastermind Emperor |
| Kirito | SAO | -2 | +1 | -1 | +2 | +3 | ISTJ — The Lone Black Swordsman |
| Roy Mustang | FMA | +2 | +2 | +1 | +2 | +2 | ENTJ — The Flame Alchemist |
| Roronoa Zoro | One Piece | -2 | +1 | -1 | +2 | +3 | ISTJ — The First Mate |
| Monkey D. Luffy | One Piece | +3 | -2 | +3 | +3 | +3 | ENFP — The Future Pirate King |
| L (Ryuzaki) | Death Note | -3 | +3 | 0 | +1 | 0 | INTP — The World's Greatest Detective |
| Kyojuro Rengoku | Demon Slayer | +3 | -1 | +2 | +3 | +3 | ENFJ — The Blazing Heart |
| Spike Spiegel | Cowboy Bebop | 0 | 0 | +2 | -1 | +1 | ISTP — The Cool Bounty Hunter |
| Guts | Berserk | -3 | 0 | -3 | +3 | -1 | ISTP — The Struggler |
| Saitama | One Punch Man | -2 | 0 | 0 | -1 | 0 | ISTP — The Hero for Fun |
| Ren Amamiya (Joker) | Persona 5 | -1 | +1 | +1 | +1 | +2 | ENFJ — The Phantom Trickster |
| Kamina | Gurren Lagann | +3 | -2 | +3 | +3 | +2 | ENFP — The Unstoppable Badass |

## Writing Match Reasons

The `matchReason` is the user's emotional payoff. Rules:

1. Write in **second person** ("you", "your")
2. Start with a trait the user would recognize in themselves
3. Connect it to the character's core appeal
4. Keep it 1-3 sentences

**Good examples:**
- "You're gentle on the outside but strong when it counts. You value deep connections and would do anything for the people you love."
- "You're confident, charismatic, and you refuse to take life too seriously — mostly because you know you've got this."
- "You're the friend who pushes others to be their best. Your confidence lifts everyone around you."

## Character Distribution Heuristic

For 70 characters, ensure:
- ~35 waifu + ~35 husbando
- Even spread across E-axis (introvert 33%, balanced 33%, extrovert 33%)
- Even spread across N-axis (independent 25%, flexible 50%, loyal 25%)
- At least 2-3 characters per personality archetype (gentle, stoic, chaotic, devoted, mastermind, rebel, heart, wise)
