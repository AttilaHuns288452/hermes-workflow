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

- Authenticated rclone remote with `scope = drive` (e.g. `sabiniano_gdrive`).
- `rclone` on PATH.
- For archives: `Compress-Archive` available on Windows.
- Hermes cron for scheduling.

## Preferred approach

1. Check for an existing authenticated rclone remote first. If one already has
   Drive scope and a working refresh token, reuse it. Do NOT run a new Google
   OAuth client/secret flow or install `gws`/`google-workspace` dependencies
   just because Drive access is needed.
2. Ensure the target Drive folder exists: `rclone mkdir <remote>:<folder>`.
3. Stage the restore-critical content under a temp staging directory if
   retention/compression is required, then create a dated archive with
   `Compress-Archive` and upload it with `rclone copyto`.
4. Enforce retention via `rclone lsjson` + `rclone deletefile` instead of
   manual Drive API calls.
5. Schedule with Hermes `cronjob(action='create', ...)` and use a PowerShell
   shell launcher that bypasses execution policy: `powershell -NoProfile -ExecutionPolicy Bypass -Command "& '<script>'"`.

## Retention logic

- List backups: `rclone lsjson <remote>:<folder> --files-only --include "<Prefix>_*.<ext>"`.
- Sort by `Path` or `Name` descending and keep only the newest N.
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

## Scripts created in this session

- Hermes Drive backup: `C:\Users\Attila\.hermes\scripts\hermes-drive-backup.ps1`
- Lending backup: `C:\Users\Attila\Documents\Playground\lending-management-system\tools\daily-supabase-gdrive-backup.ps1`

## References

- `references/drive-backup-pattern.md` — concrete patterns and command
  sequences reused across this session.
