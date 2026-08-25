# Skill Collision: open-seo vs anime-waifu-quiz — Session Notes (2026-08-20)

## OpenSEO Setup

OpenSEO (`every-app/open-seo`) cloned to `~/Documents/Projects/open-seo`. Setup protocol:

```bash
cd ~/Documents/Projects && git clone --depth 1 https://github.com/every-app/open-seo.git open-seo
cd open-seo
corepack enable
pnpm install --frozen-lockfile --config.node-linker=hoisted  # --config.node-linker=hoisted REQUIRED on Windows
cp .env.example .env.local
echo "AUTH_MODE=local_noauth" >> .env.local
pnpm run db:migrate:local
pnpm run dev  # → http://localhost:3001
curl -s http://localhost:3001/api/health  # verify
```

### Key pitfalls discovered:
1. `pnpm install` without `--config.node-linker=hoisted` → `EBUSY: resource busy or locked` on symlink creation (Windows-specific, affects `@better-auth/kysely-adapter` and others)
2. `git clone` from `/c/Users/...` MSYS path can silently fail to land the repo — always verify with `ls`
3. `AUTH_MODE` not set → defaults to `cloudflare_access` which requires `TEAM_DOMAIN` + `POLICY_AUD` env vars
4. Health check: `dataforseo: warn` and `ai: ok` are normal when those optional keys aren't set

### Health check interpretation:
- `database: ok` — D1 local DB working
- `auth: ok` with `local_noauth` — no auth, admin user injected
- `dataforseo: warn` — not needed for local dev, only for live SEO data
- `ai: ok` — SAM agent disabled without `OPENROUTER_API_KEY`, optional

## SEO Audit Notes (anime-waifu-quiz.com → animewaifucompatibility.xyz)

### Site structure
- 434 URLs in sitemap.xml
- Next.js app: homepage, quiz, library, recommendations, feedback, privacy, terms
- 427 character pages under `/character/<slug>`
- No `/blog` or `/articles` (content strategy could add this for topical authority)

### Issues found
1. **Quiz page (`/quiz`) has NO H1** — critical for SEO. Need to add visible H1 heading.
2. **Character pages (427+) lack `<meta name="description">`** — some descriptions exist in JSON-LD but not as meta tags.
3. **13 JS chunks on homepage** (79KB HTML) — consider code splitting / lazy loading for character library.
4. **No Apple touch icon** — minor.
5. **OG image is static PNG** — could use WebP for better compression.

### Strengths
- Full OG tags (title, description, image, url, site_name, locale, type)
- Full Twitter Card tags (summary_large_image)
- 4 JSON-LD blocks: WebApplication, Organization, WebSite+SearchAction, FAQPage
- Canonical tags on all pages (canonical to www domain)
- Proper robots.txt with sitemap reference
- Responsive viewport meta tag
- 434 URL sitemap
- FAQ content in structured data

### freelance-rate-calculator.com
- **DOWN** — 522 Connection Timeout (Cloudflare can't reach origin server)
- No SEO metadata, sitemap, or robots.txt reachable
- Action: fix hosting before any SEO work possible