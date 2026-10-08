// guide_qa.mjs — validate a self-contained offline docs handbook.
// Usage: node guide_qa.mjs <file:///abs/path/to/HANDBOOK.html>
// Requires playwright (adjust the import path to your install).
import { chromium } from '/home/attila/.hermes/hermes-agent/node_modules/playwright/index.mjs';

const URL = process.argv[2] || 'file:///home/attila/Documents/Projects/dentalvibe/DENTALVIBE_ENGINEERING_GUIDE.html';
const b = await chromium.launch();
const results = [], errs = [];

async function offlinePage(w, h) {
  const ctx = await b.newContext({ viewport: { width: w, height: h }, reducedMotion: 'reduce' });
  await ctx.route('**/*', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  const p = await ctx.newPage();
  p.on('console', m => { if (m.type() === 'error') errs.push(`[${w}px] ${m.text().slice(0, 120)}`); });
  p.on('pageerror', e => errs.push(`[${w}px] pageerror: ${String(e).slice(0, 120)}`));
  return p;
}

for (const [w, h] of [[390, 844], [768, 1024], [1024, 768], [1440, 900]]) {
  const p = await offlinePage(w, h);
  await p.goto(URL, { waitUntil: 'load' });
  await p.waitForTimeout(1500); // paint settle — screenshots taken earlier come out blank
  const doc = await p.evaluate(() => {
    // behavioral overflow check: scrollWidth over-reports when inner pre/table
    // wrappers hold wide scroll content; actual scrollability is the truth
    window.scrollTo(400, 0); const canScrollX = window.scrollX > 0; window.scrollTo(0, 0);
    return { canScrollX, sections: document.querySelectorAll('main > section').length };
  });
  results.push(`${w}px: h-scroll=${doc.canScrollX ? 'YES' : 'no'} sections=${doc.sections}`);
  await p.screenshot({ path: `guide_shot_${w}.png` });
  if (w === 390) {
    await p.click('#menuBtn'); await p.waitForTimeout(250);
    results.push(`390px drawer opens: ${await p.evaluate(() => document.querySelector('nav.side').classList.contains('open'))}`);
    await p.click('nav.side a'); await p.waitForTimeout(300);
    results.push(`390px nav jump hash: ${await p.evaluate(() => location.hash)}`);
  }
  if (w === 1440) {
    await p.fill('#search', 'RLS'); await p.waitForTimeout(200);
    results.push(`search 'RLS': ${await p.evaluate(() => document.querySelectorAll('#searchResults a').length)} hits`);
    await p.evaluate(() => document.querySelector('.copy').scrollIntoView());
    await p.click('.copy'); await p.waitForTimeout(150);
    results.push(`copy label after click: "${await p.evaluate(() => document.querySelector('.copy').textContent)}"`);
    const id = await p.evaluate(() => document.querySelector('main > section:nth-child(3)').id);
    await p.goto(URL + '#' + id, { waitUntil: 'load' }); await p.waitForTimeout(300);
    results.push(`deep link #${id}: "${await p.evaluate(() => document.querySelector('#' + location.hash.slice(1) + ' h2')?.textContent)}"`);
    await p.click('#themeBtn'); await p.waitForTimeout(150);
    results.push(`theme toggle: ${await p.evaluate(() => document.documentElement.dataset.theme)}`);
  }
}
await b.close();
console.log(results.join('\n'));
console.log('console/page errors:', errs.length ? '\n' + errs.join('\n') : 'NONE');
