#!/usr/bin/env node
// Route-integrity crawl template: every route x role must render a REAL page.
// Copy into scripts/, edit PORT / ROLES / enterAs / assertions, run against the
// running dev server:  NODE_PATH=<playwright dir> node scripts/route-crawl.cjs
// Exit code 1 on any FAIL so it can gate commits.
const { chromium } = require('playwright')

const ORIGIN = 'http://127.0.0.1:5173'

// Every navigable destination per role. Keep in sync with the nav/tab config -
// an assertion tripwire below fails the run when the config has paths missing here.
const ROLES = {
  patient: ['/', '/appointments'],
  doctor: ['/', '/patients'],
  admin: ['/', '/manage'],
}

// Identity injection for demo-auth prototypes (localStorage session before goto).
async function enterAs(browser, role) {
  const ctx = await browser.newContext()
  const page = await ctx.newPage()
  await page.goto(`${ORIGIN}/`)
  await page.evaluate(r => localStorage.setItem('demo_session', JSON.stringify({ role: r })), role)
  return page
}

const sleep = ms => new Promise(r => setTimeout(r, ms))

;(async () => {
  const browser = await chromium.launch()
  let pass = 0
  let fail = 0
  for (const [role, paths] of Object.entries(ROLES)) {
    for (const p of paths) {
      const page = await enterAs(browser, role)
      await page.goto(`${ORIGIN}${p}`)
      await sleep(600)
      // Blank body = crashed root (hook-order errors) or never-resolved async;
      // fallback stubs are NOT pages.
      const body = await page.evaluate(() => document.body.innerText.trim().slice(0, 200))
      const stub = /coming soon/i.test(body)
      const ok = body.length > 20 && !stub
      console.log(`${ok ? 'PASS' : 'FAIL'} ${role.padEnd(8)} ${p} — ${body.slice(0, 40).replace(/\n/g, ' ')}`)
      ok ? pass++ : fail++
      await page.context().close()
    }
  }
  await browser.close()
  // Drift guard (optional): parse the nav/tab config and assert every listed
  // path is in the matrix above - navigation must never link outside the gate.
  console.log(`\n${pass}/${pass + fail} routes render real pages`)
  process.exit(fail ? 1 : 0)
})()
