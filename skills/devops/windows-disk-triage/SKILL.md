---
name: windows-disk-triage
description: Diagnose a full Windows disk and reclaim space fast. Use when the user reports low storage, "disk blew up", or asks to find/clean junk/caches. Covers the WizTree MFT export workflow, cache-junk inventory, and safe cleanup ordering.
---

# Windows Disk Triage

## When to use
User says disk is full / space "blew up" / where did my GB go / clean the junk. On Windows (git-bash shell).

## Step 1 — Measure (5s, no admin)
```bash
powershell -NoProfile -Command 'Get-PSDrive -PSProvider FileSystem | Select-Object Name,@{n="FreeGB";e={[math]::Round($_.Free/1GB,1)}},@{n="UsedGB";e={[math]::Round($_.Used/1GB,1)}} | Format-Table -AutoSize'
```
ALWAYS single-quote the whole PowerShell command — bash expands `$_` inside double quotes and the script breaks.

## Step 2 — Full map with WizTree (the fast path)
`du`/`find` walks are useless on this machine (AppData caches + node_modules = millions of files, du -d1 times out at 4+ min). WizTree reads the MFT in seconds. User has it at `C:\Program Files\WizTree\WizTree64.exe` (check `/c/Program Files/WizTree/`).

```bash
"/c/Program Files/WizTree/WizTree64.exe" 'C:\' '/export=C:\Users\YOUR_USERNAME\AppData\Local\Temp\wiztree.csv' /admin=1 /exportfolders=1 /exportfiles=1
```
CRITICAL quirks (each one cost a failed run):
- **The drive path is a POSITIONAL first argument.** Omitting it = silent no-op, no file.
- `/admin=1` → UAC prompt (user clicks Yes) → elevated child scans; **the parent bash command exits immediately** ("DONE" prints before the file exists). The export appears ~30–60s later.
- The elevated child **holds the CSV locked while writing** — reads fail with PermissionError / "Device or resource busy". Wait until `tasklist | grep -i wiztree` shows no elevated instance before reading.
- You CANNOT taskkill the elevated child from a non-elevated shell — just wait for it to exit on its own.
- /admin=0 works without UAC but is 10x slower (full directory walk) — avoid.
- Export of a full 476 GB drive ≈ 880 MB / 5M rows. **Don't put it in Temp if you're about to clear Temp** — the cleanup deletes your own evidence (this bit us).

## Step 3 — Parse the export
Use `scripts/wiztree_parse.py` (see references/wiztree-export.md for exact CSV layout):
```bash
python "C:/Users/YOUR_USERNAME/AppData/Local/Temp/wizparse.py" C:/Users/YOUR_USERNAME/AppData/Local/Temp/wiztree.csv [YYYYMMDD]
```
Prints top-level dir sizes, biggest 45 files, and files >100MB modified since the given date (omit = since 7 days ago). The Modified column is what answers "what changed a few days ago" — cross-reference with session history for the story.

## Step 4 — Clean, safe-first order
```bash
npm cache clean --force        # typically 5–11 GB
pip cache purge
rm -rf /c/Users/YOUR_USERNAME/AppData/Local/Temp/*   # 5–8 GB; locked files just error, ignore
rm -v big installers in Downloads (WebStorm/Android Studio/etc. .exe)
rm -rf NVIDIA/DXCache/* NVIDIA/GLCache/* CrashDumps/*   # shader caches regenerate
```
Admin-only (Windows Update cache, elevated fire-and-forget — do NOT use -Wait, it hangs):
```powershell
powershell -NoProfile -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile','-Command','Stop-Service wuauserv,bits -Force -ErrorAction SilentlyContinue; Remove-Item C:\Windows\SoftwareDistribution\Download\* -Recurse -Force -ErrorAction SilentlyContinue; Start-Service wuauserv,bits -ErrorAction SilentlyContinue'"
```
Then poll free space; the elevated delete grinds through the last packages for minutes (9 GB update = 175+ items), keep verification lightweight (count items + df, NOT du — du hangs on the in-flight locks).

## Junk inventory (measured on this machine, Aug 2026)
| Item | Size | Verdict |
|---|---|---|
| `C:\Windows\SoftwareDistribution\Download` | up to 14 GB | safe to wipe (admin) |
| `C:\Windows\Installer` | ~30 GB | long-term cruft; skip unless desperate |
| `C:\Windows\WinSxS` | ~16 GB | DISM /StartComponentCleanup (admin) |
| pagefile.sys | 11–17 GB | cap via registry + reboot if needed |
| DriverStore | ~8.5 GB | `pnputil /enum-drivers` prune old versions |
| `$WinREAgent`, `$WINDOWS.~BT`, `C:\temp`, `Config.Msi` | ~3 GB | update leftovers, safe |
| `.cache\codex-runtimes`, `.cache\uv` | ~2 GB | re-downloadable |
| hermes data (AppData\Local\hermes) | ~12 GB | sessions/logs — NOT junk, ask first |

## NEVER delete without asking
- **User's AI model downloads: Ollama blobs (`~/blobs`, `~/.ollama`) and `~/.cache/huggingface`** — explicit standing rule for this user: OFF-LIMITS unless they ask. Big: 23 GB + 4 GB.
- `.android` (AVD emulator images), Store app `Packages`, user project folders (Documents/Projects, Playground), hermes session data.
- Ollama models should be removed via `ollama list` / `ollama rm <name>`, not raw file deletion.

## Pitfalls
- `rm` touching system paths (`$WinREAgent`, `$WINDOWS.~BT`) triggers the approval guard → batch the fully-safe stuff separately, present system leftovers as a list for explicit consent.
- `taskkill //PID n` fails in git-bash — use `taskkill //IM <name>.exe //F` or `cmd //c "taskkill /PID n /F"`.
- Heredocs mangle backslashes even quoted (`<<'EOF'` broke on `'\\'`) — write path-heavy Python via write_file, never heredoc.
- robocopy /L for file listing needs a REAL existing dest dir or it prints usage and dies.
- Games in Documents (CoD, Hogwarts, etc.) are usually just save folders — don't blame them; the installs live elsewhere. Verify with du before reporting.
