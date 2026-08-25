---
name: asset-image-pipeline
description: Use when each list item needs its own image.
---

# Asset Image Pipeline

Each entity must resolve to its own picture - real external image if resolvable, otherwise a deterministic generated avatar unique per name. No shared placeholder across entities.

## When to use
- Character, product, or user library where each item should show its own image
- External image API (AniList, TMDB, etc.) with fallback generator (DiceBear, etc.)
- Patching a static asset file like characters.ts or products.ts

## Workflow

1. **Audit** - count imageUrl vs total blocks; build url to ids map to find dup sharing. See references/anime-waifu-audit-2026-08-19.md.
2. **Fetch missing** - GraphQL search per cleaned name, rate limit ~0.8s (under 90/min), retry on 429. Score with SequenceMatcher + containment (0.92); try cleaned, first-token, and first-two-words variants. Accept >=0.4, flag <0.65 as LOW for manual review.
3. **Manual LOW fixes** - common reversals, true misses, aliases, romanizations. Verify via direct GraphQL search or Character(id:) lookup.
4. **Fake entities** - names with no external record stay on fallback. Remove cover image entry so getCharacterImage returns DiceBear seed=name - which is per-name distinct. Do not share one cover across two entities.
5. **Patch file** - insert imageUrl after emoji line in each block; verify count equals total blocks (minus intentional fallbacks). Re-audit dup map - remaining dups should be intentional same-person aliases.
6. **Verify** - npx next build must pass; TypeScript + static generation confirms no broken URLs.

## Fallback contract
getCharacterImage(name, realUrl) returns realUrl if present else DiceBear URL with seed=encodeURIComponent(name.replace(/\s+/g,'_')). Gender variant splits lorelei vs adventurer. Guarantees 100 percent coverage with per-entity distinctness.

## References
- references/anime-waifu-audit-2026-08-19.md - 427-block audit, 208-fetch session, LOW list, romantic-killer edge case

## Pitfalls
- AniList search is Western-order sensitive; Boa Hancock vs Hancock Boa is same id 16342 - do not flag as error.
- Cover image bx153930 is anime cover, not character - never share it across characters.
- first_seen in state.db is seconds float; do not divide by 1000.

## Ponytail notes
// ponytail: single imageUrl string, not object, saves bandwidth. Add thumbnailUrl when grid needs it.
// ponytail: O(n2) dup scan on 427 items is fine; hash map if over 10k.
