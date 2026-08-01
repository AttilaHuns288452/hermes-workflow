#!/usr/bin/env bash
# Validate a deployed sitemap.xml: check XML structure, URL count, and redirects
# Usage: bash validate-sitemap.sh https://example.com/sitemap.xml
# Depends on: curl, python3 (for xml.etree.ElementTree)

set -euo pipefail

SITEMAP_URL="${1:-}"
if [ -z "$SITEMAP_URL" ]; then
  echo "Usage: $0 <sitemap-url>"
  echo "Example: $0 https://example.com/sitemap.xml"
  exit 1
fi

echo "=== Sitemap: $SITEMAP_URL ==="

# 1. HTTP status and content type
HTTP_CODE=$(curl -s -o /tmp/sitemap.xml -w "%{http_code}" "$SITEMAP_URL")
CONTENT_TYPE=$(curl -sI "$SITEMAP_URL" | grep -i "^content-type:" | sed 's/.*: //')
echo "HTTP $HTTP_CODE | Content-Type: $CONTENT_TYPE"

if [ "$HTTP_CODE" != "200" ]; then
  echo "❌ Sitemap returned HTTP $HTTP_CODE (expected 200)"
  exit 1
fi

# 2. Validate XML structure and extract URLs
python3 -c "
import xml.etree.ElementTree as ET, sys
try:
    tree = ET.parse('/tmp/sitemap.xml')
    root = tree.getroot()
    ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    urls = root.findall(f'{ns}url')
    print(f'✅ Valid XML — {len(urls)} URLs')
    for u in urls:
        loc = u.find(f'{ns}loc')
        if loc is not None:
            url = loc.text
            lastmod = u.find(f'{ns}lastmod')
            changefreq = u.find(f'{ns}changefreq')
            tags = []
            if lastmod is not None: tags.append('lastmod')
            if changefreq is not None: tags.append('changefreq')
            tag_str = f' ({', '.join(tags)})' if tags else ''
            print(f'  {url}{tag_str}')
except ET.ParseError as e:
    print(f'❌ XML Parse Error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"

# 3. Check each URL for redirects
echo ""
echo "=== Checking for redirects ==="
BASE=$(echo "$SITEMAP_URL" | sed 's|/sitemap.xml||')
grep -oP '<loc>\K[^<]+' /tmp/sitemap.xml | while read -r url; do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>&1)
  REDIRECT=$(curl -s -o /dev/null -w "%{redirect_url}" "$url" 2>&1)
  if [ "$HTTP_CODE" = "200" ]; then
    echo "  ✅ $url → 200"
  elif [ "$HTTP_CODE" = "308" ]; then
    echo "  ❌ $url → 308 → $REDIRECT (trailing slash mismatch?)"
  else
    echo "  ⚠️  $url → $HTTP_CODE${REDIRECT:+ → $REDIRECT}"
  fi
done

rm -f /tmp/sitemap.xml
echo ""
echo "✅ Done"
