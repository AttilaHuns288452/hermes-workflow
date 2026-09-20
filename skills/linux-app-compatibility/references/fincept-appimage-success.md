# Fincept Terminal AppImage Success (2026-09-04)

## Problem
Fincept Terminal v4.5.0 (open-source AGPL build) failed on Ubuntu 24.04 with:
```
/usr/bin/FinceptTerminal: /lib/x86_64-linux-gnu/libQt6Core.so.6: version `Qt_6.8' not found
```
The `.deb` was built against Qt 6.8, but Ubuntu 24.04 ships Qt 6.4.2.

## Failed Attempts
1. **`.deb` package** — installs to `/usr/bin/FinceptTerminal`, links against system Qt 6.4 → ABI break
2. **Older `.deb` (v4.3.0, v4.4.1)** — same Qt 6.8 requirement, same failure
3. **Enterprise `.deb` (v5.0.2)** — works (bundles own Qt) but is the PAID build, not open-source

## What Worked
**AppImage (v3.0.11)** — downloaded from GitHub releases:
```bash
wget https://github.com/Fincept-Corporation/FinceptTerminal/releases/download/v3.0.12/FinceptTerminal_3.0.11_amd64.AppImage
chmod +x FinceptTerminal_3.0.11.AppImage
./FinceptTerminal_3.0.11.AppImage
```
AppImage bundles its own Qt runtime → works on any distro, no system dependency issues.

## Key Insight
When a `.deb` fails with `Qt_6.X not found`:
1. Check for an **AppImage** release first — it's the universal Linux format
2. AppImages bundle Qt, Electron, and all dependencies
3. No installation needed — just `chmod +x` and run
4. Works on Ubuntu 20.04, 22.04, 24.04, etc.

## AppImage Extraction (if needed)
```bash
./FinceptTerminal_3.0.11.AppImage --appimage-extract
# Creates squashfs-root/ with all bundled libraries
# Run via: ./squashfs-root/AppRun
```

## OAuth Sign-In Issue
Even when the AppImage launches, Qt WebEngine's embedded browser often fails OAuth sign-in on Linux:
- Error: `Invalid JSON response: <!DOCTYPE html>` (HTML error page instead of OAuth token)
- Cause: Qt WebEngine can't complete the OAuth redirect flow
- Fix: Use the **web terminal** at `https://fincept.in/open-source` instead

## Lesson
For Qt-based financial terminals on Linux:
1. **AppImage** > `.deb` (avoids all Qt version issues)
2. **Web terminal** > desktop app (avoids Qt WebEngine OAuth issues)
3. **Enterprise build** > open-source build (bundles Qt, but costs money)
