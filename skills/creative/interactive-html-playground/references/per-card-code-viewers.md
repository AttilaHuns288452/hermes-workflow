# Per-Card Code Viewers (Alternative to Global Dock)

The global code dock from `SKILL.md` works for most demos. For playgrounds where **each card has its own dedicated code viewer** (common in component gallery / cheat sheet layouts), use a per-card pattern instead.

## Pattern Overview

Each section card gets a `<pre>` element that displays the Tailwind classes used in that card's preview. The content updates live as the user interacts with controls (variant buttons, sliders, toggles) via a `MutationObserver` on the preview element's `class` attribute.

## Implementation

### 1. Add a code element to each card at build time

Use a shared `sectionCard` helper:

```javascript
function sectionCard(title, subtitle, contentHTML) {
  const div = document.createElement('div');
  div.className = 'bg-slate-800/50 rounded-xl border border-slate-700/50 p-4 md:p-6 mb-6 fade-in';
  div.innerHTML = `
    ${title ? `<div class="mb-4"><h3 class="text-lg font-semibold text-slate-100">${title}</h3>
      ${subtitle ? `<p class="text-sm text-slate-400 mt-0.5">${subtitle}</p>` : ''}</div>` : ''}
    ${contentHTML}
    ${subtitle ? `<pre data-code class="text-xs text-slate-400 mt-1 font-mono overflow-x-auto
      whitespace-pre-wrap max-h-12">${escHtml(subtitle)}</pre>` : ''}
  `;
  return div;
}
```

### 2. Wire MutationObserver after section is built

In the section builder, after setting `sec.innerHTML`, walk `.preview-box` and attach an observer to each inner preview element:

```javascript
function buildDemoSection() {
  const sec = document.createElement('div');
  sec.id = 'section-demo'; sec.className = 'category-section'; sec.style.display = 'none';
  sec.innerHTML = '<h2>Title</h2>'
    + sectionCard('Demo', 'class-a, class-b', preview('demo1') + variantButtons);

  // Wire live code displays
  sec.querySelectorAll('.preview-box').forEach(box => {
    const inner = box.querySelector('[id]');          // the demo element with id
    if (!inner) return;
    const code = box.parentElement.querySelector('[data-code]');  // ⚠️ see pitfall #1
    if (!code) return;
    code.textContent = inner.className.replace(/\s+/g, ' ').trim();
    new MutationObserver(() => {
      code.textContent = inner.className.replace(/\s+/g, ' ').trim();
    }).observe(inner, { attributes: true, attributeFilter: ['class'] });
  });
  return sec;
}
```

### 3. Variant buttons change className

Buttons use `onmouseenter`/`onclick` handlers that rewrite `className`:

```javascript
const btn = `<button onmouseenter="document.getElementById('demo1').className=
  'base-classes variant-class'" onmouseleave="document.getElementById('demo1').className=
  'base-classes'">Variant</button>`;
```

The `MutationObserver` catches every `className` write and pushes the active class list into the `<pre data-code>`.

## Pitfalls

### 1. Finding the code element correctly

❌ **Wrong:** `box.nextElementSibling` — the `.preview-box` is typically followed by a controls `<div>`, not the `<pre data-code>`:
```
.section-card
  .preview-box          ← box
  .flex.flex-wrap       ← box.nextElementSibling (controls, WRONG!)
  pre[data-code]        ← actual code element
```

✅ **Correct:** `box.parentElement.querySelector('[data-code]')` — walks up to the card root, finds the code element by attribute:

```
.section-card           ← box.parentElement
  .preview-box          ← box
  .flex.flex-wrap
  pre[data-code]        ← querySelector('[data-code]') finds this
```

### 2. Preview element must have an `id` for button handlers to target

Without an `id`, the inline `onmouseenter` handler can't reference the element. Use a helper:

```javascript
const preview = id => livePreview(
  `<div id="${id}" class="base-classes">Hover me</div>`, ''
);
```

Then check `box.querySelector('[id]')` exists before wiring — skip cards without interactive controls.

### 3. The `escHtml` helper prevents XSS in code displays

When showing variant template HTML in a `<pre>` (as source code, not rendered), escape entities:

```javascript
function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
```

Use it in template literals: `${escHtml(variantHtml)}`. The display shows `<div class="...">` as literal text, not rendered DOM.

### 4. Use `def.html` not `t.html` — closure scope trap

In a loop like `compDefs.map(t => { ... })`, `t` is valid inside the callback. But if a separate update function (e.g. `compUpdate(prop, value)`) references `t.html`, it throws `ReferenceError: t is not defined` because `t` was only in the loop scope.

**Fix:** Always reference the lookup result: `const def = compDefs.find(d => d.id === prop); def.html`.

### 5. Missing commas in array entries silently break everything

In a 2000+ line file, a missing comma in a large data array (`{...},{... no comma here}{...}`) causes a JS parse error that prevents ALL downstream code from executing — even code in other `<script>` blocks. The symptom looks like the TOC/sidebar is dead.

**Diagnosis:** Extract the `<script>` block and run `node --check temp.js`. The error points to the line AFTER the missing comma.

**Fix:** Add the missing comma. Afterward, re-check to confirm zero syntax errors.

## When to Use Per-Card vs Global Dock

| Per-card code viewer | Global code dock |
|----------------------|------------------|
| Each card has its own code display | Single code bar at bottom of screen |
| User sees code in context | User sees code in a fixed location |
| Best for gallery / cheat sheet layout | Best for focused demo with one preview + many controls |
| Code updates per card independently | Code updates for whatever preview changed |
| No layout shifting | Can overlap/cover content |
