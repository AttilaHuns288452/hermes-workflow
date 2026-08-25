# SEO Trailing-Slash Canon

`output: "export"` + `trailingSlash: true` (freelance) vs `trailingSlash: false` (anime-waifu).

- Sitemap template (`scripts/generate-sitemap.js`): freelance uses `/blog/.../` (with slash). Canonical must match or Google sees duplicates.
- Fix: loop all `app/blog/*/*.tsx`, add trailing `/` to `canonical: "https://freelancecalculator.xyz/blog/..."`
- Layout template: `title: { default, template: "%s | Brand" }` + `robots` object with `googleBot` large preview.
- robots.txt: never `Crawl-delay` — edit both `public/robots.txt` and the JS template that regenerates it.
- Verify: `curl -s https://site | grep canonical` should end with `/` iff `trailingSlash: true`.
