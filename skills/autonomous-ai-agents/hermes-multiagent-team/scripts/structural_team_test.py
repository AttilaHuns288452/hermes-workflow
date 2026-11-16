#!/usr/bin/env python3
"""Deterministic structural test for a Hermes specialist team.

Adapt ROLES and the required clause lists to the team under test, then run:
    python3 scripts/structural_team_test.py
Asserts, without model calls: shared contract skills are propagated byte-identical
into every profile-local skill tree, and every role SOUL carries the required
alignment/traceability clauses. Extend with project-specific contract strings.
"""
from pathlib import Path
import hashlib

ROOT = Path.home() / ".hermes"
TEAM = ROOT / "team"
ROLES = ["engineering", "designer", "marketing", "sales", "research", "documents", "qa"]
SHARED_SKILLS = ["autonomous-ai-agents/team-alignment-traceability"]
REQUIRED_CHARTER = [
    "## Roles",
    "## Alignment and provisioning",
    "## Traceability",
]
REQUIRED_SKILL = [
    "## Procedure",
    "## Skill Gap Rule",
    "## Verification",
]
REQUIRED_SOUL = [
    "team-alignment-traceability",
    "acceptance criteria",
    "provenance",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    charter = (TEAM / "CHARTER.md").read_text()
    for needle in REQUIRED_CHARTER:
        assert needle in charter, f"missing charter contract: {needle}"

    for rel in SHARED_SKILLS:
        canonical = ROOT / "skills" / rel / "SKILL.md"
        assert canonical.is_file(), f"missing canonical shared skill: {rel}"
        want = sha(canonical)
        for role in ROLES:
            copy = ROOT / "profiles" / role / "skills" / rel / "SKILL.md"
            assert copy.is_file(), f"{role}: shared skill not propagated: {rel}"
            assert sha(copy) == want, f"{role}: shared skill drift: {rel}"

    for rel in SHARED_SKILLS:
        skill = (ROOT / "skills" / rel / "SKILL.md").read_text()
        for needle in REQUIRED_SKILL:
            assert needle in skill, f"{rel}: missing skill contract: {needle}"

    for role in ROLES:
        soul_path = ROOT / "profiles" / role / "SOUL.md"
        assert soul_path.is_file(), f"missing role SOUL: {role}"
        soul = soul_path.read_text()
        for needle in REQUIRED_SOUL:
            assert needle in soul, f"{role}: missing alignment rule: {needle}"

    print(f"PASS: {len(ROLES)} specialists share contracts and {len(SHARED_SKILLS)} propagated skill(s)")


if __name__ == "__main__":
    main()
