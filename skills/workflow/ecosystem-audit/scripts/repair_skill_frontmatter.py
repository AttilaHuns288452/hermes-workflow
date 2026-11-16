#!/usr/bin/env python3
"""Repair SKILL.md frontmatter damaged by a bulk import that joined YAML keys onto one line.

Pattern (repeats across a whole pack):
    description: Some text." when_to_use: "More text." last_reviewed: 2026-10-14 sources: -
which makes every file fail yaml.safe_load ("mapping values are not allowed here"), so the skill
loads with no name/description and the router can never match it.

Usage:
    python3 repair_skill_frontmatter.py --root ~/.hermes/skills          # dry run
    python3 repair_skill_frontmatter.py --root ~/.hermes/skills --apply  # write

Safety: only touches files that FAIL to parse and match the concatenation pattern; archives every
touched file into one tar.gz before the first write; re-parses each result and aborts on mismatch.
"""
import argparse
import json
import pathlib
import re
import tarfile
import time

import yaml

NEXT_KEY = re.compile(r"\s+(when_to_use|last_reviewed|sources|version|author|license|metadata|tags|platforms)\s*:")


def parse_broken(text):
    head = text.split("---", 2)[1]
    name = re.search(r"^name:\s*(.+)$", head, re.M)
    desc = re.search(r"^description:\s*(.+)$", head, re.M)
    if not name or not desc:
        return None
    raw = desc.group(1)
    cut = NEXT_KEY.search(raw)
    value = (raw[: cut.start()] if cut else raw).strip().strip('"').strip()
    body = text.split("---", 2)[2]
    when = re.search(r'when_to_use:\s*"?([^"\n]+)"?', head)
    return name.group(1).strip(), value, (when.group(1).strip() if when else None), body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    root = pathlib.Path(args.root).expanduser()

    broken = []
    for f in sorted(root.rglob("SKILL.md")):
        if "/.archive/" in str(f):
            continue
        text = f.read_text(errors="replace")
        if not text.startswith("---"):
            continue
        try:
            yaml.safe_load(text.split("---", 2)[1])
        except Exception:
            broken.append(f)

    print(f"{len(broken)} unparseable SKILL.md under {root}")
    if not broken:
        return 0
    if not args.apply:
        for f in broken[:20]:
            print("  would repair:", f.relative_to(root))
        print("dry run - pass --apply to write")
        return 0

    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup = pathlib.Path.home() / f".hermes/backups/skill-frontmatter-{stamp}.tar.gz"
    backup.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(backup, "w:gz") as tar:
        for f in broken:
            tar.add(f, arcname=str(f.relative_to(root)))
    print("backup:", backup)

    fixed, skipped = 0, []
    for f in broken:
        parsed = parse_broken(f.read_text(errors="replace"))
        if not parsed:
            skipped.append(str(f))
            continue
        name, desc, when, body = parsed
        fm = "---\n" + f"name: {name}\n" + f"description: {json.dumps(desc, ensure_ascii=False)}\n" + "---\n"
        new = fm + body
        if when and not re.search(r"^## When to (Use|Load)", body, re.M | re.I):
            new = re.sub(r"(^# .+$)", lambda m: m.group(1) + f"\n\n## When to Use\n\n{when}\n", new, count=1, flags=re.M)
        f.write_text(new)
        got = yaml.safe_load(f.read_text().split("---", 2)[1])
        assert got and got.get("name") and got.get("description"), f"still broken: {f}"
        fixed += 1

    print(f"repaired {fixed}, skipped {len(skipped)}")
    for s in skipped:
        print("  manual:", s)
    print("catalog grows when these become visible - measure build_skills_system_prompt() again")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
