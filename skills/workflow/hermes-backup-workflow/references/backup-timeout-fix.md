# Backup Timeout Investigation

## ZIP Bottleneck (July 3, 2026)

## Symptoms

The `run-hermes-backup.py` script consistently timed out at 120s (cron) and even at 600s (manual). The root cause: the script uses Python `zipfile` + `shutil.copytree` to ZIP the entire Hermes home directory before uploading, and the directory contains 161,705 files.

## File Distribution

| Area | File Count | Size | Can Exclude? |
|------|-----------|------|-------------|
| `hermes-agent/` | 123,480 | (git repo) | ✅ Re-cloneable from GitHub |
| `profiles/` | 12,455 | 228 MB | ❌ Critical data |
| `lsp/` | 9,417 | 51 MB (in channel profile) | ✅ Re-downloadable |
| `skills/` | 1,377 | ~93 MB (across profiles) | ❌ Custom + hub-installed |
| `sessions/` | 160 | (per-profile session DBs) | ❌ Session history |
| Rest | ~14K | config, state, cache | Mixed |

**The ZIP bottleneck:** Python iterates every file sequentially through `zipfile.ZipFile.write()`. For 12K+ files (excluding hermes-agent/lsp), this takes 600+ seconds.

## 971-byte Empty Backup Pattern

When the script times out during ZIP creation (Step 7), the partial ZIP file that survives is exactly **971 bytes** — the ZIP End of Central Directory Record with no file entries. These accumulate on Google Drive and need manual cleanup.

Detection:
```bash
rclone ls "YOUR_RCLONE_REMOTE:Hermes Backup" | awk '$1 < 1000 {print "FAILED: " $2}'
```

## Fastest Alternative: rclone sync (no ZIP)

Skip the ZIP entirely. rclone handles file-by-file upload directly, which is much faster for many small files:

```bash
# Full backup with exclusions
rclone sync /c/Users/YOUR_USERNAME/AppData/Local/hermes \
  "YOUR_RCLONE_REMOTE:Hermes Backup/$(date +%F)/" \
  --exclude "hermes-agent/**" \
  --exclude "lsp/**" \
  --exclude "**/__pycache__/**" \
  --exclude "**/.git/**" \
  --exclude "**/node_modules/**" \
  --exclude "**/.codegraph/**" \
  --verbose --progress
```

## Retention Cleanup

The script's retention logic sorts by file name (alphabetical = date order) and keeps 5 newest. It does NOT detect failed backups. After cleanup, the healthy state was:

- `Hermes_Backup_2026-07-03.zip` — 476 MB ✅
- `Hermes_Backup_2026-07-01.zip` — 432 MB ✅
- (3 × 971-byte empty zips deleted)

## State.db Growth

The session database (`state.db`) is the single largest item:
- 426 MB on disk (as of July 3)
- Primary driver of ZIP size (476 MB backup vs 432 MB on July 1)
- Grows ~44 MB per day

---

## rclone Verification Hang (July 16, 2026)

### Symptoms

The ZIP+upload approach succeeded at creating the archive (504.7 MB, 14,817 files in ~49s),
but the upload step timed out at 600s. Direct rclone calls revealed a **verification hang**:

1. Upload itself completes quickly (504 MiB in ~60s @ 8.5 MiB/s)
2. rclone then enters a post-upload verification phase — checksum retrieval from Google Drive stalls
3. `--progress` shows total transferred doubling every cycle: 504 MiB → 1009 MiB → 1.479 GiB
4. File shows 100% / 504.685 MiB but "0 B/s" on verification passes
5. rclone retries until the Python `subprocess.run(timeout=600)` kills it

The file **is** fully uploaded and visible on Drive during this phase — rclone just can't get a checksum back from Google Drive to confirm.

### Root Cause

Google Drive's checksum API can be slow or unresponsive for large files immediately after upload. rclone's default behavior is to verify uploaded files by fetching the remote checksum, and it retries indefinitely if that call stalls.

### Fix

The script now uses:
```
rclone copyto --ignore-checksum --size-only <local> <remote>
```

- `--ignore-checksum` — skip remote checksum verification entirely
- `--size-only` — size-based comparison is sufficient for a fresh upload

With these flags: 504.7 MiB uploaded in **28.8s @ 17.8 MiB/s**.
Timeout raised from 600s → 900s as safety net.

### File ID (for reference)

`Hermes_Backup_2026-07-16.zip` → Google Drive file ID: `1sll01eyaWEmJ7AFME2A_iCcBX-d3La4j`

### Retention State After Recovery

Remote had 5 backups (07-09 through 07-15). After uploading 07-16, deleted 07-09 to maintain 5 max. Final set: 07-10, 07-11, 07-13, 07-15, 07-16.

### Warnings (non-critical)

- `state.db-shm` — permission denied (locked by active Hermes WAL writer)
- `profiles/codingprofile/state.db-shm` — same reason, expected
- These .db-shm/.db-wal files are SQLite WAL journals; skipping them has no data impact
