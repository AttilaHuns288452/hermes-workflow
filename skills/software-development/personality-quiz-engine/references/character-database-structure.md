# Character Database Structure Guide

## Personality vector range

Each axis uses -3 to +3 scale:
- -3 = extreme left (introvert, heart-driven, serious, relaxed, independent)
- +3 = extreme right (extrovert, logic-driven, playful, driven, loyal)
- 0 = neutral / balanced

## Character distribution guidelines

Aim for roughly even distribution across all personality quadrants. This prevents users from feeling "stuck" getting the same type of character every time they retake the quiz.

### Recommended distribution for 60 characters:

| Quadrant | Description | Characters | % |
|----------|-------------|-----------|--|
| High E, High P | Social, Driven | 10-12 | ~17-20% |
| High E, Low P | Social, Relaxed | 8-10 | ~13-17% |
| Low E, High P | Introverted, Driven | 10-12 | ~17-20% |
| Low E, Low P | Introverted, Relaxed | 8-10 | ~13-17% |
| Balanced center | Mixed traits | 6-8 | ~10-13% |

## Personality type labels

Map each character to a recognizable personality archetype + a thematic tagline:

```typescript
personality: "ISTJ — The Silent Guardian",    // MBTI-like + role
personality: "ENFP — The Chaotic Fun-Bringer", // MBTI-like + role
personality: "INFJ — The Tragic Hero",         // MBTI-like + role
```

## Match reason writing

The `matchReason` field is shown to the user as the primary emotional hook. Write it in second person ("you"):

**Good:**
"You're protective, loyal, and don't waste words. Your strength shows when the people you care about need you."

**Bad:**
"This character is a protector. They are loyal and strong."

## Common character archetypes to include

For an anime waifu/husbando quiz, include at least one of each:

- **The Gentle One** (Hinata, Tanjiro) — Low E, Low L, High N
- **The Stoic Guardian** (Mikasa, Levi) — Low E, High L, High N
- **The Chaotic Fun** (Power, Chika) — High E, High V, Low N
- **The Devoted Worker** (Rem, Genos) — Low E, High P, High N
- **The Mastermind** (Lelouch, Makima) — High L, High P, Low N
- **The Rebel** (Zero Two, Spike) — High V, High P, Low N
- **The Heart** (Marin, Mitsuri) — High E, Low L, Low P
- **The Wise One** (Frieren, Kakashi) — Low E, Balanced L, Low P
