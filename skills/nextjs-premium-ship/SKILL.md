---
name: nextjs-premium-ship
description: Polish and ship premium Next.js static sites.
---

# Next.js Premium Ship

Class-level skill for turning `output: "export"` Next.js sites from boring to premium and shipping SEO-clean.

## When to use
- User says site is boring / wants premium / periwinkle polish
- Tab still shows Vercel triangle (`app/favicon.ico` default)
- SEO sitemap vs canonical drift, `Crawl-delay` present, missing title templates

## Premium redesign (periwinkle system)

**No new deps, shortest diff.** One `globals.css` pass + `layout.tsx` + `page.tsx` + component accents.

- `globals.css` `@theme`: `--color-primary-*` → `#5e6ad2` / `#4f46e5` / `#4338ca`, `--background #f8f9ff`, `glass-nav` (blur 16px + saturate 1.2), `card` (20px radius, soft shadow + inset), `premium-input`, slider thumb `#5e6ad2`, grain via SVG turbulence.
- `layout.tsx`: `themeColor #5e6ad2`, `glass-nav` header `h-[60px]` `max-w-6xl`, `Try it →` pill, `bg-[#f8f9ff]`.
- `page.tsx` hero: dark `#0f1229` with 3 periwinkle mesh blobs + grid + grain, editorial `Design your ideal freelance` gradient `[#a5b4fc → white → #c7d2fe]`, glass badges, peek rate card (desktop, `rotate-[1.5deg]`). Guides/timeline/FAQ/CTA all `#eef2ff` / `#c7d2fe` with hover lift.
- `RateCalculator.tsx` `sliderFill`: `linear-gradient(to right, #5e6ad2 0%, #818cf8 ${pct}%, #eef2ff ...)`
- `ResultCard.tsx`: hero `from-[#5e6ad2] via-[#4f46e5] to-[#3730a3]`, billable bar same, cards `#eef2ff`/`#c7d2fe`.

## Fitting favicons (not boring FC)

Next.js App Router auto-discovers `app/icon.*` + `app/apple-icon.*` + `app/favicon.ico`. No `<link rel="icon">` needed.

```bash
# 32px tab + 180px Apple + ICO via sharp (already installed)
# freelance: periwinkle gradient #5e6ad2→#312e81, white calculator + $ + 9-dot grid
# anime-waifu: dark #0f0f1a, purple→pink→blue heart + sparkle (matches quiz vibe)

# Then generate ICO (Vista PNG-ICO, 32x32)
node -e "
const fs=require('fs'), sharp=require('sharp');
(async()=>{
  const svg=fs.readFileSync('app/icon.svg','utf8');
  const png=await sharp(Buffer.from(svg)).png().toBuffer();
  const h=Buffer.alloc(6); h.writeUInt16LE(0,0); h.writeUInt16LE(1,2); h.writeUInt16LE(1,4);
  const d=Buffer.alloc(16); d[0]=32; d[1]=32; d.writeUInt16LE(1,4); d.writeUInt16LE(32,6);
  d.writeUInt32LE(png.length,8); d.writeUInt32LE(22,12);
  const ico=Buffer.concat([h,d,png]);
  fs.writeFileSync('app/favicon.ico', ico);
  fs.writeFileSync('public/favicon.ico', ico);
})();
"

# Remove legacy tag in anime-waifu layout.tsx
# Before: <link rel="icon" href="/logo.png" type="image/png" />
# After:  (delete it — let Next discover app/icon.svg)

# Pitfall: patching layout with escaped quotes breaks CRLF preconnect
# Fix: <link rel="preconnect" href="https://fonts.googleapis.com" /> — not rel=\"preconnect\"

# Verify
curl -s https://example.com/icon.svg | head -c 400
curl -sI https://example.com/favicon.ico  # Content-Type: image/vnd.microsoft.icon
npm run build  # freelance 19 pages incl /icon.svg, waifu 434 incl /icon.svg
```

User signal: plain `FC` text on `#5e6ad2` reads as boring. Always add a fitting shape (calculator, heart, etc.) + gradient.

## SEO quick wins (output:export + trailingSlash)

- `public/robots.txt`: **remove `Crawl-delay: 10`** — throttles Googlebot/Bing, never helps.
- Canonical drift: `next.config.ts` `trailingSlash: true` + `scripts/generate-sitemap.js` uses `/blog/.../` → blog `canonical` must end with `/`. Loop-fix 7 files:
  ```bash
  for f in app/blog/*/*.tsx; do
    node -e "let t=require('fs').readFileSync('$f','utf8');
    t=t.replace(/canonical:\s*\"https:\/\/freelancecalculator\.xyz(\/blog\/[^\"]+)\"/g,(m,p)=>p.endsWith('/')?m:m.replace(p,p+'/'));
    require('fs').writeFileSync('$f',t)"
  done
  ```
- `layout.tsx` titles: `title: { default: "...", template: "%s | Freelance Calculator" }` so subpages get suffix.
- `robots`: object ` { index:true, follow:true, googleBot:{ index:true, follow:true, "max-image-preview":"large","max-snippet":-1,"max-video-preview":-1 } }` unlocks large previews.
- Keep `alternates.canonical` + `openGraph.url` trailing-slash consistent with sitemap.

## Ship

```bash
npm run build  # 18/18 + 427 char pages, TypeScript clean
git add app/icon.svg app/apple-icon.svg app/favicon.ico public/favicon.ico app/layout.tsx public/robots.txt scripts/generate-sitemap.js app/blog/
git commit -m "feat: premium polish + fitting favicons + SEO canon fix"
git push origin master  # Vercel auto-deploys
curl -s https://example.com/robots.txt | grep -v Crawl-delay
curl -s https://example.com | grep -o 'rel="canonical"[^>]*'
```

## References

- `references/periwinkle-system.md` — full #5e6ad2 token map
- `references/favicon-sharp-ico.md` — SVG → PNG-ICO recipe, CRLF pitfall
- `references/seo-trailing-slash.md` — trailingSlash canon audit

## Pitfalls (from session)

- `Crawl-delay` in `generate-sitemap.js` regenerates `robots.txt` on every build — edit the JS template, not just `public/robots.txt`.
- `git checkout -- public/sitemap.xml` after build — sitemap is generated, don't commit churn.
- Sharp must be available for ICO gen (already in both projects via Next deps). No new package needed.
