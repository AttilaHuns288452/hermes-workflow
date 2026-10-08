---
name: scraping-bot-walled-sites
description: Get content from sites that block scrapers (Reddit, Cloudflare-walled forums). Use when web_extract/firecrawl/web_search 403, refuse the site, or return block pages. RSS/Atom feeds are the highest-yield bypass; mirrors and proxies are fallbacks.
---

# Scraping bot-walled sites

Sites like Reddit block datacenter IPs and scrapers with 403 + a block page.
Standard web tools (web_extract, firecrawl) fail on them. There is a probe
ladder — climb it in order, stop at the first rung that returns real content.

## The ladder

1. **Site's own RSS/Atom feed** — highest yield, often completely unblocked.
   Reddit: append `.rss` to any URL (post, subreddit, user). Returns the post
   + every comment as Atom entries. One curl, no auth.
2. **JSON API endpoints** — Reddit `.json` is 403-blocked from datacenter IPs,
   but try before mirrors (some sites only block HTML, not JSON).
3. **Mirror instances** — redlib/libreddit mirrors. Live list:
   `https://raw.githubusercontent.com/redlib-org/redlib-instances/main/instances.json`
   (fields: `url`). Expect most to be bot-walled too (go-away, Anubis,
   Cloudflare) — probe several; `http=200` + tiny body is still a block page.
4. **CORS/reader proxies** — allorigins (`api.allorigins.win/raw?url=…`),
   corsproxy.io, r.jina.ai. Unreliable and often 403 on Reddit; cheap to try.

## Pitfalls

- **403 with a large body (100–200KB) is a block page, not content.** Check
  the first bytes for HTML boilerplate before parsing.
- `http=200` is NOT success on mirrors — anubis/go-away pages return 200.
  Grep the body for "bot" / "Verifying" / "Checking".
- Reddit RSS: entry #1 is the post, subsequent entries are comments (title
  prefixed `/u/username on <post title>`). Comment bodies are HTML-escaped
  inside the Atom `<content>` element — unescape before reading.
- web tools configured with Firecrawl may *refuse* the site ("we do not
  support this site") — that's a Firecrawl policy block, not a config error.

## Verification

Real-content check: parse and confirm you got the expected post title + body
before acting on the content. Block pages are styled consistently; a few
hundred bytes of CSS = wall.

Worked recipe: `references/reddit-rss-bypass.md`.
