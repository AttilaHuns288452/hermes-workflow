# Google Search Console Setup Guide

## Step 1: Add Property
1. Go to `https://search.google.com/search-console`
2. Click "Add property"
3. Choose **"URL prefix"** (NOT "Domain" — this is important)
4. Enter your full URL
5. Click "Continue"

### ⚠️ CRITICAL: www vs non-www MUST match your sitemap

Before adding the property, determine your site's canonical URL:
```bash
# Check which version redirects to which
curl -s -o /dev/null -w '%{http_code} -> %{redirect_url}' "https://your-site.com/"
echo ""
curl -s -o /dev/null -w '%{http_code} -> %{redirect_url}' "https://www.your-site.com/"
```

- If non-www returns 200 and www redirects → **property must be `https://your-site.com`** (non-www)
- If www returns 200 and non-www redirects → **property must be `https://www.your-site.com`** (www)
- The sitemap URL in robots.txt must also match this canonical version

**Google will NOT follow 307/308 redirects on sitemap URLs.** If your sitemap is at `https://www.example.com/sitemap.xml` but your GSC property is `https://example.com` (non-www), Google will get a redirect at the property level and report "Couldn't fetch" even though the sitemap itself works fine.

## Step 2: Verify Ownership

**Option A — HTML meta tag (for URL prefix property):**
1. Copy the `<meta name="google-site-verification" content="...">` tag
2. Paste it into your `app/layout.tsx` file:
   ```tsx
   verification: {
     google: "your-verification-code-here",
   },
   ```
3. Build and deploy (`git push` auto-deploys to Vercel)
4. Go back to Search Console and click "Verify"
5. You should see a green checkmark

**Option B — DNS TXT record (for Domain property, covers all subdomains):**
1. Google gives you a TXT value: `google-site-verification=xxxxx`
2. Go to Vercel → Project → Domains tab → click your domain → "Edit DNS Records"
3. Click "Add Record":
   - Type: TXT
   - Name: @
   - Value: `google-site-verification=xxxxx`
   - TTL: Auto or 60
4. Click Add → Save
5. Wait 1-5 minutes (DNS propagation)
6. Go back to Search Console → click "Verify"

## Step 3: Submit Sitemap
1. In Search Console, click "Sitemaps" in the left sidebar
2. In the "Add a new sitemap" box, type: `sitemap.xml`
3. Click "Submit"

## Troubleshooting "Couldn't Fetch"

**First — verify the sitemap itself works:**
```bash
curl -sL https://your-site.com/sitemap.xml | head -10
# Should return valid XML with 200 OK
```

**If the sitemap loads fine but GSC says "Couldn't fetch", systematically check:**

### Check 1: GSC property type (MOST COMMON CAUSE)
- Did you add the property as **"URL prefix"** (correct) or **"Domain"** (problematic for sitemap)?
- URL prefix property = exact URL match required. If your sitemap is at `https://www.example.com/sitemap.xml` but your property is `https://example.com` (non-www), **Google can't match them** because the non-www 308-redirects to www.
- Fix: Delete the property, re-add with the **exact same www/non-www form** as your sitemap URL.

### Check 2: robots.txt Sitemap URL
```bash
curl -sL https://your-site.com/robots.txt
```
Must contain `Sitemap: https://your-site.com/sitemap.xml` — the URL must match the property exactly.

### Check 3: No 308 redirects on sitemap URLs
For Vercel sites with `trailingSlash: true` in next.config.ts:
```bash
# Check if any sitemap URLs redirect
curl -s https://your-site.com/sitemap.xml | grep -oP '<loc>\K[^<]+' | while read url; do
  echo -n "$(curl -s -o /dev/null -w '%{http_code}' "$url") $url"
  echo ""
done
```
If any show **308**, the sitemap URL is missing a trailing slash. Fix: add `/` to all URLs in the sitemap.

### Check 4: Force Google to re-crawl (don't wait 24-48h)
If sitemap is technically correct but GSC still shows an old "Couldn't fetch":
1. In Search Console → **Sitemaps** → click your sitemap URL
2. Click the **"Test"** button
3. Wait 10-30 seconds — if green check ✅ "Sitemap is valid", the technical fix is working
4. Then click **"Request Indexing"** to force Google to update the status
5. Alternatively, use **URL Inspection**: paste `https://your-site.com/sitemap.xml` → "Request Indexing"

The "Test" feature does a live fetch in real-time and bypasses cached failure results.

### Check 5: DNS resolution from Google
```bash
# Verify DNS resolves from Google's own DNS (8.8.8.8)
nslookup your-site.com 8.8.8.8
```
Should return IP addresses (Vercel edge IPs). If it fails, your DNS is misconfigured and Google can't reach your site.

### Quick reference: "Couldn't fetch" causes
| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| sitemap.xml loads fine in browser, GSC says couldn't fetch | GSC property type (www vs non-www) or stale cache | Re-add correct property, or use "Test" → "Request Indexing" |
| URLs inside sitemap return 308 | trailingSlash mismatch | Add/remove trailing slashes to match next.config |
| sitemap.xml returns 404 | Not in public/ or build script broken | Check public/sitemap.xml exists |
| robots.txt wrong Sitemap URL | BASE_URL changed | Update in build script, rebuild, push |
| "Pending" for days | Google hasn't crawled yet | Use "Test" → "Request Indexing" to force |
