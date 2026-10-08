#!/usr/bin/env node
// Width/margin geometry probe: shell width, side margins, header<->content
// edge alignment, and document overflow per route x width. Complements
// overflow_scan.cjs (spill detection) by measuring the CONTAINER system.
//
// Usage:
//   node width_margin_probe.cjs [baseUrl] [widths] [routes]
//   node width_margin_probe.cjs http://127.0.0.1:8873 1920,1440,1280,768,390,320 "/,/gadgets"
//   node width_margin_probe.cjs http://127.0.0.1:8873 1920 "#/,#/gadgets"   (hash router)
//
// Routes: plain paths are appended to baseUrl; routes starting with '#' are
// appended as-is (HashRouter). Exit code 1 if any route overflows or the
// header/content left edges disagree (mismatched container tokens).

const path = require("path");
const os = require("os");
const { chromium } = require(path.join(os.homedir(), ".hermes/hermes-agent/node_modules/playwright"));

const BASE = process.argv[2] || "http://127.0.0.1:8873";
const WIDTHS = (process.argv[3] || "1920,1440,1280,768,390,320").split(",").map(Number);
const ROUTES = (process.argv[4] || "/,/gadgets").split(",");
// Elements carrying the project's container classes. Adjust per project.
const SHELL = '[class*="max-w-["], .section, .container';

(async () => {
  const browser = await chromium.launch();
  let failed = false;
  for (const w of WIDTHS) {
    const page = await browser.newPage({ viewport: { width: w, height: 900 } });
    for (const route of ROUTES) {
      const url = route.startsWith("#") ? BASE + route : BASE.replace(/\/$/, "") + route;
      await page.goto(url, { waitUntil: "networkidle" });
      await page.waitForTimeout(150);
      const m = await page.evaluate((shellSel) => {
        const rects = [...document.querySelectorAll(shellSel)]
          .map((el) => el.getBoundingClientRect())
          .filter((r) => r.width > 0);
        const shell = rects.sort((a, b) => b.width - a.width)[0] || null;
        const headerEl = document.querySelector("header");
        const mainEl = document.querySelector("main");
        const hr = headerEl ? headerEl.querySelector(shellSel)?.getBoundingClientRect() : null;
        const mr = mainEl ? (mainEl.querySelector(shellSel) || mainEl).getBoundingClientRect() : null;
        return {
          shellW: shell ? Math.round(shell.width) : null,
          left: shell ? Math.round(shell.left) : null,
          right: shell ? Math.round(window.innerWidth - shell.right) : null,
          aligned: hr && mr ? Math.abs(hr.left - mr.left) <= 1 : null,
          overflow: document.documentElement.scrollWidth > window.innerWidth,
        };
      }, SHELL);
      const problems = [];
      if (m.overflow) problems.push("OVERFLOW");
      if (m.aligned === false) problems.push("MISALIGNED");
      if (problems.length) failed = true;
      console.log(
        `${w}px ${route} shell=${m.shellW} margins=${m.left}/${m.right} aligned=${m.aligned} ${problems.join(",")}`
      );
    }
    await page.close();
  }
  await browser.close();
  process.exit(failed ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(2); });
