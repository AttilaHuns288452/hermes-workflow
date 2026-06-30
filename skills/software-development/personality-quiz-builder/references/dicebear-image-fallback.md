# DiceBear Avatar Fallback for 100% Character Image Coverage

## Problem
AniList API only covers ~36% of characters (152/420 popular anime characters). Many niche/romance characters are not in AniList's database.

## Solution: Dual-Source Image Strategy

### Tier 1: AniList API (real character art)
### Tier 2: DiceBear Generated Avatars (fallback)

[DiceBear](https://dicebear.com) is a free, no-API-key SVG avatar generator. Creates unique, deterministic avatars from any text seed.

```typescript
export function getCharacterImageWithGender(name: string, gender: string, realImageUrl?: string): string {
  if (realImageUrl) return realImageUrl;
  const seed = encodeURIComponent(name.replace(/\s+/g, '_'));
  if (gender === 'husbando') {
    return `https://api.dicebear.com/9.x/adventurer/svg?seed=${seed}&backgroundColor=d1d4f9,c0aede,b6e3f4`;
  }
  return `https://api.dicebear.com/9.x/lorelei/svg?seed=${seed}&backgroundColor=b6e3f4,c0aede,ffd5dc,ffdfbf`;
}
```

### Integration Pattern
Replace `if (imageUrl) ... else emoji` pattern with a single `<img>` that always has a source plus `onError` safety net:

```tsx
<img
  src={getCharacterImageWithGender(ch.name, ch.gender, ch.imageUrl)}
  alt={ch.name}
  className="w-full h-full object-cover"
  onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
/>
```

### DiceBear Styles & Backgrounds
- **lorelei** — anime-inspired female (waifu default)
- **adventurer** — adventure-style male (husbando default)
- **Backgrounds**: `b6e3f4` (blue), `c0aede` (purple), `ffd5dc` (pink), `ffdfbf` (peach)

### Characteristics
- No rate limits, no API key, SVG output (2-15KB)
- Same seed = same avatar (CDN cache-friendly)
- Always `encodeURIComponent()` the seed for special chars
- Update ALL image renders in codebase: library grid, detail panel, quiz results main card + top-10 list
