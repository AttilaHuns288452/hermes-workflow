import subprocess
import sys
import os

# Path to the lending backup script — set $LENDING_BACKUP_SCRIPT env var to override
script = os.environ.get(
    "LENDING_BACKUP_SCRIPT",
    r"C:\Path\To\lending-management-system\tools\daily-supabase-gdrive-backup.ps1"
)
result = subprocess.run(
    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script],
    capture_output=True,
    text=True,
)
if result.stdout:
    print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)
sys.exit(result.returncode)
