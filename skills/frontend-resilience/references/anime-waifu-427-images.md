# Anime Waifu Quiz — 427 Images, Zero Blanks

## Session: 2026-08-19

### Problem
User: "make sure my all characters in my anime wiafu website are complete character image their character image is there"
- `lib/characters.ts`: 427 characters, 219 with `imageUrl` (AniList CDN `s4.anilist.co`), 208 without.
- Existing helper `lib/images.ts:getCharacterImageWithGender()` already guaranteed DiceBear fallback (`lorelei` for waifu, `adventurer` for husbando) — 100% coverage in theory.
- Real bug: `onError` in 6 places only did `style.display='none'` → blank tile when either AniList or DiceBear failed. No emoji shown.

### Files Patched (ponytail: reuse helper, one-line onError fixes)
1. `app/services/CharacterLibrary.tsx` — grid `+` absolute emoji overlay; detail panel already had correct fallback
2. `app/services/AnimeQuiz.tsx` — top-10 `w-10 h-10` list (was pure-hide)
3. `app/services/AnimeRecommend.tsx` — `w-16 h-16` main + `w-7 h-7` stacked avatars (2 fixes)
4. `components/Marquee.tsx` — `w-8 h-8` pills
5. `app/character/[slug]/page.tsx` — related carousel (hero fixed delegate completed)
6. Delegation: 4 parallel subagents via `delegate_task` (DeepSeek V4 Flash @ commandcode), 1500s timeout, 429 retry.

### Helper (source of truth)
```ts
// lib/images.ts
export function getCharacterImageWithGender(name: string, gender: string, realImageUrl?: string): string {
  if (realImageUrl) return realImageUrl;
  const seed = encodeURIComponent(name.replace(/\s+/g, '_'));
  if (gender === 'husbando') return `https://api.dicebear.com/9.x/adventurer/svg?seed=${seed}&backgroundColor=d1d4f9,c0aede,b6e3f4`;
  return `https://api.dicebear.com/9.x/lorelei/svg?seed=${seed}&backgroundColor=b6e3f4,c0aede,ffd5dc,ffdfbf`;
}
```

### Verification
```bash
grep -c 'imageUrl:' lib/characters.ts          # 219
grep -c 'id: "' lib/characters.ts              # 427
npx next build # ✓ Compiled, 438 static pages (427 chars + 11 routes), 3.3s
grep -rn "style.display" app components --include="*.tsx"  # all now include emoji fallback
```

### Stack
- Next.js 16 static export (`output: export`), Tailwind via PostCSS, TypeScript, Vercel
- AdSense `ca-pub-4645179646749256` — DiceBear only, no copyrighted images
- 427 chars auto-generated, archetype system

### Lesson
Never ship `onError` that only hides — every media tile needs meaningful fallback (emoji). Grep every caller of the image helper, not just the reported page.
