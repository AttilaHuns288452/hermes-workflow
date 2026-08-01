# DiceBear Avatar Replacement for Copyrighted Images

## When to Use

Your site got an AdSense/DMCA flag for using copyrighted character images (AniList, official game art, movie stills). You need to replace them with royalty-free generated avatars.

## DiceBear API

Free, no API key, no rate limit on SVG generation. Offers 30+ styles. Two styles that work for anime characters:

- **`lorelei`** — soft anime style, good for waifu/female characters
- **`adventurer`** — rounder adventure style, good for husbando/male characters

Format: `https://api.dicebear.com/9.x/{style}/svg?seed={seed}&backgroundColor={colors}`

The `seed` parameter deterministically generates the same avatar for the same text — so each character always gets the same portrait.

## Full Integration

### `lib/images.ts` — two-function pattern

```ts
"use client";

export function getCharacterImage(name: string, realImageUrl?: string): string {
  if (realImageUrl) return realImageUrl;
  const seed = encodeURIComponent(name.replace(/\s+/g, '_'));
  return `https://api.dicebear.com/9.x/lorelei/svg?seed=${seed}&backgroundColor=b6e3f4,c0aede,ffd5dc,ffdfbf,d1d4f9`;
}

export function getCharacterImageWithGender(name: string, gender: string, realImageUrl?: string): string {
  if (realImageUrl) return realImageUrl;
  const seed = encodeURIComponent(name.replace(/\s+/g, '_'));
  if (gender === 'husbando') {
    return `https://api.dicebear.com/9.x/adventurer/svg?seed=${seed}&backgroundColor=d1d4f9,c0aede,b6e3f4`;
  }
  return `https://api.dicebear.com/9.x/lorelei/svg?seed=${seed}&backgroundColor=b6e3f4,c0aede,ffd5dc,ffdfbf`;
}
```

### `public/ads.txt` — must exist

```
google.com, pub-YOUR_PUBLISHER_ID, DIRECT, f08c47fec0942fa0
```

### Component usage

```tsx
<img
  src={getCharacterImageWithGender(ch.name, ch.gender, ch.imageUrl)}
  alt={ch.name}
  className="w-full h-full object-cover"
  loading="lazy"
  onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
/>
```

## Stripping Copyrighted imageUrl Fields

### Count how many imageUrl lines exist:

```bash
grep -c "imageUrl:" lib/characters.ts
```

### Remove all imageUrl lines:

```bash
sed -i '/imageUrl:/d' lib/characters.ts
```

### Verify zero remain:

```bash
grep -c "imageUrl:" lib/characters.ts
# Should return 0 (exit code 1) = none left
```

## Fixing Missing `id` Fields in Auto-Generated Data

After stripping imageUrl, you may hit build errors if character entries were auto-generated without `id` fields (TypeScript requires them). Backfill with this Python script:

```python
import re

with open('lib/characters.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixes = 0
result = list(lines)
i = 0
while i < len(result):
    stripped = result[i].strip()
    if stripped == '{' and i > 0:
        prev = result[i-1].strip()
        if prev in ('},', '}'):
            has_id = False
            name_idx = -1
            for j in range(i + 1, min(i + 6, len(result))):
                s = result[j].strip()
                if s.startswith('id:'): has_id = True; break
                if s.startswith('name:'): name_idx = j; break
            if not has_id and name_idx > 0:
                m = re.match(r'(\s*)name:\s*"([^"]+)"', result[name_idx])
                if m:
                    indent, name_val = m.group(1), m.group(2)
                    slug = name_val.lower()
                    replace_map = {
                        'é':'e','ü':'u','ö':'o','ä':'a','è':'e','ê':'e',
                        'à':'a','ï':'i','ñ':'n','ç':'c',
                        "'":'',"'":'','’':''
                    }
                    for k, v in replace_map.items():
                        slug = slug.replace(k, v)
                    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
                    result.insert(name_idx, f'{indent}id: "{slug}",\n')
                    fixes += 1
                    i += 1
    i += 1

with open('lib/characters.ts', 'w', encoding='utf-8') as f:
    f.writelines(result)
print(f'Fixed {fixes} missing IDs')
```

## Required Companion Pages

These must exist and meet minimum length for AdSense review:

| Page | Min words | Key elements |
|------|-----------|-------------|
| Privacy Policy | 800+ | Cookie disclosure (AdSense), data collection (localStorage), GDPR/CCPA rights, contact |
| About | 500+ | Site description, content disclaimer (fan project), contact email |
| Terms of Service | 600+ | IP disclaimer (trademarks belong to owners), "as is" disclaimer, liability limits |

## What Does NOT Work

- **Image cropping APIs** (apilayer smart crop, remove.bg, ClipDrop) — cropping a copyrighted image doesn't change its copyright status
- **Image compression/resizing** — same problem
- **Adding filters/watermarks** — still derivative of copyrighted work
- **Linking to source instead of embedding** — AdSense scans page content, not just served files
