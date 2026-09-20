# Working generator: GadgetWise → Figma board (reference implementation)

Source of truth for every rule in this skill: ~/Documents/Projects/gadgetwise-figma/build_figma_board.py

## Structure

```python
PAGES = [
    ("01 · Home", "/index.html", {}),                                   # dict = localStorage seed
    ("07 · Recommender · Step 2 Budget", "/recommendations.html",
     'rec:2:click [data-cat=laptops]; goto 2'),                        # str 'rec:' = wizard drive
    ("10 · Recommender · Results", "/recommendations.html",
     'rec:5:click [data-cat=laptops]; goto 2; click [data-budget="20-40k"];'
     ' goto 3; click [data-use=programming]; goto 4; click #calcBtn; goto 5'),
]
```

Wizard seed grammar: `rec:N:action; action` where action =
- `click SELECTOR` — click on the currently visible pane
- `goto N` — advance to absolute step N via `[data-step=cur] [data-next=cur+1]` clicks

Landing assertion: `pg.is_visible(f'[data-step="{step_n}"]')` — fails the build if the wizard
lands short. Stepper sub-label text is NOT proof of landing.

## CSS flatten (one pass over ALL stylesheets, alias chains resolved in-map)

```python
def flatten_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    root_vars = {}
    for m in re.finditer(r":root\s*\{([^}]*)\}", css):
        root_vars.update(re.findall(r"(--[\w-]+)\s*:\s*([^;}]+)", m.group(1)))
    css = re.sub(r":root\s*\{[^}]*\}", "", css)
    for _ in range(4):   # alias chains: --accent: var(--primary) -> #1D5BA4
        for name, val in root_vars.items():
            root_vars[name] = re.sub(r"var\((--[\w-]+)\)",
                lambda m: root_vars.get(m.group(1), m.group(0)).strip(), val).strip()
            css = css.replace(f"var({name})", root_vars[name])
    css = re.sub(r"@keyframes[^{]+\{(?:[^{}]*\{[^}]*\})*[^}]*\}", "", css)
    for pat in [r"animation[^;]*;", r"transition[^;]*;", r"backdrop-filter[^;]*;"]:
        css = re.sub(pat, "", css)
    css = re.sub(r"position:\s*(?:sticky|fixed)", "position: static", css)
    return css, root_vars
```

The returned `root_vars` (fully resolved) is what you substitute into captured markup —
resolving only the CSS strands inline `style="color:var(--ink-2)"` and SVG `fill="var(--x)"`.

## rgba flattening — blend over the element's real background

```python
# over white page: c*a + 255*(1-a);  over dark hero band (#14213A): c*a + band*(1-a)
def over(m, band):
    a = float(m.group(4)); r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
    f = lambda c: round(c * a + band * (1 - a))
    return f"#{f(r):02X}{f(g):02X}{f(b):02X}"
css = re.sub(r"rgba\((\d+),(\d+),(\d+),([\d.]+)\)", lambda m: over(m, 255), css)
body = re.sub(r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*([\d.]+)\s*\)",
              lambda m: over_white_on_band(m, (20, 33, 58)), body)   # hero-band scrims only
```

## In-page cleanup (page.evaluate, BEFORE innerHTML extraction)

```js
() => {
  document.querySelectorAll('script,style,template,noscript,link').forEach(e => e.remove());
  document.querySelectorAll('.skip-link').forEach(e => e.remove());   // negative-offset = phantom space
  document.querySelectorAll('*').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) el.remove();
  });
  document.querySelectorAll('a[href]').forEach(a => a.setAttribute('href', '#'));
  return document.body.innerHTML;
}
```

## Banned-token assert scans the BODY only

```python
board_body = doc.split("</head>", 1)[1]
for banned in ["<script", "<style", "position:fixed", "position:sticky", "@keyframes",
               "var(", "rgba(", "backdrop-filter", "<use ", "<symbol"]:
    assert banned not in board_body, f"banned '{banned}' in output body"
assert doc.count('class="frame"') == EXPECTED_FRAMES
assert doc.count("{") == doc.count("}")
```

## Geometry + content QA (node, playwright from hermes-agent node_modules)

Per `.frame`: `w === expected`, no descendant `right > frame.right + 2`, `innerText.length > 40`,
element count reported. Content markers per frame class (budget band label in budget frames,
`BEST MATCH` + `#[1-5]` in results frames, seeded item names in account frames).
Vision spot-checks AFTER geometry: screenshot by nth `.frame` index, not by assumed file name.
