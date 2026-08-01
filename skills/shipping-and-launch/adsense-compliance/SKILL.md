---
name: adsense-compliance
description: >-
  Prepares content/fan websites for Google AdSense review. Covers the #1 rejection
  reason (copyrighted images), thin content, missing legal pages, and the review
  request workflow.
trigger: user mentions AdSense rejection, policy violation, copyright flag, or review request
---

# AdSense Compliance for Content / Fan Sites

## The #1 rejection: copyrighted images
Fan sites (anime, games, celebrities) that use official artwork **will be rejected**.  
AniList, MyAnimeList, Pinterest, IMDB, and similar image sources are all copyrighted.

**Fix:** Strip all external image URLs → fallback to a procedural avatar service that generates unique royalty-free images from text seeds.

```bash
# Strip all imageUrl lines from a TS/JS data file
sed -i '/imageUrl:/d' lib/characters.ts
```

- DiceBear (`https://api.dicebear.com/9.x/lorelei/svg?seed=...`) — good for anime-style avatars
- DiceBear Adventurer — good for male/husbando characters
- Avataaars, Bottts, etc. available via DiceBear

Do NOT crop/hotlink copyrighted images expecting to pass review. A cropped copyrighted image is still copyrighted.

## Required pages (all three or AdSense will reject)

| Page | What it must cover |
|------|-------------------|
| `/privacy` | Local storage disclosure, cookie notice (AdSense uses cookies), GDPR/CCPA rights, contact email, children's privacy |
| `/terms` | Fan-project disclaimer (trademarks belong to owners), "as is" / entertainment-purposes-only, liability limits |
| `/about` | Site description, how it works, content/copyright disclaimer, **contact info** (email required) |

The privacy policy must name **Google AdSense** and link to Google's opt-out and ad settings pages.

Placeholder contact email is fine, but it must exist and be visible.

## ads.txt
Must be in `<public>/ads.txt` with the correct format:
```
google.com, pub-XXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0
```

## Content sufficiency
- Quiz/survey-only sites are borderline — add at least a library/browse section and an about page with substantial text
- Each character/item entry needs original written descriptions (your own personality profiles, match reasons, etc.)
- Don't just copy-paste wiki descriptions

## Before requesting review
1. Deploy the fix (Vercel, Netlify, etc.)
2. Verify the live site shows: About page, Privacy page, Terms page, ads.txt
3. No broken image references (check console)
4. Go to [AdSense Policy Center](https://adsense.google.com) → click **Request review**
5. Review takes 1-3 business days

## See Also

- `references/anime-fan-site-vercel-workflow.md` — Next.js + Vercel-specific workflow for anime quiz/fan sites (DiceBear per-character avatars, auto-fix missing IDs, deployment steps)

## Pitfalls
- Don't add imageUrl back later thinking "it's fine now" — AdSense re-scans periodically
- "Smart crop" APIs don't solve copyright — the image is still the same copyrighted work
- Thin legal pages (<100 words each) get auto-rejected — write substantial text
- If the site has UGC (comments, reviews), you need moderation and a UGC policy
- If the site is primarily single-page / single-function, add more content before re-submitting
