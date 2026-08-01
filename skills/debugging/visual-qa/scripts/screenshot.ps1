# Windows PowerShell screenshot + browser open template
# Usage: Edit $url and $outPath, then run via: powershell -ExecutionPolicy Bypass -File this.ps1

$url = "http://localhost:9876"           # CHANGE THIS
$outPath = "C:\Users\Attila\Downloads\screenshot.png"  # CHANGE THIS

# Kill existing Edge to avoid session restore
taskkill /f /im msedge.exe 2>$null
Start-Sleep -Seconds 1

# Open fresh
Start-Process "msedge" -ArgumentList "--new-window --no-first-run $url"
Start-Sleep -Seconds 4

# Screenshot primary display
Add-Type -AssemblyName System.Windows.Forms
$screen = [System.Windows.Forms.Screen]::PrimaryScreen
$bmp = New-Object System.Drawing.Bitmap($screen.Bounds.Width, $screen.Bounds.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0, $screen.Bounds.Size)
$bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bmp.Dispose()

Write-Output "SCREENSHOT_OK: $outPath"
