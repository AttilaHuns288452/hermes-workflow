# Free CLI SEO Audit Workflow

When PageSpeed Insights quota is exhausted, or you need a quick audit without paid tools, use this CLI-only workflow. Every tool below is free, no API keys required.

## 1. W3C HTML Validation

```bash
curl -s -H "Content-Type: text/html; charset=utf-8" \
  "https://validator.w3.org/nu/?out=json&doc=https://example.com" \
  | python -c "
import json, sys
d = json.load(sys.stdin)
msgs = d.get('messages',[])
errors = [m for m in msgs if m.get('type')=='error']
print(f'Errors: {len(errors)}, Other: {len(msgs)-len(errors)}')
for m in errors[:10]:
  print(f'  ERROR line {m.get(\"lastLine\",\"?\")}: {m.get(\"message\",\"\")[:120]}')
"
```

**Interpreting results:**
- **8 errors all about `button` descendant of `label` with `for`** → AdSense cookie consent code. Third-party, not fixable on your end. Low priority.
- **Errors about `trailing slash on void elements`** → Next.js default HTML output (`<br/>` vs `<br>`). Cosmetic only, XHTML-style slashes are valid HTML5. Medium-low priority.
- **0 errors** → Clean HTML. Good signal for technical SEO.

## 2. Security Headers

```bash
curl -sI "https://example.com" | head -20
```

**What Next.js/Vercel sites typically have:**
- ✅ `Strict-Transport-Security: max-age=63072000` — HSTS enabled
- ✅ `Server: Vercel` — hosted on Vercel
- ✅ `X-Vercel-Cache: HIT` — good caching
- ❌ Missing `Content-Security-Policy` — not critical for SEO but security best practice
- ❌ Missing `X-Frame-Options` — click-jacking protection
- ❌ Missing `X-Content-Type-Options` — MIME-sniffing protection
- ❌ Missing `Referrer-Policy` — referrer info control

**To add CSP on Vercel:** Use `vercel.json`:
```json
{
  "headers": [{
    "source": "/(.*)",
    "headers": [
      { "key": "Content-Security-Policy", "value": "default-src 'self'; img-src *; script-src 'self' 'unsafe-eval' 'unsafe-inline' https://pagead2.googlesyndication.com; style-src 'self' 'unsafe-inline'" },
      { "key": "X-Frame-Options", "value": "DENY" },
      { "key": "X-Content-Type-Options", "value": "nosniff" },
      { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" }
    ]
  }]
}
```

## 3. SSL Certificate Check

```bash
echo | openssl s_client -servername example.com -connect example.com:443 2>/dev/null \
  | openssl x509 -noout -subject -dates -ext subjectAltName 2>/dev/null
```

**Expected output:**
```
subject=CN=*.example.com
notBefore=Jun 17 08:49:26 2026 GMT
notAfter=Sep 15 08:49:25 2026 GMT    ← 90-day cert (Vercel auto-renewed)
X509v3 Subject Alternative Name: 
    DNS:*.example.com, DNS:example.com
```

**Red flags:**
- Certificate expired or expiring <7 days
- SubjectAltName missing the `www` subdomain
- Wildcard mismatch (e.g. `*.netlify.app` instead of `*.example.com`)

## 4. Raw HTML Content Audit

Save this Python script and pipe the site's HTML into it:

```python
#!/usr/bin/env python
"""Analyze raw HTML for SEO signals"""
import sys, re

html = sys.stdin.read()

imgs = len(re.findall(r'<img', html))
links = len(re.findall(r'<a ', html))
h1 = len(re.findall(r'<h1[ >]', html, re.I))
h2 = len(re.findall(r'<h2[ >]', html, re.I))
h3 = len(re.findall(r'<h3[ >]', html, re.I))

imgs_with_alt = len(re.findall(r'<img[^>]*alt="[^"]*"', html, re.I))
imgs_no_alt = imgs - imgs_with_alt
og_count = len(re.findall(r'property="og:', html))

print("Images: %d (%d with alt, %d without alt)" % (imgs, imgs_with_alt, imgs_no_alt))
print("Links: %d" % links)
print("Headings: h1=%d, h2=%d, h3=%d" % (h1 or 0, h2 or 0, h3 or 0))
print("Has canonical: %s" % ("canonical" in html.lower()))
print("OG tags: %d" % og_count)
print("Has JSON-LD: %s" % ("application/ld+json" in html))
print("Page size: %d bytes" % len(html))
print("Meta viewport: %s" % ("viewport" in html.lower()))
print("Meta description: %s" % ("name=\"description\"" in html.lower() or "name='description'" in html.lower()))
print("Robots meta: %s" % ("robots" in html.lower()))
```

Usage:
```bash
curl -s "https://example.com" | python analyze.py
```

**Critical signals (fix immediately):**
- `h1=0` in raw HTML → heading is client-rendered by React. Google may see no heading at all. Add server-rendered H1 + H2 in the page component.
- `Images: N (0 with alt)` → all images loaded via JS/React. Verify each has `alt` attribute in the JSX.
- `Has canonical: False` → missing canonical tag on this page.

## 5. Server-Rendered Headings Pattern (Next.js)

If a Next.js page shows `h1=0` in raw HTML but shows headings in the browser, the heading is rendered by client-side React. Fix:

**Bad (React-only heading):**
```tsx
// app/page.tsx
export default function Home() {
  return <QuizLoader />;  // Heading is inside this client component
}
```

**Good (server-rendered + React UI):**
```tsx
// app/page.tsx
export default function Home() {
  return (
    <>
      <h1 className="sr-only">Page Title — Site Name</h1>
      <section className="max-w-4xl mx-auto px-4 mb-6 text-center">
        <h2 className="text-3xl font-bold">Visible Heading</h2>
        <p className="text-gray-600 text-lg">
          Intro paragraph describing the page. 30-50 words with key terms.
        </p>
      </section>
      <QuizLoader />  {/* Client component below the SEO content */}
    </>
  );
}
```

**Why this works:** The server-rendered H1 (sr-only for screenreaders, visible to bots) + H2 + intro paragraph appear in the raw HTML that Googlebot receives. The React component hydrates below them, adding interactive content. Google sees both layers.

## 6. React Duplicate ID / Key Bug Detection

If search/filter UI returns wrong results (e.g. searching "Bleach" shows non-Bleach characters):

```bash
# Check for duplicate IDs in data file
grep -oP 'id: "\K[^"]+' lib/data.ts | sort | uniq -d
```

**Bug signature:** Duplicate `id` values used as React `key` props cause reconciliation failures — React reuses stale DOM nodes instead of properly filtering.

**Fix:** Remove duplicate entries. For entries that differ meaningfully (e.g. same person at different life stages), assign unique IDs.

**Guard (add to CI/build):**
```bash
# In package.json scripts or CI pipeline
python -c "
import re
with open('lib/data.ts') as f:
    ids = re.findall(r'id: \"([^\"]+)\"', f.read())
if len(ids) != len(set(ids)):
    from collections import Counter
    dupes = {k:v for k,v in Counter(ids).items() if v>1}
    raise SystemExit(f'ERROR: Duplicate IDs found: {dupes}')
print(f'OK: {len(set(ids))} unique IDs')
"
```

## 7. Indexly API Quick Reference

If the user has an Indexly API key and wants to check SEO visibility:

```bash
# Validate key
curl -s --request GET --url 'https://app.indexly.ai/api/v1/validate' \
  --header 'X-API-Key: KEY_HERE'

# Visibility history (requires Growth plan)
curl -s "https://app.indexly.ai/api/v1/brand-analysis/SITE_ID/history?days=30" \
  --header 'X-API-Key: KEY_HERE'

# Competitor analysis (requires Growth plan)
curl -s "https://app.indexly.ai/api/v1/brand-analysis/SITE_ID/brands" \
  --header 'X-API-Key: KEY_HERE'
```

**Free tier limitation:** Visibility and brand analysis endpoints return `"Upgrade Required"` on non-Growth plans. The free tier only supports key validation and dashboard access via web UI.

**Finding site IDs:** Log in to app.indexly.ai → the URL after `/dashboard/sites/` is the site ID (e.g., `https://app.indexly.ai/dashboard/sites/6a34.../setup` → `6a34...`).
