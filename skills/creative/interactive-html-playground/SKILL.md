---
name: interactive-html-playground
description: Build single-file HTML playgrounds with interactive demos, live code previews, and copy-friendly output. Covers the MutationObserver code dock pattern, slider-to-class wiring, event handling hygiene, and GitHub Pages deployment for self-contained HTML learning tools.
category: creative
version: 1.0.0
---

# Interactive HTML Playground

Build single-file interactive HTML demo/playground pages where users explore CSS utilities, UI patterns, or any parameterized visual concept with real-time feedback and copyable code.

## Pattern Overview

A playground is one self-contained `.html` file with:
- **Category navigation** — sidebar or tab bar to switch between demo groups
- **Interactive demos** — option buttons, sliders, toggles that modify a live preview
- **Live code dock** — floating bottom bar that auto-captures and displays the current preview's classes
- **Copy buttons** — one-click copy of the displayed code

## Live Code Dock — Core Pattern

The code dock is a MutationObserver-based pattern that auto-detects class changes on any `[data-preview]` element in the currently visible section and displays the active Tailwind/CSS classes.

### Implementation

```javascript
// 1. Single global observer
function initDockObserver() {
  const observer = new MutationObserver(mutations => {
    for (const m of mutations) {
      if (m.type === 'attributes' && m.attributeName === 'class') {
        const section = m.target.closest('.category-section');
        if (section && section.style.display !== 'none') {
          dockUpdate(m.target);
        }
      }
    }
  });
  observer.observe(document.body, { subtree: true, attributes: true, attributeFilter: ['class'] });
}

// 2. Dock update — reads classes, shows Tailwind + CSS
function dockUpdate(el) {
  const ignored = ['preview-box','rounded-lg','p-4','border-slate-700/30','transition-all','duration-300'];
  const classes = Array.from(el.classList).filter(c => !ignored.some(i => c.includes(i))).join(' ');
  dockCode.textContent = classes;
  code.dataset.tw = classes;
  code.dataset.css = generateCss(classes);
}
```

### Key Design Decisions

- **One dock per page** — not N code viewers per section (use per-card code viewers for gallery/cheat-sheet layouts; see [`references/per-card-code-viewers.md`](references/per-card-code-viewers.md))
- **`class` attribute only** — MutationObserver filters to `attributeFilter: ['class']`
- **Visible-section filter** — only updates for the currently displayed demo
- **Tab switcher** — Tailwind view + CSS equivalent view
- **Expand/collapse** — for long class strings

## Layout Rule: Preview Must Stay Visible

When controls modify a preview, keep the preview in the viewport without scrolling. The user's #1 UX complaint is "I have to scroll down to see the change and scroll up again to set the changes."

**Fix: Put preview BEFORE controls**, or use `sticky top-4` / side-by-side grid on wide screens. Never stack 6+ control cards above a preview.

```javascript
// ❌ Bad: 6 control cards then preview
html += `<div>Direction</div><div>Wrap</div><div>Justify</div>...`;
html += `<div>Live Preview</div>`;  // off-screen, need to scroll

// ✅ Good: preview first, controls below
html += `<div class="md:sticky md:top-4">Live Preview</div>`;
html += `<div>Direction</div><div>Wrap</div>...`;
```

For side-by-side layout:
```html
<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
  <div class="md:col-span-2 md:sticky md:top-4 md:self-start">
    <!-- Live Preview -->
  </div>
  <div class="space-y-4"><!-- Controls --></div>
</div>
```

## Pitfalls

### 1. Slider/range demos bypass the observer
Sliders modify `element.style.*` (inline styles), not `className`. The observer never fires.

**Fix:** In the slider handler, also update Tailwind-equivalent classes on a `[data-preview]` element:
```javascript
preview.className = preview.className.replace(/m-\d+|border-\d+|p-\d+/g, '').trim();
preview.classList.add(`m-${m}`, `border-${b}`, `p-${p}`);
```

### 2. Always pass `this` to click handlers, never `event?.target`
```javascript
// ❌ Breaks on synthetic events
onclick="copyCode()" → function copyCode() { const btn = event?.target; ... }
// ✅ Works everywhere
onclick="copyCode(this)" → function copyCode(btn) { ... }
```

### 3. Button ID / prop name mismatches
If button groups use IDs like `flex-dir-btns` but the handler uses prop name `direction` to build `flex-direction-btns`, the active state never updates. Keep IDs and handler prop names in sync.

### 4. All demos need code display
Every interactive section that modifies visual state must show the resulting code. The code dock handles this globally via `[data-preview]`.

### 5. Copy button must give feedback
```javascript
navigator.clipboard.writeText(code).then(() => {
  btn.textContent = '✓ Copied!';
  setTimeout(() => { btn.textContent = 'Copy'; }, 1500);
});
```

## React / JSX Live Playgrounds

Same playground pattern, but the demo code is **JSX compiled in the browser**. Full recipe with CDN URLs, the compile function, hook exposure, and deep-link routing: [`references/react-jsx-live-editor.md`](references/react-jsx-live-editor.md)

Key points:
- **Use `@babel/standalone`** (scoped npm package, latest 7.x) — the old `babel-standalone` package is DEAD (latest is 6.26.0; `@babel/standalone@7.24.7` style pins 404). `https://cdn.jsdelivr.net/npm/@babel/standalone@7/babel.min.js` works; the global is still `Babel`.
- **React 18 UMD** + `ReactDOM.createRoot` — no build step, works from `file://`.
- **Expose hooks via `new Function`** — pass `useState, useEffect, …` as function arguments so example code can call them bare (`useState(0)` not `React.useState(0)`).
- Convention: user code must define a component named `App`; auto-render it.
- **Deep links** (`#/section-id`) + `hashchange` router make every lesson/component independently testable headlessly — build them in from the start.
- Example code strings must avoid backticks and `${` (they live in template literals).

### Tailwind inside the React REPL (teach React + Tailwind together)

`<script src="https://cdn.tailwindcss.com">` works in a live JSX REPL — the CDN's MutationObserver generates utilities for dynamically-inserted preview DOM, no rebuild needed. Patterns:

- Examples style with **utility classes in `className`** (`bg-slate-900`, `rounded-2xl`, `border-slate-700/60`) — teach React and Tailwind in one example.
- **Conditional classes** via template-string concatenation: `className={'rounded-lg ' + (on ? 'bg-emerald-500' : 'bg-rose-500')}` — this doubles as the styling lesson itself.
- Inline `style` **only for dynamic values** (HSL color, avatar size from props).
- Delete your custom `.demo-*` CSS classes once examples convert — Tailwind preflight resets buttons anyway.
- User's Tailwind playground (tailwind-playground repo) is the sibling tool; cross-link both from each other's headers.

### Teaching-depth structure (when the user says "replicate its depth")

Users who own a CSS playground expect the same **depth** in a React playground. Data model that scales (all in `js/*.js` arrays, `index.html` only has the shell):

- `CATEGORIES[]` → `sections[]` (lessons): each lesson = `{id, icon, title, desc, points[] (key-point pills), code}`. `findLesson(id)` resolves id → lesson; `#/<id>` deep links.
- `COMPONENTS[]`: `{id, icon, name, desc, code}` — "most-used" components (Switch, Progress, Dropdown, Tooltip, Pagination, Breadcrumb, Spinner, StatCard, EmptyState, Rating…) plus hooks-drill classics (Todo, Tabs, Accordion, Stopwatch).
- A **"Understanding React" category** (how React calls components, render→commit→effect cycle, why hooks need stable call order) — the user explicitly wants the mental model explained, not just copyable code.
- Hash router: `#/`, `#/component/<id>`, `#/repl` — makes every lesson headless-testable (see verification below).

### UX patterns this user expects (tailwind-playground parity)

When the user says "navigate like the tailwind css playground" or "hide the css", these are their established preferences for playground tools:

**Sidebar navigation (the user's favorite)** — left sidebar, not header tabs:
- Fixed-width sidebar (`250px`) with: logo head, search box, grouped link list (lesson categories + a Components group), footer with counts.
- Links show icon + title; `.active` state tracks the current lesson/component (data-id matching).
- Mobile (<900px): sidebar becomes a fixed drawer (`translateX(-100%)` → `.open`), hamburger in header toggles it, semi-transparent overlay closes it.
- Main area = `#shell{flex:1;display:flex}` wrapping sidebar + content column; each nav action also closes the drawer.
- Deep links still work — `route()` on load highlights the active sidebar item.

**Focus mode / hide-the-CSS toggle** (user asked: "instead of the whole tailwind css line just say some css, but make sure it still acts the same") — default ON:
- Keep the real code in a `realCode` variable; the editor shows a sanitized copy where every `className` value becomes `className="some css"`; the PREVIEW still compiles `realCode` (`compile(force)` param) so visuals never degrade.
- Sanitize: `code.replace(/className="[^"]*"/g,'className="some css"').replace(/className=\{[^}]*\}/g,'className="some css"')` — the brace regex is safe because lesson data never nests braces inside `className={}`.
- Editing while hidden auto-reveals (setHideCss(false)) so the user never fights the placeholder.
- Copy button copies `realCode`, never the sanitized editor text.
- Persist the toggle in localStorage; button label shows the action (`👁 css` = click to reveal).

**Try-it tips for comprehensiveness** — a `TRY` map keyed by lesson/component id (`js/guide.js`) rendered as a green hint box above the editor (`renderTry(id)`). One actionable exercise per item ("Call setCount twice in one click…") makes the guide comprehensive without bloating lesson bodies.

## Headless Verification (mandatory before shipping)

Playgrounds are JS-driven — `curl` proves nothing. Verify with Edge/Chrome headless before pushing:

```bash
msedge --headless --disable-gpu --dump-dom --virtual-time-budget=8000 "file:///C:/path/index.html#/deep-link" 2>/dev/null | grep -c 'class="card"'
msedge --headless --disable-gpu --screenshot=out.png --window-size=1440,900 --virtual-time-budget=8000 "file:///C:/path/index.html"
```

Pitfalls:
- **`--virtual-time-budget` is required** — without it the dump races the CDN scripts and `Babel is not defined` appears.
- **grep false positives**: `--dump-dom` output includes the page's own inline `<script>` source. Grepping for `Counter` or `Rendered` can match the script text, not the rendered DOM. Assert on **live state instead**: parse `id="statusText"` (`Rendered` vs `Error`) and `id="errorPanel"` content, plus the rendered `#preview` text.
- A screenshot alone doesn't prove interaction works — pair it with the dump-dom state assertions.

## Multi-file split for large playgrounds

A playground that outgrows a single `write_file` (stream timeouts ~8K tokens per call) still deploys as "static": split into `index.html` + `js/data.js` loaded via `<script src>`. Works from `file://` and GH Pages unchanged. Write data files separately, then patch `index.html` to reference them.

## Deployment

For static single-file HTML playgrounds:
```bash
gh repo create <owner>/<name> --public --source=. --remote=origin --push
gh api repos/<owner>/<name>/pages -X POST -f "source[branch]=main" -f "source[path]=/"
```

## Section Builder Template

```javascript
function buildDemoSection() {
  const sec = document.createElement('div');
  sec.id = 'section-demo';
  sec.className = 'category-section';
  sec.style.display = 'none';
  // Option buttons → data-preview element
  // Code dock picks up class changes automatically
}
```

## Structuring Interactive Demos

📎 [`references/large-file-surgery.md`](references/large-file-surgery.md) — Python-based method for safely editing 2000+ line single-file playgrounds when `patch()` can't handle template-literals.

Each demo section needs:
1. **Option controls** — `<button class="btn-option">` elements that call an update handler
2. **Live preview** — `<div data-preview>` whose className is modified by the handler
3. **Handler functions** — global functions that update preview classes

### Option Button Template
```html
<button class="btn-option" onclick="handlerName(this, 'value')">Label</button>
```

### Handler Pattern
```javascript
window.handlerName = function(btn, value) {
  btn.closest('.section-card').querySelectorAll('.btn-option').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const preview = btn.closest('.section-card').querySelector('[data-preview]');
  preview.className = preview.className.replace(/old-class-pattern/g, '').trim();
  preview.classList.add(value);
};
```
