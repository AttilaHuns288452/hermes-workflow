#!/usr/bin/env python3
"""Repo drift check: does the public hermes-workflow repo still describe and carry
the live skill tree?

Compares ~/.hermes/skills against the repo's skills/ by frontmatter name (dir name
fallback), and checks the counts advertised in the repo's own docs.

Exit 0 = in sync (or only unpublished local work, reported).
Exit 1 = the repo is stale or its docs advertise a wrong number.
"""
from __future__ import annotations

import pathlib
import re
import sys

import yaml

REPO = pathlib.Path.home() / "Documents/Projects/hermes-workflow"
REPO_SKILLS = REPO / "skills"
LIVE = pathlib.Path.home() / ".hermes/skills"
DOC_COUNT_FILES = ["README.md", "SKILLS_CATALOG.md", "INTEGRATION.md"]


def collect(root: pathlib.Path) -> dict[str, pathlib.Path]:
    out: dict[str, pathlib.Path] = {}
    for f in root.rglob("SKILL.md"):
        if "/.archive/" in str(f) or "/node_modules/" in str(f):
            continue
        name = f.parent.name
        try:
            fm = yaml.safe_load(f.read_text(errors="replace").split("---", 2)[1])
            if isinstance(fm, dict) and fm.get("name"):
                name = str(fm["name"])
        except Exception:
            pass
        out.setdefault(name, f)
    return out


def advertised_counts() -> list[tuple[str, int]]:
    found = []
    for rel in DOC_COUNT_FILES:
        p = REPO / rel
        if not p.exists():
            continue
        text = p.read_text(errors="replace")
        nums = re.findall(r"\b(1[,.][0-9]{3}|[0-9]{4})\b\s*(?:SKILL\.md|skills)", text, re.I)
        if not nums:
            nums = re.findall(r"skills[- ]([0-9]{4})", text, re.I)
        if nums:
            found.append((rel, int(nums[0].replace(",", "").replace(".", ""))))
    return found


def main() -> int:
    repo, live = collect(REPO_SKILLS), collect(LIVE)
    shared = set(repo) & set(live)
    repo_only = sorted(set(repo) - set(live))
    local_only = sorted(set(live) - set(repo))
    differs = [n for n in shared if repo[n].read_bytes() != live[n].read_bytes()]

    actual_files = len([f for f in REPO_SKILLS.rglob("SKILL.md") if "/node_modules/" not in str(f)])
    actual = actual_files
    print(f"repo SKILL.md files: {actual_files} | unique names: {len(repo)} | live: {len(live)} | shared: {len(shared)}")
    print(f"stale (content differs): {len(differs)} | unpublished local: {len(local_only)} | library-only: {len(repo_only)}")
    for n in differs[:5]:
        print(f"  stale: {n}")
    for n in local_only[:5]:
        print(f"  unpublished: {n}")

    bad_counts = [(f, n) for f, n in advertised_counts() if n != actual]
    for f, n in bad_counts:
        print(f"COUNT DRIFT: {f} advertises {n}, repo holds {actual}")

    if bad_counts or differs:
        print("DRIFT: repo needs a sync (skill-library-publication)")
        return 1
    print("OK: repo matches the live tree" + (" (new local work pending publication)" if local_only else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
