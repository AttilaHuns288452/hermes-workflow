# QA recipes (Playwright sync API)

Runnable patterns for the verification loop. Serve the repo first:
`python3 -m http.server <port>` in the repo root.

## Hit-test every CTA and image-CTA (catches "button does nothing")

```python
res = pg.evaluate("""() => {
    const out = [];
    for (const a of document.querySelectorAll('a.btn, .store-badges a')) {
        a.scrollIntoView({block:'center'});
        const r = a.getBoundingClientRect();
        const cx = Math.min(Math.max(r.x + r.width/2, 1), innerWidth-1);
        const cy = Math.min(Math.max(r.y + r.height/2, 1), innerHeight-1);
        const top = document.elementFromPoint(cx, cy);
        out.push({t: a.textContent.trim().slice(0,16) || a.querySelector('img')?.alt,
                  hit: top && (a.contains(top) || top.contains(a)) ? 'SELF' : (top ? top.tagName : 'NULL')});
    }
    return out;
}""")
# every entry must be SELF; 'IMG' or another tag = something covers it or it is not a link
```

## Grid stacking check per viewport (cascade-order bug detector)

```python
cols = pg.evaluate("""() => {
    const g = document.querySelector('.the-grid');
    return g ? getComputedStyle(g).gridTemplateColumns.split(' ').length : 'n/a';
}""")
# desktop expect 2; tablet/mobile expect 1. If mobile still reports 2, a
# page-scoped rule defined AFTER the media query is winning the cascade.
```

Also assert `document.documentElement.scrollWidth <= clientWidth` — but remember
overflow passes on squeezed grids; the column count is the real assertion.

## Broken-image check that does not false-fail on lazy loading

```python
h = pg.evaluate("document.body.scrollHeight")
for y in range(0, h, 900):
    pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(40)
pg.wait_for_timeout(300)
broken = pg.evaluate("[...document.images].filter(i=>!(i.complete&&i.naturalWidth>0)).length")
```

## Section-local tag balance after markup surgery

```python
import re
t = pathlib.Path(page).read_text()
i = t.find(section_anchor)
seg = t[i:t.find("</section>", i)]
o, c = len(re.findall(r"<div[ >]", seg)), seg.count("</div>")
assert o == c, (o, c)
```

## CSS surgery post-checks

```python
assert css.count("{") == css.count("}")
# then in Playwright, computed-style spot checks of every class the surgery touched:
getComputedStyle(el).backgroundColor / fontFamily / gridTemplateColumns
# catches regex purges that ate a fresh rule via substring match
```

## Live-deploy verification after push

```bash
sleep 150   # GH Pages cold start
for i in 1 2 3 4 5; do
  html=$(curl -s https://user.github.io/repo/page.html)
  new=$(echo "$html" | grep -c 'new-selector')
  old=$(echo "$html" | grep -c 'removed-selector')
  [ "$new" -ge 1 ] && [ "$old" = "0" ] && { echo LIVE; break; }
  sleep 45
done
```

## Full audit sweep (one pass, 5 pages x 3 viewports)

Per viewport, per page: networkidle + scroll-through, then assert
`scrollWidth <= clientWidth`, broken images == 0, console errors == 0,
`querySelectorAll('h1').length >= 1`, and heading outline has no h1->h3 jumps.
Collect into a results dict; report ALL OK or the failing cells only.

## Extracting embedded base64 images from a doc

```python
import base64, pathlib, re
src = pathlib.Path(doc).read_text()
out = pathlib.Path(repo / "assets/app-reference"); out.mkdir(exist_ok=True)
imgs = re.findall(r'\[image\d+\]:\s*<data:image/(\w+);base64,([A-Za-z0-9+/=]+)>', src)
for num, ext, b64 in imgs:
    (out / f"image{num}.{ext}").write_bytes(base64.b64decode(b64))
```

Use for app-spec docs whose embedded screenshots are other brands' UI: extract
to an assets/app-reference folder for the team, never onto the public site.

## Score-breakdown / factor-matrix QA (decision-support sites)

For sites that render N factor cells each with label + numeric score + weight chip
+ progress bar (AI-visualization pattern):

1. **Order cells by weight desc, then score desc** — the factors that decided the
   outcome render first. Fixed data order buries the deciding factors below the
   fold and reads as a dashboard, not an explanation.
2. **Color bars semantically, not by brand**: green for strong, brand for mid,
   red for weak, neutral for unscored. Ten uniform brand-colored bars encode
   nothing (38/100 looks identical to 100/100).
3. **Overlap probe** (labels + right-aligned numerics collide in narrow cells,
   vision QA flags it as 'text rendered on top of text'):

```python
cells = pg.evaluate("""() => [...document.querySelectorAll('.factor-cell')].map(c => {
    const r = c.getBoundingClientRect();
    const kids = [...c.children].map(k => k.getBoundingClientRect());
    return {w: Math.round(r.width),
            overlap: kids.some((a,i) => kids.slice(i+1).some(b => a.right > b.left))};
})""")
# any overlap:true or cell width < ~150px → widen the grid minmax and add
# flex-shrink:0 to the numeric span
```

4. Keep the ×N weight explanation to one plain-language line ('×3 counts triple');
   'weighted average, rescaled to 100' is leaked-implementation voice.
