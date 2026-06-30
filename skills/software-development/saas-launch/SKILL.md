---
name: saas-launch
description: "End-to-end workflow for building, deploying, SEO-optimizing, and monetizing a SaaS or side-project web app. Covers Next.js build, SEO content, Vercel deploy, Google Search Console, Google Analytics, AdSense, affiliate monetization, and traffic generation. Handles beginner-level handholding with step-by-step instructions."
triggers:
  - saas
  - side project
  - launch
  - monetize
  - deploy to vercel
  - make money from website
  - publish web app
  - freelance tool
  - calculator app
  - bootstrap saas
  - zero experience deploy
platforms: [windows, linux, macos]
---

# SaaS Launch - Build, Deploy, Monetize

## When to Use

- User asks to build a web app/SaaS/tool that can make money
- User has zero experience and needs hand-holding (step-by-step, no jargon assumed)
- User wants to deploy a Next.js static site to Vercel
- User asks about monetization: AdSense, affiliates, lead magnets
- User needs help getting first visitors (Reddit, LinkedIn, Facebook groups)

## User Preferences (Filipino Audience / Zero-Experience)

When the user is Filipino or has zero experience:
- **Use Taglish (Tagalog + English)** for social post templates targeting Filipino freelancer Facebook groups
- **Refer to dollar amounts as USD but explain in PHP context** — "Kita USD, gastos PHP" is a powerful framing
- **Lead with lifestyle aspirations** — "walang commute, naka-pambahay lang, may time para sa pamilya" resonates more than "earn more money"
- **Give exact copy-paste posts** — users with zero experience need exact templates, not suggestions to "write something"
- **List numbered actionable steps** — "Step 1: Go to X, Step 2: Click Y" format, not paragraphs
- **Show expected outcomes** — each step should say "Expected: X visitors" or "Expected: $Y/month" so they know what to expect
- **Use Facebook group suggestions** — Freelancers Philippines, VA Philippines, Online Filipino Freelancers are the primary channels
- **Avoid platform-jargon** — say "the link to your site" not "your deployment URL"

## Core Workflow

### Phase 1 - Build

1. **Define the core value proposition** - one clear job the tool does
2. **Scaffold with Next.js App Router + TypeScript + Tailwind** — For **static hosts** (GitHub Pages, S3, Netlify): use `output: "export"` in next.config.ts. For **Vercel**: `output: "export"` can work with GitHub import — keep `outputDirectory` at `.next` in vercel.json (the default). Vercel's builder generates both `.next/` (routing metadata) and `out/` (static files) and serves correctly. Remove `output: "export"` only if the app uses API routes, middleware, or needs SSR/ISR features.
3. **Keep it zero-dependency runtime** - no auth, no DB, no API keys for MVP
4. **Add help tooltips** on every form field - users without domain knowledge need guidance. Pattern:
   - `FieldConfig.help` - plain-language explanation
   - `FieldConfig.tip` - a concrete typical range hint
   - `lifeLabel` - optional reframe to lifestyle/outcome language
   - Rendered via a HelpIcon component (click-to-reveal popover)
5. **Add "Not sure?" entry point** - a button below the heading that shows preset cards with descriptions, so users who have no idea what numbers to put can click one to get started. See `templates/help-tooltip-components.tsx` for the `NotSureBanner` component pattern.
6. **Lifestyle-first messaging** - users respond better to "design your ideal life" than "calculate your rate". Reframe the tool around the outcome (freedom, lifestyle, dreams) not the mechanics (numbers, rates, formulas). Replace field labels with lifestyle questions (see `templates/help-tooltip-components.tsx` for the `lifeLabel` pattern).
7. **Essential pages**: Privacy Policy, Terms of Service, Affiliate Disclosure (legal compliance for monetization)

### Phase 2 - SEO Content

1. **Blog index page** (`/blog/page.tsx`) with post cards (title, description, date, read time)
2. **3-5 blog posts targeting keywords** (1,000-2,000 words each with internal links back to the tool)
   - Each post gets its own directory: `app/blog/<keyword-slug>/page.tsx`
   - Include Open Graph metadata per post
   - Use `prose` classes for readable long-form content
   - End each post with a CTA linking back to the tool
3. **Auto-generated sitemap** - script that writes `public/sitemap.xml`, `out/sitemap.xml`, and `public/robots.txt` with correct `Sitemap:` URL
4. **robots.txt must match the deployed domain** - use build script to auto-generate with the right `BASE_URL`
5. **Metadata** — set a default in `app/layout.tsx` (title, description, keywords, Open Graph, Twitter Card, verification meta tags), then **override per page** (see "Per-page metadata" section below)
6. **`robots.txt` + `sitemap.xml`** — create both files directly in `public/`. On Vercel, files in `public/` are served automatically at the root — no build script needed to copy them to `out/`. See `references/static-files-setup.md` for exact file contents.

#### ⚠️ Next.js App Router — per-page metadata (avoid duplicate titles)

Every page MUST export its own `metadata` object. The root layout's metadata is a **fallback default** — if you don't override it per page, ALL pages will share the SAME `<title>` and `<meta name="description">` in search results. SEO crawlers (Indexly, Screaming Frog) will flag this as a critical issue.

**The fix** — add to every `app/<route>/page.tsx`:

```tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Unique Title for This Page — Site Name",
  description: "Unique description that describes what's on this specific page.",
};
```

**Client components (`"use client"`):** You cannot export `metadata` from them. Split into two files:
1. `app/<route>/page.tsx` (server component) — exports metadata, imports client form
2. `app/<route>/FormComponent.tsx` (client component) — keeps `"use client"`, exports nothing

Example — feedback page split:
```tsx
// app/feedback/page.tsx — SERVER
import type { Metadata } from "next";
import FeedbackForm from "./FeedbackForm";
export const metadata: Metadata = {
  title: "Feedback & Suggestions — Site Name",
  description: "Share your feedback, suggest new characters, or report bugs.",
};
export default function FeedbackPage() { return <FeedbackForm />; }
```

```tsx
// app/feedback/FeedbackForm.tsx — CLIENT
"use client";
export default function FeedbackForm() { /* ... form JSX ... */ }
```

**Detection** via curl:
```bash
# Each page must show a DIFFERENT <title>
for page in "" "/quiz" "/about" "/contact"; do
  echo -n "$page → "
  curl -s "https://your-site.com${page}" | grep -oP '<title>[^<]+</title>' || echo "(none)"
done
```

**Sitemap + metadata relationship:** After adding unique metadata per page, update `public/sitemap.xml` to include ALL routes so Google can crawl and index each page's distinct title/description.

### Phase 3 - Deploy to Vercel

**Checking deployment status via GitHub:**
After a `git push`, Vercel's bot adds a check-run on the commit. To find the deployment URL from the terminal:
```bash
# List latest deployments
gh api repos/<owner>/<repo>/deployments -q '.[0].statuses_url'
gh api <statuses_url> -q '.[0].target_url'
```
The Vercel bot comments with a preview URL and a production URL once the build completes. If the build fails, the check will be marked "failure" with a link to the build logs.

**Custom domain setup:**
After buying a domain through Vercel (Domains tab → "Buy a Domain"), the site auto-routes. No DNS config needed for basic serving.

**GitHub import method (recommended for beginners):**
1. Create GitHub repo - push source
2. Go to `vercel.com/new` - "Import Git Repository" - select the repo
3. Vercel auto-detects Next.js and builds on push - no config needed
4. Every `git push` triggers auto-deploy
5. **`vercel.json` `outputDirectory`** — must be `".next"` (the default). Changing it to `"out"` breaks the build because Vercel reads `routes-manifest.json` from this directory, and that file only exists in `.next/`. If you see `The file "/vercel/path0/out/routes-manifest.json" couldn't be found`, this is the cause — revert `outputDirectory` to `".next"`.

**Drag-drop method (fallback for static export):**
1. Build locally: `npm run build`
2. Drag the `out/` folder to `vercel.com/new` - "Drag and drop your project folder here"
3. Note: this does NOT auto-deploy on updates (manual re-drag required)
4. Note: drag-drop works for static exports (`output: "export"`) because Vercel serves the `out/` folder as static files. GitHub import method also works with `output: "export"` — just keep `outputDirectory` as `.next` (the default) in vercel.json. Drag-drop is simpler but doesn't auto-deploy.

### Phase 4 - Google Setup

**Google Search Console:**
1. Verify via HTML meta tag in `app/layout.tsx` under `verification.google` — this works for **URL prefix** property type
2. For **Domain** property type (covers all subdomains), you need a DNS **TXT record**:
   - Go to Vercel → Your Project → **Domains** tab → click the domain → **"Edit DNS Records"**
   - Add a **TXT record** with Name `@` and Value `google-site-verification=<code>`
   - Click Add → Save → wait 1-5 minutes → click "Verify" in Search Console
3. Submit `sitemap.xml` after verification
4. "Couldn't fetch" usually means:
   - robots.txt has wrong `Sitemap:` URL (fix in build script)
   - Property added as "Domain" instead of "URL prefix" (delete and re-add)

**Google Analytics 4:**
1. Create property at `analytics.google.com`
2. Get Measurement ID (`G-XXXXXXXXXX`)
3. Add GA4 script to `app/layout.tsx` head using `dangerouslySetInnerHTML`
4. Replace ALL 3 placeholders (appears in script src, gtag config, and dataLayer)

### Phase 5 - Monetization

| Method | Setup Time | Revenue Potential | Notes |
|--------|-----------|-------------------|-------|
| Google AdSense | 30 min + 2-4 week approval | $2-15/mo at 500-2K visits | Needs ~20 pages indexed first |
| Affiliate Marketing | 30 min per program | $10-500+/mo | Best ROI per visitor |
| Lead Magnet (email capture) | 1-2 hrs | Future upsells | Free PDF - email - affiliate |

**Affiliate Programs for Freelance/Business Tools:**
| Program | Sign Up | Payout |
|---------|---------|--------|
| FreshBooks | freshbooks.com/affiliate | $10-20/signup |
| Upwork | upwork.com/affiliate | $50-100/signup |
| Mercury (banking) | mercury.com/affiliate | $200-500/funded |
| Bonsai (contracts) | hellobonsai.com/affiliate | $20-50/signup |
| Novo (banking) | novo.co/affiliate | $50-100/signup |
| QuickBooks | quickbooks.intuit.com/affiliate | $10-50/signup |

**Affiliate Links as Friendly Recommendations (non-affiliate UX):**

If the user is NOT actually affiliated with the services they recommend, convert the links to a subtle footer bar:

```tsx
// Small recommendation pills at the bottom of the page, not a big section
const RECOMMENDATIONS = [
  { name: "FreshBooks", desc: "Accounting", url: "https://www.freshbooks.com/", icon: "\uD83D\uDCCA" },
  { name: "Upwork", desc: "Find work", url: "https://www.upwork.com/", icon: "\uD83D\uDCBC" },
];

// Render as small inline pill badges in the footer:
// "Tools freelancers might find useful: FreshBooks · Upwork · Mercury · Bonsai"
```

Pattern:
- Remove the word "affiliate" entirely
- No commission amounts
- No "we earn from links" disclaimers
- Place in footer corner as small text
- Use pill-style badges or simple inline text separators (·)
- Remove separate Affiliate Disclosure page if not needed

**AdSense Integration:**
- Add script to `<head>` in layout
- Add `<ins>` placeholder in the component (at results section, after results show)
- Mark ads with `no-print` class for clean PDF exports
- Replace `ca-pub-XXXXXXXXXXXXXXXX` with real publisher ID
- **Create `public/ads.txt`** — AdSense requires an `ads.txt` file in the site root directory. The file must contain exactly: `google.com, pub-<YOUR_ID>, DIRECT, f08c47fec0942fa0`
- Also copy ads.txt to `out/` during build (in the generate script)
- **Update generate script** — add a step that copies `public/ads.txt` to `out/ads.txt` and also auto-generates `robots.txt` with the correct `Sitemap:` URL
- **Run `npm run build` after all changes** to ensure out/ contains the latest files

### Phase 6 - Traffic Generation

**Social Post Templates (tailor to audience):**

General English (Reddit, LinkedIn, Facebook):
```
I made a free calculator that shows freelancers their real hourly rate
- including taxes, health insurance, and unpaid time off. We all undercharge
without realizing it. Try it: [URL]
```

Filipino audience (Facebook groups, r/buhaydigital):
```
Ano bang ideal freelance life ang gusto mo? Walang commute, kita USD,
time with family. Gumawa ako ng free tool na lifestyle designer -
sabihin mo lang yung buhay na gusto mo, kukwentahin nito yung rate
na kailangan mo. Libre: [URL]
```

**Reddit Strategy:**
- DO NOT create new posts with your link (will get banned)
- DO sort by "New" in relevant subreddits and reply to people asking for help
- Good subreddits: r/freelance, r/Upwork, r/buhaydigital, r/webdev (Showoff Saturday), r/SideProject, r/coolgithubprojects
- Reply template: "I was in the same boat - this free calculator helped me figure it out: [URL]"

**Platform-Specific Tips:**
- LinkedIn: post as status update (no restrictions)
- Facebook Groups: "Freelancers Philippines", "VA Philippines", "Digital Nomads"
- Rotation: post every 2-3 days, rotate the angle (helpful tip vs personal story vs question to group)

## Pitfalls

- **sitemap.xml and robots.txt use the old domain** if you change URLs - always update the `BASE_URL` in the build script and push to trigger rebuild
- **Google Search Console "Couldn't fetch"** is usually a sitemap URL mismatch or property type mismatch, not an actual XML issue
- **Reddit bans self-promotion** - always reply to existing questions, never create a new post with your link
- **AdSense needs indexed content** - don't apply until Google has crawled at least 10-20 pages (usually 2-4 weeks after sitemap submission)
- **Affiliate links need `rel="noopener noreferrer"`** and an FTC-compliant disclosure page
- **Static export limitations** - no API routes, no server-side features. If the tool needs backend logic, use client-side JavaScript or an external API
- **Help tooltip positioning** - on mobile, tooltips that overflow should auto-flip. Use `bottom-full` + `left-1/2 -translate-x-1/2` as default, test on mobile viewport
- **`.vercel.app` URLs blocked on Facebook** - Facebook treats `*.vercel.app` as suspicious/temporary and blocks posts containing them. Must use a custom domain or a link shortener (Bit.ly, TinyURL) to share on Facebook
- **AdSense `crossOrigin` prop in JSX** - use `crossOrigin` (capital O) not `crossorigin` in Next.js TSX files, or TypeScript will fail the build
- **Inline `<script>` in Next.js head** - must use `dangerouslySetInnerHTML={{ __html: `...` }}` rather than plain `<script>` tags, or Next.js Turbopack will fail to parse the JavaScript syntax
- **Domain change requires URL updates in 3 places** - when buying a new domain, update (1) `scripts/generate-sitemap.js` BASE_URL, (2) `app/layout.tsx` OpenGraph `url` and `siteName`, (3) `app/layout.tsx` JSON-LD schema `url`. Then rebuild and push
- **Vercel bot deployment on GitHub** — after a `git push`, find the deployment URL via `gh api repos/<owner>/<repo>/deployments` and check the latest status. The green checkmark (✓) next to a commit on GitHub shows Vercel's deployment link — click it to open the preview
- **`git pull --rebase` before push when Vercel bot conflicts** — Vercel may push auto-generated branches (e.g. `vercel/install-vercel-speed-insights-wqtnhw`, `vercel/install-vercel-web-analytics-feszdl`) and occasionally commits to master (config changes, speed-insights setup). If `git push` is rejected with "Updates were rejected because the remote contains work that you do not have locally", run `git pull --rebase && git push` to integrate and retry
- **Vercel + `output: "export"` works** — Contrary to some advice, GitHub import works fine with `output: "export"` as long as `outputDirectory` stays at `.next` in vercel.json. The build produces both `.next/` (routing metadata including `routes-manifest.json`) and `out/` (static files). Vercel serves the static files correctly. **Error signature**: `The file "/vercel/path0/out/routes-manifest.json" couldn't be found` means `outputDirectory` was incorrectly set to `"out"` — revert to `".next"`.
- **Vercel `outputDirectory` must be `".next"`** — If you change `outputDirectory` in `vercel.json` to `"out"`, Vercel's framework builder will fail because it needs `routes-manifest.json` which lives in `.next/`. This file is generated by `next build` regardless of `output: "export"` setting. Always keep `outputDirectory: ".next"` (or omit it, since `.next` is the default) when using `framework: "nextjs"`.
- **`public/` files are served automatically on Vercel** — No build script is needed to copy `public/robots.txt`, `public/sitemap.xml`, or `public/ads.txt` to `out/`. Vercel serves files from `public/` directly at the root URL. The copy-to-out script is only needed for static host deploys.
- **Vercel Search Console Domain verification needs TXT record in Vercel DNS** — for Domain property (not URL prefix), add a TXT record under Vercel → Project → Domains → Edit DNS Records. Type `TXT`, Name `@`, Value `google-site-verification=<code>`. No external DNS provider needed if domain was bought through Vercel
- **AdSense verification flow** — after adding the AdSense code and `ads.txt`, go back to AdSense and click the appropriate verify button. AdSense checks both the `<script>` tag in `<head>` and the `ads.txt` file in the root. If it says the `ads.txt` can't be found, make sure (1) `public/ads.txt` exists with the correct content and (2) the build output (`out/`) includes the file via a copy script. For Next.js projects on Vercel, `public/` files are served directly at the root path — no special handling needed.
- **Browser showing ads.txt as raw text is normal** — the browser will display the `ads.txt` content as plain text (`google.com, pub-...`) since it's not HTML. This is correct behavior and does not mean something is broken.

### Feedback Form Component Pattern

After the MVP is built, add a feedback form to collect user suggestions. Pattern:

```tsx
function FeedbackForm() {
  const [name, setName] = useState("");
  const [message, setMessage] = useState("");
  const [sent, setSent] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Store in localStorage — no backend needed for MVP
    const existing = JSON.parse(localStorage.getItem("<project>-feedback") || "[]");
    existing.push({ name, message, date: new Date().toISOString() });
    localStorage.setItem("<project>-feedback", JSON.stringify(existing));
    setSent(true);
  };

  if (sent) {
    return <p className="text-green-600 font-medium text-sm">Thank you for your feedback! 🙏</p>;
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <input type="text" placeholder="Your name (optional)" ... />
      <textarea placeholder="How can we improve?" required rows={3} ... />
      <button type="submit">Send Feedback 💬</button>
    </form>
  );
}
```

Add the FeedbackForm component to the same file as the main component (or as a separate import). Place it below the results section, wrapped in a card matching the site's design system.

**Upgrade path for real submissions:** localStorage-only feedback is a dead-end (you never see the submissions). To get real feedback:

1. Create a Google Form at `https://forms.google.com/` with fields for Name + Message
2. Publish and get the embed URL (looks like `https://docs.google.com/forms/d/e/.../viewform?embedded=true`)
3. Replace the inline form with an `<iframe>` pointing to that URL, or embed the form link in the thank-you message
4. Google Form submissions are emailed to you automatically (Google Forms → Responses → email notification)

## Verification

```bash
curl -sL https://<url>/ -> 200 with correct <title>
curl -sL https://<url>/sitemap.xml -> valid XML with correct <loc> URLs
curl -sL https://<url>/robots.txt -> has correct Sitemap: URL
curl -sL https://<url>/ads.txt -> contains google.com, pub-...
All blog pages return 200
OG image loads at /og-image.png
Privacy, Terms pages all return 200
```

On Vercel, `public/` files are served directly at root — verify with curl, no `out/` check needed.

## Related Skills

- `software-development/setup` - initial project scaffolding
- `productivity/ai-marketing-skills` - ongoing marketing automation after launch
- `workflow/task_tier` - classifies request scope
- `note-taking/obsidian` - documentation after project is built

## Post-Launch SEO Audit & Monitoring

After deployment, run a free CLI-based SEO audit to check for issues before Google does:

```bash
# 1. HTML validation (W3C)
curl -s -H "Content-Type: text/html; charset=utf-8" \
  "https://validator.w3.org/nu/?out=json&doc=https://your-site.com" \
  | python -c "import json,sys; d=json.load(sys.stdin); print('Errors:', len([m for m in d['messages'] if m.get('type')=='error']))"

# 2. Security headers
curl -sI "https://your-site.com" | head -20

# 3. Raw HTML content audit (headings, images, alt text, OG tags, canonical)
curl -s "https://your-site.com" | python analyze.py

# 4. All pages return 200
for page in "" "/blog" "/privacy" "/terms"; do
  echo "$page → $(curl -so /dev/null -w '%{http_code}' \"https://your-site.com${page}\")"
done
```

See `references/free-cli-seo-audit.md` for the full CLI audit workflow including:
- React heading detection (server-rendered vs client-only)
- React duplicate key debugging for search/filter components
- SSL certificate inspection
- Indexly API quick reference (if the user monitors via Indexly)

## Supporting Files

- **`references/google-search-console-setup.md`** — Search Console property setup, verification, and sitemap submission
- **`references/social-post-templates.md`** — Platform-specific post templates for Reddit, Facebook, LinkedIn
- **`references/adsense-and-vercel-dns.md`** — AdSense ads.txt creation, real AdSense ID replacement, and Search Console Domain verification via Vercel DNS TXT records
- **`references/free-cli-seo-audit.md`** — Complete free CLI SEO audit workflow: W3C validation, security headers, SSL check, content analysis, React heading detection, duplicate key debugging, and Indexly API reference
