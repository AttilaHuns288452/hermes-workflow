// generate-sitemap.js
// Place in: scripts/generate-sitemap.js
// Run via: node scripts/generate-sitemap.js (auto-runs after npm run build)
//
// This script writes sitemap.xml and robots.txt to both public/ (for dev)
// and out/ (for static export), with the correct domain URLs.
//
// To use: update BASE_URL to your deployed domain, add pages to PAGES array.
// The build script in package.json should run this after next build:
//   "build": "next build && node scripts/generate-sitemap.js"

const fs = require("fs");
const path = require("path");

// Change this to your actual deployed domain!
const BASE_URL = "https://your-site.vercel.app";

const PAGES = [
  { url: "", changefreq: "weekly", priority: 1.0 },
  { url: "/blog", changefreq: "weekly", priority: 0.8 },
  { url: "/privacy", changefreq: "yearly", priority: 0.3 },
  { url: "/terms", changefreq: "yearly", priority: 0.3 },
  { url: "/affiliate-disclosure", changefreq: "yearly", priority: 0.3 },
  // Add blog posts here:
  { url: "/blog/your-first-post", changefreq: "monthly", priority: 0.7 },
  { url: "/blog/your-second-post", changefreq: "monthly", priority: 0.7 },
];

function generateSitemap() {
  const today = new Date().toISOString().split("T")[0];

  const urls = PAGES.map(page => `  <url>
    <loc>${BASE_URL}${page.url}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>`).join("\n");

  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>`;

  const publicPath = path.join(__dirname, "..", "public", "sitemap.xml");
  const outPath = path.join(__dirname, "..", "out", "sitemap.xml");
  fs.writeFileSync(publicPath, sitemap);
  fs.writeFileSync(outPath, sitemap);

  // Auto-generate robots.txt with correct sitemap URL
  const robotsTxt = [
    "# Robots.txt",
    "User-agent: *",
    "Allow: /",
    "",
    "Sitemap: " + BASE_URL + "/sitemap.xml",
    "",
    "Crawl-delay: 10",
    "",
  ].join("\n");

  const robotsPublicPath = path.join(__dirname, "..", "public", "robots.txt");
  const robotsOutPath = path.join(__dirname, "..", "out", "robots.txt");
  fs.writeFileSync(robotsPublicPath, robotsTxt);
  fs.writeFileSync(robotsOutPath, robotsTxt);

  console.log("Sitemap and robots.txt generated for: " + BASE_URL);
}

generateSitemap();
