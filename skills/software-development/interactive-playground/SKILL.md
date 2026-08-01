---
name: interactive-playground
description: Build single-file interactive HTML code playgrounds with live preview and auto-capturing code display. Use when the user wants a hands-on demo/explorer where every interactive section shows its current state as copyable Tailwind classes and CSS equivalents.
---

# Interactive HTML Playground

Build an interactive single-file HTML playground where every demo section's current state is always visible as copyable code — using one global observer instead of per-section code viewers.

## When to Use

- User wants an interactive demo/playground (Tailwind, CSS, Flexbox, Grid, typography explorer, etc.)
- User demands "copy-paste friendly code for everything" — all interactive sections must show their current state as copyable code
- You need a Ponytail approach: one mechanism for N sections instead of N individual code viewers

## Architecture

```
MutationObserver
    ↓ watches `class` attribute changes on [data-preview] elements
Floating Code Dock (sticky bottom bar)
    ├── Tailwind / CSS tab toggle
    ├── Copy button (copies current tab content)
    ├── Expand/collapse (max-height toggle)
    └── Source label ("from: colors")
```

## Site Structure

- **Sidebar** — category list with search, progress dots showing visited sections
- **Welcome screen** — shown initially with quick-start links
- **Category sections** — each is a `<div class="category-section" id="section-{name}" style="display:none">`
- **Floating Code Dock** — sticky bottom bar, slides up when a demo is active

## Key Convention

1. Each interactive demo section wraps its live element in `<div data-preview class="...">`
2. Sidebar navigation sets `display: block` on the target section and `display: none` on all others
3. The observer only processes class changes on `[data-preview]` inside the currently visible section
4. All interactive buttons use the pattern: `onclick="handlerName(this, 'value')"` — never `event.target`

## Core Implementation

### HTML (sticky dock, placed before `</main>`)

```html
<div id="codeDock" class="sticky bottom-0 z-40 ... backdrop-blur border-t ...">
  <div class="max-w-5xl mx-auto px-4 py-2">
    <div class="flex items-center justify-between mb-1">
      <div class="flex items-center gap-2 text-xs text-slate-400">
        <span class="font-medium text-slate-300">Active Classes</span>
        <button class="tab-btn-xs active" data-dock-tab="tw" onclick="dockSwitchTab(this,'tw')">Tailwind</button>
        <button class="tab-btn-xs" data-dock-tab="css" onclick="dockSwitchTab(this,'css')">CSS</button>
      </div>
      <button onclick="dockCopy(this)" class="text-xs ...">Copy</button>
    </div>
    <pre class="overflow-x-auto max-h-20"><code id="dockCode" class="block text-xs text-emerald-300 font-mono"></code></pre>
  </div>
</div>
```

### CSS

```css
#codeDock {
  transition: transform 0.35s cubic-bezier(0.4,0,0.2,1), opacity 0.25s;
  transform: translateY(100%);
  opacity: 0;
}
#codeDock.visible {
  transform: translateY(0);
  opacity: 1;
}
```

### JS — MutationObserver

```javascript
function initDockObserver() {
  if (dockObserver) dockObserver.disconnect();
  dockObserver = new MutationObserver(mutations => {
    for (const m of mutations) {
      if (m.type === 'attributes' && m.attributeName === 'class') {
        const section = m.target.closest('.category-section');
        if (section && (section.style.display === 'block' || section.style.display === '')) {
          dockUpdate(m.target);
        }
      }
    }
  });
  dockObserver.observe(document.body, {
    subtree: true,
    attributes: true,
    attributeFilter: ['class']
  });
}
```

### JS — Dock Update

```javascript
function dockUpdate(el) {
  const dock = document.getElementById('codeDock');
  const code = document.getElementById('dockCode');
  if (!dock || !code) return;
  const ignored = ['preview-box','bg-slate-900/70','rounded-lg','p-4','border',
    'border-slate-700/30','transition-all','duration-300','fade-in','ease'];
  const classes = Array.from(el.classList).filter(c => !ignored.some(i => c.includes(i))).join(' ').trim();
  const cssLines = classes.split(/\s+/).map(cls => twToCss(cls)).filter(Boolean);
  code.dataset.tw = classes;
  code.dataset.css = cssLines.length ? `/* Tailwind classes */\n${cssLines.join('\n')}` : '/* no CSS mapping */';
  const activeTab = dock.querySelector('.tab-btn-xs.active');
  code.textContent = activeTab?.dataset?.dockTab === 'css' ? code.dataset.css : code.dataset.tw;
  dock.classList.add('visible');
}
```

### JS — Tab Switching & Copy

```javascript
function dockSwitchTab(btn, tab) {
  btn.closest('#codeDock').querySelectorAll('.tab-btn-xs').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('dockCode').textContent =
    tab === 'css' ? code.dataset.css : code.dataset.tw;
}
function dockCopy(btn) { /* clipboard.writeText(code.textContent) */ }
function dockRefresh() { /* find visible section's [data-preview], call dockUpdate */ }
```

## Demo Section Pattern

Each interactive demo follows this structure:

```javascript
function buildSectionX() {
  const sec = document.createElement('div');
  sec.id = 'section-x';
  sec.className = 'category-section';
  sec.style.display = 'none';

  let html = `<div class="section-card ...">`;
  html += `<div class="flex flex-wrap gap-2 mb-4">
    ${items.map((s,i) =>
      `<button class="btn-option ${i===0?'active':''}" onclick="handlerName(this,'${s}')">${s}</button>`
    ).join('')}
  </div>`;
  html += `<div data-preview class="preview-box ...">...</div>`;
  html += `</div>`;

  sec.innerHTML = html;
  return sec;
}
```

## Button Handler Pattern

Every handler follows the same pattern:
1. Find container with `btn.closest('.section-card')`
2. Deactivate all `btn-option` in container
3. Activate clicked button
4. Find `[data-preview]` in container
5. Update its className (remove old class, add new one)

```javascript
function handlerName(btn, cls) {
  const c = btn.closest('.section-card');
  c.querySelectorAll('.btn-option').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const preview = c.querySelector('[data-preview]');
  preview.className = preview.className.replace(/old-class-regex/g, '').trim();
  preview.classList.add(cls);
}
```

## Section Card Builder with Auto Code Display

Every interactive card should auto-generate a code `<pre>` showing the active Tailwind classes. Use a shared `sectionCard()` function with a `data-code` element that auto-populates from the subtitle:

```javascript
function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function sectionCard(title, subtitle, contentHTML) {
  const div = document.createElement('div');
  div.className = 'bg-slate-800/50 rounded-xl border border-slate-700/50 p-4 md:p-6 mb-6 fade-in';
  div.innerHTML = `
    ${title ? `<div class="mb-4"><h3 class="text-lg font-semibold text-slate-100">${title}</h3>${subtitle ? `<p class="text-sm text-slate-400 mt-0.5">${subtitle}</p>` : ''}</div>` : ''}
    ${contentHTML}
    ${subtitle ? `<pre data-code class="text-xs text-slate-400 mt-1 font-mono overflow-x-auto whitespace-pre-wrap max-h-12">${escHtml(subtitle)}</pre>` : ''}
  `;
  return div;
}
```

The `escHtml()` call prevents HTML/angle-brackets in the subtitle from breaking `innerHTML`.

### ponytail: `sc` shorthand

```javascript
// ponytail: outerHTML wrapper so sectionCard() works in string concat
const sc = (...a) => sectionCard(...a).outerHTML;
```

⚠️ **Pitfall: self-referencing.** `const sc = (...a) => sc(...a).outerHTML` creates infinite recursion. Always reference the original function name (`sectionCard`), not the shorthand itself.

## Live Code Display on Interactive Preview Changes

When variant buttons modify a preview element's `className`, use a `MutationObserver` to update the sibling code display reactively — without changing any button's inline handler:

```javascript
// Call after sec.innerHTML = html;
sec.querySelectorAll('.preview-box').forEach(box => {
  const inner = box.querySelector('[id]');
  if (!inner) return;
  const code = box.nextElementSibling;          // the <pre data-code>
  if (code?.hasAttribute('data-code')) {
    code.textContent = inner.className.replace(/\s+/g,' ').trim();
    new MutationObserver(() => {
      code.textContent = inner.className.replace(/\s+/g,' ').trim();
    }).observe(inner, { attributes: true, attributeFilter: ['class'] });
  }
});
```

This pattern works with any button that uses `onmouseenter`/`onmouseleave`/`onclick` — the observer fires on every `class` attribute change regardless of the trigger mechanism.

## Data-Driven Component Library

When you need 10+ interactive component cards (Navbar, Card, Alert, Badge, Avatar, etc.) all following the same controls-left / preview-right / code-below layout, define them as **data** instead of writing N separate builders:

```javascript
const compDefs = [
  { id: 'badge', title: 'Badge', html: 'Status',
    variants: {
      gray: { c:'bg-slate-100 text-slate-800 text-xs rounded-full px-2.5 py-0.5',
              d:'bg-slate-100 text-slate-800 text-xs rounded-full' },
      red:  { c:'bg-red-100 text-red-800 text-xs rounded-full px-2.5 py-0.5',
              d:'bg-red-100 text-red-800 text-xs rounded-full' },
      // variants without `h` key use the component-level `html`
    }
  },
  { id: 'alert', title: 'Alert',
    variants: {
      success: { c:'bg-green-500/15 border-green-500/30 text-green-300 px-4 py-3',
                 d:'bg-green-500/15 text-green-300',
                 h:'<span>✓ Saved successfully.</span>' },  // `h` = per-variant innerHTML
      error:   { c:'bg-red-500/15 border-red-500/30 text-red-300 px-4 py-3',
                 d:'bg-red-500/15 text-red-300',
                 h:'<span>✗ Something went wrong.</span>' },
    }
  },
];
```

**Data fields:** `c` = container classes (preview wrapper), `d` = description string (fallback), `h` = inner HTML for the preview (use this to show the actual source code).

Render with one loop (inline template literal). Show the **full HTML source** as code, not just class descriptions:

```javascript
html += compDefs.map(t => {
  const keys = Object.keys(t.variants), fst = keys[0], v = t.variants[fst];
  const pid = t.id[0].toUpperCase() + t.id.slice(1);
  return `<div class="section-card ...">
    <div class="flex-1 min-w-[140px]">
      <h3>${t.title}</h3>
      <div id="comp-${t.id}-btns">
        ${keys.map((k,i) => `<button class="btn-option ${i===0?'active':''}"
          onclick="compUpdate('${t.id}','${k}')">${k}</button>`).join('')}
      </div>
    </div>
    <div class="w-full md:w-3/5">
      <div id="comp${pid}Preview" class="${v.c}">${v.h||t.html||''}</div>
    </div>
    <pre class="text-xs text-slate-400 mt-1 font-mono overflow-x-auto whitespace-pre-wrap max-h-32"
         id="comp${pid}Code">${escHtml(v.h||t.html||v.d||'')}</pre>
  </div>`;
}).join('');
```

Use a `<pre>` and `escHtml()` so the HTML source renders as text, not markup. Use `v.h || t.html || v.d` as the fallback chain: prefer per-variant HTML, then component default HTML, then description string.

Update with one data-driven handler (no per-component branches), also showing the HTML source:

```javascript
window.compUpdate = function(prop, value) {
  // 1. Highlight the active button
  document.querySelectorAll(`[id^="comp-${prop}-btns"] .btn-option`)
    .forEach(b => b.classList.remove('active'));
  const container = document.getElementById(`comp-${prop}-btns`);
  if (container) container.querySelectorAll('.btn-option').forEach(b => {
    if (b.textContent.trim() === value ||
        b.getAttribute('onclick')?.includes("'"+value+"'"))
      b.classList.add('active');
  });

  // 2. Update preview + code display from data
  const pid = prop[0].toUpperCase() + prop.slice(1);
  const el = document.getElementById('comp'+pid+'Preview');
  const code = document.getElementById('comp'+pid+'Code');
  if (!el||!code) return;
  const def = compDefs.find(d => d.id === prop);
  if (!def||!def.variants[value]) return;
  const v = def.variants[value];
  el.className = v.c;
  if (v.h) el.innerHTML = v.h;
  // Show full HTML source — textContent auto-escapes
  code.textContent = v.h||t.html||v.d||'';
};
```

### Pitfalls

- **ID mismatch = silent failure.** ...
- **Landing page vs section content separation.** Promotional CTAs, feature callouts, and quick-start links belong on the **landing/welcome page** (shown by default), NOT inside feature sections like Components. The welcome screen is the first thing users see — put priority content there, ordered by most-common-first. Feature sections contain interactive demos for that utility.
- **JS validation in inline HTML playgrounds.** To validate inline `<script>` content with `node --check`, extract the second (main) script block by finding both `<script>` positions: `s2 = c.find('<script>', e1)` after the first `</script>`. Python approach: `c.split('<script>')[2].split('</script>')[0]`. Run `node --check` on the extracted file.
- **Brace matching in JS object data arrays.** ...
- **Single quotes vs template literals.** `html += '...${...}...'` — inside single-quoted JS strings `${...}` renders as literal text. Use backticks: `` html += `...${...}...` ``.
- **Dual-axis components** (e.g. Button has variant + size) combine two state keys into one preview. Keep them as separate functions outside the data loop, since the data-driven handler maps one prop → one element.
- **Missing trailing comma on last entry.** When extending a JS data array (e.g. `compDefs`) via Python/scripted text replacement, the last existing entry may lack a trailing comma before `];`. After insertion, JS sees `} } }{"id":"new" }` — a syntax error. Always add a `,` to the last pre-existing entry before inserting.
- **HTML escaping for code display.** Use `escHtml()` for template-literal injection into `innerHTML`, and `.textContent` for dynamic code updates (`.textContent` auto-escapes). Never put user-provided or data-driven HTML strings into `innerHTML` without escaping.

## CSS Equivalent Mapping

Provide a `twToCss()` function mapping common Tailwind classes to CSS. Include: flex, grid, spacing (p-/m-/gap-), typography (text-/font-), border, shadow, opacity, display, position, overflow, cursor, and responsive prefixes.

```javascript
function twToCss(cls) {
  if (cls === 'flex') return 'display: flex;';
  if (cls.startsWith('p-')) return `padding: ${cls.replace('p-','') * 0.25}rem;`;
  // ... add more as needed
  return null;
}
```

## Section Categories to Cover

When building a Tailwind playground, cover at minimum: typography, colors, backgrounds, width, height, margin, padding, border, border-radius, display, flexbox, grid, position, overflow, shadow, opacity, cursor, hover, transition, transform, responsive, z-index, sizing, spacing, filters, lists, tables, object-fit.

Each with 3-10 clickable option buttons and a `[data-preview]` element.

## Verification Checklist

- [ ] All 28-29 sections render (check `category-section` count)
- [ ] All `event?.target` references removed — every handler passes `this` explicitly
- [ ] Code dock slides up when clicking any demo button
- [ ] Tailwind/CSS tabs toggle correctly
- [ ] Copy button copies the displayed code
- [ ] Sidebar search narrows results
- [ ] Progress dots update as sections are visited
- [ ] File opens from `file://` without server
- [ ] No console errors
- [ ] Code displays show full HTML source (not just class names)
- [ ] Code displays update when variant buttons are clicked/hovered

## Ponytail Rationale

Instead of wiring a code viewer into N individual sections (N× repetitive HTML + N× handler edits), one MutationObserver + one dock handles all sections automatically. ~80 lines of JS replaces ~200+ lines of per-section boilerplate. The observer is cheap: attribute-only filter, only processes the currently visible section.
