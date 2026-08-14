"""Audit a skills library: frontmatter parse, missing descriptions, dangling
reference/template/script paths, missing required_commands, name collisions.

Usage:
  python audit_skills.py <dir1> [<dir2> ...]     # explicit dirs
  python audit_skills.py --hermes               # primary dir + config.yaml external_dirs

Exits 0 when clean, 1 when issues found. Prints every issue; collisions are
informational (mirrored collections are by design).
"""
import glob
import os
import shutil
import sys
import yaml


def main():
    args = sys.argv[1:]
    if "--hermes" in args or not args:
        hermes_home = os.path.expandvars(r"%LOCALAPPDATA%\hermes")
        dirs = [os.path.join(hermes_home, "skills")]
        cfg = yaml.safe_load(open(os.path.join(hermes_home, "config.yaml"), encoding="utf-8"))
        dirs += [d for d in cfg.get("skills", {}).get("external_dirs", []) if os.path.isdir(d)]
    else:
        dirs = [d for d in args if os.path.isdir(d)]

    names: dict[str, list[str]] = {}
    issues = []
    total = 0
    for d in dirs:
        for md in glob.glob(os.path.join(d, "*", "SKILL.md")):
            total += 1
            try:
                txt = open(md, encoding="utf-8", errors="replace").read()
                parts = txt.split("---", 2)
                if len(parts) < 3:
                    issues.append(f"NO FRONTMATTER: {md}")
                    continue
                meta = yaml.safe_load(parts[1]) or {}
                name = meta.get("name", os.path.basename(os.path.dirname(md)))
                if not meta.get("description"):
                    issues.append(f"NO DESCRIPTION: {md}")
                for key in ("references", "templates", "scripts"):
                    for ref in (meta.get(key) or []):
                        # doubled-prefix and ../-escaping refs both fail this check
                        base = os.path.join(os.path.dirname(md), key)
                        if not os.path.exists(os.path.normpath(os.path.join(base, ref))):
                            issues.append(f"MISSING {key}/{ref}: {md}")
                for c in (meta.get("required_commands") or []):
                    if not shutil.which(c):
                        issues.append(f"MISSING CMD '{c}': {md}")
                names.setdefault(name, []).append(md)
            except Exception as e:
                issues.append(f"PARSE ERR {md}: {str(e)[:80]}")

    dups = {n: p for n, p in names.items() if len(p) > 1}
    print(f"TOTAL SKILL.md: {total} | unique names: {len(names)} | collisions: {len(dups)}")
    for n, p in sorted(dups.items()):
        print(f"  DUP '{n}': " + "; ".join(p))
    print(f"ISSUES ({len(issues)}):")
    for i in issues:
        print("  ", i)
    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
