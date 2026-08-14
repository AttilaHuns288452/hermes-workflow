#!/usr/bin/env python3
"""Static + browser audit for generated Figma frames. Run: python audit.py [frames_dir]
Checks: tag balance (self-closing-aware), unresolved <use> refs, CSS braces outside
<style>, brace balance per style block, hardcoded colors vs token whitelist (adapt the
whitelist to the project palette), leaf-text overflow (nowrap elements where
scrollWidth > clientWidth), and render uniqueness via PNG md5 (byte-identical frame
renders = dropped content). Exits 1 with findings, 0 when clean.
On Windows use the absolute python (bare `python` may lack playwright).
"""
import glob, os, re, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "frames")
SELF_CLOSING = {"path", "rect", "line", "text", "use", "circle", "input", "br", "hr", "img"}

# Tokens allowed outside :root (adapt per project). Everything else flagged.
TOKEN_WHITELIST = {
    "#ffffff", "#0d9488", "#0f766e", "#e6f4f3", "#1e293b", "#475569", "#94a3b8",
    "#f6f8f8", "#e2e8f0", "#b45309", "#fef3c7", "#15803d", "#dcfce7", "#1d4ed8",
    "#dbeafe", "#b91c1c", "#fee2e2", "#64748b",
}

findings = []
def report(cat, msg):
    findings.append(f"[{cat}] {msg}")

for f in sorted(glob.glob(os.path.join(FRAMES_DIR, "*.html"))):
    name = os.path.basename(f)
    src = open(f, encoding="utf-8").read()
    head = src.split("<body>", 1)[0]
    blocks = re.findall(r"<style>.*?</style>", head, re.S)
    stripped = head
    for b in blocks:
        stripped = stripped.replace(b, "")
    if "{" in stripped or "}" in stripped:
        report("CSS", f"{name}: braces outside <style>")
    for i, b in enumerate(blocks):
        if b.count("{") != b.count("}"):
            report("CSS", f"{name}: style block {i} brace imbalance")
    body = src.split("<body>", 1)[1].split("</body>", 1)[0]
    for tag in ["div", "span", "svg", "symbol", "defs", "textarea", "label", "button"]:
        opens = len(re.findall(rf"<{tag}(?:[ >])", body))
        closes = len(re.findall(rf"</{tag}>", body))
        if opens != closes:
            report("TAGS", f"{name}: <{tag}> {opens} open / {closes} close")
    ids = set(re.findall(r'<symbol id="([^"]+)"', src))
    uses = set(re.findall(r'<use href="#([^"]+)"', src))
    missing = uses - ids
    if missing:
        report("REFS", f"{name}: unresolved icons {sorted(missing)}")
    if re.search(r"lorem|TODO|FIXME|xxx", src, re.I):
        report("CONTENT", f"{name}: lorem/TODO detected")
    for m in re.finditer(r"(#[0-9a-fA-F]{6})\b", src):
        c = m.group(1).lower()
        if c not in TOKEN_WHITELIST:
            line = src[:m.start()].count("\n") + 1
            report("COLOR", f"{name}:{line}: hardcoded {c}")

# render uniqueness (dropped-content detector)
hashes = {}
for p in glob.glob(os.path.join(FRAMES_DIR, "..", "qa", "*.png")):
    h = hashlib.md5(open(p, "rb").read()).hexdigest()
    if h in hashes:
        report("DUP", f"{hashes[h]} and {os.path.basename(p)} render byte-identical")
    hashes[h] = os.path.basename(p)

try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 500, "height": 20000})
        for f in sorted(glob.glob(os.path.join(FRAMES_DIR, "*.html"))):
            name = os.path.basename(f)
            pg.goto("file:///" + f.replace("\\", "/"))
            issues = pg.evaluate("""() => {
                const out = [];
                const fr = document.querySelector('.frame').getBoundingClientRect();
                if (Math.round(fr.width) !== 390 || Math.round(fr.height) !== 844)
                    out.push('frame ' + fr.width + 'x' + fr.height);
                document.querySelectorAll('.frame *').forEach(el => {
                    if (el.children.length === 0 && el.textContent.trim().length > 0) {
                        if (getComputedStyle(el).whiteSpace !== 'nowrap') return;
                        if (el.scrollWidth > el.clientWidth + 2)
                            out.push('overflow: "' + el.textContent.trim().slice(0, 28) + '"');
                    }
                });
                return out.slice(0, 8);
            }""")
            for i in issues:
                report("OVERFLOW", f"{name}: {i}")
        b.close()
except Exception as e:
    report("BROWSER", f"playwright failed: {e}")

if findings:
    print(f"{len(findings)} FINDINGS:")
    print("\n".join(findings))
    sys.exit(1)
print("AUDIT CLEAN — zero findings")
