---
name: drive-backups
description: "Automated Google Drive backup workflows using rclone — archive, upload, retention, and scheduling for disaster recovery."
version: 1.0
author: agent
license: MIT
---

# Drive Backups

Use when the user asks to create or maintain automated backups to Google Drive,
especially when an authenticated `rclone` Drive remote already exists on this
machine.

## Prerequisites

- Authenticated rclone remote with `scope = drive` (e.g. `YOUR_RCLONE_REMOTE`).
- `rclone` on PATH.
- For archives: `Compress-Archive` available on Windows.
- Hermes cron for scheduling.

## Preferred approach

1. **Verify the real data directory first.** Applications can have a legacy
   `~/.appname` directory alongside the real data home (e.g. Hermes stores its
   config at `AppData/Local/hermes`, not `~/.hermes`). Run the app's own path
   command (`hermes config path`, `pip show`, etc.) to confirm — never assume
   `~/.appname` is authoritative. Backing up the wrong directory gives a false
   sense of security.
2. Check for an existing authenticated rclone remote first. If one already has
   Drive scope and a working refresh token, reuse it. Do NOT run a new Google
   OAuth client/secret flow or install `gws`/`google-workspace` dependencies
   just because Drive access is needed.
3. Ensure the target Drive folder exists: `rclone mkdir <remote>:<folder>`.
4. **Determine backup scope for plug-and-play restoration.** A backup that
   supports full recovery on a new device needs more than the config file:
   include `.env` (secrets), `auth.json` (OAuth tokens), profile directories,
   session databases, custom scripts, and any external configs (rclone, etc.).
   Cache files that can be regenerated (model lists, build stamps) should be
   excluded to keep archive size manageable. See `references/` for a worked
   example with Hermes.
5. **Create the archive directly from source** — do NOT copy to a staging
   directory first. When the data is large (hundreds of MB to GB), a staging
   copy doubles disk I/O and time. Write the ZIP directly by iterating over
   the source tree and adding entries to `zipfile.ZipFile`.
Use smarter compression. SQLite databases (`.db`, `.db-shm`, `.db-wal`)
and already-compressed media (PNG, JPG, MP4) should use `ZIP_STORED` (no
compression) rather than `ZIP_DEFLATED`. Compressing these wastes CPU for
negligible space savings. Text files (`.yaml`, `.json`, `.py`, `.md`) should
still use `ZIP_DEFLATED`.
7. Enforce retention via `rclone lsjson` + `rclone deletefile` instead of
manual Drive API calls.
8. Schedule with Hermes `cronjob(action='create', ...)` and use a PowerShell
shell launcher that bypasses execution policy: `powershell -NoProfile

## Retention logic

- List backups: `rclone lsjson <remote>:<folder> --files-only --include "<Prefix>_*.<ext>"`.
- Sort by `Path` or `Name` **ascending** (oldest first), keep only the newest N by
  slicing `[:-keep]` for deletion. A descending sort (`reverse=True`) deletes the
  wrong entries.
- Delete older items with `rclone deletefile <remote>:<folder>/<path>`.
- Log both the kept count and deleted count.

## Windows pitfalls

- `Join-Path` in some PowerShell versions accepts only 2 positional arguments.
  Use `[System.IO.Path]::Combine` or chained `Join-Path` for deeper paths.
- `Compress-Archive` must be invoked from the archive parent directory so the
  tree inside the zip is relative, not absolute.
- Long upload/sync jobs can hit terminal foreground timeouts. Use
  `notify_on_complete=true` with `background=true`.
- `rclone lsjson` can return either a single object or an array; handle both
  when parsing.
- **`\Users` path pitfall in Python scripts.** When writing Python scripts that
  embed Windows paths in docstrings, `C:\Users` contains `\U` which Python's
  lexer treats as the start of an 8-hex-digit Unicode escape. Use a raw string
  `r"""..."""` for the docstring, but be aware that high Unicode characters
  (em-dashes, non-ASCII punctuation) on the same line as the opening `r"""`
  can trigger linter errors. Safest: keep the raw string's first line clean
  (no `\U`, no special chars) or use forward slashes in paths altogether.
- **Backing up `.env` files.** On Windows, `.env` files in the skill directory
  may be filtered by `.gitignore` or `ignore_patterns`. If a backup script
  copies from source to staging, explicitly include dot-files that carry
  secrets. When using `zipfile.ZipFile` directly, allow specific hidden files
  like `.env` and `.skills_prompt_snapshot.json` through the filter.

## Supporting patterns

For full "plug-and-play" recovery of an application environment, maintain
three scripts:

| Script | Role |
|--------|------|
| `run-backup.py` | Archive + upload + retention (runs on schedule) |
| `restore-backup.py` | Download + extract + place files (runs on new machine) |
| `sync-credentials.py` | Propagate root `.env` + `auth.json` to all profiles |

### Python direct-to-ZIP pattern (no staging)

```python
import tempfile, zipfile
from pathlib import Path

hermes_home = Path(hermes_home)
with tempfile.TemporaryDirectory(prefix="backup-") as tmpdir:
    backup_path = Path(tmpdir) / "Backup.zip"
    with zipfile.ZipFile(backup_path, "w") as zf:
        for src_path in sorted(hermes_home.rglob("*")):
            if src_path.is_dir():
                continue
            # Smart compression: STORED for already-compressed types
            suffix = src_path.suffix.lower()
            if suffix in (".db", ".db-shm", ".db-wal", ".png", ".jpg", ".mp4"):
                ctype = zipfile.ZIP_STORED
            else:
                ctype = zipfile.ZIP_DEFLATED
            arcname = str(src_path.relative_to(hermes_home)).replace("\\", "/")
            zf.write(src_path, arcname, compress_type=ctype)
    # Upload
    subprocess.run(["rclone", "copyto", str(backup_path), f"{remote}:{folder}/{backup_name}"])
```

## References

- `references/hermes-backup-context.md` — Hermes environment structure:
  finding the real home, profile architecture, MCP server inheritance,
  credential sync, and content scope for plug-and-play backup/restore.
