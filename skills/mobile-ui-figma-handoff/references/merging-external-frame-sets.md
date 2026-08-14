# Merging a prebuilt external frame set (per-file HTML → one Figma board)

When the user hands over an EXISTING folder of `NN_Name.html` screens (built by
another tool/session, e.g. an `*_UI/` folder in Downloads) and asks to fix
inconsistencies and make it Figma-importable. These differ from generator output:
each file carries its own `<style>` + SVG sprite, frames are bare
`<div class="frame" data-od-id="...">` (no frame-wrap, no visible label), and the
files are usually CRLF.

Verified recipe (2026-08-14, Guardian Alert UI, 14 frames):

## 1. Content audit first (cheap, catches most "inconsistencies")

```bash
grep -o '>[A-Z][^<]\{3,80\}<' 04_04_Home.html   # visible copy
grep -o '[a-z]*@domain\.ph' *.html | sort | uniq -c   # identity consistency
grep -l '—' *.html                                # em-dash sweep (user rule: none)
grep -c '<nav class="bottom-nav"' *.html          # nav coverage map
```
Check against the product's canonical story: same accounts/emails/places across
variants, team lists match the proposal doc, device serials/states consistent.
Auth screens legitimately have no nav; every tabbed screen must.

## 2. Extraction regex + the closing-div trap

```python
m = re.search(r'(<div class="frame".*?)\n\s*</div>\s*</body>', t, re.S)
```
This regex CONSUMES the frame's own final `</div>` (the one before `</body>`),
so the merged wrapper must close BOTH frame and wrap:

```python
wraps.append(f'<div class="frame-wrap"><div class="frame-label">{label}</div>\n{s}\n      </div>\n    </div>')
#                                        ^ group(1) minus its closing div   ^ frame   ^ wrap
```
With only one closing `</div>`, frame 1 never closes and Chromium nests ALL
subsequent frames inside frame 1. Symptoms: per-frame `innerHTML.length` in the
60K+ range (file was 20K), while `children.length` still reads 1. html5lib may
parse the same file as clean siblings — trust the BROWSER DOM, it is the renderer.

## 3. Sprite union (per-file sprites are incomplete)

Each source file defines only the icons it uses. The merged board must union:

```python
syms = {}
for f in files:
    for sm in re.finditer(r'<symbol id="([^"]+)"[^>]*>(.*?)</symbol>', open(f, encoding='utf-8').read(), re.S):
        syms[sm.group(1)] = sm.group(0)
sprite_block = '<svg width="0" height="0" style="position:absolute;visibility:hidden;"><defs>' + ''.join(syms.values()) + '</defs></svg>'
```
Without this, every `<use href="#icon-...">` whose symbol lived in another
file's sprite renders broken in the merged board.

## 4. Browser verification probe (authoritative)

```python
r = pg.evaluate('''() => {
  const fs = [...document.querySelectorAll("div.frame")];
  return {
    n: fs.length,
    size_ok: fs.every(e => e.offsetWidth===390 && e.offsetHeight===844),
    bad_icons: fs.reduce((a,e)=>a+[...e.querySelectorAll("svg use")].filter(u=>!u.getAttribute("href")||!document.querySelector(u.getAttribute("href"))).length,0),
    lens: fs.map(e=>e.innerHTML.length).join(","),          // re-parenting detector
    nav: fs.map(e=>e.querySelector("nav.bottom-nav")?1:0).join("")
  };
}''')
```
- Use `div.frame` / `nav.bottom-nav` — bare `.frame`/`.bottom-nav` confusion cost a debugging round.
- `lens` per frame must stay plausible (< file size); one 60K entry = nesting bug.
- html5lib (`pip install html5lib`) is a useful structural cross-check but Chromium wins disagreements.

## 5. Missing product moment

If the deck lacks the app's defining interaction (distress-button app with no
alert-fired screen), ADD one frame for it using the existing tokens — reviewers
see the hole before any polish issue. Copy an existing file's head+style+sprite
as the base; add missing icons to the sprite (`<symbol>` lines, lucide paths).

## 6. Misc

- CRLF files: anchor regexes on `\s*`, not literal `\n`.
- Third-party frames often lack visible labels (title tag only); emit a
  `.frame-label` per frame during merge so Figma gets named frames.
- `open(f, encoding='utf-8').read()` normalizes CRLF to LF on read; writing back
  with text mode re-emits platform newlines — harmless for html.to.design.
