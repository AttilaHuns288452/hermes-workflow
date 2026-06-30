# AdSense ads.txt Setup + Search Console Domain Verification

## Ads.txt Setup

When AdSense asks you to create an `ads.txt` file, it will give you a line like:
```
google.com, pub-4645179646749256, DIRECT, f08c47fec0942fa0
```

### Steps:

1. Create `public/ads.txt` in the project root with that exact line
2. Update the build script (`scripts/generate-sitemap.js`) to copy ads.txt to the `out/` folder:
   ```javascript
   const adsTxt = fs.readFileSync(path.join(__dirname, "..", "public", "ads.txt"), "utf-8");
   fs.writeFileSync(path.join(__dirname, "..", "out", "ads.txt"), adsTxt);
   ```
3. Update AdSense script `<src>` in layout from placeholder `ca-pub-XXXXXXXXXXXXXXXX` to real `ca-pub-XXXXXXXXXX`
4. Update any `<ins>` ad units in components (they have `data-ad-client="ca-pub-..."`) — there may be multiple
5. Rebuild and push: `npm run build && git add -A && git commit -m "Add AdSense ID and ads.txt" && git push`
6. After Vercel deploys, verify: `curl https://yoursite.com/ads.txt` should return your AdSense line
7. Click **"I've published the ads.txt file"** in AdSense

### File location on Vercel (GitHub deployment):
- Static file at `public/ads.txt` → available at `https://yoursite.com/ads.txt`
- Must be copied to `out/ads.txt` during the build script for static export

## Google Search Console Domain Verification via Vercel DNS

### Problem: "Couldn't fetch" or "Domain not verified"

When adding a **Domain** property (not URL prefix) in Search Console:

1. Search Console gives you a TXT record value: `google-site-verification=<code>`
2. Go to Vercel → Project → **Domains** → click your domain → **"Edit DNS Records"**
3. Click **"Add Record"** and enter:
   - **Type:** `TXT`
   - **Name:** `@` (or leave empty)
   - **Value:** `google-site-verification=<code>`
   - **TTL:** `60` or Auto
4. Click **Add** → **Save**
5. Wait 1-5 minutes for propagation (Vercel DNS propagates fast)
6. Go back to Search Console → click **"Verify"**

### Why it says "Couldn't fetch"
- Most common: property is "Domain" type but sitemap was submitted with full URL instead of just `sitemap.xml`
- Second most common: robots.txt `Sitemap:` URL uses the wrong domain
- Third: the sitemap was just submitted and Google hasn't crawled it yet (wait 1-24 hours)
- New domains sometimes need 24-48 hours for full DNS propagation across Google's crawler infrastructure

### Verification type comparison
| Method | Property Type | Best For |
|--------|--------------|----------|
| HTML meta tag in layout.tsx | **URL prefix** (e.g. `https://site.com/`) | Single subdomain, quick setup |
| TXT DNS record in Vercel | **Domain** (e.g. `site.com`) | Covers all subdomains, better for SEO |
