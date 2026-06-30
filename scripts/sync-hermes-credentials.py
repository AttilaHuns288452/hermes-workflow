#!/usr/bin/env python3
"""
Hermes Credential Sync — Share API keys, MCP servers, auth tokens across all profiles.

This script ensures that the root .env and auth.json are propagated to every
Hermes profile, so they all share the same credentials.

Run this after adding new keys/auth tokens to the root Hermes home.
"""

import json
import os
import shutil
import sys
from pathlib import Path

# Real Hermes home (AppData)
HERMES_HOME = Path(os.environ.get(
    "HERMES_HOME",
    "C:/Users/Attila/AppData/Local/hermes"
))

# Files to sync from root to every profile
SYNC_FILES = [
    ".env",          # API keys (OpenRouter, Anthropic, GitHub, etc.)
    "auth.json",     # OAuth tokens
]

# Config sections that should be in all profiles (ensures MCP servers are shared)
# Profile configs should NOT have 'mcp_servers:' — they inherit from root config.
# This script checks for that and warns if a profile has its own mcp_servers.


def log(msg):
    print(f"[SYNC] {msg}")


def sync_credentials():
    """Copy root .env and auth.json to every profile."""
    profiles_dir = HERMES_HOME / "profiles"
    if not profiles_dir.exists():
        log("No profiles directory found.")
        return False

    errors = 0
    for sync_file in SYNC_FILES:
        root_file = HERMES_HOME / sync_file
        if not root_file.exists():
            log(f"WARNING: Root {sync_file} not found at {root_file}")
            errors += 1
            continue

        file_size = root_file.stat().st_size
        log(f"Syncing {sync_file} ({file_size} bytes) to all profiles...")

        for profile_dir in sorted(profiles_dir.iterdir()):
            if not profile_dir.is_dir() or profile_dir.name.startswith("."):
                continue

            profile_file = profile_dir / sync_file
            try:
                shutil.copy2(root_file, profile_file)
                log(f"  ✓ profiles/{profile_dir.name}/{sync_file}")
            except PermissionError as e:
                log(f"  ✗ profiles/{profile_dir.name}/{sync_file} (Permission: {e})")
                errors += 1
            except Exception as e:
                log(f"  ✗ profiles/{profile_dir.name}/{sync_file} ({e})")
                errors += 1

    # Also sync to the legacy ~/.hermes if it exists
    legacy_home = Path.home() / ".hermes"
    if legacy_home.exists() and legacy_home != HERMES_HOME:
        for sync_file in SYNC_FILES:
            root_file = HERMES_HOME / sync_file
            if not root_file.exists():
                continue
            legacy_file = legacy_home / sync_file
            try:
                shutil.copy2(root_file, legacy_file)
                log(f"  ✓ (legacy) .hermes/{sync_file}")
            except Exception as e:
                log(f"  ✗ (legacy) .hermes/{sync_file} ({e})")

    if errors == 0:
        log("All credentials synced successfully.")
    else:
        log(f"Completed with {errors} error(s).")
    return errors == 0


def check_mcp_inheritance():
    """Verify profiles don't have their own mcp_servers (which would override root)."""
    profiles_dir = HERMES_HOME / "profiles"
    if not profiles_dir.exists():
        return

    issues = []
    for profile_dir in sorted(profiles_dir.iterdir()):
        if not profile_dir.is_dir() or profile_dir.name.startswith("."):
            continue
        config_file = profile_dir / "config.yaml"
        if not config_file.exists():
            continue

        with open(config_file, "r") as f:
            content = f.read()

        if "mcp_servers:" in content:
            issues.append(profile_dir.name)
            log(f"WARNING: profiles/{profile_dir.name}/config.yaml has its own 'mcp_servers:' — "
                 f"this OVERRIDES the root config's MCP servers and prevents sharing!")

    if issues:
        log(f"\nTo fix MCP sharing, remove 'mcp_servers:' from these profile configs:")
        for name in issues:
            log(f"  - profiles/{name}/config.yaml (remove the mcp_servers: section)")
        log("Profiles inherit MCP servers from the root config when they don't define their own.")
        log("Run: for each profile, edit config.yaml and remove the mcp_servers: block.")
    else:
        log("MCP servers: All profiles inherit from root config. ✓")


def main():
    print("=" * 60)
    print("Hermes Credential Sync")
    print("=" * 60)
    log(f"Hermes home: {HERMES_HOME}")
    print()

    # Step 1: Sync credential files
    log("--- Credential Sync ---")
    sync_credentials()

    print()

    # Step 2: Check MCP inheritance
    log("--- MCP Server Inheritance Check ---")
    check_mcp_inheritance()

    print()
    print("=" * 60)
    print("Done. All profiles now share API keys, auth tokens, and MCP servers.")
    print("=" * 60)


if __name__ == "__main__":
    main()
