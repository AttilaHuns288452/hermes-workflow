#!/usr/bin/env python3
"""Audit all Hermes skill dirs for broken SKILL.md files.

Checks per SKILL.md: frontmatter parses, description present, referenced
linked files exist (references/templates/scripts), required_commands on PATH,
and name collisions across dirs. Prints ISSUES: N; exit 1 if any.

Usage: python scripts/audit-skill-dirs.py [hermes_root]
Default hermes_root: ~/AppData/Local/hermes (overridable, e.g. on Linux ~/.hermes).
"""
import glob
import os
import shutil
import sys
import yaml

HERMES_ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/AppData/Local/hermes")
PRIMARY = os.path.join(HERMES_ROOT, "skills")
if not os.path.isdir(PRIMARY):
    print("No skills dir at", PRIMARY); sys.exit(2)

dirs = [PRIMARY]
cfg_path = os.path.join(HERMES_ROOT, "config.yaml")
if os.path.exists(cfg_path):
    cfg = yaml.safe_load(open(cfg_path, encoding="utf-8")) or {}
    dirs += [d for d in cfg.get("skills", {}).get("external_dirs", []) if os.path.isdir(d)]

names: dict[str, list[str]] = {}
issues: list[str] = []
total = 0
for d in dirs:
    for md in glob.glob(os.path.join(d, "*", "SKILL.md")):
        total += 1
        try:
            txt = open(md, encoding="utf-8", errors="replace").read()
            parts = txt.split("---", 2)
            if len(parts) < 3:
                issues.append(f"NO FRONTMATTER: {md}"); continue
            meta = yaml.safe_load(parts[1]) or {}
            name = meta.get("name", os.path.basename(os.path.dirname(md)))
            if not meta.get("description"):
                issues.append(f"NO DESCRIPTION: {md}")
            for key in ("references", "templates", "scripts"):
                for ref in (meta.get(key) or []):
                    p = os.path.normpath(os.path.join(os.path.dirname(md), key, ref))
                    if not os.path.exists(p):
                        issues.append(f"MISSING {key}/{ref}: {md}")
            for c in (meta.get("required_commands") or []):
                if not shutil.which(c):
                    issues.append(f"MISSING CMD '{c}': {md}")
            names.setdefault(name, []).append(md)
        except Exception as e:  # noqa: BLE001 - report any parse failure
            issues.append(f"PARSE ERR {md}: {str(e)[:80]}")

# ponytail: the primary dir + ~/.agents/skills mirror is a by-design sync; only
# collisions where a name appears in 2+ DISTINCT dirs are suspicious
dups = {n: p for n, p in names.items() if len({os.path.dirname(x) for x in p}) > 1}
print(f"TOTAL SKILL.md: {total} | unique names: {len(names)} | cross-dir collisions: {len(dups)}")
for n, p in sorted(dups.items()):
    print(f"  DUP '{n}':")
    for x in p:
        print(f"    - {x}")
print(f"ISSUES ({len(issues)}):")
for i in issues[:40]:
    print("  ", i)
sys.exit(1 if issues else 0)
