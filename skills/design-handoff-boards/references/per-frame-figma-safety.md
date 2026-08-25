# Per-frame Figma-safety routine (no merge)

Run when individual `frames/NN_*.html` already exist and need to be import-safe
for `html.to.design`, but you are NOT producing a single merged import board
(`merge_frames.py` already does this inline — don't double-run it there).

Paste and edit the `frames` list. Run `python - << 'PY'`.

```python
import pathlib, re

base = pathlib.Path("C:/Users/Attila/Documents/Projects/<project>/design/frames")
frames = ["34_Dentist_Analytics_Empty.html","14_Dentist_Analytics.html",
          "15_Dentist_Transactions.html","35_Dentist_Add_Payment_Dialog.html",
          "57_Income_Receipt.html","66_Income_Add_Expense.html","58_Income_Reports.html"]

def fix(p):
    t = p.read_text(encoding="utf-8")
    # 1) resolve CSS vars
    vm = {m.group(1): m.group(2).strip() for m in re.finditer(r'--([a-z0-9-]+)\s*:\s*([^;}\n]+);', t)}
    t = re.sub(r'var\(--([a-z0-9-]+)(?:,\s*([^)]+))?\)',
               lambda m: vm.get(m.group(1), (m.group(2) or '').strip().strip('"').strip("'")), t)
    # 2) inline <use href="#id"> sprites
    syms = {m.group(1): (m.group(2), m.group(3))
            for m in re.finditer(r'<symbol id="([^"]+)"[^>]*viewBox="([^"]+)"[^>]*>(.*?)</symbol>', t, re.S)}
    def use(m):
        o, sid = m.group(1), m.group(2).lstrip('#')
        if sid not in syms: return m.group(0)
        vb, inner = syms[sid]
        cls = re.search(r'class="([^"]+)"', o)
        w = re.search(r'width="([^"]+)"', o); h = re.search(r'height="([^"]+)"', o)
        st = re.search(r'style="([^"]+)"', o)
        a = f' class="{cls.group(1)}"' if cls else ''
        wh = ((' width="' + w.group(1) + '"') if w else '') + ((' height="' + h.group(1) + '"') if h else '')
        s = f' style="{st.group(1)}"' if st else ''
        return f'<svg viewBox="{vb}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"{a}{s}{wh}>{inner}</svg>'
    t = re.sub(r'(<svg[^>]*>)\s*<use href="#([^"]+)"[^>]*/?>\s*</svg>', use, t, flags=re.S)
    t = re.sub(r'<svg style="display:none".*?</svg>\s*', '', t, flags=re.S)
    t = re.sub(r'<symbol.*?</symbol>\s*', '', t, flags=re.S)
    # 3) other negatives
    t = t.replace('<a ', '<div ').replace('</a>', '</div>')
    t = re.sub(r'rgba\(0,\s*0,\s*0,\s*[^)]+\)', '#e2e8f0', t)
    p.write_text(t, encoding="utf-8")

for n in frames:
    fix(base / n)

# verify
for n in frames:
    t = (base / n).read_text(encoding="utf-8")
    bad = [x for x in ["var(","<use","<symbol","rgba(","position:absolute","position:fixed","<a "] if x in t]
    print(("OK  " if not bad else "BAD "), n, bad or '')
```

Asserts (run after): `var(` / `<use` / `<symbol` / `rgba(` / `position:absolute` / `position:fixed` all absent, and `width:390px;height:844px` present in each frame.
