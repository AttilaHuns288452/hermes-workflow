# Session Reference: Anime Waifu/Husbando Quiz

Built during 2026-06-17 session for user Attila.
Deployed at: https://www.animewaifucompatibility.xyz

## Character Database Stats
- 70 characters total: 35 waifus + 35 husbandos
- Series covered: Naruto, AOT, JJK, Demon Slayer, One Piece, Bleach, Re:Zero, SAO, Spy×Family, Chainsaw Man, Fate, Evangelion, Death Note, Fullmetal Alchemist, Steins;Gate, Mob Psycho, Berserk, JoJo, Toradora, Konosuba, Your Name, Monogatari, and more

## Questions
- 20 questions, 4 answers each (upgraded from 15 for better accuracy)
- Each answer modifies 1-2 axes by -3 to +3
- Questions probe: recharging style, decision-making, weekend preference, vibe, conflict handling, friend role, partner preference, life approach, relationship dynamic, anime genre, plot twist reaction, power fantasy, personal motto, vacation style, valued trait, protagonist type, insult reaction, anime power, friend group, backstory

## Matching Algorithm (v2 - Akinator-like)
- Weighted Euclidean distance with axis match bonus (replaced pure cosine similarity)
- Certainty scoring based on gap between #1 and #2 match
- Weights: E=1.2, L=1.0, V=1.3, P=1.1, N=1.4 (Loyalty and Vibe matter most)

## Aesthetic Upgrades
- Sakura petals falling animation on landing page
- Full-screen loading screen with spinner + sparkles
- Pulsing glow on result hero card  
- Gradient background shifts
- Animated heartbeat on emojis
- Fade-in-up transitions between screens
- Gradient text titles (purple-pink-blue)
- Featured characters shown as pill badges on landing
- Per-question emoji indicators (🌸🌺💮🏵️🌷🌹🌻🌼💐)

## Key Fixes
- Dark mode CSS was overriding gradient backgrounds - removed `@media (prefers-color-scheme: dark)` custom properties and `body { background }` rule
- Font display: swap added for FCP improvement
- Character names shown on landing page for engagement

## Key Files
- `lib/characters.ts` — 70 characters with emoji, personality descriptions, match reasons
- `lib/questions.ts` — 20 questions with answer modifiers
- `lib/matching.ts` — Weighted distance engine + certainty scoring
- `app/services/AnimeQuiz.tsx` — Complete quiz UI with sakura background, loading screen, 20 questions, results, feedback form

## Deployment
- GitHub: AttilaHuns288452/anime-waifu-quiz
- Vercel: auto-deploy via GitHub import
- Custom domain: www.animewaifucompatibility.xyz
- Characters are 30KB static data — acceptable size
- OG image generated via FAL AI

## Social Media Strategy (Filipino Audience)
FB groups: Freelancers Philippines, VA Philippines, Online Filipino Freelancers
Reddit: r/buhaydigital
Use Taglish: "Sinong anime waifu/husbando ka based sa personality mo?"
