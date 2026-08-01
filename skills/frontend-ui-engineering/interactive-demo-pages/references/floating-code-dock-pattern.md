# Floating Code Dock Pattern

## Problem

20+ interactive demo sections, each toggling CSS classes on a `[data-preview]` element. Adding a code viewer to every section individually means ~150 lines of repetitive HTML.

## Ponytail Solution: One Observer, One Dock

Replace N per-section code viewers with one floating code dock at the page bottom. A single `MutationObserver` watches ALL `[data-preview]` elements and updates the dock whenever classes change.

## Implementation

### 1. HTML (sticky bottom dock)

```html
<div id="codeDock" class="sticky bottom-0 z-40 bg-slate-900/95 backdrop-blur border-t border-slate-700/50">
  <div class="max-w-5xl mx-auto px-4 py-2">
    <div class="flex items-center justify-between mb-1">
      <div class="flex items-center gap-2 text-xs text-slate-400">
        <span class="font-medium">Active Classes</span>
        <button class="tab-btn-xs active" data-dock-tab="tw"
          onclick="dockSwitchTab(this,'tw')">Tailwind</button>
        <button class="tab-btn-xs" data-dock-tab="css"
          onclick="dockSwitchTab(this,'css')">CSS</button>
      </div>
      <button onclick="dockCopy(this)"
        class="text-xs text-slate-400 hover:text-slate-200 px-2 py-0.5 rounded">
        <svg><!-- clipboard icon --></svg> Copy
      </button>
    </div>
    <pre class="overflow-x-auto max-h-20">
      <code id="dockCode" class="text-xs text-emerald-300"></code>
    </pre>
  </div>
</div>
```

### 2. MutationObserver (one-time init)

```js
// Watches class changes on ALL [data-preview] elements
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
observer.observe(document.body, {
  subtree: true,
  attributes: true,
  attributeFilter: ['class']
});
```

### 3. Dock update function

```js
function dockUpdate(el) {
  // Structural classes to always filter out
  const ignored = [
    'preview-box', 'bg-slate-900/70', 'rounded-lg',
    'p-4', 'border', 'border-slate-700/30',
    'transition-all', 'duration-300', 'fade-in', 'ease'
  ];

  const classes = Array.from(el.classList)
    .filter(c => !ignored.some(i => c.includes(i)))
    .join(' ');

  const activeTab = document.querySelector('.tab-btn-xs.active');
  const isCss = activeTab?.dataset?.dockTab === 'css';

  if (isCss) {
    const cssLines = classes.split(/\s+/)
      .map(cls => twToCss(cls)).filter(Boolean);
    dockCode.textContent = cssLines.length
      ? `/* Tailwind */\n${cssLines.join('\n')}`
      : '/* no CSS mapping */';
  } else {
    dockCode.textContent = classes || el.className;
  }

  // Store for tab switching & copy
  dockCode.dataset.tw = classes;
  dockCode.dataset.css = cssLines.join('\n');
  dockCode.dataset.activeTab = isCss ? 'css' : 'tw';
}
```

### 4. CSS mapping (scale as needed)

```js
function twToCss(cls) {
  if (cls.startsWith('p-'))
    return `padding: ${cls.replace('p-','') * 0.25}rem;`;
  if (cls.startsWith('m-'))
    return `margin: ${cls.replace('m-','') * 0.25}rem;`;
  if (cls.startsWith('gap-'))
    return `gap: ${cls.replace('gap-','') * 0.25}rem;`;
  if (cls === 'flex') return 'display: flex;';
  if (cls === 'grid') return 'display: grid;';
  if (cls.startsWith('shadow-')) {
    const shadows = {sm:'0 1px 2px',md:'0 4px 6px',lg:'0 10px 15px',xl:'0 20px 25px'};
    return shadows[cls.replace('shadow-','')]
      ? `box-shadow: ${shadows[cls.replace('shadow-','')]};` : null;
  }
  return null; // unmapped — skip
}
```

### 5. Tab switching & copy

```js
function dockSwitchTab(btn, tab) {
  // Deactivate all, activate clicked
  btn.closest('#codeDock').querySelectorAll('.tab-btn-xs')
    .forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  // Swap text from dataset
  dockCode.textContent = dockCode.dataset[tab === 'css' ? 'css' : 'tw'];
}

function dockCopy(btn) {
  navigator.clipboard.writeText(dockCode.textContent).then(() => {
    btn.innerHTML = '✓ Copied!';
    setTimeout(() => { btn.textContent = 'Copy'; }, 1500);
  });
}
```

## When NOT to Use

| Pattern | Better approach |
|---------|----------------|
| Single interactive element | One `<pre><code>` next to it |
| Syntax-highlighted code | Library (Prism, highlight.js) per section |
| < 3 sections with sparse interactions | Handler-side `refreshCode()` call |
| Server-rendered / static content | Include code statically in HTML |

## Pitfalls

- **Rapid class changes** (e.g., animation frames) — MutationObserver fires on every frame. Add an RAF debounce if needed.
- **Structural class filter list drifts** — maintain the `ignored` array when adding new wrapper classes.
- **Multiple visible sections** — the observer updates on every visible section. The `section.style.display !== 'none'` guard prevents this.
- **Tab switch must read from dataset, not re-query DOM** — the stored `dataset.tw` / `dataset.css` are the source of truth.
