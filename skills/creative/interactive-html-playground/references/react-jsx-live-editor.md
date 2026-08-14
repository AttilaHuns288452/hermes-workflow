# React / JSX Live Editor Recipe

Working pattern from the react-playground build (React 18 + Babel standalone, no build step, works from `file://` and GH Pages).

## CDN scripts (pinned, jsdelivr)

```html
<script src="https://cdn.jsdelivr.net/npm/react@18.3.1/umd/react.production.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/react-dom@18.3.1/umd/react-dom.production.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@babel/standalone@7/babel.min.js"></script>
```

**Trap:** the npm package `babel-standalone` is abandoned at 6.26.0 — any `babel-standalone@7.x` URL 404s (verified against jsdelivr + npm registry). The maintained package is the scoped `@babel/standalone` (7.29.x as of 2026-08); its browser global is still `Babel`.

## Compile + render

```js
const HOOKS = ['useState','useEffect','useRef','useMemo','useCallback','useReducer','useContext','useLayoutEffect'];
let root = null;

function compile() {
  try {
    const out = Babel.transform(editor.value, { presets: ['react'] }).code;
    const factory = new Function('React', 'createElement', ...HOOKS,
      out + '\n;return typeof App !== "undefined" ? App : null;');
    const App = factory(React, React.createElement, ...HOOKS.map(h => React[h]));
    if (!App) throw new Error('Define a component named App');
    if (root) { root.unmount(); root = null; }
    preview.innerHTML = '';
    root = ReactDOM.createRoot(preview);
    root.render(React.createElement(App));
  } catch (e) {
    errorPanel.style.display = 'block';
    errorPanel.textContent = '⚠ ' + (e.message || e);
  }
}
```

- Convention: example code defines `App`; the playground renders it. Document this in the starter template.
- `new Function` with hooks as parameters lets lesson code call `useState(0)` bare — no `React.` prefix, cleaner teaching examples.
- Babel `presets: ['react']` leaves modern JS (const/arrows) untouched — fine in current browsers.

## Editor UX

- Debounced auto-run (`setTimeout(compile, 350)` on `input`) + a Run button + Ctrl/Cmd+Enter.
- Status line: green/red dot + `Rendered`/`Error` + render time — doubles as the headless-verification signal.
- Error panel: red, monospace, shows `e.message`.
- Copy button reads the editor; toast "✓ Copied!".

## Data-driven lessons + deep links

Structure content as data arrays so lessons/components are just entries:

```js
const CATEGORIES = [{ name, icon, sections: [{ id, icon, title, desc, points: [], code }] }];
const COMPONENTS  = [{ id, icon, name, desc, code }];
```

Router (hash-based, testable headlessly):

```js
function route() {
  const h = location.hash || '';
  if (h === '#/components') return showComponents();
  if (h === '#/repl') return openRepl();
  const cm = h.match(/^#\/component\/(.+)$/);
  if (cm) return openComponent(decodeURIComponent(cm[1]));
  const sm = h.match(/^#\/(.+)$/);
  if (sm && findLesson(sm[1])) return openSection(sm[1]);
  showHome();
}
window.addEventListener('hashchange', route);
```

Rule for example code strings: **no backticks, no `${`** inside (they live in template literals). Use `+` concatenation in examples; escape `'` as `&apos;` when it appears inside JSX text.

## Large content → split files

If the file exceeds ~8K tokens per write call (stream timeouts), split:
- `index.html` (structure, CSS, REPL machinery, router)
- `js/lessons.js` (+ `js/lessons2.js` via `CATEGORIES.push(...)`)
- `js/components.js`

`<script src>` from `file://` works fine; GH Pages serves it unchanged. Add a `findLesson(id)` helper that attaches the category name to the section for breadcrumbs.
