---
name: windows-bloatware-removal
description: Remove Windows bloatware - scan, consult, then uninstall.
---

# Windows Bloatware Removal

Safely remove OEM bloat, adware/PUPs, junk games, duplicate apps, and leftover AVs on Windows. Verified end-to-end 2026-08 (Acer Nitro, Win11).

## User rules (Attila's machine — ALWAYS apply)

- **Consult BEFORE uninstalling.** Present a bundle list (A = safe junk, B = startup disables, C = ask-user items) and get explicit approval. Never uninstall unapproved items.
- **KEEP:** Overwolf, CurseForge, Adobe Acrobat, CapCut, TradingView.
- **Browsers:** only Chrome + Brave (remove Firefox/Opera/Opera GX; Edge is unremovable — see pitfalls).
- **AV:** keep Bitdefender (best free, AV-TEST 6/6/6) + Malwarebytes (on-demand, no conflict). Remove Trend Micro / AVG / Avast leftovers.
- Never touch: real games (Steam/Epic/GOG), dev tools, personal apps.
- Guardrail: agent NEVER deletes files manually. Use official uninstallers; for orphans remove only registry keys (reg export backup first) and tell user which leftover folders to delete.

## Workflow

### 1. Read-only scan + baselines
Run `scripts/bloatware_scan.ps1` (elevation NOT needed): lists Store apps, classic uninstall entries with UninstallString/InstallLocation, startup Run keys, disk free. **Before touching anything, snapshot disk free + RAM used + process count** — the user WILL ask for before/after numbers; a missing baseline means an honest "no baseline exists". Boot duration is usually NOT measurable (Diagnostics-Performance event log often empty — say so, never fabricate). Note: on Acer machines expect Acer factory bloat + bundled demo games + SweetLabs adware + multiple AVs.

### 2. Present bundles, get approval (clarify tool)
- A: adware/PUP, OEM trialware, junk games/demos, duplicates, AV leftovers
- B: startup disables (rename, reversible — see below)
- C: heavy apps user may use (browsers, AV choice, emulators, VPN, etc.)
User picks; proceed only with what's approved.

### 3. Run removal ELEVATED (one UAC prompt, tell user to click Yes)
Shell is normally non-elevated. Pattern:
```powershell
Start-Process powershell.exe -Verb RunAs -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','C:\...\remove.ps1' -WindowStyle Hidden
```
The elevated child is DETACHED — the script must append to a log file; poll for a `DONE-MARKER` line with SIMPLE commands (`sleep N; grep -c DONE-MARKER log`) — complex `for`-loop one-liners get blocked by the terminal parser. Store apps: `Remove-AppxPackage` + `Remove-AppxProvisionedPackage -Online`. Classic apps: parse UninstallString (see quirks ref). Startup disables: rename Run value to `disabled_<name>` (reversible — never delete).

### 4. Startup — FOUR mechanisms, Run keys are NOT enough
1. **Run keys** (HKCU + HKLM + WOW6432Node) — rename to `disabled_<name>`.
2. **Services** — some apps start via `Automatic` services (ExpressVPNService); `Set-Service -StartupType Manual` + stop.
3. **Scheduled tasks with Logon/Boot triggers** — THE hidden one: **Acer Care Center mirrors every Run key as a task under `\CareCenter\`** (EADM=Epic, SunJavaUpdateSched, Wondershare, Adobe Sync, Edge autolaunch…). Disable those mirror tasks or the apps relaunch after reboot despite disabled Run keys. Enumerate: `Get-ScheduledTask | where Triggers match Logon|Boot`. Also disable dead tasks of uninstalled apps — but strip quotes from `Actions.Execute` BEFORE `Test-Path` (quoted paths fail the check → you wrongly disable tasks for KEPT apps like NitroSense/Brave/NVIDIA/Google updaters; re-enable promptly). `Get-ScheduledTask -TaskName` does NOT accept path prefixes — split `TaskPath`/`TaskName` at the last `\`.
4. **Startup folders** (user + ProgramData).
Re-registration watch: BlueStacks re-adds its Run key, Chrome/Edge re-add autolaunch keys — re-rename and point the user to the in-app setting as the permanent fix.

### 5. Verify + report
Re-run the registry check for target names; report removed / kept / remaining-with-reason, disk before→after. Full audit log at the log path. Restore notes: `disabled_*` renames, `uninstall_backup.reg`.

## Pitfalls (all hit in production)

- **MSI exit 1619** = orphaned install (cached MSI gone, e.g. Acer bootstrap installs). Don't retry — check registration via packed GUID under `HKLM\...\Installer\UserData\S-1-5-18\Products\<packed>`; if unregistered, `reg export` then remove the uninstall key.
- **Steam-managed entries**: UninstallString contains `steam://` or key is `Steam App <id>` → SKIP, tell user to uninstall via Steam.
- **Stuck Inno uninstallers** show an invisible dialog and hang `-Wait` forever → bounded `WaitForExit(90000)` + Kill, plus an elevated watcher process that kills `unins000|Uninstall.exe` processes older than ~25s.
- **Edge uninstall exit 93** = "Browser/WebView is sticky, uninstall not allowed" — Microsoft blocks it when WebView2-dependent apps exist (Hermes desktop, Seelen UI, Electron bubbles). Do NOT fight it; report as by-design.
- **Unquoted UninstallString with spaces** (`C:\Program Files (x86)\...\Uninstall.exe` without quotes) breaks naive splitting → find the `.exe` token, join prefix.
- **PowerShell `$args` is an automatic variable** — never use it as a function parameter name; Start-Process fails silently ("START FAILED").
- **Silent-flag ladder**: Inno `/VERYSILENT /SUPPRESSMSGBOXES /NORESTART` → NSIS `/S` → original args (some, e.g. Fishdom, only work with original `/U:...xml` args).
- **Orphan keys live in any of 3 hives** (HKLM / WOW6432Node / HKCU) — check all; hardcoding HKLM fails.
- **PC shutdown mid-run is safe**: uninstallers are idempotent (re-run skips removed), MSI is transactional. Just resume with the same script.
- Trend Micro uninstaller needs GUI click-through (`Remove.exe`); Opera launches UI uninstaller. Tell the user windows may pop up. `Remove.exe /S` exit 0 can still leave 2000+ files + registry keys — the GUI wizard is the real uninstaller.
- **Disk drops after reboot are usually Windows Update staging** (`C:\Windows\SoftwareDistribution\Download` can hold 6+ GB) — check before claiming a regression.
- **Fresh reboot required for real after-numbers**: disables applied mid-session don't affect the current boot (uptime check reveals an old boot) — tell the user to reboot, then re-measure.

## Support files
- `scripts/bloatware_scan.ps1` — read-only enumeration (reuse verbatim).
- `references/windows-uninstaller-quirks.md` — exit codes, packed-GUID check code, watcher script, Edge-93 log evidence.
