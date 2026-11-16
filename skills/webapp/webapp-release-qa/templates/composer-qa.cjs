// Composer QA — geometry + overlap + behavior for a chat input/send row.
// Usage: BASE=<origin> node composer-qa.cjs   (default BASE: http://127.0.0.1:5173)
// ADAPT BEFORE RUNNING: the switchRole() hook and the form/input/send selectors to your app.
const { chromium } = require('playwright'); // adjust require() to your playwright install path
const BASE = process.env.QA_BASE || 'http://127.0.0.1:5173';
const results = [];
const t = (name, ok, detail = '') => { results.push({ name, ok }); console.log(`${ok ? 'PASS' : 'FAIL'} ${name}${detail ? ' — ' + detail : ''}`); };

// ADAPT: how your app switches user/role. The injection must be VERIFIED (see below) —
// an unconsumed injection silently runs every scenario as the same user.
async function switchRole(ctx, role) {
  await ctx.addInitScript((r) => localStorage.setItem('app_session', JSON.stringify({ role: r })), role);
}

// The generic occluder scan: every visible fixed/absolute element intersecting the input box.
// This is the check that catches dev pills / FABs / nav edges targeted asserts don't name.
async function inputOccluders(p) {
  return p.evaluate(() => {
    const form = document.querySelectorAll('form');
    const f = form[form.length - 1];
    const input = f && f.querySelector('input, textarea');
    if (!input) return ['no input'];
    const ir = input.getBoundingClientRect();
    return [...document.querySelectorAll('body *')].filter((el) => {
      if (el.contains(input) || input.contains(el)) return false;
      const cs = getComputedStyle(el);
      if (cs.position !== 'fixed' && cs.position !== 'absolute') return false;
      if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) return false;
      const r = el.getBoundingClientRect();
      if (r.width < 4 || r.height < 4) return false;
      const ox = Math.min(ir.right, r.right) - Math.max(ir.left, r.left);
      const oy = Math.min(ir.bottom, r.bottom) - Math.max(ir.top, r.top);
      return ox > 2 && oy > 2;
    }).map((el) => `${el.tagName}.${(el.className || '').toString().slice(0, 40)} "${(el.textContent || '').trim().slice(0, 12)}"`);
  });
}

(async () => {
  const b = await chromium.launch();
  for (const role of ['patient', 'staff']) {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
    await switchRole(ctx, role);
    const p = await ctx.newPage();
    const errors = [];
    p.on('pageerror', (e) => errors.push(String(e)));
    await p.goto(`${BASE}/messages`, { waitUntil: 'networkidle' });
    await p.waitForTimeout(500);

    // VERIFY the role switch landed before any role-conditional verdict below:
    // t(`${role}: session switched`, await p.locator('[data-role="' + role + '"]').count() > 0);

    // form.last() because picker screens may carry their own search form;
    // `form input` (no attribute equality — a type-less input is still a text input)
    const form = p.locator('form').last();
    const input = form.locator('input, textarea').first();
    const send = form.locator('button').last();
    t(`${role}: composer exists`, (await input.count()) > 0 && (await send.count()) > 0);

    const geo = await p.evaluate(() => {
      const form = document.querySelectorAll('form');
      const f = form[form.length - 1];
      const nav = document.querySelector('nav.fixed, [class*="fixed bottom-0"]');
      const r = (el) => el ? el.getBoundingClientRect() : null;
      return { form: r(f), navTop: nav && r(nav).top, winH: window.innerHeight };
    });
    t(`${role}: composer fully above nav`, geo.form && geo.form.top >= 0 && geo.form.bottom <= geo.navTop + 0.5,
      `formBottom=${Math.round(geo.form.bottom)} navTop=${Math.round(geo.navTop)}`);

    const overlaps = await inputOccluders(p);
    t(`${role}: nothing overlaps the input`, overlaps.length === 0, overlaps.join(' | '));

    // behavior: empty send no-op, send + clear, Enter sends, new message in view
    await input.fill('');
    await send.click().catch(() => {});
    await p.waitForTimeout(300);
    const marker = 'QA composer ' + Date.now();
    await input.fill(marker);
    t(`${role}: send enabled when typed`, !(await send.isDisabled().catch(() => true)));
    await send.click();
    await p.waitForTimeout(500);
    t(`${role}: sent message appears`, (await p.locator(`text=${marker}`).count()) > 0);
    t(`${role}: input clears after send`, (await input.inputValue()) === '');
    const box = await p.locator(`text=${marker}`).last().boundingBox();
    t(`${role}: new message in view`, box && box.y + box.height <= 844 && box.y >= 0, JSON.stringify(box));
    await input.fill(marker + ' enter');
    await input.press('Enter');
    await p.waitForTimeout(500);
    t(`${role}: Enter key sends`, (await p.locator(`text=${marker} enter`).count()) > 0);
    t(`${role}: no page errors`, errors.length === 0, errors.join('; ').slice(0, 200));
    await ctx.close();
  }

  // font-scale sweep: grows fixed chrome (labels wrap) past any hard-coded reserve
  for (const [w, h, fs] of [[320, 720, 13], [390, 844, 15], [412, 915, 15]]) {
    const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2 });
    await switchRole(ctx, 'patient');
    const p = await ctx.newPage();
    await p.goto(`${BASE}/messages`, { waitUntil: 'networkidle' });
    await p.addStyleTag({ content: `nav.fixed * { font-size: ${fs}px !important }` });
    await p.waitForTimeout(300);
    const g = await p.evaluate(() => {
      const form = document.querySelectorAll('form');
      const f = form[form.length - 1].getBoundingClientRect();
      const nav = document.querySelector('nav.fixed, [class*="fixed bottom-0"]').getBoundingClientRect();
      return { fb: f.bottom, nt: nav.top };
    });
    t(`scaled ${w}x${h} fs${fs}: composer clear`, g.fb <= g.nt + 0.5, `formBottom=${Math.round(g.fb)} navTop=${Math.round(g.nt)}`);
    await ctx.close();
  }

  await b.close();
  const fails = results.filter((r) => !r.ok).length;
  console.log(`\n${results.length - fails}/${results.length} pass`);
  process.exit(fails ? 1 : 0);
})();
