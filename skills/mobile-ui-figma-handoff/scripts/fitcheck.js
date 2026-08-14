// Vertical-fit + frame-origin check for generated mobile UI design files.
// Usage: node fitcheck.js <dir-with-html-files>
// Checks per file: frame sits at y=0 (phantom-space detector), frame scrollHeight
// fits the design height (default 844), deepest element bottom within the frame.
// Prints OK/CLIP per file; exit code 1 if any CLIP.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const dir = process.argv[2];
const H = process.argv[3] ? parseInt(process.argv[3]) : 844;
if (!dir) { console.error('usage: node fitcheck.js <dir> [height=844]'); process.exit(2); }

(async () => {
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.html')).sort();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 500, height: 20000 } });
  let bad = 0;
  for (const f of files) {
    await page.goto('file:///' + path.join(dir, f).replace(/\\/g, '/'), { waitUntil: 'networkidle' });
    const m = await page.evaluate((H) => {
      const fr = document.querySelector('.frame');
      if (!fr) return { noFrame: true };
      const frr = fr.getBoundingClientRect();
      let deepest = { bottom: -1, what: '' };
      for (const el of fr.querySelectorAll('*')) {
        const r = el.getBoundingClientRect();
        if (r.height > 0 && r.bottom > deepest.bottom) deepest = { bottom: Math.round(r.bottom), what: el.tagName.toLowerCase() + '.' + String(el.className).split(' ')[0] };
      }
      return { y: Math.round(frr.y), scrollH: fr.scrollHeight, clientH: fr.clientHeight, deepest: deepest.bottom, what: deepest.what };
    }, H);
    if (m.noFrame) { console.log(`SKIP ${f}: no .frame`); continue; }
    const yOff = m.y !== 0 ? ` Y=${m.y}` : '';
    const clip = m.scrollH > H + 1 || m.deepest > H + 1;
    if (clip) bad++;
    console.log(`${clip ? 'CLIP' : 'OK  '} ${f}: scrollH=${m.scrollH} clientH=${m.clientH} deepestBottom=${m.deepest}${yOff ? yOff + ' <- phantom space?' : ''}`);
  }
  await browser.close();
  process.exit(bad ? 1 : 0);
})();
