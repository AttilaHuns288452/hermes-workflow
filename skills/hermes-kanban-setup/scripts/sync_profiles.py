"""Sync skills.external_dirs and mcp_servers from global config into all profiles.

Run this after adding new MCP servers, skill directories, or creating profiles.
Preserves per-profile model/provider/toolsets — only touches skills + MCP keys.
"""

import yaml
import os
import sys

HERMES_HOME = os.path.expandvars(r"C:\Users\Attila\AppData\Local\hermes")
GLOBAL_CONFIG = os.path.join(HERMES_HOME, "config.yaml")
PROFILES_DIR = os.path.join(HERMES_HOME, "profiles")

# Profiles to skip (intentionally minimal / different setup)
SKIP = set()  # empty — sync everything, orchestrator included


def sync_profile(profile_name: str, global_skills: list, global_mcp: dict) -> bool:
    path = os.path.join(PROFILES_DIR, profile_name, "config.yaml")
    if not os.path.exists(path):
        print(f"  {profile_name}: SKIP (no config.yaml)")
        return False

    with open(path) as f:
        cfg = yaml.safe_load(f)

    if "skills" not in cfg:
        cfg["skills"] = {}
    old_skills = len(cfg["skills"].get("external_dirs", []))
    old_mcp = len(cfg.get("mcp_servers", {}))

    cfg["skills"]["external_dirs"] = global_skills
    cfg["mcp_servers"] = global_mcp

    with open(path, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    model = cfg.get("model", {})
    model_str = model if isinstance(model, str) else model.get("default", "?")
    print(f"  {profile_name:16s} skills {old_skills}→{len(global_skills)}  MCP {old_mcp}→{len(global_mcp)}  model={model_str}")
    return True


def main():
    with open(GLOBAL_CONFIG) as f:
        global_cfg = yaml.safe_load(f)

    global_skills = global_cfg.get("skills", {}).get("external_dirs", [])
    global_mcp = global_cfg.get("mcp_servers", {})

    print(f"Global: {len(global_skills)} skill dirs, {len(global_mcp)} MCP servers")
    print(f"Syncing {len(os.listdir(PROFILES_DIR))} profiles...")

    for profile in sorted(os.listdir(PROFILES_DIR)):
        if profile in SKIP:
            print(f"  {profile}: SKIP (in skip list)")
            continue
        profile_dir = os.path.join(PROFILES_DIR, profile)
        if os.path.isdir(profile_dir):
            sync_profile(profile, global_skills, global_mcp)

    print("\nDone. All profiles match global config for skills + MCP.")


if __name__ == "__main__":
    main()
