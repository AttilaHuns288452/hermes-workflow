# Data-Driven Component Library (Variant Switching)

Alternative to per-section handlers when you need 15+ components with 2-4 style variants each. Used by the tailwind-playground project to generate 33 component templates from a single JSON dataset.

## Architecture

```
compDefs (JSON array of component specs)
  → buildComponents() iterates & renders cards
  → compUpdate(id, variantKey) switches variant
  → Code label auto-reflects current variant description
```

Each component spec:

```js
{ id: 'tabs',            // URL-safe id used in switch function
  title: 'Tabs',         // Human heading
  html: '<default html>',// Optional default inner markup (used when variants don't have 'h')
  variants: {
    pills:    { c: 'flex gap-1 ...',            d: 'tabs with rounded pills',      h: '<button>…</button>' },
    underline:{ c: 'flex gap-4 border-b ...',   d: 'tabs with underline',          h: '<button>…</button>' },
    cards:    { c: 'flex gap-2 ...',            d: 'tabs with card-style buttons', h: '<button>…</button>' }
  }
}
```

### Properties per variant

| Key | Purpose | Required |
|-----|---------|----------|
| `c` | CSS classes on the preview container | Yes — this is what variant buttons toggle |
| `d` | Description / code label — shown in monospace under the preview | Yes — serves as the "cheat sheet" text, and fallback when both `h` and `html` are absent |

## Switching Function

```js
function compUpdate(prop, value) {
  const pid = prop[0].toUpperCase() + prop.slice(1);
  const el = document.getElementById('comp' + pid + 'Preview');
  const code = document.getElementById('comp' + pid + 'Code');
  if (!el || !code) return;
  const def = compDefs.find(d => d.id === prop);
  if (!def || !def.variants[value]) return;
  const v = def.variants[value];
  el.className = v.c;
  if (v.h) el.innerHTML = v.h;
  // Fallback chain: variant HTML → constructed element → default HTML → description
  // prettyHTML (defined in parent SKILL.md) adds indentation for readability
  code.textContent = prettyHTML(v.h || '<div class="'+(v.c||'')+'">'+(def.html||v.d||'')+'</div>');
}
```

### Fallback chain semantics

When the user clicks a variant, the code display shows the best available representation of "the full code":

1. **`v.h`** — variant-specific HTML template (preferred — shows exact markup)
2. **Constructed element** — combines the variant's wrapper classes (`v.c`) with the component's default inner HTML (`def.html`) into `<div class="v.c">def.html</div>`
3. **`v.d`** — description / short class string (worst case, no HTML at all)
```

## When to use this

| Pattern | Use case |
|---------|----------|
| **Data-driven** (compDefs) | 10+ components, each with 2-5 variants. All components share the same rendering layout. |
| **Per-section handlers** | < 5 demos, each with unique interaction (sliders, drag, complex JS). |

## Notes

- The `c` property IS the className — it replaces the preview's entire className. If the preview has structural base classes that shouldn't change, prefix them in every variant.
- The `d` property doubles as documentation. In the tailwind-playground it's shown verbatim as the code label.
- For components that need zero JS interaction (pure visual), set `html` to the full inner HTML and omit `h` from each variant. For components that need different markup per variant, omit `html` and set `h` on each variant.

## Pitfalls

### `t.html` vs `def.html` — variable scoping in updater functions

The builder's `.map()` callback has `t` in scope (the current component definition). The updater function does NOT — it must use the looked-up definition instead:

```js
// Builder — t.html works fine
compDefs.map(t => {
  return escHtml(v.h || t.html || v.d || '');
});

// Updater — t is undefined here. Use def.html (from compDefs.find(...))
function compUpdate(prop, value) {
  const def = compDefs.find(d => d.id === prop);
  code.textContent = v.h || def.html || v.d || '';  // CORRECT
  // code.textContent = v.h || t.html || v.d || '';  // ReferenceError
}
```

### All variants need `v.h` for distinct HTML — or the fallback kicks in

If one variant lacks `v.h` but the component has a `html` field, the fallback chain constructs `<div class="v.c">def.html</div>`. This correctly shows the wrapper classes + default inner HTML. But if ALL variants share the same `def.html`, the code display will only differ by the wrapper classes (`v.c`). The user sees "the classes changed" which is correct but less informative than true variant-specific HTML.

To get full variant-specific HTML: ensure every variant has a distinct `h` property. The effort scales with the number of variants but produces the richest code display.

## Beyond the Data-Driven Pattern

### Dual-axis components (Button: 2 independent toggle axes)

The data-driven `compUpdate` assumes one prop → one preview. For dual-axis components (var × size), the update function must combine both state values:

```js
if (prop === 'btnVar' || prop === 'btnSize') {
  compState[prop] = value;
  const btn = document.getElementById('compBtnPreview');
  const vars = {solid:'bg-blue-600 ...', outline:'border-2 ...', ghost:'text-slate-300 ...'};
  const siz = {sm:'px-3 py-1.5 text-xs', md:'px-4 py-2 text-sm', lg:'px-6 py-3 text-base'};
  btn.className = (vars[compState.btnVar]||vars.solid) + ' ' + (siz[compState.btnSize]||siz.md);
  code.textContent = prettyHTML('<button class="' + btn.className + '">Button</button>');
  return; // must return before the general-purpose compUpdate runs
}
```

**Why separate from compDefs:** Button needs a click handler per axis (two separate `<div>s` of buttons), not one, and the preview is a single `<button>` element shared by both axes. The data-driven template (one preview + one button row) can't represent this.

### State-machine components (Input: default/focus/error/disabled)

Components that affect multiple DOM properties (class string, disabled attribute, hint text, hint color) use a state lookup table, not variant class replacement:

```js
if (prop === 'input') {
  const el = document.getElementById('compInput');
  const hint = document.getElementById('compInputHint');
  const st = {default: 'border-slate-600 ...', focus: 'border-blue-400 ...', error: 'border-red-500 ...', disabled: 'border-slate-700 ...'};
  el.className = 'w-full bg-slate-800 ... ' + (st[value]||st.default);
  el.disabled = value === 'disabled';
  hint.textContent = stateMessages[value];
  hint.className = 'text-xs mt-1 ' + (value==='error' ? 'text-red-400' : 'text-slate-500');
  code.textContent = prettyHTML('<input class="' + el.className + '" type="email" ... />');
  return;
}
```

**When to use:** The data-driven pattern handles cosmetic class changes. When a state also changes text, attributes (disabled), or sibling elements, a dedicated handler is simpler than extending the data model.

### Preserving the fallback chain between initial render and runtime

The initial render (template literal in `buildComponents()`) and `compUpdate()` MUST agree on what text goes into the code display. The fallback chain (`v.h` → constructed wrapper → `v.d`) must match:

```js
// Initial render (inside .map(): t = current compDef)
escHtml(prettyHTML(v.h || '<div class="'+(v.c||'')+'">'+(t.html||v.d||'')+'</div>'))

// Runtime (def = compDefs.find() result)
code.textContent = prettyHTML(v.h || '<div class="'+(v.c||'')+'">'+(def.html||v.d||'')+'</div>')
```

The `t` vs `def` distinction is required by scoping — `t` only exists in the `.map()` callback. See the main SKILL.md Pitfalls for the full explanation of why `t.html` fails at runtime.
