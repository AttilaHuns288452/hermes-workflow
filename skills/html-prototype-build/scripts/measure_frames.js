#!/usr/bin/env node
// Per-frame fit metrics for fixed-size mockup frames (refit loop in SKILL.md).
// Usage: node measure_frames.js <fileOrUrl> <frameSelector> [contentSelector]
// Prints JSON [{i, frameH, contentBottom, gap, over, overX}] then pageOverX.
// Refit rule: over>0 -> grow the frame's height token by `over`; gap above the row's
// target band (~25-40px) -> shrink the height token by (gap - targetGap).
let pw;
try { pw = require('playwright'); }
catch (e) { pw = require(process.env.PLAYWRIGHT_PATH || '/home/attila/.hermes/hermes-agent/node_modules/playwright'); }
const path = require('path');

(async () => {
  const [target, frameSel, contentSel] = process.argv.slice(2);
  if (!target || !frameSel) {
    console.error('usage: node measure_frames.js <fileOrUrl> <frameSelector> [contentSelector]');
    process.exit(1);
  }
  const url = /^(https?|file):/.test(target) ? target : 'file://' + path.resolve(target);
  const browser = await pw.chromium.launch();
  const page = await browser.newPage({ viewport: { width: 4000, height: 1200 } });
  await page.goto(url, { waitUntil: 'load' });
  const out = await page.evaluate(([frameSel, contentSel]) => {
    const rows = [...document.querySelectorAll(frameSel)].map((f, i) => {
      const fr = f.getBoundingClientRect();
      const c = (contentSel && f.querySelector(contentSel)) || f.lastElementChild;
      const inner = c ? (c.lastElementChild || c) : null;
      const cb = inner ? inner.getBoundingClientRect().bottom - fr.top : fr.height;
      return { i, frameH: Math.round(fr.height), contentBottom: Math.round(cb),
               gap: Math.round(fr.height - cb), over: Math.round(Math.max(0, cb - fr.height)),
               overX: f.scrollWidth - f.clientWidth };
    });
    return { rows, pageOverX: Math.max(0, document.body.scrollWidth - document.body.clientWidth) };
  }, [frameSel, contentSel || null]);
  console.log(JSON.stringify(out, null, 1));
  await browser.close();
})().catch((e) => { console.error(e.message); process.exit(1); });
