---
name: linux-system-backups
description: "Use when configuring Timeshift, snapshot bloat, backups, or diagnosing a disk that blew up / is full on the Linux host."
---

# Linux System Backups (Timeshift + local backup jobs)

Scope: the Linux Mint host's system-level backups. The Hermes Google Drive backup has its own skill (`hermes-backup-workflow`); the rclone rules at the bottom apply to it and to any other upload script here.

## Triage: disk full / "my storage blew up"

Run this ladder first — it isolates the growing consumer before you delete anything.

1. `df -h` — which filesystem is full and how much is left; work on that mount.
2. Pick a drill-down direction by splitting home vs the rest: `du -xh --max-depth=2 ~ | sort -rh | head` and `du -xh --max-depth=1 /usr /var /opt /timeshift 2>/dev/null | sort -rh | head`. (Scanning `/` needs root for some subtrees and `sudo` here prompts for a password, so scan the known-large roots individually without it rather than hanging on a sudo du.)
3. Drill down level by level into the biggest subtree (`du --max-depth=N`, `sort -rh | head`) until one dir or file dominates.
4. "Sudden" growth is almost always an accumulating store — a snapshot/backup/rotation dir, logs, or a growing DB — not static content. `ls -lt` the suspect dir to confirm it is still growing before concluding.

Prime suspects on this host (check every one, not just the obvious):

- **Timeshift** `/timeshift` — see the filter-mechanics and diagnosis sections below.
- **Hermes state-snapshots** `~/.hermes/state-snapshots/` — the daily `hermes backup -q` cron copies `state.db` WHOLESALE into a new dated dir, so each snapshot is as big as `state.db` and they accumulate. Retention is `--keep N` (parser default 3), but the quick-backup path has dropped the flag and fallen back to a hardcoded keep of 20 before — verify with `ls ~/.hermes/state-snapshots | wc -l` after a run instead of trusting the flag. Reclaim by keeping the 2–3 newest and `rm -rf` the rest, then shrink `state.db` (below) so future snapshots are small. `hermes update` overwrites hermes-agent code, so any local fix to the snapshot path must be re-applied after updates.
- **A single large `.db` file** — a big SQLite file is often mostly freelist (rows deleted, never vacuumed), so file size overstates live data. Diagnose before deleting it:
  - `sqlite3 <db> "PRAGMA page_count; PRAGMA freelist_count;"` — freelist_count near page_count means `VACUUM` will shrink it hard.
  - `sqlite3 <db> "SELECT name, SUM(pgsize)/1048576 FROM dbstat GROUP BY name ORDER BY 2 DESC LIMIT 10;"` — which table/index actually holds the bytes.
  - `VACUUM` needs no live process holding the DB — stop the writer first; copy it aside if unsure.

## Timeshift filter mechanics

- Config lives at `/etc/timeshift/timeshift.json`; the `exclude` array is the user filter list Timeshift writes into `rsync --exclude-from` (verified in installed source, `~/timeshift-25.12.4+zena/src/Utility/RsyncTask.vala`).
- rsync filter semantics: first matching rule wins; `+` includes, `-` excludes; `**` crosses directories.
- Home directories are excluded by default. The only way home content enters a snapshot is an explicit `+ /home/<user>/.**` (hidden files) or `+ /home/<user>/**` (everything) — a stray include rule is the usual cause of multi-hundred-GB snapshots.
- To include a directory but skip junk inside it: a bare `+ /home/<user>/<dir>/` anchor (permits descent), then `- <dir>/junk/` rules, THEN the blanket `+ /home/<user>/<dir>/**`. Children are matched individually in order — the blanket include must come after the junk excludes, or rsync matches it first and copies everything.
- Timeshift passes `--delete-excluded`, so anything a `-` rule matches is also purged from previous snapshots on the next run.
- The GUI writes this same file (its Users tab toggles the `+ /home/<u>/.**` entry). After hand-editing the JSON, do not change Users settings without re-reading the file.

Current approved filter set: include `.hermes` (minus state-snapshots, recovery, tmp, broken-install-backup, `state.db.*.bak`, hermes-agent/) and `.ollama`; exclude `/var/lib/libvirt/images` (VM disks), `/home/**`, `/root/**`. System files (`/usr`, `/var`, `/opt`, `/boot`, `/etc`) always snapshot and are expected to be tens of GB on first run.

## Diagnosing a Timeshift snapshot that grabbed storage

1. Read `exclude` in the config and compute each `+` rule's cost with `du -sh` on the paths it matches.
2. `sudo du -sh /timeshift/snapshots/*/localhost/* | sort -rh | head` — see what was actually copied and compare against live dirs.
3. Sanity-check JSON counters: `snapshot_count` is a running total, and a preposterous value means corrupt state — reset it to the real snapshot count.
4. After changing filters, take one test snapshot, then `du` its `localhost/` subdirs to confirm the rules fired. Existing snapshots keep their old contents until deleted — a config fix alone reclaims nothing.

## System config edits from this harness

- `sudo python3 - <<EOF` fails — sudo consumes the script text as password input. Write the file to /tmp as the user, then `sudo cp /tmp/x /etc/... && sudo chown root:root /etc/...`. Keep a `.bak` beside any file in /etc before overwriting.
- `timeshift` is single-instance: while a create/delete runs, every other call fails with "Another instance of this application is running". Poll `pgrep -f timeshift` instead of re-invoking.

## Long-running jobs

- A foreground `terminal` call that hits its timeout KILLS the child mid-work — a backup killed mid-upload leaves an orphan artifact and no completion record. Anything over ~4 minutes: run in background and poll, or split into chunks that each finish well under the limit.
- Manual `timeshift --create` on this host takes ~10 minutes (~47 GB of system files). Poll `du -sh /timeshift/snapshots/<name>` until the size stops growing.
- `timeshift --delete --snapshot <name>` frees the space immediately and is the cheap way to reclaim disk after a config fix.

## rclone upload rules (any backup script on this host)

- Force IPv4 with `--bind 0.0.0.0` — rclone prefers IPv6 and this network intermittently has no v6 route; a v6 dial fails the whole transfer ("network is unreachable").
- Google Drive uploads need `--ignore-checksum --size-only`, or rclone hangs in post-upload checksum verification with the file already safely on Drive.
- Wrap uploads in 3 attempts with 60s backoff; on final failure KEEP the local artifact and raise loudly — silent loss is worse than disk usage.
- Verify by listing the remote and comparing size — `rclone lsjson <remote>: --files-only --include '<pattern>'` — never by trusting the uploader's exit code alone.
