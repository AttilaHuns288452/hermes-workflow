---
name: roblox-game-design
description: "Use when designing or reworking a Roblox game: core loop, tutorial/FTUE, levels, economy, retention phases, juice, grind, curation"
---


# Roblox Game Design Fundamentals

## When to Load

Load for the structural craft of a Roblox experience: core loop and meta-game architecture, tutorial/FTUE structure, level design, economy design, retention-phase planning, juice/game feel, Bartle balance, grind avoidance, Today's Picks or Moments readiness. Route elsewhere: metrics/discovery → `roblox-growth-design`; persuasion/pricing → `roblox-player-psychology`; VFX → `roblox-animation-vfx`; economy telemetry → `roblox-analytics`.


## Quick Reference

- **Core loop first**: three layers must each work: core loop (moment-to-moment), meta-game (hour-to-hour), long-term progression (day-to-day). If the raw actions aren't fun, nothing above them survives.
- **Retention phases**: D0–7 understandability/novelty/stability → D7–30 progression/mastery/return triggers → D30–90 social comparison/LiveOps → D90+ community.
- **Teach invisibly**: teach through experience, never popups; environmental teaching, dynamic UI, kinesthetic learning, show don't tell, inverted pyramid of complexity.
- **Levels**: Kishōtenketsu (safe intro → develop → twist → conclusion) plus the invisible hand (coins/lighting guide without text) and fairness (deaths feel the player's fault).
- **Economy**: every source needs a sink; soft/hard/social currencies; prices must scale with the power curve; watch hoarding, churn at choke points, currency devaluation.
- **Duplicates are fuel, never waste.** In a collection system, ask what the SECOND copy of an item does before shipping the first. If the answer is "nothing", that is a dead interaction, and it is usually the most common one: permanent world spawns mean a repeat pickup is the DEFAULT path, not an edge case. Proven shapes: N duplicates fuse into a higher tier, a duplicate feeds a separate counter/currency, or it re-rolls a variant. Cap duplicate payouts per day so they stay secondary to active play (faucet cap, not price nerf).
- **Cap the faucet, not the price.** Long-lived economies throttle income (daily caps, per-activity counters) rather than raising prices for the same reward, which reads as a wall. A cap needs two things: a visible ceiling the player can understand, and a number picked from data rather than guessed — with 0 players, instrument first and defer the number.
- **AFK and active must not invalidate each other.** If idle earning is a legitimate method, active play has to beat it on rate, variety and unlock value, and the idle path must still have a cap so it cannot replace the game. State both numbers in the design doc.
- **A session needs a clock.** Currencies give players something to spend; a depleting meter (warmth, campfire fuel, timer) gives the session a shape and doubles as the faucet cap.
- **Anti-grind**: grind is a state of mind, not a mechanic. Fix with juice, skill ceilings, and measurable chunks.
- **Bartle**: Achievers/Explorers/Socializers/Killers form an ecosystem; over-serve one and the others leave.
- **Field data**: measured onboarding/monetization/retention numbers (2026; see full.md).

> Full framework details, checklists, case studies (Stardew, Hades, Artifact), and the curation/Moments prep: [references/full.md](references/full.md)
