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
