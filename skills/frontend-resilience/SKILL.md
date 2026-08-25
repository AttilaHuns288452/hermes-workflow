---
name: frontend-resilience
description: Use when grids or lists must never show blank images.
---

# Frontend Resilience

## Overview
Guarantee 100% image coverage for media-heavy UIs. One deterministic helper + emoji `onError` on every render, so no tile ever goes blank. Reuse existing helpers; patch every caller once.

## When to Use
- Catalog / character / gallery grids (100+ items, some missing `imageUrl`)
- Top-N rankings, marquees, carousels, related-item strips
- Static export (`output: export`) where broken URLs can't be fixed at request time
- AdSense constraints that forbid copyrighted images (generated fallbacks required)

## The Guarantee Stack

1. **Single helper — `lib/images.ts` pattern**
```ts
export function getCharacterImageWithGender(name: string, gender: string, realImageUrl?: string): string {
  if (realImageUrl) return realImageUrl;
  const seed = encodeURIComponent(name.replace(/\s+/g, '_'));
  if (gender === 'husbando') return `https://api.dicebear.com/9.x/adventurer/svg?seed=${seed}&backgroundColor=d1d4f9,c0aede,b6e3f4`;
  return `https://api.dicebear.com/9.x/lorelei/svg?seed=${seed}&backgroundColor=b6e3f4,c0aede,ffd5dc,ffdfbf`;
}
```

2. **Emoji fallback on every `<img>` — never just `display='none'`**
```tsx
// Grid tile — absolute overlay
onError={(e) => { const img=e.target as HTMLImageElement; img.style.display='none'; img.parentElement!.innerHTML+=`<span class="absolute inset-0 flex items-center justify-center text-3xl bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">${ch.emoji}</span>`; }}

// Small circle — insert sibling span
onError={(e) => { const img=e.target as HTMLImageElement; img.style.display='none'; const s=document.createElement('span'); s.className='w-7 h-7 rounded-full border-2 border-white bg-gray-100 flex items-center justify-center text-[10px] shrink-0'; s.textContent=r.emoji; img.parentElement!.insertBefore(s, img); }}
```

3. **Reuse first** — grep `getCharacterImage*` and `onError` before writing a new helper.

## Checklist
- [ ] Data allows optional `imageUrl`; helper guarantees DiceBear fallback
- [ ] Every `<img>` via helper has `onError` → emoji (grep `style.display` — no pure-hide)
- [ ] Variants by context: grid overlay vs hero replace vs circle insert
- [ ] `npx next build` shows expected static page count

## Pitfalls
- Fixing only the reported page leaves marquee/recommendations/top-10 blank — grep every caller and patch all.
- DiceBear can still 429/timeout; `onError` → emoji is the second guarantee.
- `next/image` unnecessary for static external SVGs; plain `<img>` + helper is shortest diff.

## References
- `references/anime-waifu-427-images.md` — 427-character session, files patched, build 438 pages.

## Verification
```bash
grep -rn "style.display" app components --include="*.tsx"
npx next build  # expect Generating static pages (438/438)
```
