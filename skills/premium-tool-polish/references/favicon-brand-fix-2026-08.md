# Favicon Brand Fix 2026-08 — freelance-rate-calculator

Follow-up to periwinkle pass. Fixes Vercel triangle favicon in browser tab.

## Problem
`app/favicon.ico` was default Next.js / Vercel triangle (26K, 4 icons). Browser tabs show it even after periwinkle redesign — generic AI fingerprint.

## Fix (commit 0b24f17, build 19/19 incl. `○ /icon.svg`)
- `app/icon.svg` — 32px tab icon:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="7" fill="#5e6ad2"/>
  <text x="16" y="19" text-anchor="middle" font-family="system-ui,sans-serif" font-weight="800" font-size="13" fill="white" letter-spacing="-0.5">FC</text>
</svg>
```
- `app/apple-icon.svg` — 180px iOS:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 180">
  <rect width="180" height="180" rx="36" fill="#5e6ad2"/>
  <text x="90" y="108" text-anchor="middle" font-family="system-ui,sans-serif" font-weight="800" font-size="78" fill="white" letter-spacing="-1.5">FC</text>
</svg>
```
- `app/favicon.ico` + `public/favicon.ico` — 627B Vista PNG-ICO via `sharp` (no new dep if already present):
```js
const sharp=require('sharp');
const svg='<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#5e6ad2"/><text x="16" y="19" text-anchor="middle" font-family="system-ui,sans-serif" font-weight="800" font-size="13" fill="white">FC</text></svg>';
const png=await sharp(Buffer.from(svg)).png().toBuffer();
const header=Buffer.alloc(6); header.writeUInt16LE(0,0); header.writeUInt16LE(1,2); header.writeUInt16LE(1,4);
const dir=Buffer.alloc(16); dir[0]=32; dir[1]=32; dir.writeUInt16LE(1,4); dir.writeUInt16LE(32,6); dir.writeUInt32LE(png.length,8); dir.writeUInt32LE(22,12);
require('fs').writeFileSync('app/favicon.ico', Buffer.concat([header,dir,png]));
require('fs').writeFileSync('public/favicon.ico', Buffer.concat([header,dir,png]));
```
Next.js auto-discovers `app/icon.*` / `app/apple-icon.*` / `app/favicon.ico` — no `metadata.icons` needed. `icon.svg` covers modern browsers immediately; `favicon.ico` covers hard-cached tabs.

## Verification
- `npm run build` → `○ /icon.svg` appears (19 routes), TypeScript clean
- Live: `curl -s https://freelancecalculator.xyz/icon.svg` returns periwinkle FC SVG
- Live: `curl -sI https://freelancecalculator.xyz/favicon.ico` → `200 image/vnd.microsoft.icon 627B`
- Client: hard-refresh `Ctrl+Shift+R` / clear site data — browsers cache favicons aggressively

## Why this shape
Single-color periwinkle + white FC matches glass-nav brand, `system-ui` avoids font load, `rx 7` matches `rounded-xl` system. Keeps `output: export` static compatible.

Skipped: ICO generation via `to-ico` / `favicons` lib, multi-size ICO — add when 16px/48px separately needed.
