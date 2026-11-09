#!/usr/bin/env python3
"""Cross-check module dependency ids against installed (and optionally enabled)
modules. A dependency the launcher cannot resolve crashes its start path with a
bare NullReferenceException, so run this after every install / enable change.

Usage: audit_module_deps.py [modules-dir] [--enabled id1,id2,...]
  modules-dir   default: $GAME/Modules or ./Modules
  --enabled     comma list of enabled module ids; deps outside it are flagged
                too (a dep on a DISABLED module crashes the same way)
Exits 1 if any dependency is unresolvable.
"""
import os, sys, xml.etree.ElementTree as ET

def module_id(sm):
    root = ET.parse(sm).getroot()  # mod manifests are user-chosen; the game runs their dlls anyway
    m = root if root.tag == "Module" else root.find("Module")
    if m is not None and m.find("Id") is not None:
        return m.find("Id").get("value")
    return os.path.basename(os.path.dirname(sm))

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    enabled = None
    for a in sys.argv[1:]:
        if a.startswith("--enabled"):
            enabled = set(a.split("=", 1)[1].split(","))
    mods_dir = args[0] if args else os.path.join(os.environ.get("GAME", ""), "Modules")
    if not os.path.isdir(mods_dir):
        for cand in ("Modules", os.path.join("Game", "Modules")):
            if os.path.isdir(cand):
                mods_dir = cand
    ids = {}
    manifests = {}
    for name in sorted(os.listdir(mods_dir)):
        sm = os.path.join(mods_dir, name, "SubModule.xml")
        if not os.path.isfile(sm):
            continue
        if os.path.getsize(sm) == 0:
            print(f"HUSK: {name}: empty SubModule.xml (bad extraction?)")
            continue
        ids[module_id(sm)] = name
        manifests[name] = sm
    bad = 0
    for name, sm in manifests.items():
        for dep in ET.parse(sm).getroot().findall(".//DependedModule"):
            did = dep.get("Id")
            if did not in ids:
                print(f"BROKEN: {name} -> {did} (no such module)")
                bad += 1
            elif enabled is not None and did not in enabled:
                print(f"BROKEN: {name} -> {did} (installed but DISABLED)")
                bad += 1
    print(f"{len(ids)} modules checked, {bad} unresolvable dependencies")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
