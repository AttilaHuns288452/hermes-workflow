$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$ProjectFile = Join-Path $ProjectRoot 'LendingManagementSystem.csproj'
$BackupDir = Join-Path $ProjectRoot 'tmp'
$LogDir = Join-Path $BackupDir 'backup-logs'
$RemoteName = $env:RCLONE_REMOTE
if (-not $RemoteName) { $RemoteName = 'my_gdrive' }
$RemoteFolder = 'BackupFolder'
$BackupPrefix = 'my-backup'
$KeepBackups = 2

$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
$env:DOTNET_NOLOGO = '1'

New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

$today = Get-Date -Format 'yyyy-MM-dd'
$backupName = "$BackupPrefix-$today.json"
$backupPath = Join-Path $BackupDir $backupName
$logPath = Join-Path $LogDir "$BackupPrefix-$today.log"

function Write-BackupLog {
    param([Parameter(Mandatory = $true)][string]$Message)

    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "[$timestamp] $Message" | Tee-Object -FilePath $logPath -Append
}

function Invoke-LoggedCommand {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    Write-BackupLog "Running: $FilePath $($Arguments -join ' ')"
    $output = & $FilePath @Arguments 2>&1
    $exitCode = $LASTEXITCODE

    foreach ($line in $output) {
        Write-BackupLog $line.ToString()
    }

    if ($exitCode -ne 0) {
        throw "Command failed with exit code ${exitCode}: $FilePath $($Arguments -join ' ')"
    }
}

$rclone = (Get-Command 'rclone' -ErrorAction Stop).Source
$remoteRoot = "${RemoteName}:$RemoteFolder"
$remoteBackup = "$remoteRoot/$backupName"

Write-BackupLog "Starting daily lending backup."

if (Test-Path -LiteralPath $backupPath) {
    Remove-Item -LiteralPath $backupPath -Force
}

Invoke-LoggedCommand -FilePath 'dotnet' -Arguments @(
    'run',
    '--project', $ProjectFile,
    '--',
    '--backup', $backupPath
)

Invoke-LoggedCommand -FilePath 'dotnet' -Arguments @(
    'run',
    '--project', $ProjectFile,
    '--',
    '--preview-backup', $backupPath
)

Invoke-LoggedCommand -FilePath $rclone -Arguments @('mkdir', $remoteRoot)
Invoke-LoggedCommand -FilePath $rclone -Arguments @('copyto', $backupPath, $remoteBackup)

$listingOutput = & $rclone 'lsjson' $remoteRoot '--files-only' '--include' "$BackupPrefix-*.json" 2>&1
if ($LASTEXITCODE -ne 0) {
    foreach ($line in $listingOutput) {
        Write-BackupLog $line.ToString()
    }
    throw "Failed to list backups in ${remoteRoot}."
}

$itemsJson = ($listingOutput | Out-String).Trim()
$items = @()
if ($itemsJson.Length -gt 0) {
    $items = @($itemsJson | ConvertFrom-Json)
}

$backupItems = @(
    $items |
        Where-Object { $_.Name -like "$BackupPrefix-*.json" } |
        Sort-Object -Property Name -Descending
)

$oldItems = @($backupItems | Select-Object -Skip $KeepBackups)
foreach ($item in $oldItems) {
    $oldRemotePath = "$remoteRoot/$($item.Path)"
    Invoke-LoggedCommand -FilePath $rclone -Arguments @('deletefile', $oldRemotePath)
}

Write-BackupLog "Uploaded $backupName to $remoteRoot."
Write-BackupLog "Retention complete. Kept $([Math]::Min($backupItems.Count, $KeepBackups)) backup file(s); deleted $($oldItems.Count)."
Write-BackupLog "Daily lending backup finished."
