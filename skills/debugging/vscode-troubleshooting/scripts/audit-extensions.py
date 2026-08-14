"""Audit VS Code extension dirs for truly broken installs + stale duplicates.

Uses Node-style resolution (package.json "main" like ./out/src/extension
resolves to extension.js/.cjs/.mjs). Windows paths. No deps (stdlib only).

Usage:
    "C:\\Users\\Attila\\AppData\\Local\\Programs\\Python\\Python311\\python.exe" audit-extensions.py
"""
import glob
import json
import os

BASE = os.path.expanduser("~/.vscode/extensions")

broken = []
for pkg in glob.glob(os.path.join(BASE, "*/package.json")):
    d = os.path.dirname(pkg)
    try:
        data = json.load(open(pkg, encoding="utf-8"))
    except Exception as e:
        broken.append((os.path.basename(d), "BAD JSON: %s" % e))
        continue
    main = data.get("main")
    if not main:
        continue
    m = main[2:] if main.startswith("./") else main
    cands = [os.path.join(d, m)] + [
        os.path.join(d, m + e) for e in (".js", ".cjs", ".mjs")
    ]
    if not any(os.path.exists(c) for c in cands):
        broken.append((os.path.basename(d), main))

print("TRULY BROKEN:" if broken else "All extensions intact")
for name, main in broken:
    print(" ", name, "->", main)

# duplicate version dirs (same extension id, multiple versions)
names = {}
for d in glob.glob(os.path.join(BASE, "*")):
    n = os.path.basename(d)
    ext = n.rsplit("-", 1)[0]
    names.setdefault(ext, []).append(n)
for ext, vers in sorted(names.items()):
    if len(vers) > 1:
        print("DUPLICATE:", ext, vers)
