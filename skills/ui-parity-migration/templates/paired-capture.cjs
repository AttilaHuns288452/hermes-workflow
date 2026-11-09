// Starter harness: paired capture of APP vs REFERENCE at the same routes/roles/viewports.
// Copy, fill APP_URL / REF_URL / ACCOUNTS / password source, then: node paired-capture.cjs
// Output: <OUT>/<side>/<role>-<route>-<vp>.png + matching .txt (innerText) for side-by-side diffing.
const { chromium } = require('playwright');
const fs = require('fs');

const APP_URL = 'https://app.example.com';
const REF_URL = 'https://reference.example.com';
const OUT = '/tmp/cmp';
const ACCOUNTS = { patient: 'maria@example.com', doctor: 'doctor@example.com', owner: 'owner@example.com' };
const PASSWORD = process.env.QA_PASSWORD || '';
const ROUTES = {
  patient: ['/', '/appointments', '/book', '/profile'],
  doctor: ['/doctor', '/doctor/calendar'],
  owner: ['/owner', '/owner/manage'],
};
const VPS = { desktop: { width: 1440, height: 900 }, mobile: { width: 390, height: 844 } };

// Landmark wait: never settle on a fixed timeout (lazy chunks paint empty shells for seconds).
async function waitHydrated(page) {
  for (let i = 0; i < 25; i++) {
    try {
      const t = await page.evaluate(() => document.body.innerText);
      if (!/Loading/.test(t) && t.split('\n').filter(Boolean).length > 6) return true;
    } catch (e) { /* navigation in flight */ }
    await page.waitForTimeout(800);
  }
  return false;
}

async function login(page, base, email) {
  await page.goto(base, { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForTimeout(1200);
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', PASSWORD);
  // The form's submit button. Do NOT use button:has-text("Sign in") — that is the mode toggle.
  await page.locator('form button:not([type="button"])').first().click();
  await page.waitForLoadState('domcontentloaded').catch(() => {});
  return waitHydrated(page);
}

async function captureSet(base, outDir, label) {
  const browser = await chromium.launch();
  for (const role of Object.keys(ROUTES)) {
    for (const [vpName, vp] of Object.entries(VPS)) {
      const ctx = await browser.newContext({ viewport: vp, locale: 'en-US', timezoneId: 'Asia/Manila' });
      const page = await ctx.newPage();
      const ok = await login(page, base, ACCOUNTS[role]);
      console.log(label, role, vpName, ok ? 'hydrated' : 'STUCK');
      for (const route of ROUTES[role]) {
        const tag = `${role}-${route === '/' ? 'home' : route.replace(/\//g, '_').replace(/^_/, '')}-${vpName}`;
        await page.goto(base + route, { waitUntil: 'domcontentloaded', timeout: 45000 }).catch(() => {});
        await waitHydrated(page);
        await page.screenshot({ path: `${outDir}/${tag}.png`, fullPage: true }).catch(() => {});
        fs.writeFileSync(`${outDir}/${tag}.txt`, await page.evaluate(() => document.body.innerText));
      }
      await ctx.close();
    }
  }
  await browser.close();
}

(async () => {
  fs.mkdirSync(`${OUT}/app`, { recursive: true });
  fs.mkdirSync(`${OUT}/ref`, { recursive: true });
  await captureSet(APP_URL, `${OUT}/app`, 'app');
  await captureSet(REF_URL, `${OUT}/ref`, 'ref');
  // Then: normalize both .txt sets (trim, drop blank lines) and line-diff the pairs.
  // Classify each diff line as DATA / INTENTIONAL / UI-GAP — only UI-GAP is work.
})();
