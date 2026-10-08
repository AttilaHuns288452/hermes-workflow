#!/usr/bin/env node
/**
 * Responsive correctness sweep: routes x widths x engines, no screenshots.
 * Flags horizontal page overflow, clipped text, and page errors.
 *
 *   node responsive-sweep.cjs <base-url> [route ...] [--engines=chromium,firefox,webkit] [--widths=320,390,...]
 *
 * Exit: 0 clean, 1 findings, 2 setup/usage error.
 */
"use strict";

const os = require("os");
const path = require("path");

const args = process.argv.slice(2);
const flags = {};
const pos = [];
for (const a of args) {
  const m = a.match(/^--([\w-]+)=(.*)$/);
  if (m) flags[m[1]] = m[2];
  else pos.push(a);
}
const base = (pos.shift() || "").replace(/\/$/, "");
if (!base) {
  console.error("usage: node responsive-sweep.cjs <base-url> [route ...] [--engines=...] [--widths=...]");
  process.exit(2);
}
const routes = pos.length ? pos : ["/"];
const engines = (flags.engines || "chromium").split(",").filter(Boolean);
const widths = (flags.widths || "320,360,390,412,480,640,768,834,1024,1280,1366,1440,1920,2560")
  .split(",")
  .map(Number)
  .filter((n) => n > 0);

function loadPlaywright() {
  const candidates = [
    process.env.PLAYWRIGHT_MODULE,
    "playwright",
    path.join(os.homedir(), ".hermes/hermes-agent/node_modules/playwright"),
  ].filter(Boolean);
  for (const c of candidates) {
    try {
      return require(c);
    } catch (_) {
      /* try next */
    }
  }
  console.error("playwright not found; set PLAYWRIGHT_MODULE to its path");
  process.exit(2);
}

// Two detectors: page-level horizontal overflow + clipped text on leaf elements.
function detect() {
  const de = document.documentElement;
  const overflow = de.scrollWidth - de.clientWidth;
  const clipped = [];
  for (const el of document.querySelectorAll("body *")) {
    const txt = (el.textContent || "").trim();
    if (!txt || txt.length > 200) continue;
    const hasTextChild = Array.from(el.childNodes).some((n) => n.nodeType === 3 && n.textContent.trim());
    if (el.children.length > 0 && !hasTextChild) continue;
    const st = getComputedStyle(el);
    if (st.overflowX === "auto" || st.overflowX === "scroll" || st.textOverflow === "ellipsis") continue;
    if (el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 1) {
      clipped.push(`${el.tagName}.${String(el.className).slice(0, 40)} "${txt.slice(0, 40)}" ${el.scrollWidth}>${el.clientWidth}`);
    }
  }
  return { overflow, clipped: clipped.slice(0, 6) };
}

(async () => {
  const pw = loadPlaywright();
  const findings = [];
  let loads = 0;
  for (const name of engines) {
    const engine = pw[name] || pw.chromium;
    const browser = await engine.launch();
    for (const w of widths) {
      const ctx = await browser.newContext({ viewport: { width: w, height: 900 } });
      for (const route of routes) {
        const page = await ctx.newPage();
        const errors = [];
        page.on("pageerror", (e) => errors.push(String(e).slice(0, 120)));
        page.on("console", (m) => {
          if (m.type() === "error") errors.push(m.text().slice(0, 120));
        });
        const url = base + route;
        try {
          await page.goto(url, { waitUntil: "load", timeout: 25000 });
          await page.waitForTimeout(300);
          const r = await page.evaluate(detect);
          loads++;
          const tags = [];
          if (r.overflow > 1) tags.push(`OVERFLOW +${r.overflow}`);
          for (const c of r.clipped) tags.push(`CLIP ${c}`);
          for (const e of errors.slice(0, 2)) tags.push(`PAGEERROR ${e}`);
          console.log(`${name} ${w}px ${route} :: ${tags.length ? tags.join(" | ") : "OK"}`);
          if (tags.length) findings.push(`${name} ${w}px ${route}`);
        } catch (err) {
          findings.push(`${name} ${w}px ${route}`);
          console.log(`${name} ${w}px ${route} :: NAVFAIL ${String(err).split("\n")[0].slice(0, 120)}`);
        }
        await page.close();
      }
      await ctx.close();
    }
    await browser.close();
  }
  console.log(`\n${loads} loads, ${findings.length} with findings`);
  process.exit(findings.length ? 1 : 0);
})();
