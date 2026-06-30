#!/usr/bin/env python3
r"""
Hermes Daily Google Drive Backup — COMPREHENSIVE PLUG-AND-PLAY EDITION

Backs up EVERYTHING related to Hermes so you can restore on a new device
and be back in business immediately.

Backup target: sabiniano_gdrive:Hermes Backup (Google Drive)
Hermes home:   C:\Users\Attila\AppData\Local\hermes
"""

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────
# The REAL Hermes home (NOT ~/.hermes — that's a stale legacy dir)
REAL_HERMES_HOME = Path(os.environ.get(
    "HERMES_HOME",
    "C:/Users/Attila/AppData/Local/hermes"
))
FALLBACK_HERMES_HOME = Path.home() / ".hermes"

STAGING_DIR = REAL_HERMES_HOME / "tmp"
LOG_DIR = REAL_HERMES_HOME / "tmp" / "backup-logs"

REMOTE = "sabiniano_gdrive"
DRIVE_FOLDER = "Hermes Backup"
KEEP = 5  # Keep 5 most recent backups

RCLONE_CONFIG = Path(os.environ.get(
    "RCLONE_CONFIG",
    str(Path.home() / "AppData/Roaming/rclone/rclone.conf")
))

# ── What to include in the backup ────────────────────────────────────────────
# These are everything needed to fully restore Hermes on a new machine.
BACKUP_ITEMS = [
    # Root config & identity
    "config.yaml",
    "SOUL.md",
    ".env",                # <-- CRITICAL: API keys shared by all profiles
    "auth.json",           # <-- CRITICAL: OAuth tokens
    "channel_directory.json",

    # Skills (custom + hub-installed)
    "skills/",

    # Memories (persistent cross-session memory)
    "memories/",

    # Session database (SQLite + FTS5 — full session history)
    "state.db",
    "state.db-shm",
    "state.db-wal",

    # Caches (model lists, provider caches)
    "provider_models_cache.json",
    "models_dev_cache.json",
    "ollama_cloud_models_cache.json",
    "context_length_cache.yaml",
    ".skills_prompt_snapshot.json",

    # Configuration & scripts
    "scripts/",
    "plugins/",

    # Cron definitions
    "cron/",

    # Hooks
    "hooks/",

    # Kanban (multi-agent work queue)
    "kanban.db",
    "kanban/",

    # Gateway state
    "gateway_state.json",
    "gateway-service/",
    "platforms/",

    # Shared directory
    "shared/",

    # Pairing (DM auth)
    "pairing/",

    # Response store
    "response_store.db",
    "response_store.db-shm",
    "response_store.db-wal",

    # Verification evidence
    "verification_evidence.db",

    # Logs
    "logs/",

    # Image & audio cache (can be re-downloaded, but nice to have)
    "image_cache/",
    "audio_cache/",

    # Runtime state
    "runtime/",

    # State snapshots (Hermes system state)
    "state-snapshots/",
    "processes.json",
    "desktop-build-stamp.json",
]

# Additional external paths to backup
EXTERNAL_BACKUP_DIRS = [
    # External skill repos referenced in config.yaml
    "C:/Users/Attila/Documents/Repos/external-skills/",
]

EXTERNAL_BACKUP_FILES = [
    # Rclone config (needed to restore to Google Drive)
    str(RCLONE_CONFIG),
]


# ── Helper Functions ─────────────────────────────────────────────────────────

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
    today = datetime.date.today().isoformat()
    log_path = LOG_DIR / f"hermes-drive-backup-{today}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def zipdir(zf, src_dir, arc_prefix=""):
    """Add all files from src_dir into zip with arc_prefix."""
    src_dir = Path(src_dir)
    if not src_dir.exists():
        return
    for path in sorted(src_dir.rglob("*")):
        if path.is_dir() or path.name.startswith("."):
            continue
        arcname = str(Path(arc_prefix) / path.relative_to(src_dir))
        zf.write(path, arcname)


def zipfile_entry(zf, src_path, arcname):
    """Add a single file to the zip archive."""
    src_path = Path(src_path)
    if src_path.exists() and src_path.is_file():
        try:
            zf.write(src_path, arcname)
        except PermissionError:
            log(f"  SKIPPED (permission denied): {src_path}")
        except Exception as e:
            log(f"  SKIPPED ({e}): {src_path}")
        else:
            log(f"  + {arcname}")
    else:
        log(f"  - {arcname} (not found)")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Hermes comprehensive Google Drive backup"
    )
    parser.add_argument("--name", default=None, help="Custom backup name")
    parser.add_argument(
        "--hermes-home",
        default=str(REAL_HERMES_HOME),
        help=f"Hermes home path (default: {REAL_HERMES_HOME})",
    )
    parser.add_argument(
        "--keep", type=int, default=KEEP,
        help=f"Number of older backups to keep on remote (default: {KEEP})",
    )
    args = parser.parse_args()

    hermes_home = Path(args.hermes_home)
    keep = args.keep
    today = datetime.date.today().isoformat()
    backup_name = args.name or f"Hermes_Backup_{today}.zip"
    backup_path = STAGING_DIR / backup_name

    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    log("=" * 60)
    log(f"Starting Hermes backup to {REMOTE}:{DRIVE_FOLDER}")
    log(f"Hermes home: {hermes_home}")
    log(f"Backup file: {backup_name}")
    log("=" * 60)

    # ── Step 1: List & purge old backups on remote ───────────────────────
    log("--- Step 1: Managing remote backup retention ---")
    list_proc = run(
        [
            "rclone", "lsjson",
            f"{REMOTE}:{DRIVE_FOLDER}",
            "--files-only",
            "--include", "Hermes_Backup_*.zip",
        ],
        check=False,
    )
    old_deleted = 0
    if list_proc.returncode == 0 and list_proc.stdout.strip():
        items = json.loads(list_proc.stdout)
        if isinstance(items, dict):
            items = [items]
        old = sorted(
            items,
            key=lambda item: item.get("Path") or item.get("Name") or "",
            reverse=True,
        )[keep:]
        for item in old:
            old_path = item.get("Path") or item.get("Name")
            if old_path:
                remote = f"{REMOTE}:{DRIVE_FOLDER}/{old_path}"
                log(f"  Deleting old backup: {old_path}")
                run(["rclone", "deletefile", remote], check=False)
                old_deleted += 1
    elif list_proc.returncode != 0:
        log(f"  Remote listing failed (non-fatal): {list_proc.stderr.strip()}")

    # ── Step 2: Create staging area ──────────────────────────────────────
    log("--- Step 2: Staging backup files ---")
    account_dir = STAGING_DIR / "backup-account"
    if account_dir.exists():
        shutil.rmtree(account_dir, ignore_errors=True)
    account_dir.mkdir(parents=True, exist_ok=True)

    collected_count = 0
    for rel in BACKUP_ITEMS:
        src = hermes_home / rel
        if not src.exists():
            log(f"  - {rel} (not found)")
            continue
        dst = account_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", ".git"))
            else:
                shutil.copy2(src, dst)
            collected_count += 1
            log(f"  + {rel}")
        except PermissionError as e:
            log(f"  ! {rel} (permission: {e})")
        except Exception as e:
            log(f"  ! {rel} ({e})")

    # ── Step 3: Include ALL profiles ─────────────────────────────────────
    profiles_src = hermes_home / "profiles"
    if profiles_src.exists():
        log("--- Profiles ---")
        profiles_dst = account_dir / "profiles"
        profiles_dst.mkdir(parents=True, exist_ok=True)
        for profile_dir in sorted(profiles_src.iterdir()):
            if not profile_dir.is_dir():
                continue
            profile_name = profile_dir.name
            log(f"  + profiles/{profile_name}/")
            try:
                shutil.copytree(
                    profile_dir,
                    profiles_dst / profile_name,
                    dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", ".git", ".codegraph"),
                )
                collected_count += 1
            except PermissionError as e:
                log(f"  ! profiles/{profile_name} (permission: {e})")
            except Exception as e:
                log(f"  ! profiles/{profile_name} ({e})")

    # ── Step 4: Backup external directories ──────────────────────────────
    log("--- External directories ---")
    ext_dir = account_dir / "external"
    ext_dir.mkdir(parents=True, exist_ok=True)
    for ext_path_str in EXTERNAL_BACKUP_DIRS:
        ext_path = Path(ext_path_str)
        if ext_path.exists():
            dirname = ext_path.name
            try:
                shutil.copytree(
                    ext_path,
                    ext_dir / dirname,
                    dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", ".git", "node_modules"),
                )
                collected_count += 1
                log(f"  + external/{dirname}/")
            except Exception as e:
                log(f"  ! external/{dirname} ({e})")
        else:
            log(f"  - external/{ext_path.name} (not found)")

    # ── Step 5: External single files ────────────────────────────────────
    log("--- External files ---")
    for file_path_str in EXTERNAL_BACKUP_FILES:
        fp = Path(file_path_str)
        if fp.exists() and fp.is_file():
            dst = account_dir / "external" / fp.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(fp, dst)
            collected_count += 1
            log(f"  + external/{fp.name}")
        else:
            log(f"  - {fp.name} (not found)")

    # ── Step 6: Write manifest ───────────────────────────────────────────
    log("--- Creating manifest ---")
    manifest = {
        "backup_date": datetime.datetime.now().isoformat(),
        "hostname": os.uname().nodename,
        "hermes_home": str(hermes_home),
        "items_collected": collected_count,
        "backup_files": BACKUP_ITEMS,
        "profiles": [p.name for p in profiles_src.iterdir()] if profiles_src.exists() else [],
        "notes": (
            "Restore: download the ZIP, run restore-hermes-backup.py "
            "--backup <zip> --hermes-home <target>"
        ),
    }
    with open(account_dir / "backup-manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    log(f"  + backup-manifest.json")

    # ── Step 7: Create ZIP ───────────────────────────────────────────────
    log("--- Creating archive ---")
    if backup_path.exists():
        backup_path.unlink()
    file_count = 0
    with zipfile.ZipFile(backup_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(account_dir.rglob("*")):
            if path.is_dir():
                continue
            # Skip hidden/temp files in the staging root itself
            if path.name.startswith(".") and path.parent == account_dir:
                continue
            arcname = path.relative_to(account_dir)
            try:
                zf.write(path, arcname)
                file_count += 1
            except Exception as e:
                log(f"  ! {arcname} ({e})")
    log(f"  Created {backup_name} with {file_count} files ({backup_path.stat().st_size / 1024 / 1024:.1f} MB)")

    # ── Step 8: Upload to Google Drive ───────────────────────────────────
    log("--- Uploading to Google Drive ---")
    remote = f"{REMOTE}:{DRIVE_FOLDER}/{backup_name}"
    run(["rclone", "copyto", str(backup_path), remote])
    log(f"  Uploaded successfully")

    # ── Step 9: Cleanup local staging ────────────────────────────────────
    log("--- Cleanup ---")
    shutil.rmtree(account_dir, ignore_errors=True)
    try:
        backup_path.unlink()
        log("  Removed local staging zip")
    except Exception:
        pass

    log("=" * 60)
    log(f"BACKUP COMPLETE — {collected_count} items, {file_count} files")
    log(f"Retention: {keep} backup(s); deleted {old_deleted} old")
    log(f"Remote: {REMOTE}:{DRIVE_FOLDER}/{backup_name}")
    log("=" * 60)


if __name__ == "__main__":
    main()
