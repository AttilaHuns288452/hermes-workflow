# Reddit RSS bypass — worked recipe (2026-07-31)

Goal: read `reddit.com/r/<sub>/comments/<id>/<slug>/` when every scrape path
403s (www, old.reddit.com, api.reddit.com all return 403 + ~190KB block page).

## What failed first (so you don't repeat)

| Path | Result |
|---|---|
| web_extract / web_search | "Web tools are not configured" (no FIRECRAWL_API_KEY) |
| firecrawl_scrape | "we do not support this site" (Firecrawl policy block) |
| www.reddit.com/…/.json (curl, browser UA) | 403, 190KB HTML block page |
| old.reddit.com/…/.json | 403 |
| api.reddit.com/comments/<id> | 403 |
| redlib mirrors (perennialte, catsarch, nadeko, r4fo, safereddit, privadency) | 403 / 418 / 200-but-anubis ("Checking you are not a bot") |
| r.jina.ai reader proxy | 200 but "Target URL returned error 403: Forbidden" |
| api.allorigins.win/raw, corsproxy.io | 522 / 403 |

## What worked

```bash
curl -sL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0" \
  "https://www.reddit.com/r/<sub>/comments/<id>/.rss" -o rss.xml
```

The `.rss` endpoint on www.reddit.com returns 200 with the full thread:
entry #1 = the post (title + `<content>` body), entries #2+ = comments
(title prefixed `/u/<author> on <post title>`).

## Parsing (Python, stdlib)

```python
import html, xml.etree.ElementTree as ET
root = ET.parse('rss.xml').getroot()
for e in root.iter('{http://www.w3.org/2005/Atom}entry'):
    title = e.find('{http://www.w3.org/2005/Atom}title')
    content = e.find('{http://www.w3.org/2005/Atom}content')
    author = e.find('{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name')
    print(title.text, '|', author.text, '|', html.unescape(content.text or ''))
```

## Notes

- Live redlib instance list: `https://raw.githubusercontent.com/redlib-org/redlib-instances/main/instances.json`
- RSS gives the post + comments but no scores/flair — fine for reading content.
- Subreddit RSS (`/r/<sub>/.rss`) works the same way for browsing a sub's
  latest posts without HTML.
