# Anime Fan Site — Vercel + Next.js Workflow

## Context
Anime/fan sites on Vercel (Next.js, static export) hit the same AdSense issues. This reference captures the specific workflow from the `anime-waifu-quiz` project.

## DiceBear per-character avatars
Replace 200+ copyrighted image URLs with seed-based DiceBear avatars in one pass:

```bash
# Strip all imageUrl lines
sed -i '/imageUrl:/d' lib/characters.ts

# The image helper already had DiceBear fallback, so no per-character import change needed
```

DiceBear lorelei (female) + adventurer (male) — seed=`characterName` generates a unique consistent avatar per character. Zero per-image config.

## Auto-fix missing IDs after stripping
When you remove image lines, check that every character entry still has required fields (the build may discover missing `id` fields that were previously hidden):

```python
# Python one-off: find objects missing 'id' field, add from index
import re
with open("lib/characters.ts") as f: src = f.read()
entries = re.split(r'(?=^\s+\{)', src, flags=re.MULTILINE)
fixed = []
for i, e in enumerate(entries):
    if e.strip() and 'id:' not in e:
        name_match = re.search(r"name:\s*'([^']+)'", e)
        id_val = name_match.group(1).lower().replace(' ', '-') if name_match else f"char-{i}"
        e = e.replace('{', f'{{ id: \'{id_val}\',', 1)
    fixed.append(e)
open("lib/characters.ts", "w").write(''.join(fixed))
```

## Legal pages — must exist before review
Drop-in privacy/terms/about for an anime quiz site:

| Page | Content |
|------|---------|
| `/privacy` | Local storage, cookies (AdSense), Google AdSense named, GDPR/CCPA rights, contact email, kids' privacy |
| `/terms` | Fan-project disclaimer (trademarks belong to owners), as-is entertainment purpose, liability limits |
| `/about` | What the site does, how matching works, copyright disclaimer, contact email |

## AGENTS.md — encode workflow for future sessions
```markdown
# Anime Waifu Quiz — Hermes Workflow

## Stack
- Next.js 16 (static export: `output: "export"`)
- Tailwind CSS via PostCSS, TypeScript
- Deployed on Vercel

## AdSense Compliance
- NO copyrighted images (AniList, MAL, etc.) — DiceBear only
- Required pages: `/privacy`, `/terms`, `/about`, `ads.txt`
- If adding character images, use seed-based procedural avatars only

## Commands
- `npx next build` — static export build
- `npx vercel deploy --prod --yes --token <token>` — auto-deploy

## Pages
/, /quiz, /library, /recommendations, /character/[slug] (438 generated), /about, /feedback, /privacy, /terms
```

## Deployment
```bash
git add -A && git commit -m "AdSense fixes: remove copyrighted images, expand legal pages"
git pull --rebase && git push origin master
npx next build && npx vercel deploy --prod --yes --token <token>
```

## Verification before review
```bash
curl -sL https://site.vercel.app/about | grep -oP '<title>[^<]+</title>'
curl -sL https://site.vercel.app/ads.txt
curl -sL https://site.vercel.app/privacy | grep -i 'google'
```
