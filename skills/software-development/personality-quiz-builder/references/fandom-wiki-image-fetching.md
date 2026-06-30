# Fandom Wiki: Character Portraits for Game Characters

Game characters (Genshin Impact, Honkai, etc.) are often **not in AniList's anime-focused character database**. Fall back to Fandom wikis which have high-quality character portraits.

## How It Works

Fandom wikis use the MediaWiki API. The key endpoint for finding images is `allimages`:

```
GET {wiki_base}/api.php?action=query&list=allimages&aifrom={Character_Name_Portrait}&ailimit=5&format=json&prop=imageinfo&iiprop=url
```

## Wiki Base URLs

| Game | Wiki Base URL |
|------|---------------|
| Genshin Impact | `https://genshin-impact.fandom.com` |
| Bleach | `https://bleach.fandom.com` |
| Honkai Impact 3rd | `https://honkai-impact-3rd.fandom.com` |
| Fate series | `https://typemoon.fandom.com` |
| Naruto | `https://naruto.fandom.com` |

## Search Pattern

Most Fandom wikis name character portrait files as `{CharacterName}_Portrait.png` or `{CharacterName}_Profile.png`:

```python
import json, urllib.request, time

WIKI = "https://genshin-impact.fandom.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def find_portrait(wiki_base: str, character_name: str) -> str | None:
    """Search a Fandom wiki for a character portrait image."""
    # Try multiple naming patterns
    for term in [
        f"{character_name}_Portrait",
        f"{character_name}_Profile",
        f"{character_name}_Character",
    ]:
        url = f"{wiki_base}/api.php?action=query&list=allimages" \
              f"&aifrom={urllib.request.quote(term)}&ailimit=3" \
              f"&format=json&prop=imageinfo&iiprop=url"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read())
        images = data.get("query", {}).get("allimages", [])
        for img in images:
            name = img["name"]
            if "portrait" in name.lower() or "profile" in name.lower():
                return img["url"]
        time.sleep(0.3)
    return None
```

## Example: Genshin Impact Characters

```python
GENSHIN_WIKI = "https://genshin-impact.fandom.com"
portraits = {
    "Clorinde": f"{GENSHIN_WIKI}/api.php?action=query&list=allimages" \
                f"&aifrom=Clorinde_Portrait&ailimit=1&format=json" \
                f"&prop=imageinfo&iiprop=url",
    "Nilou": f"{GENSHIN_WIKI}/api.php?action=query&list=allimages" \
             f"&aifrom=Nilou_Portrait&ailimit=1&format=json" \
             f"&prop=imageinfo&iiprop=url",
}
```

Result URLs have the pattern:
`https://static.wikia.nocookie.net/{wiki-slug}/images/{hash}/{filename}/revision/latest/scale-to-width-down/1000?cb=timestamp`

## Why This Works for Game Characters

- **Genshin Impact** characters are fully documented on the Genshin wiki with official portrait PNGs
- **Honkai Impact 3rd** chars are on the Honkai wiki (AniList uses Chinese names; search with English names)
- **Bleach** characters have clean anime profile images on the Bleach wiki
- **Naruto** characters are well-documented on the Naruto wiki

## When to Use

| When | Use |
|------|-----|
| Character is from a game (Genshin, Honkai, Arknights) | Fandom wiki first |
| AniList search returns "Character ID not found" | Fandom wiki fallback |
| AniList match is obviously wrong (wrong series) | Try Fandom wiki before fixing |
| Need a clean full-body portrait | Fandom wiki often has better portraits than AniList |

## Pitfalls

- **Name format**: Use the exact character name as it appears on the wiki (capitalization matters)
- **Rate limiting**: Fandom API is generous but add 0.3s delay between calls to be safe
- **URL readability**: The raw API URL includes `revision/latest?cb=...` which works fine as an image src
- **No guarantee**: Minor characters may not have separate portrait files. Fall back to DiceBear.
- **Non-ASCII characters**: Characters like "Kyōraku" with macrons cause encoding errors in URL. Use `urllib.request.quote()` or search with ASCII-only names.
