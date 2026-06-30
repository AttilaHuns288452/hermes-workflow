---
name: api-mega-list
description: "Search and browse the API Mega List — 10,498 ready-to-use Apify-based APIs across 18 categories (AI, Social Media, E-commerce, Lead Gen, Developer Tools, MCP Servers, Real Estate, Jobs, and more). Use when the user asks to find an API for a specific task, browse APIs by category, discover tools for web scraping, lead generation, social media automation, or MCP server integration."
category: productivity
version: 1.0.0
author: Hermes Agent + cporter202
triggers:
  - "find an API for"
  - "search APIs for"
  - "API to"
  - "API that can"
  - "browse APIs"
  - "available APIs"
  - "API mega list"
  - "apify actor"
  - "scraper for"
  - "MCP server for"
  - "lead generation API"
  - "social media API"
  - "search for data about"
  - "find data on"
  - "data source for"
  - "where to get data about"
  - "API for data"
metadata:
  decide:
    keywords: [api, apify, mega list, scraper, mcp server, lead gen, web scraping, social media api, api catalog, api directory]
    domain: productivity
    confidence: high
---

# API Mega List Skill

## Overview

The [API Mega List](https://github.com/cporter202/API-mega-list) — **26,005 ready-to-use APIs** (primarily Apify Actors) organized into **18 categories**. The repo is cloned at `~/Documents/Projects/API-mega-list/`.

## Repository Structure

```
~/Documents/Projects/API-mega-list/
├── agents-apis-697/           # README.md — 697 agent/scraper APIs
├── ai-apis-1208/              # README.md — 1,208 AI & LLM APIs
├── automation-apis-4825/      # README.md — 4,825 automation APIs
├── business-apis-2/           # README.md — 2 business APIs
├── developer-tools-apis-2652/ # README.md — 2,652 developer tools
├── ecommerce-apis-2440/       # README.md — 2,440 e-commerce APIs
├── integrations-apis-890/     # README.md — 890 integration APIs
├── jobs-apis-848/             # README.md — 848 jobs & recruitment APIs
├── lead-generation-apis-3452/ # README.md — 3,452 lead gen APIs
├── mcp-servers-apis-131/      # README.md — 131 MCP server APIs
├── news-apis-590/             # README.md — 590 news APIs
├── open-source-apis-768/      # README.md — 768 open source APIs
├── other-apis-1297/           # README.md — 1,297 other/misc APIs
├── real-estate-apis-851/      # README.md — 851 real estate APIs
├── seo-tools-apis-710/        # README.md — 710 SEO tools
├── social-media-apis-3268/    # README.md — 3,268 social media APIs
├── travel-apis-397/           # README.md — 397 travel APIs
├── videos-apis-979/           # README.md — 979 video APIs
├── settings/                  # Build scripts + full Apify actor list
├── FOLLOW_CREATOR.md          # Creator info
└── README.md                  # Master list (26K+ lines, 7MB)
```

## How to Search

### 1. By Category — Quick Category Overview

```bash
CATEGORIES=(
  "agents-apis-697:Agents & Scrapers"
  "ai-apis-1208:AI & LLM"
  "automation-apis-4825:Automation"
  "business-apis-2:Business"
  "developer-tools-apis-2652:Developer Tools"
  "ecommerce-apis-2440:E-commerce"
  "integrations-apis-890:Integrations"
  "jobs-apis-848:Jobs & Recruitment"
  "lead-generation-apis-3452:Lead Generation"
  "mcp-servers-apis-131:MCP Servers"
  "news-apis-590:News"
  "open-source-apis-768:Open Source"
  "other-apis-1297:Other"
  "real-estate-apis-851:Real Estate"
  "seo-tools-apis-710:SEO Tools"
  "social-media-apis-3268:Social Media"
  "travel-apis-397:Travel"
  "videos-apis-979:Videos"
)
```

### 2. By Keyword — grep any category

```bash
# Search all categories for a keyword
grep -i "<keyword>" ~/Documents/Projects/API-mega-list/*/README.md

# Search specific category
grep -i "<keyword>" ~/Documents/Projects/API-mega-list/ai-apis-1208/README.md

# Search with context (—A or -B)
grep -i -A2 "<keyword>" ~/Documents/Projects/API-mega-list/mcp-servers-apis-131/README.md

# Get count of matching APIs
grep -c "^| \[" ~/Documents/Projects/API-mega-list/social-media-apis-3268/README.md
```

### 3. By API Name with Category

```bash
# Find which category an API belongs to
grep -rl "<api-name-part>" ~/Documents/Projects/API-mega-list/*/README.md | head -5
```

### 4. Get a Random API from a Category

```bash
# Random API from AI category
grep "^| \[" ~/Documents/Projects/API-mega-list/ai-apis-1208/README.md | shuf -n 1
```

## Category Inventory

| # | Category | Dir | APIs | Typical Use Cases |
|---|----------|-----|------|-------------------|
| 1 | **Agents & Scrapers** | `agents-apis-697` | 697 | Web scraping, data extraction, crawlers |
| 2 | **AI & LLM** | `ai-apis-1208` | 1,208 | GPT scrapers, content gen, image gen, document AI |
| 3 | **Automation** | `automation-apis-4825` | 4,825 | Workflow automation, batch processing |
| 4 | **Business** | `business-apis-2` | 2 | Business data and operations |
| 5 | **Developer Tools** | `developer-tools-apis-2652` | 2,652 | OCR, proxy, IP geolocation, vector DBs, MCP |
| 6 | **E-commerce** | `ecommerce-apis-2440` | 2,440 | Amazon, Walmart, eBay, AliExpress pricing/scraping |
| 7 | **Integrations** | `integrations-apis-890` | 890 | Platform connectors, API bridges |
| 8 | **Jobs & Recruitment** | `jobs-apis-848` | 848 | LinkedIn, Indeed, Upwork, Glassdoor |
| 9 | **Lead Generation** | `lead-generation-apis-3452` | 3,452 | Google Maps, email/phone, B2B enrichment |
| 10 | **MCP Servers** | `mcp-servers-apis-131` | 131 | Model Context Protocol servers (Brave, Figma, Slack, etc.) |
| 11 | **News** | `news-apis-590` | 590 | News aggregators, RSS, media monitoring |
| 12 | **Open Source** | `open-source-apis-768` | 768 | GitHub, GitLab, open-source data |
| 13 | **Other** | `other-apis-1297` | 1,297 | Uncategorized, miscellaneous |
| 14 | **Real Estate** | `real-estate-apis-851` | 851 | Zillow, Realtor, Rightmove, property tools |
| 15 | **SEO Tools** | `seo-tools-apis-710` | 710 | Keywords, SERP, backlinks, domain tools |
| 16 | **Social Media** | `social-media-apis-3268` | 3,268 | Instagram, Twitter/X, TikTok, LinkedIn, Reddit |
| 17 | **Travel** | `travel-apis-397` | 397 | Flights, hotels, travel data |
| 18 | **Videos** | `videos-apis-979` | 979 | YouTube, TikTok, video download/transcription |

## Pricing Notes

- **Pay-per-result:** Most APIs cost $0.001–$0.50 per 1K results
- **Monthly subscriptions:** $7–$10/month for Twitter/X tools
- **Rental versions**: Extended access tiers available
- **Free tiers**: Some tools advertise no API keys needed or free usage
- All links contain affiliate code `fpr=p2hrc6`

## Common Search Patterns

```bash
# Find all MCP servers by function
grep -i "mcp" ~/Documents/Projects/API-mega-list/mcp-servers-apis-131/README.md | head -10

# Find social media scrapers by platform
grep -i "instagram\\|tiktok\\|twitter\\|linkedin" ~/Documents/Projects/API-mega-list/social-media-apis-3268/README.md | head -10

# Find e-commerce pricing APIs
grep -i "price\\|pricing\\|monitor" ~/Documents/Projects/API-mega-list/ecommerce-apis-2440/README.md | head -10

# Find lead generation tools
grep -i "email\\|phone\\|enrich" ~/Documents/Projects/API-mega-list/lead-generation-apis-3452/README.md | head -10

# Search for data about a specific topic (stocks, crypto, weather, etc.)
grep -i "stock\\|crypto\\|weather\\|news" ~/Documents/Projects/API-mega-list/*/README.md | head -15
```

## Data Search Patterns
When the user asks to "search for data about X" or "find data on X", use these targeted searches to find relevant APIs:

```bash
# Financial data (stocks, crypto, forex)
grep -i "stock\\|equit\\|crypto\\|forex\\|finance" ~/Documents/Projects/API-mega-list/*/README.md

# Economic/macro data
grep -i "gdp\\|inflation\\|unemployment\\|cpi" ~/Documents/Projects/API-mega-list/*/README.md

# Company/business data
grep -i "company\\|business\\|corporate\\|SEC\\|filing" ~/Documents/Projects/API-mega-list/*/README.md

# Location/geographic data
grep -i "geocode\\|map\\|location\\|address\\|coordinate" ~/Documents/Projects/API-mega-list/*/README.md

# Media/content data (videos, news, social)
grep -i "youtube\\|tiktok\\|instagram\\|news\\|trend" ~/Documents/Projects/API-mega-list/*/README.md
```

The 18 categories cover 26,005 APIs — many of which are dedicated data scrapers for specific verticals. If a data source exists on the public web, there's likely an Apify actor that can extract it.

## Integration with Existing Hermes Skills

| If the user asks about | Route this skill's output to |
|-----------------------|------------------------------|
| MCP servers | `mcp-integrations` — wire new MCP servers into Hermes config |
| Social media scraping | `ecc-bridge` — some ECC agents may complement these APIs |
| Lead generation | Cross-reference with the user's Apollo/ZoomInfo alternatives |
| Web scraping | `free-ai-tools` or direct Apify integration |
| AI content generation | `free-ai-model-router` for equivalent free model alternatives |

## Pitfalls

- **Affiliate links**: All API links contain `?fpr=p2hrc6` — these are Apify affiliate links
- **Category overlaps**: Some APIs appear in multiple categories; always search across all READMEs
- **Pricing may be outdated**: Verify prices on the actual Apify actor page before budgeting
- **Not all APIs are free**: Most are paid per-result or subscription; check pricing before recommending
- **README is huge**: The main README is 26K+ lines and 7MB; always search individual category directories for speed
- **Rate limits**: Apify actors have per-user rate limits; check the actor's Apify page for specifics
- **MCP Servers require setup**: MCP servers listed need to be wired into Hermes config.yaml (see `mcp-integrations` skill)

## Related
- `mcp-integrations` — for wiring MCP servers into Hermes config
- `free-ai-tools` — alternative free model/tool ecosystem
- `ecc-bridge` — ECC agents that may complement Apify scrapers
