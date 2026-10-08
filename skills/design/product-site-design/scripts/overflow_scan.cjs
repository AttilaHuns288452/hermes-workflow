#!/usr/bin/env node
// Responsive overflow contract scan: document scan + leaf walk with rect adjudication.
// Usage: node overflow_scan.cjs <baseURL> <route1,route2,...> [widthsCSV] [localStorage k=v,k=v ...]
//   Routes may be hash routes ("#/admin"); widths default 320,390,768,1280,1440,1920.
//   Each trailing k=v arg adds one run with those localStorage keys preset (persisted UI toggles).
// Exit 1 when document overflows or a leaf spills past its parent's border box; cosmetic spills print as WARN.
"use strict";

let pw = null;
for (const m of ["playwright", "/home/attila/.hermes/hermes-agent/node_modules/playwright"]) {
  try { pw = require(m); break; } catch (_) {}
}
if (!pw) { console.error("playwright not resolvable (try: npm i -D playwright)"); process.exit(2); }

const argv = process.argv.slice(2);
const base = argv[0];
const routes = (argv[1] || "").split(",").filter(Boolean);
const widths = (argv[2] || "320,390,768,1280,1440,1920").split(",").map(Number);
const states = [{ label: "default", kv: null }];
for (const arg of argv.slice(3)) {
  const kv = {};
  for (const pair of arg.split(",")) {
    const i = pair.indexOf("=");
    if (i > 0) kv[pair.slice(0, i)] = pair.slice(i + 1);
  }
  states.push({ label: arg, kv });
}
if (!base || routes.length === 0) {
  console.error("usage: node overflow_scan.cjs <baseURL> <route1,route2,...> [widthsCSV] [k=v,k=v ...]");
  process.exit(2);
}

const SCAN = () => {
  const docOverflow = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) - window.innerWidth;
  const clipped = [];
  const warns = [];
  for (const el of document.querySelectorAll("body *")) {
    if (!el.clientWidth || el.clientWidth < 20) continue;
    const spill = el.scrollWidth - el.clientWidth;
    if (spill <= 1) continue;
    const p = el.parentElement;
    if (!p) continue;
    const r = el.getBoundingClientRect();
    const pr = p.getBoundingClientRect();
    const item = {
      sel: el.tagName.toLowerCase() + (typeof el.className === "string" && el.className.trim() ? "." + el.className.trim().split(/\s+/).slice(0, 3).join(".") : ""),
      client: el.clientWidth,
      scroll: el.scrollWidth,
      text: (el.textContent || "").replace(/\s+/g, " ").trim().slice(0, 40),
    };
    if (r.right > pr.right + 1) clipped.push(item);
    else if (spill > 20) warns.push(item);
  }
  return { docOverflow, clipped, warns };
};

(async () => {
  const browser = await pw.chromium.launch();
  let fails = 0;
  for (const state of states) {
    for (const w of widths) {
      const ctx = await browser.newContext({ viewport: { width: w, height: 900 } });
      if (state.kv) await ctx.addInitScript((kv) => { for (const k in kv) localStorage.setItem(k, kv[k]); }, state.kv);
      const page = await ctx.newPage();
      for (const route of routes) {
        await page.goto(base + route, { waitUntil: "load" });
        await page.waitForTimeout(400);
        const txtLen = await page.evaluate(() => (document.body.innerText || "").trim().length);
        if (txtLen < 50) {
          console.log(`FAIL ${route} @${w} [${state.label}] body near-blank (${txtLen} chars) - wrong route URL (missing #/ for hash routers) or page failed to render; overflow numbers untrustworthy`);
          fails++;
          continue;
        }
        const r = await page.evaluate(SCAN);
        const bad = r.docOverflow > 1 || r.clipped.length > 0;
        if (bad) fails++;
        console.log(`${bad ? "FAIL" : "ok  "} ${route} @${w} [${state.label}] doc+${r.docOverflow}px clipped=${r.clipped.length} warn=${r.warns.length}`);
        for (const o of r.clipped.slice(0, 8)) console.log(`   CLIP ${o.sel} client=${o.client} scroll=${o.scroll} "${o.text}"`);
        for (const o of r.warns.slice(0, 3)) console.log(`   warn ${o.sel} client=${o.client} scroll=${o.scroll} "${o.text}"`);
      }
      await ctx.close();
    }
  }
  await browser.close();
  if (fails) { console.error(`\n${fails} failing route/width/state combos`); process.exit(1); }
  console.log("\nall clean");
})();
