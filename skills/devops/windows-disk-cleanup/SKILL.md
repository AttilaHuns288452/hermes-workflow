---
name: windows-disk-cleanup
description: Diagnose and reclaim Windows disk space fast. Use when the user asks why storage is full, disk "blew up", what's eating space, or wants cleanup on Windows. WizTree CLI export + junk inventory + consent boundaries.
---

# Windows Disk Cleanup

## Fast path: WizTree CLI (installed at `C:\Program Files\WizTree`)
Never grind `du`/`find` over AppData or node_modules-heavy dirs (minutes → timeout). WizTree reads the MFT in seconds.

```bash
# UAC prompt appears — user must click Yes
"/c/Program Files/WizTree/WizTree64.exe" 'C:\' '/export=C:\Users\YOUR_USERNAME\AppData\Local\Temp\wiztree.csv' /admin=1 /exportfolders=1 /exportfiles=1
```

Pitfalls (all bit me):
- The drive arg is POSITIONAL and comes FIRST. Wrong syntax silently exits, no file.
- `/admin=1`: parent exits immediately after spawning the elevated child (never `-Wait` on it). Child scans ~1 min then writes the CSV. The export file is LOCKED until the child exits — reads fail with PermissionError / "Device busy". Wait for the WizTree process to disappear, or `powershell Stop-Process -Name WizTree64 -Force`, then read.
- `/admin=0` = slow fallback (5+ min on 475 GB), avoid.
- CSV format: banner line, then header `File Name,Size,Allocated,Modified,Attributes,Files,Folders`. Size = col 1 (NOT col 0), dirs end with `\`, dir attr = 16, file attr = 32. Parse with `scripts/parse_wiztree_csv.py`.
- The CSV is the only full-drive index — don't wipe it with a Temp cleanup until analysis is done (session lesson: it WAS in Temp and got deleted).
- Free space DIPS while the export writes (CSV ~650 MB on this drive) — at <1 GB free it looks alarming; wait for the child to exit, don't abort the scan.
- Parser junk-bucket regexes OVER-MATCH: `WER|ReportQueue` patterns flag app install dirs (WindowsApps, Office Addins, VS Code extensions) — the "crash dumps" bucket read 8.4 GB when real CrashDumps was 139 MB. Cross-check buckets against `AppData\Local\CrashDumps` + `Windows\Minidump` before reporting; the BIGGEST FILES list is ground truth.

## Drive state (git-bash-safe)
```bash
powershell -NoProfile -Command 'Get-PSDrive -PSProvider FileSystem | Select Name,@{n="FreeGB";e={[math]::Round($_.Free/1GB,1)}}'   # single-quote it!
# or: df -h /c | tail -1
```
Double quotes let bash mangle `$_.Free` into a path — always single-quote PowerShell one-liners in git-bash.

## Junk inventory (safe, regenerable)
- npm: `npm cache clean --force`; pip: `pip cache purge`
- `%TEMP%`, `C:\temp`, CrashDumps
- Browser/Electron caches: `Chrome|Edge|Brave\User Data\*\Cache|Code Cache|GPUCache`, `Roaming\<app>\Cache` (Discord, opencode, Minecraft `webcache2.bak-*`)
- NVIDIA `DXCache`/`GLCache` (shader caches, regenerate)
- `$WinREAgent`, `$WINDOWS.~BT`, `Config.Msi` (upgrade leftovers)
- `SoftwareDistribution\Download` (needs admin: stop wuauserv/bits → delete → restart; re-downloadable)
- `.cache\codex-runtimes`, stale installers in Downloads
- `pnpm store prune`; `uv cache clean`; `poetry cache clear --all` (pip/npm are not the only package caches)
- `AppData\Local\Ollama\updates_v2\OllamaSetup.exe` (installer cache, ~1.5 GB)
- Hermes `AppData\Local\hermes\state-snapshots\` — daily DB backups ~0.8–1 GB each; prune middle dailies, KEEP newest + `full-state` + `pre-update` (housekeeping default, ~3.5 GB/run)
- `.__capcut_export_temp_folder_*` at drive root, `Config.Msi` contents

## Consent boundaries (user preference — never cross)
- NEVER delete AI model caches without explicit per-item consent: Ollama blobs (`C:\Users\YOUR_USERNAME\blobs` — user explicitly keeps these), `~/.cache/huggingface` (ask first; only delete after user confirms unused), `.android` AVDs, Playground/Documents content.
- EXCEPTION — `~/.ollama/models/blobs/*-partial` = interrupted downloads, never loadable by Ollama; delete without consent. The protected dir is `C:\Users\YOUR_USERNAME\blobs` (OLLAMA_MODELS), NOT the default `~/.ollama/models`. Re-measure partials at cleanup time — Ollama prunes its own failed pulls, so CSV sizes can shrink hours after the scan.
- No-answer consent default (user's style): empty clarify response → proceed with provable junk only (partials, old daily snapshots, caches); never AVDs, models in use, Videos, pagefile changes; surface skipped items at the end.
- Cleanup batches touching system dirs (`$WinREAgent`, `$WINDOWS.~BT`) trigger approval gating — split into "safe caches" (no prompt) + "system dirs" (needs consent) and ask explicitly.

## Verify
`df` before/after each batch; report freed GB per item. Windows Update deletion continues in background after elevated script exits — poll free space, don't block.

## git-bash quirks (bit me here)
- `taskkill //IM x //F` → "Invalid argument". Use `powershell -NoProfile -Command "Stop-Process -Name x -Force"` (also needed to kill elevated processes — non-elevated taskkill can't).
- Python heredocs with backslashes get mangled → write the parser with write_file, run the file.
- `du` hangs on dirs locked by in-flight deletes — wrap in `timeout 25` or skip.

## Windows GUI-app config fix pattern (Seelen example)
App config lives in `AppData\Roaming\<vendor>\settings.json` (Seelen: `com.seelen.seelen-ui\settings.json`). Fix = backup file, edit JSON (python json load/dump), kill process with Stop-Process — the app's service usually auto-restarts it. Widgets/plugins are sibling files (e.g. `widgets\*.slu`) — remove file AND its config key. Seelen specifics: `byWallpaper[*].muted=true` pauses live wallpaper playback; `streamingMode=true` pauses animations globally; `performanceMode.onBattery=Extreme` + `byWidget.@seelen/wallpaper-manager.coveragePauseThreshold=0.8` = pause on battery / heavy window coverage (the "pause only when unplugged or multitasking" config).
