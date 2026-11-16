#!/usr/bin/env python3
"""Repo drift check: does the public hermes-workflow repo still describe and carry
the live skill tree?

Compares ~/.hermes/skills against the repo's skills/ by frontmatter name (dir name
fallback), and checks the counts advertised in the repo's own docs.

Exit 0 = in sync (or only unpublished local work, reported).
Exit 1 = the repo is stale or its docs advertise a wrong number.
Exit 2 = the live skills root is missing, so comparison is impossible.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

import yaml

REPO = pathlib.Path(__file__).resolve().parents[1]
REPO_SKILLS = REPO / "skills"
LIVE = pathlib.Path.home() / ".hermes/skills"
DOC_COUNT_FILES = ["README.md", "SKILLS_CATALOG.md", "INTEGRATION.md"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live-root", type=pathlib.Path, default=LIVE,
                        help="live skills root (default: ~/.hermes/skills)")
    parser.add_argument("--repo-root", type=pathlib.Path, default=REPO,
                        help="published repository root (default: script parent)")
    return parser.parse_args()


def is_archived(path: pathlib.Path) -> bool:
    return ".archive" in path.parts or "node_modules" in path.parts


def collect_by_path(root: pathlib.Path) -> dict[str, pathlib.Path]:
    return {
        str(f.relative_to(root)): f
        for f in root.rglob("SKILL.md")
        if not is_archived(f)
    }


def collect(root: pathlib.Path) -> dict[str, pathlib.Path]:
    out: dict[str, pathlib.Path] = {}
    for f in sorted(root.rglob("SKILL.md")):
        if is_archived(f):
            continue
        name = f.parent.name
        try:
            fm = yaml.safe_load(f.read_text(errors="replace").split("---", 2)[1])
            if isinstance(fm, dict) and fm.get("name"):
                name = str(fm["name"]).strip().casefold()
        except Exception:
            pass
        out.setdefault(name, f)
    return out


def advertised_counts(repo_root: pathlib.Path) -> list[tuple[str, int]]:
    found = []
    for rel in DOC_COUNT_FILES:
        p = repo_root / rel
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
    args = parse_args()
    repo_root = args.repo_root.resolve()
    repo_skills = repo_root / "skills"
    live_root = args.live_root.expanduser().resolve()
    if not repo_skills.is_dir():
        raise SystemExit(f"repo skills root does not exist: {repo_skills}")
    if not live_root.is_dir():
        print(f"LIVE ROOT MISSING: {live_root}; unable to compare repository drift")
        return 2
    repo = collect(repo_skills)
    live = collect(live_root)
    repo_paths = collect_by_path(repo_skills)
    live_paths = collect_by_path(live_root)
    shared_paths = set(repo_paths) & set(live_paths)
    stale_paths = sorted(
        rel for rel in shared_paths
        if repo_paths[rel].read_bytes() != live_paths[rel].read_bytes()
    )
    # Name-based output preserves the old useful summary, while path-based comparison
    # prevents duplicate frontmatter names from hiding a changed copy.
    repo_only = sorted(set(repo) - set(live))
    local_only = sorted(set(live) - set(repo))

    actual_files = len(repo_paths)
    print(f"repo SKILL.md files: {actual_files} | unique names: {len(repo)} | live: {len(live)} | shared: {len(set(repo) & set(live))}")
    print(f"stale (path content differs): {len(stale_paths)} | unpublished local: {len(local_only)} | library-only: {len(repo_only)}")
    for rel in stale_paths[:5]:
        print(f"  stale: {rel}")
    for n in local_only[:5]:
        print(f"  unpublished: {n}")

    bad_counts = [(repo_root / f, n) for f, n in advertised_counts(repo_root) if n != actual_files]
    for f, n in bad_counts:
        print(f"COUNT DRIFT: {f} advertises {n}, repo holds {actual_files}")

    if bad_counts or stale_paths:
        print("DRIFT: repo needs a sync (skill-library-publication)")
        return 1
    print("OK: repo matches the live tree" + (" (new local work pending publication)" if local_only else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
