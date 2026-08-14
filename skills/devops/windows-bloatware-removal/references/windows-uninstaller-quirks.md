# Windows Uninstaller Quirks — field notes from 2026-08 bloatware run

Verified against ~55 uninstalls on Win11 (Acer Nitro). All items below caused real failures or delays in production.

## Exit codes / signals

| Signal | Meaning | Handling |
|---|---|---|
| MSI `1619` | Cached MSI missing / product not truly registered (common with Acer `BOOTSTRATOR=1` installs, old Rovio games). `/x` and `/i REMOVE=ALL` both fail. | Check registration (below). If unregistered → reg export backup + delete uninstall key. Files remain on disk; tell user to delete folders manually (agent policy: no manual file deletion). |
| Inno uninstaller hangs with invisible dialog (`MainWindowTitle` empty or "Uninstall program") | Uninstaller waiting on hidden prompt; `-Wait` blocks forever. | Bounded `WaitForExit(90000)` + `Kill()`; run elevated watcher (below). |
| Edge setup exit `93` | "Browser/WebView is sticky, uninstall not allowed" — deliberate Microsoft safeguard when WebView2-dependent apps exist. | Accept. Report as by-design. Check `%TEMP%\msedge_installer.log` for the exact line: `Browser/WebView is sticky, uninstall not allowed.` |
| Opera `opera.exe /uninstall` exit `38` | Transient — uninstaller runs detached and completes async. Re-check registry; entry often gone minutes later. | Treat non-zero as "check again", not failure. |
| EXE exit `0` but uninstall key remains | Uninstaller async cleanup (Trend Micro pattern) or wrong silent flag accepted-but-ignored. | Re-scan registry before declaring; remove orphan key only if install folder verified empty/missing. |

## MSI registration check (packed GUID)

Product codes are stored byte-reversed in the installer registry. Check before treating an MSI as orphan:

```powershell
function Pack-Guid([string]$g) {
  $hex = $g -replace '[{}]','' -replace '-',''
  return (($hex.Substring(6,2)+$hex.Substring(4,2)+$hex.Substring(2,2)+$hex.Substring(0,2) +
           $hex.Substring(10,2)+$hex.Substring(8,2)+$hex.Substring(14,2)+$hex.Substring(12,2)+$hex.Substring(16,16)).ToUpper())
}
# registered if either path exists:
# HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\UserData\S-1-5-18\Products\<packed>
# HKLM:\SOFTWARE\Classes\Installer\Products\<packed>
```
Registered-but-1619 → try `/x {GUID} /qn /norestart`, fallback `/i {GUID} REMOVE=ALL /qn /norestart`.

## Stuck-uninstaller watcher (elevated, kills only the stuck ones)

```powershell
$deadline = (Get-Date).AddMinutes(25)
while ((Get-Date) -lt $deadline) {
  Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $_.ProcessName -match '^(unins000|Uninstall)$' -and $_.StartTime -lt (Get-Date).AddSeconds(-25) } |
    ForEach-Object { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }
  Start-Sleep -Seconds 5
}
```
25s threshold is safe: real uninstalls finish in <10s; the stuck ones are dialogs. Watch out: a non-elevated shell cannot kill an elevated uninstaller — the watcher must run elevated too (Start-Process -Verb RunAs).

## Registry surgery rules

- Orphan uninstall keys can live in ANY of: `HKLM\...\Uninstall`, `HKLM\...\WOW6432Node\...\Uninstall`, `HKCU\...\Uninstall` — always check all three.
- `reg export <key> backup.reg /y` BEFORE deleting any key (hive prefix must be `HKEY_LOCAL_MACHINE` / `HKEY_CURRENT_USER`, not `HKLM`/`HKCU`).
- Startup disable = rename Run value to `disabled_<name>` (reversible). Never delete.
- Inno keys end `_is1` and store `InstallLocation` — use it to find `unins000.exe` when UninstallString is empty.

## Silent-flag ladder (per uninstaller type)

1. Inno (`unins000.exe`, `Uninstall*.exe`): `/VERYSILENT /SUPPRESSMSGBOXES /NORESTART`
2. NSIS: `/S`
3. Original UninstallString args — some custom uninstallers ONLY work this way (e.g. Fishdom 3 needs `/U:...uninstall.xml`; UNWISE needs `/U <INSTALL.LOG>`)

## Known GUI-required uninstallers

- Trend Micro `Remove.exe` — wizard, needs human click-through
- Opera `opera.exe /uninstall` — UI uninstaller
- Some old InstallShield (`UNWISE.EXE`) — hangs even with `/U`; treat as orphan after one bounded attempt

## PS scripting pitfalls

- **`$args` is an automatic variable.** Naming a function parameter `$args` makes Start-Process fail silently (logged "START FAILED"). Use `$argList`.
- Unquoted UninstallString with spaces (`C:\Program Files (x86)\x\Uninstall.exe`) — don't split on first space; find the `.exe` token and take prefix as path.
- Elevated `Start-Process -Verb RunAs` is detached: child MUST log to a file; parent polls for `DONE-MARKER` line.
- Mid-run reboot/shutdown is safe: uninstallers idempotent, MSI transactional. Re-run same script to resume.
