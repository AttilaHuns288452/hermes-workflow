#!/usr/bin/env python3
"""
Hermes Restore — Plug-and-Play Recovery

Restores a Hermes backup ZIP from Google Drive back onto a new machine.
After running this, Hermes should work exactly as it did on the source machine.

Usage:
  # List available backups on Google Drive
  python restore-hermes-backup.py --list

  # Restore the latest backup
  python restore-hermes-backup.py --restore-latest

  # Restore a specific backup by name
  python restore-hermes-backup.py --restore Hermes_Backup_2026-06-30.zip

  # Restore from a local ZIP file
  python restore-hermes-backup.py --local-backup /path/to/Hermes_Backup_2026-06-30.zip
"""

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REMOTE = os.environ.get("RCLONE_REMOTE", "hermes_gdrive")
DRIVE_FOLDER = os.environ.get("RCLONE_BACKUP_PATH", "Hermes Backup")

# The target Hermes home on the new machine
DEFAULT_HERMES_HOME = Path(os.environ.get(
    "HERMES_HOME",
    str(Path.home().parent / Path.home().name / "AppData/Local/hermes" if os.name == "nt" else Path.home() / ".config/hermes")
))
LEGACY_HERMES_HOME = Path.home() / ".hermes"

RCLONE_CONFIG_DIR = Path.home() / "AppData/Roaming/rclone"


def run(cmd, check=True, timeout=120):
    print(f"[RUN] {' '.join(cmd)}")
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Command timed out after {timeout}s: {' '.join(cmd)}")
    if check and proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return proc


def log(msg: str):
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)


def list_backups():
    """List available backups on Google Drive."""
    log(f"Listing backups at {REMOTE}:{DRIVE_FOLDER}...")
    proc = run(
        ["rclone", "lsf", f"{REMOTE}:{DRIVE_FOLDER}",
         "--include", "Hermes_Backup_*.zip"],
        check=False,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        log("  No backups found or rclone not configured.")
        log("  Ensure rclone is installed and the RCLONE_REMOTE env var is set ($RCLONE_REMOTE).")
        return []

    backups = [line.strip() for line in proc.stdout.strip().split("\n") if line.strip()]
    backups.sort(reverse=True)
    log(f"  Found {len(backups)} backup(s):")
    for b in backups:
        log(f"    - {b}")
    return backups


def restore_from_zip(zip_path, target_dir):
    """Extract a Hermes backup ZIP into the target directory.

    The backup contains a 'backup-account/' directory with the real Hermes
    data, plus optional 'profiles/' and 'external/' dirs.
    """
    target_dir = Path(target_dir)
    log(f"Restoring to: {target_dir}")

    # Create target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)

    # ── First pass: read manifest ────────────────────────────────────────
    manifest_data = {}
    with zipfile.ZipFile(zip_path, "r") as zf:
        if "backup-manifest.json" in zf.namelist():
            manifest_data = json.loads(zf.read("backup-manifest.json"))
            log(f"  Backup date: {manifest_data.get('backup_date', 'unknown')}")
            log(f"  Source host: {manifest_data.get('hostname', 'unknown')}")
            log(f"  Profiles:    {', '.join(manifest_data.get('profiles', []))}")
            log(f"  Items:       {manifest_data.get('items_collected', '?')}")

    # ── Extract full backup ──────────────────────────────────────────────
    log(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(target_dir)

    log(f"  Extracted to {target_dir}")

    # ── Copy root files up from backup-account/ ──────────────────────────
    backup_root = target_dir / "backup-account"
    if backup_root.exists():
        log("Moving backup-account contents to Hermes home root...")
        for item in sorted(backup_root.iterdir()):
            dest = target_dir / item.name
            if item.is_dir():
                if dest.exists():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copytree(item, dest)
                log(f"  {item.name}/ → {dest}")
            else:
                shutil.copy2(item, dest)
                log(f"  {item.name} → {dest}")
        shutil.rmtree(backup_root, ignore_errors=True)

    # ── Handle external files (rclone config, etc.) ──────────────────────
    ext_dir = target_dir / "external"
    if ext_dir.exists():
        log("Processing external files...")
        for item in ext_dir.iterdir():
            if item.name == "rclone.conf":
                # Install rclone config to the right location
                rclone_target = RCLONE_CONFIG_DIR / "rclone.conf"
                RCLONE_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, rclone_target)
                log(f"  rclone.conf → {rclone_target}")
            elif item.is_dir():
                # External skill repos — copy to Documents/Repos/
                repos_target = Path.home() / "Documents/Repos"
                repos_target.mkdir(parents=True, exist_ok=True)
                dest = repos_target / item.name
                if dest.exists():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copytree(item, dest)
                log(f"  {item.name}/ → {dest}")
        shutil.rmtree(ext_dir, ignore_errors=True)

    # ── Ensure .env is linked to profiles ────────────────────────────────
    root_env = target_dir / ".env"
    if root_env.exists():
        profiles_dir = target_dir / "profiles"
        if profiles_dir.exists():
            for profile_dir in profiles_dir.iterdir():
                if profile_dir.is_dir():
                    profile_env = profile_dir / ".env"
                    # Use hardlink or copy to keep in sync
                    if not profile_env.exists():
                        shutil.copy2(root_env, profile_env)
                        log(f"  Synced .env → profiles/{profile_dir.name}/.env")
                    else:
                        log(f"  .env already exists for profiles/{profile_dir.name}/")

    log("=" * 60)
    log("RESTORE COMPLETE")
    log(f"Hermes is now at: {target_dir}")
    log("Next steps:")
    log("  1. Start Hermes: hermes")
    log("  2. Verify your profiles: hermes profile list")
    log("  3. Check MCP servers: hermes mcp list")
    log("  4. If restoring to a new machine, install rclone and set $RCLONE_REMOTE")
    log("=" * 60)


def download_backup(backup_name, dest_dir):
    """Download a specific backup from Google Drive."""
    dest_path = dest_dir / backup_name
    log(f"Downloading {backup_name} from {REMOTE}:{DRIVE_FOLDER}...")
    remote = f"{REMOTE}:{DRIVE_FOLDER}/{backup_name}"
    run(["rclone", "copyto", remote, str(dest_path)])
    log(f"  Downloaded to {dest_path}")
    return dest_path


def restore_latest():
    """Find and restore the most recent backup."""
    backups = list_backups()
    if not backups:
        log("No backups available. Cannot restore.")
        return False
    latest = backups[0]
    log(f"Latest backup: {latest}")

    with tempfile.TemporaryDirectory(prefix="hermes-restore-") as tmp:
        dest_path = download_backup(latest, Path(tmp))
        restore_from_zip(dest_path, DEFAULT_HERMES_HOME)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Hermes plug-and-play restore tool"
    )
    parser.add_argument("--list", action="store_true", help="List available backups")
    parser.add_argument("--restore", type=str, default=None,
                        help="Restore a specific backup by filename from Google Drive")
    parser.add_argument("--restore-latest", action="store_true",
                        help="Restore the most recent backup from Google Drive")
    parser.add_argument("--local-backup", type=str, default=None,
                        help="Restore from a local ZIP file")
    parser.add_argument("--target", type=str, default=str(DEFAULT_HERMES_HOME),
                        help=f"Target Hermes home (default: {DEFAULT_HERMES_HOME})")
    args = parser.parse_args()

    target = Path(args.target)

    if args.list:
        list_backups()
        return

    if args.restore_latest:
        restore_latest()

    elif args.restore:
        with tempfile.TemporaryDirectory(prefix="hermes-restore-") as tmp:
            dest_path = download_backup(args.restore, Path(tmp))
            restore_from_zip(dest_path, target)

    elif args.local_backup:
        backup_path = Path(args.local_backup)
        if not backup_path.exists():
            log(f"Error: backup not found at {backup_path}")
            sys.exit(1)
        restore_from_zip(backup_path, target)

    else:
        parser.print_help()
        log("\nTip: run with --list to see available backups, or --restore-latest to restore the latest")


if __name__ == "__main__":
    main()
