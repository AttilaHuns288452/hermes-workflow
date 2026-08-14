# Bloatware scan - READ ONLY. Enumerates Store apps, classic programs, startup entries.
# Usage: powershell.exe -NoProfile -ExecutionPolicy Bypass -File bloatware_scan.ps1
# No elevation needed.
$ErrorActionPreference = 'SilentlyContinue'

Write-Output "===== STORE APPS (non-system, non-framework) ====="
Get-AppxPackage |
  Where-Object { $_.SignatureKind -eq 'Store' } |
  Sort-Object Name |
  ForEach-Object { "{0} | {1}" -f $_.Name, $_.Version }

Write-Output ""
Write-Output "===== CLASSIC PROGRAMS (uninstall registry) ====="
$paths = @(
  'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
  'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
  'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*'
)
Get-ItemProperty $paths |
  Where-Object { $_.DisplayName } |
  Sort-Object DisplayName |
  ForEach-Object { "{0} | {1} | {2} | key={3} | US={4}" -f $_.DisplayName, $_.DisplayVersion, $_.Publisher, $_.PSChildName, $_.UninstallString }

Write-Output ""
Write-Output "===== STARTUP: logon/boot scheduled tasks (hidden mechanism) ====="
Get-ScheduledTask | ForEach-Object {
  $t = $_.Triggers | Where-Object { $_.CimClass.CimClassName -match "Logon|Boot" }
  if ($t) {
    $trig = ($t | ForEach-Object { $_.CimClass.CimClassName }) -join ","
    "{0}{1} [{2}] {3} -> {4}" -f $_.TaskPath, $_.TaskName, $_.State, $trig, ($_.Actions | Select-Object -First 1).Execute
  }
}

Write-Output ""
Write-Output "===== STARTUP (Run keys + startup folder) ====="
$runKeys = @(
  'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run',
  'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run',
  'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run'
)
foreach ($k in $runKeys) {
  if (Test-Path $k) {
    Get-ItemProperty $k | ForEach-Object {
      $_.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' } |
        ForEach-Object { "{0} :: {1}" -f $k, $_.Name }
    }
  }
}
Get-ChildItem "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup" -ErrorAction SilentlyContinue |
  ForEach-Object { "STARTUP FOLDER :: $($_.Name)" }
Get-ChildItem 'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup' -ErrorAction SilentlyContinue |
  ForEach-Object { "STARTUP FOLDER (all users) :: $($_.Name)" }

Write-Output ""
Write-Output "===== DISK ====="
Get-PSDrive C | ForEach-Object { "C: free = {0:N1} GB of {1:N1} GB" -f ($_.Free/1GB), (($_.Free+$_.Used)/1GB) }
