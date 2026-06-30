# AniList API: Batch Fetching Character Images

## API

AniList provides a public GraphQL API at `https://graphql.anilist.co`. No authentication required for character lookups.

### Single Character Lookup

```bash
curl -s 'https://graphql.anilist.co' \
  -H 'Content-Type: application/json' \
  -d '{"query":"query ($search: String) { Character(search: $search) { image { large } } }","variables":{"search":"Gojo Satoru"}}'
```

Response:
```json
{
  "data": {
    "Character": {
      "image": {
        "large": "https://s4.anilist.co/file/anilistcdn/character/large/b127691-9zqh1xpIubn7.png"
      }
    }
  }
}
```

Image URL pattern: `https://s4.anilist.co/file/anilistcdn/character/large/{id}.{ext}`

## Rate Limiting

- ~5 requests/second before hitting 429 ("Too Many Requests")
- **Safe approach**: 3 concurrent requests, 2.5s delay between batches
- For 371 characters → ~124 batches × 2.5s = ~5 minutes
- Python scripts: use `time.sleep(0.7)` between requests (~86 req/min — safe)
- On HTTP 429, back off with exponential sleep (5s, 10s, 15s)

## Media-First Search (Preferred for Accuracy)

General character search is fuzzy and often returns wrong matches (see pitfalls below). **Search within a specific anime/media instead** for vastly better results:

```graphql
query($media: String) {
  Media(search: $media, type: ANIME) {
    characters(page: 1, perPage: 50) {
      nodes {
        id
        name { full }
        image { large }
      }
      pageInfo { hasNextPage total }
    }
  }
}
```

```python
import json, urllib.request, time
from difflib import SequenceMatcher

def find_char_in_media(media_name, char_name_hint):
    """Find a character by searching within a specific anime's character list."""
    query = '''
    query($media: String) {
      Media(search: $media, type: ANIME) {
        characters(page: 1, perPage: 50) {
          nodes { id name { full } image { large } }
        }
      }
    }
    '''
    payload = json.dumps({"query": query, "variables": {"media": media_name}}).encode()
    req = urllib.request.Request("https://graphql.anilist.co", data=payload, headers={
        "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"
    })
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    chars = data["data"]["Media"]["characters"]["nodes"]
    
    hint = char_name_hint.lower()
    # Try exact substring first, then fuzzy
    for c in chars:
        nm = c["name"]["full"].lower()
        if hint in nm or SequenceMatcher(None, hint, nm).ratio() > 0.8:
            return c
    return None
```

**Limitation**: AniList only returns the first 50 characters per media page. Minor characters (e.g. Obito Uchiha in Naruto, Kaina Tsutsumi in MHA) may not appear. Use pagination or direct search + media verification instead.

## Character ID Verification

After fetching images, **verify** the character identity by looking up the AniList ID embedded in the image URL:

```python
ID_QUERY = '''
query($id: Int) {
  Character(id: $id) {
    name { full }
    media(page: 1, perPage: 3) { nodes { title { romaji } } }
  }
}
'''

# Extract ID from URL like "https://s4.anilist.co/file/anilistcdn/character/large/b21174-xxx.jpg"
import re
m = re.search(r'/(large/)(?:b)?(\d+)', image_url)
if m:
    al_id = int(m.group(2))
    # Verify character name + media matches expectations
```

Always verify after automated matching. Many "successful" matches point to wrong characters.

## Batch Fetch Script (Node.js)

```javascript
const https = require('https');
const fs = require('fs');

const characters = []; // Populate with [{ id, name }]
const results = {};
const CHUNK_SIZE = 3;
const DELAY_MS = 2500;

let chunkIndex = 0;

function fetchChunk() {
  const chunk = characters.slice(chunkIndex * CHUNK_SIZE, (chunkIndex + 1) * CHUNK_SIZE);
  if (chunk.length === 0) {
    // Write results to file
    return;
  }

  let done = 0;
  for (const char of chunk) {
    const body = JSON.stringify({
      query: `query ($search: String) { Character(search: $search) { image { large } } }`,
      variables: { search: char.name }
    });
    const req = https.request({ hostname: 'graphql.anilist.co', method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }
    }, res => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          if (json?.data?.Character?.image?.large) {
            results[char.id] = json.data.Character.image.large.replace(/\\\//g, '/');
          }
        } catch(e) {}
        if (++done === chunk.length) {
          chunkIndex++;
          setTimeout(fetchChunk, DELAY_MS);
        }
      });
    });
    req.write(body);
    req.end();
  }
}
fetchChunk();
```

## Adding Images to the Character File

After fetching, add `imageUrl` to each character in `characters.ts`:

```javascript
const regex = new RegExp(`(id: "${char.id}",\\n[\\s\\S]*?emoji: "[^"]+",)`);
const match = content.match(regex);
if (match && !match[1].includes('imageUrl:')) {
  const newLine = match[1] + `\n    imageUrl: "${url}",`;
  content = content.replace(match[1], newLine);
}
```

## Character Search Name Variations

AniList's search can be picky. Try these fallbacks:
- `"Levi"` instead of `"Levi Ackerman"` — works ✓
- `"Lelouch Lamperouge"` instead of `"Lelouch vi Britannia"` — works ✓
- `"Kamado Tanjiro"` instead of `"Tanjiro Kamado"` — sometimes fails, use `"Tanjiro"` ✓
- `"Monkey D. Luffy"` — works as full name ✓

Results: ~100-120 hits out of 370 characters (~27-32%). The rest need fallback strategies.

## Fuzzy Matching Hazards (Critical)

AniList character search uses fuzzy name matching that frequently returns wrong characters. **Always verify matches** using character ID lookup or media-title filtering.

### Real-world wrong matches (all from real runs):

| Searched For | Got Instead | Why |
|-------------|-------------|-----|
| Obito Uchiha (Naruto) | Obito (Parasyte) | Name collision, Naruto's Obito not in top 50 |
| Shadow (Eminence in Shadow) | Shadow the Hedgehog (Sonic) | Generic name matched popular franchise first |
| Pucci (JoJo) | Cappuccino (Kobayashi) | Fuzzy match "Pucci" → "Cappuccino" |
| Yuji Itadori (JJK) | Wasuke Itadori (grandfather) | Same surname, wrong character |
| Toshiro Hitsugaya (Bleach) | Toshirou Tsubaki (Hikaru no Go) | Phonetic similarity |
| Aizen Sosuke (Bleach) | Rosa Ushiromiya (Umineko) | No obvious connection — pure fuzzy tag mismatch |
| Historia Reiss (AOT) | Menou Historia (wrong series) | "Historia" matched second word |
| Lumine (Genshin) | Suman Dark (D.Gray-man) | No connection at all |
| Himeko Murata (Honkai) | Jizi Wuliangta (correct char, CN name) | Correct match but CN name is confusing |

### Defensive checks to prevent wrong matches:

1. **Filter by media**: After search, check the character's media includes the expected series title
2. **ID verification**: Look up the character ID from the image URL and verify name + media
3. **Name threshold ≥ 0.8**: Don't accept fuzzy matches below 0.85 similarity
4. **Known-bad name list**: Flag characters named "Shadow", "Pucci", "Historia", "Lumine" for manual review

### Fuzzy matching pitfalls safe list example

```python
SUSPICIOUS_NAMES = {
    "Shadow", "Pucci", "Historia", "Lumine", "Obito",
    "Nagataro", "Klein", "Toshiro", "Toushirou"
}
# These names commonly match wrong characters — require media verification
```

## Multi-Pass Strategy for 100% Coverage

Instead of one monolithic run, use a **multi-pass approach**:

| Pass | Approach | Expected Coverage |
|------|----------|-------------------|
| 1 | Batch name-search on AniList | ~30-50% |
| 2 | Apply results + retry failed names with alternate spellings | +5-10% |
| 3 | Media-first search for remaining (search by series) | +10-15% |
| 4 | Targeted fix for known-wrong matches | +5% |
| 5 | Fandom Wiki fallback for game characters | Covers remaining game chars |
| 6 | DiceBear/SVG fallback in UI layer | 100% guaranteed |

Each pass applies its results to the file, then the next pass works on the shrinking pool of failures.

## Multi-API Fallback Chain

For maximum coverage, try APIs in order:

| Priority | API | Method | Coverage | Notes |
|----------|-----|--------|----------|-------|
| 1 | **AniList** | GraphQL `Character(search:)` | ~30% | Best quality, free, needs ~2s delay between batches |
| 2 | **Jikan** (MyAnimeList) | REST `GET /v4/characters?q=` | ~5-10% more | No auth, rate limit 30 req/10s. Use fuzzy name matching since Jikan names differ from our generated names. |
| 3 | **Kitsu** | REST `/api/edge/characters?filter[name]=` | Limited | Complex relationship chain for images. Often returns `image: null`. Only use as last resort. |
| N/A | **DiceBear** | SVG avatar generator | 100% guaranteed | Not a real photo, but every character gets a unique avatar. See `references/dicebear-image-fallback.md`. |

### Jikan API (2nd attempt)

```javascript
function jikanSearch(name) {
  const q = encodeURIComponent(name.replace(/\([^)]*\)/g, '').trim());
  https.get(`https://api.jikan.moe/v4/characters?q=${q}&limit=1&order_by=favorites&sort=desc`, res => {
    let d = '';
    res.on('data', c => d += c);
    res.on('end', () => {
      const r = JSON.parse(d)?.data?.[0];
      if (r?.images?.jpg?.image_url) {
        // Accept if name matches loosely (first word or full name)
        const apiName = (r.name || '').toLowerCase();
        const ourName = name.toLowerCase();
        if (apiName.includes(ourName.split(' ')[0]) || ourName.includes(apiName)) {
          return r.images.jpg.image_url;
        }
      }
    });
  });
}
```

### DiceBear Universal Fallback

In the UI layer, replace every `{imageUrl ? img : emoji}` pattern with an avatar function:

```typescript
export function getCharacterImage(name: string, realImageUrl?: string): string {
  if (realImageUrl) return realImageUrl;
  const seed = encodeURIComponent(name.replace(/\s+/g, '_'));
  return `https://api.dicebear.com/9.x/lorelei/svg?seed=${seed}&backgroundColor=b6e3f4,c0aede,ffd5dc,ffdfbf`;
}
```

**Must update ALL locations** where character images render:
- Library grid cards
- Library detail panel
- Quiz result main character image
- Quiz result top-10 list images
- Featured character previews
- Recommendations page

Search for all `imageUrl ?` and `onError` patterns — there's typically 4-6 locations per app.

### 100% Coverage Strategy

1. Run AniList batch fetch first → ~30% coverage
2. Run Jikan batch on remaining → ~35-40% coverage  
3. Apply DiceBear fallback in component layer → 100% coverage

**Important**: If the characters.ts file is regenerated (e.g. after adding characters or fixing archetypes), ALL previously-fetched imageUrls are lost. Always re-run the fetch script after regeneration, or add imageUrls to the generator itself.
