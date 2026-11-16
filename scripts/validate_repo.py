#!/usr/bin/env python3
"""Validate the public repository's portable configuration and documentation.

This is intentionally dependency-light: CI supplies PyYAML, while the local setup
already uses it for skill and drift checks. It validates only repository-owned
configuration and metadata, not third-party vendored project fixtures.
"""
from __future__ import annotations

import pathlib
import re
import sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _check_duplicate_mapping_keys(node, path: str = "") -> None:
    """Inspect SafeLoader nodes without constructing arbitrary Python objects."""
    if isinstance(node, yaml.MappingNode):
        seen = set()
        for key_node, value_node in node.value:
            key = getattr(key_node, "value", None)
            if key in seen:
                where = path or "<root>"
                raise ValueError(f"duplicate YAML key {key!r} at {where}")
            seen.add(key)
            child = f"{path}.{key}" if path else str(key)
            _check_duplicate_mapping_keys(value_node, child)
    elif isinstance(node, yaml.SequenceNode):
        for index, child in enumerate(node.value):
            _check_duplicate_mapping_keys(child, f"{path}[{index}]")


def load_yaml_text(text: str):
    # compose with SafeLoader, then construct with safe_load. No custom constructor
    # or yaml.load is needed, so !!python/object payloads cannot execute.
    node = yaml.compose(text, Loader=yaml.SafeLoader)
    if node is not None:
        _check_duplicate_mapping_keys(node)
    return yaml.safe_load(text)


def load_yaml(path: pathlib.Path):
    return load_yaml_text(path.read_text(encoding="utf-8"))


def tracked_config_files() -> list[pathlib.Path]:
    paths = [ROOT / "config.yaml.template"]
    paths.extend((ROOT / ".github").rglob("*.yml"))
    paths.extend((ROOT / ".github").rglob("*.yaml"))
    return sorted({p for p in paths if p.is_file()})


def check_config_template(errors: list[str]) -> None:
    path = ROOT / "config.yaml.template"
    try:
        config = load_yaml(path)
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)}: YAML parse failed: {exc}")
        return

    if not isinstance(config, dict):
        errors.append("config.yaml.template: top level must be a mapping")
        return
    for section in ("model", "providers", "fallback_providers", "mcp_servers", "delegation"):
        if section not in config:
            errors.append(f"config.yaml.template: missing required section {section!r}")
    placeholder_text = "\n".join(str(config.get(key, "")) for key in ("model", "providers", "fallback_providers"))
    if "YOUR_" not in placeholder_text:
        errors.append("config.yaml.template: model/provider placeholders were removed")
    mcp = config.get("mcp_servers", {})
    if not isinstance(mcp, dict):
        errors.append("config.yaml.template: mcp_servers must be a mapping")
    else:
        for name, entry in mcp.items():
            if not isinstance(entry, dict):
                errors.append(f"config.yaml.template: MCP entry {name!r} is not a mapping")
                continue
            if "command" not in entry and "url" not in entry:
                errors.append(f"config.yaml.template: MCP {name!r} needs command or url")
            args = entry.get("args")
            if args is not None and (not isinstance(args, list) or not all(isinstance(arg, str) for arg in args)):
                errors.append(f"config.yaml.template: MCP {name!r}.args must be a list of strings")
            if any(str(k).startswith("args[") for k in entry):
                errors.append(f"config.yaml.template: MCP {name!r} uses invalid args[N] keys")

    raw = path.read_text(encoding="utf-8")
    if re.search(r"(?m)^\s*args\[\d+\]:", raw):
        errors.append("config.yaml.template: invalid indexed args keys remain")
    if re.search(r"(?m)^\s*[- ]+C:/Users/YOUR_USERNAME", raw):
        errors.append("config.yaml.template: hardcoded Windows placeholder path remains")
    if "YOUR_MODEL_ID" not in raw or "YOUR_PROVIDER_ID" not in raw:
        errors.append("config.yaml.template: portable model/provider placeholders missing")
    if "${HERMES_WORKFLOW_ROOT}/skills" not in raw:
        errors.append("config.yaml.template: repository skills path is not portable")


def check_public_paths(errors: list[str]) -> None:
    """Catch machine-specific paths in public text; secret scans run separately."""
    ignored = {".git", "node_modules"}
    for path in ROOT.rglob("*"):
        try:
            rel = path.relative_to(ROOT)
        except ValueError:
            continue
        if path.is_symlink() or not path.is_file() or any(part in ignored for part in rel.parts):
            continue
        if path.name == ".env" or (path.name.startswith(".env.") and path.name != ".env.example"):
            continue
        if ".pytest_cache" in path.parts or path.suffix.lower() in {".pyc", ".lock"}:
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        # Historical audit/checkpoint notes may intentionally preserve local evidence.
        # Only block machine-specific paths in executable/configuration surfaces and
        # newly maintained public workflow metadata, not archival reports or vendored docs.
        if "/home/attila" in text and not any(part in {"skills", "external"} for part in rel.parts):
            if rel not in {pathlib.Path("README.md"), pathlib.Path("HERMES_TEAM_AUDIT_2026-10-11.md"), pathlib.Path("HERMES_TEAM_CHECKPOINT_2026-10-10.md"), pathlib.Path("docs-four-repo-integration.md"), pathlib.Path("four-repo-integration-manifest.json"), pathlib.Path("scripts/validate_repo.py")}:
                errors.append(f"{rel}: contains private /home/attila path")
def check_documented_count(errors: list[str]) -> None:
    skill_count = sum(1 for p in (ROOT / "skills").rglob("SKILL.md") if ".archive" not in p.parts)
    for rel in ("README.md", "SETUP.md", "SKILLS_CATALOG.md"):
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        numbers = [int(x.replace(",", "")) for x in re.findall(r"\b(\d{1,3}(?:,\d{3})+)\s+skills?\b", text, re.I)]
        for number in set(numbers):
            if number != skill_count:
                errors.append(f"{rel}: documented skill count {number} != actual {skill_count}")


def main() -> int:
    errors: list[str] = []
    for path in tracked_config_files():
        try:
            load_yaml(path)
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: YAML parse failed: {exc}")
    check_config_template(errors)
    check_public_paths(errors)
    check_documented_count(errors)
    if errors:
        print(f"VALIDATION FAILED: {len(errors)} issue(s)")
        for error in errors:
            print(f"ERROR {error}")
        return 1
    print(f"VALIDATION OK: {len(tracked_config_files())} config file(s), public path scan, template schema, and docs count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
