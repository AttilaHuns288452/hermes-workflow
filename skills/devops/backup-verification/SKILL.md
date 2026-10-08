---
name: backup-verification
description: "Use when verifying backups are complete and restorable."
---
# Backup Verification

A backup job's success log proves the job ran, not that the data is in the artifact.
Backup scripts silently skip large files, coverage tables drift from the code, and
uploads land truncated. Verification = inspect the artifact and compare it against
the live data.

## Procedure

1. **Live inventory first.** `du -sh <data-home>/* | sort -rh` plus hidden dotfiles.
   The most irreplaceable data is usually the largest item (session/state DBs) and
   the most likely to be silently skipped for size.
2. **Coverage map from the script's include/exclude list** — map every inventory
   item to included / skipped / regenerable. Docs, READMEs, and coverage tables in
   skills drift; the script's file-walk filters are the source of truth. Grep the
   script for `continue`/`skip`/name-filter conditions and account for every hit.
   Pitfall: an item excluded by a filter never appears in any log line — the run
   output looks perfectly clean. The omission is only visible in the artifact.
3. **Regenerable vs irreplaceable.** Caches, node_modules, git clones of remotes
   the user still owns = exclude. Session DBs, memories, credentials, non-git user
   data = must be in. The decryption key must NOT be inside the encrypted archive —
   a backup that contains its own key is an unencrypted backup with extra steps.
   Confirm the user stores the key separately before declaring recovery possible.
4. **Run a real backup; compare file count + size to the previous run.** Pitfall:
   after "fixing" coverage, the archive size must jump by roughly the compressed
   size of the newly included items. No delta means the fix didn't land. Size is a
   cheap second signal when content checks get skipped.
5. **Verify the REMOTE artifact, never the local file** (upload truncation, wrong
   folder, retention deleting the wrong entries):
   - `rclone lsjson <remote>:<path> --files-only` → size matches the local archive,
     file count matches intended retention.
   - Round-trip decrypt: `rclone cat <crypt-remote>:<file> > /tmp/verify.zip`,
     byte size must equal the remote listing.
   - Integrity: `zipfile.ZipFile(path).testzip()` (CRC of ALL entries), then assert
     each must-have entry exists with its expected size. For DB files, check magic
     bytes (`SQLite format 3\0`) before trusting the entry.
   - Delete the temp copy afterwards (it can be GBs).
6. **Live databases need consistent snapshots at creation time** or verification
   will pass while restore is torn: use `sqlite3 <db> ".backup <out>"` (WAL-safe)
   instead of copying `state.db`/`-wal`/`-shm` mid-write.

## Pitfalls

- Never accept "the script logged success" or "the upload finished" as evidence of
  content — only the artifact contents are. (why: skips and truncations are
  invisible in success output)
- Size checks on encrypted remotes: crypt overhead is ~nonce bytes; a decrypted
  size within ~0.1% of the remote ciphertext size is a match; a 3-4× mismatch
  means the wrong file or a truncated download.
- Assert remote count == intended retention N after the run; sort-order bugs in
  retention code delete the wrong backups silently.
