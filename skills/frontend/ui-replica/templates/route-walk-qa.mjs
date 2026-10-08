// Role × route walk QA harness — copy and edit CONFIG.
// Requires: playwright (NODE_PATH=<hermes-agent>/node_modules if not global).
// Usage: node route-walk-qa.mjs   → shots in OUT + "page errors: N" (must be 0).
import { chromium } from 'playwright'

const CONFIG = {
  BASE: 'http://localhost:4177', // local preview, or the LIVE deployment URL
  OUT: '/tmp/replica-shots',
  roles: [
    {
      name: 'patient',
      // localStorage keys the app's context reads at mount; set BEFORE route loads
      session: { 'dv_demo_session': { user: { id: 'u-pat' }, role: 'patient' } },
      routes: ['/', '/book', '/appointments'],
    },
    { name: 'doctor', session: {}, routes: ['/doctor'] },
    { name: 'owner', session: {}, routes: ['/owner'] },
  ],
}

const b = await chromium.launch()
const errors = []
for (const cfg of CONFIG.roles) {
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })
  const page = await ctx.newPage()
  page.on('pageerror', (e) => errors.push(`[${cfg.name}] pageerror: ${String(e).slice(0, 200)}`))
  page.on('console', (m) => { if (m.type() === 'error') errors.push(`[${cfg.name}] console: ${m.text().slice(0, 200)}`) })
  await page.goto(CONFIG.BASE + '/', { waitUntil: 'networkidle' })
  await page.evaluate((s) => { for (const [k, v] of Object.entries(s)) localStorage.setItem(k, typeof v === 'string' ? v : JSON.stringify(v)) }, cfg.session)
  for (const route of cfg.routes) {
    await page.goto(CONFIG.BASE + route, { waitUntil: 'networkidle' })
    await page.waitForTimeout(450)
    const safe = route.replace(/\//g, '_') || '_root'
    await page.screenshot({ path: `${CONFIG.OUT}/${cfg.name}-${safe}.png`, fullPage: true })
    const body = await page.evaluate(() => document.body.innerText)
    if (/\bLoading\b/.test(body) && body.length < 40) errors.push(`[${cfg.name}] ${route} stuck on Loading`)
  }
  await ctx.close()
}
console.log('page errors:', errors.length)
errors.forEach((e) => console.log(' ', e))
await b.close()
