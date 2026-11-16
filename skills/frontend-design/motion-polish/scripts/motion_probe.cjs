#!/usr/bin/env node
// Motion perception probe. Proves an entrance is SEEABLE, not merely running.
//
// Usage: node motion_probe.cjs <url> [--region=x,y,w,h] [--ms=150] [--frames=16]
//        [--out=/tmp] [--playwright=/path/to/playwright]
//
// Reports:
//   1. Per-frame mean absolute pixel delta timeline. The page-appear frame is
//      usually one enormous value; animation is everything AFTER it.
//   2. Which animation/transition lifecycle events actually fired.
//   3. 'motion share': deltas after the page-appear frame as a fraction of total
//      visual change. Low share + short tail = the user sees 'it loaded'.
//
// Run against PRODUCTION when the question is 'can the user see it', and against
// a local build when iterating. Requires Pillow for the pixel diff.

const path = require('path');
const fs = require('fs');
const { execFileSync } = require('child_process');

const argv = process.argv.slice(2);
const arg = (name, dflt) => {
  const hit = argv.find((a) => a.startsWith('--' + name + '='));
  return hit ? hit.split('=').slice(1).join('=') : dflt;
};

function loadPlaywright() {
  const candidates = [arg('playwright', null), process.env.PLAYWRIGHT_MODULE, 'playwright'].filter(Boolean);
  for (const c of candidates) {
    try { return require(c.startsWith('.') || c.startsWith('/') ? path.resolve(c) : c); }
    catch (e) { /* try next */ }
  }
  console.error('Could not resolve playwright. Pass --playwright=/path/to/playwright or set PLAYWRIGHT_MODULE.');
  process.exit(2);
}

(async () => {
  const url = argv.find((a) => !a.startsWith('--'));
  if (!url) { console.error('Usage: node motion_probe.cjs <url> [--region=x,y,w,h]'); process.exit(2); }
  const region = arg('region', null);
  const interval = Number(arg('ms', 150));
  const frames = Number(arg('frames', 16));
  const outDir = arg('out', '/tmp');

  const { chromium } = loadPlaywright();
  const browser = await chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: 1440, height: 1000 } })).newPage();

  // Real lifecycle events. Zero here means nothing animated at all.
  await page.addInitScript(() => {
    window.__motionEvents = [];
    for (const type of ['animationstart', 'animationend', 'transitionrun', 'transitionend']) {
      document.addEventListener(type, (e) => {
        window.__motionEvents.push({ type, name: e.animationName || e.propertyName || '?', t: Math.round(performance.now()) });
      }, true);
    }
  });

  const t0 = Date.now();
  await page.goto(url, { waitUntil: 'load' });
  const clip = region
    ? region.split(',').reduce((o, v, k) => Object.assign(o, { [['x', 'y', 'width', 'height'][k]]: Number(v) }), {})
    : null;
  const shots = [];
  for (let i = 0; i < frames; i++) {
    const file = path.join(outDir, 'motion-frame-' + i + '.png');
    await page.screenshot(clip ? { path: file, clip } : { path: file });
    shots.push({ file, ms: Date.now() - t0 });
    await page.waitForTimeout(interval);
  }
  const events = await page.evaluate(() => window.__motionEvents || []);
  await browser.close();

  const py = [
    'from PIL import Image, ImageChops',
    'import json, sys',
    'files = json.load(open(sys.argv[1]))',
    'prev = None; out = []',
    'for f in files:',
    '    im = Image.open(f["file"]).convert("RGB")',
    '    if prev is not None:',
    '        d = ImageChops.difference(prev, im)',
    '        out.append({"ms": f["ms"], "delta": round(sum(d.convert("L").getdata())/(im.width*im.height), 2)})',
    '    prev = im',
    'print(json.dumps(out))',
  ].join('\n');
  const listFile = path.join(outDir, 'motion-files.json');
  fs.writeFileSync(listFile, JSON.stringify(shots));
  const deltas = JSON.parse(execFileSync('python3', ['-c', py, listFile], { encoding: 'utf8' }));

  const peak = Math.max(1e-9, ...deltas.map((d) => d.delta));
  const appearIdx = deltas.findIndex((d) => d.delta === peak);
  const after = deltas.slice(appearIdx + 1);
  const afterSum = after.reduce((s, d) => s + d.delta, 0);
  const total = deltas.reduce((s, d) => s + d.delta, 0) || 1e-9;

  console.log('frame timeline (mean abs pixel delta):');
  for (const d of deltas) {
    console.log('  t' + String(d.ms).padStart(5) + 'ms ' + String(d.delta).padStart(7) + ' ' + '#'.repeat(Math.min(40, Math.round(d.delta / 3))));
  }
  console.log('\npage-appear frame: t' + (deltas[appearIdx] ? deltas[appearIdx].ms : '?') + 'ms (delta ' + peak.toFixed(1) + ')');
  console.log('motion after appear: ' + after.length + ' frames, ' + afterSum.toFixed(1) + ' total, ' + ((afterSum / total) * 100).toFixed(1) + '% of all visual change');
  console.log('last visible delta at t' + (after.length ? after[after.length - 1].ms : 'n/a') + 'ms');
  console.log('\nanimation events fired: ' + events.length);
  const byName = {};
  for (const e of events) byName[e.type + ':' + e.name] = (byName[e.type + ':' + e.name] || 0) + 1;
  for (const k of Object.keys(byName)) console.log('  ' + k + ' x' + byName[k]);

  console.log('\nread:');
  console.log('  - 0 events              -> nothing animated; the code is not shipping or not applying.');
  console.log('  - events, low share / short tail -> motion drowned by the page-appear event;');
  console.log('    stage the entrance AFTER first paint and raise travel/duration.');
  console.log('  - target: deltas still moving ~1s after first paint, motion share >~30%.');
})();
