# Vercel Deployment on Windows — GitHub Import Workflow

Deploying a Next.js (or any static) site to Vercel from a Windows environment. The **GitHub import** path is the most reliable; the Vercel CLI (`vercel deploy`) frequently fails on Windows due to credential/browser OAuth and npm/npx tar issues.

## Reliable Workflow: Build → Git Push → Vercel Import

### Step 1 — Build locally
```bash
cd ~/your-project
npm run build
```

If using Next.js static export, verify `out/` directory was created with an `index.html`.

### Step 2 — Push to GitHub
```bash
git add -A
git commit -m "Deployment update"
git push
```

### Step 3 — Import on Vercel
1. Go to `https://vercel.com/new` in a browser
2. Sign in with GitHub (OAuth flow)
3. Select the repository from the GitHub import list
4. Vercel auto-detects Next.js and configures the build
5. Deploy — within ~1-2 minutes the site is live
6. On every subsequent `git push`, Vercel auto-deploys

## Why the GitHub Import Path Works

| Problem | Cause | Solution |
|---------|-------|----------|
| `npx vercel deploy` | Requires `vercel login` which opens a browser OAuth — impossible in headless terminal | GitHub import avoids the CLI entirely |
| `npm install -g vercel` tar errors on Windows | MSYS/npm cache corruption — `TAR_ENTRY_ERROR ENOENT` during npx extraction | Don't use CLI; use GitHub import |
| CLI `--token` flag | Need to generate a Vercel API token via the web UI first | Circular dependency — can't generate token without browser |
| CI/CD setup complexity | Environment variables, deploy hooks, team permissions | GitHub import is 3 clicks with zero config |

## Vercel Site URL

After import, Vercel assigns a URL like:
```
https://<project-name>-<random-slug>.vercel.app
```

## How to Update the Live Site

1. Make changes locally
2. `npm run build` (verify no errors)
3. `git add -A && git commit -m "desc" && git push`
4. Vercel auto-deploys the new build (~1-2 min)

## Updating Sitemap URL

The sitemap's `<loc>` URLs must match your actual deployment URL:

```javascript
// scripts/generate-sitemap.js (or equivalent)
const BASE_URL = "https://your-project.vercel.app"; // ← update this
```

Also update `openGraph.url` in `app/layout.tsx` (or your metadata file) to match.

## Post-Deployment: Google Search Console Setup

### Step 1 — Add verification meta tag
1. Go to `https://search.google.com/search-console`
2. Click **"Add property"** → **"URL prefix"**
3. Enter your Vercel URL (e.g. `https://project.vercel.app`)
4. Choose **"HTML tag"** verification
5. Copy the `<meta name="google-site-verification" content="...">` tag
6. Add the `content` value to your metadata in `app/layout.tsx`:

```typescript
verification: {
  google: "your-verification-code-here",
},
```

7. `git commit && git push` — Vercel auto-deploys with the tag live
8. Back in Search Console, click **"Verify"** — green checkmark confirms

### Step 2 — Submit sitemap
1. In Search Console, click **"Sitemaps"** in the left sidebar
2. Enter: `sitemap.xml`
3. Click **Submit**

### Step 3 — Troubleshooting "Couldn't fetch"
If Search Console shows **"Couldn't fetch"** for your sitemap:

**Most likely cause: robots.txt has a wrong Sitemap URL.**

Check your live robots.txt:
```bash
curl https://your-site.vercel.app/robots.txt
```

If it shows a Sitemap URL pointing to the wrong domain (old custom domain, localhost, etc.), Googlebot follows that URL and fails. Fix:

1. Update your build script (e.g. `scripts/generate-sitemap.js`) to also write `robots.txt` with the correct `Sitemap` URL on every build:

```javascript
// In your sitemap generation script, add:
const robotsTxt = `User-agent: *
Allow: /

# Sitemap
Sitemap: ${BASE_URL}/sitemap.xml

# Crawl-delay
Crawl-delay: 10
`;
// Write to both public/ and out/
fs.writeFileSync(robotsPublicPath, robotsTxt);
fs.writeFileSync(robotsOutPath, robotsTxt);
```

2. Also update `robots.txt` as a static file in `public/` as a fallback.
3. `git push` → Vercel auto-deploys → Search Console auto-fetches the correct URL on next crawl.

If the sitemap was already submitted with a stale URL, **delete it first** (three-dot menu → "Delete sitemap"), then re-submit.

**Other causes of "Couldn't fetch":**
- Search Console property uses **"Domain"** type but sitemap was submitted under **"URL prefix"** (or vice versa) — check which property type you created
- Sitemap URL has a trailing slash issue — try both `/sitemap.xml` and `sitemap.xml`
- Google just hasn't crawled yet — wait 24-48 hours

## Monetization Checklist (for beginner-friendly SaaS launches)

After the site is live and indexed:

### Affiliate Programs (higher value per conversion)
- **FreshBooks**: `freshbooks.com/affiliate` — $10-20/signup
- **Upwork**: `upwork.com/affiliate` — $50-100/signup
- **Mercury**: `mercury.com/affiliate` — $200-500/funded account
- **Bonsai**: `hellobonsai.com/affiliate` — $20-50/signup

Replace placeholder URLs in your affiliate component, rebuild, push.

### Google AdSense
- Apply at `adsense.google.com` once ~20 pages are indexed
- Tool pages (calculators) have higher RPM ($4-8 vs typical $1-2)
- Insert the AdSense script in your `<head>` and use `<ins class="adsbygoogle">` placeholders in your layout

### Google Analytics 4
- Create a property in `analytics.google.com`
- Get your Measurement ID (starts with `G-`)
- Add the GA4 script and gtag config to your layout's `<head>`

## Beginners: How to Get First Visitors

Copy-paste this to Reddit, Facebook groups, or LinkedIn:

> *"I made a free tool to figure out what to charge as a freelancer. Calculates your real hourly rate including taxes, health insurance, and unpaid time off. We all undercharge without realizing it. Try it: https://your-site.vercel.app"*

Best places:
- **Reddit**: r/freelance, r/Upwork, r/copywriting, r/webdev — sort by "New" and find people asking about rates
- **Facebook**: "Freelancers United", "Digital Nomad Life"
- **LinkedIn**: Post as a status update with the link

## Vercel CLI — Token-Based Deploy (Working on Windows)

The CLI path **works on Windows** when you have a Vercel API token. Steps:

1. Get a token from `https://vercel.com/account/tokens` (create one via browser)
2. Deploy from the project root:
   ```bash
   cd /c/Users/.../project
   npx vercel deploy --prod --yes --token <token>
   ```
   The `--yes` flag is required to confirm without interactive prompts.
   The `--prod` flag promotes to the production URL immediately.
3. The CLI links the project automatically on first deploy, then caches the link for subsequent deploys.

**Note:** `--yes` must come BEFORE `--token` in some Vercel CLI versions. Correct order: `vercel deploy --prod --yes --token <token>`.

This path avoids GitHub webhook setup entirely — useful when auto-deploy isn't configured.

## Common Pitfalls

- **Auto-deploy not triggering after git push**: If Vercel doesn't auto-deploy after a push, first check the Vercel dashboard → Deployments tab to see if a build was triggered. If nothing appears after 2-3 minutes, the GitHub integration webhook may be stale. Fixes:
  1. Add a `vercel.json` to explicitly declare the framework — this kicks Vercel's framework detection into re-evaluating the project:
     ```json
     { "framework": "nextjs", "buildCommand": "npm run build", "outputDirectory": ".next", "installCommand": "npm install" }
     ```
  2. Push an empty commit to force a recheck: `git commit --allow-empty -m "Trigger Vercel deploy"`
  3. **Manual fallback**: Go to Vercel dashboard → Project → Deployments → click ⋮ → "Redeploy" → "Build and deploy". This always works regardless of webhook state.
  4. **Token-based CLI fallback**: If the webhook is disconnected, deploy directly using Vercel CLI with a token (see "Vercel CLI — Token-Based Deploy" above). This works on Windows as long as you have a valid Vercel API token. The CLI does NOT need `vercel login` — just `--token <token>` is sufficient.\n- `metadataBase` must be set for custom domains
- **`metadataBase` must be set for custom domains**: If deploying with a custom domain (e.g., `www.example.com`), set `metadataBase` in `layout.tsx` at the top of the metadata object. Without it, OG images and Twitter cards resolve to `http://localhost:3000`, producing broken share previews:
  ```typescript
  export const metadata: Metadata = {
    metadataBase: new URL("https://www.example.com"),
    // ... rest of metadata
  };
  ```
- **No `.env` on Vercel**: If the site needs API keys at build time, add them in Vercel Dashboard → Project → Settings → Environment Variables.
- **Wrong root directory**: If using a monorepo, configure the root directory in Vercel project settings.
- **Build fails on Vercel but works locally**: Check Node.js version — Vercel may use a different default version. Set `engines` in `package.json` or configure in Vercel settings.
- **Static export + `next/link`**: Static exports on Vercel work fine, but routing is client-side only. All pages listed in the build output will be served.
- **Domain not yet purchased**: The `.vercel.app` subdomain works indefinitely for free — no need to buy a custom domain to start earning.
- **robots.txt with stale sitemap URL**: If you change domains or deployment URLs, the robots.txt `Sitemap:` URL must be updated. Auto-generate it from your build script to prevent stale URLs.
- **Search Console "Couldn't fetch"**: Always check `robots.txt` first — it's the #1 cause for beginners. The sitemap URL in robots.txt must exactly match the property URL in Search Console.