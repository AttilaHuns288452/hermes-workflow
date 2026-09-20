---
name: linux-app-compatibility
description: Use when running Windows desktop apps on Linux.
version: 0.1.0
author: Attila, Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [linux, desktop, wine, electron, qt, compatibility, installation]
    related_skills: [linux-mint-customization]
---

# Linux App Compatibility

Decision framework and troubleshooting for running desktop apps on Linux Mint/Ubuntu. Many Windows apps have native Linux alternatives that avoid Wine entirely.

## When to Use

- User wants to install/run a Windows .exe on Linux
- Wine fails to launch a GUI app (process running but no window)
- Electron app crashes or shows blank screen under Wine
- App reports missing Qt version or GLX/EGL errors
- Need to find where a .deb package actually installed its binaries

## Decision Ladder (lazy order)

1. **Native Linux version exists?** Use it. Check:
   - npm packages (`npm info <pkg>`, `npx <pkg>`)
   - AppImage / Flatpak / Snap
   - Self-contained builds that bundle their own runtime
   - Docker/Podman if GUI forwarding works
   - Official website downloads for Linux

2. **Check the .deb's real contents before assuming failure:**
   - `dpkg -I <file>.deb | grep Depends` — see what it actually needs
   - `dpkg -L <package>` — find where binaries actually live (often `/opt/<app>/bin/`, not `/usr/bin/`)
   - The `.desktop` file `Exec=` line may differ from the real binary path

3. **Qt version mismatch?** (common with self-contained .deb builds)
   - Error: `version 'Qt_6.8' not found` or similar
   - Check system Qt: `strings /usr/lib/x86_64-linux-gnu/libQt6Core.so.6 | grep "Qt_6\."`
   - Fix: Look for a build that bundles its own Qt (Enterprise, portable, or AppImage builds)
   - Don't upgrade system Qt — breaks other packages

4. **Wine as last resort**, but expect GPU issues on NVIDIA Optimus
   - Wine's wined3d needs an EGL context from the GPU driver
   - NVIDIA proprietary driver often exposes `driver (null)` to Wine's EGL
   - Every env var hack (LIBGL_ALWAYS_SOFTWARE, GALLIUM_DRIVER, MESA_LOADER_DRIVER_OVERRIDE) may fail
   - If Wine processes run but no window appears: GPU binding failed, not an app bug

## Common Patterns

### Electron Apps on Wine
- Electron 41+ needs V8 snapshot + ICU data files. If these are small (<1MB when they should be 100MB+), Wine's PE loader can't map them.
- Copying `.pak`, `icudtl.dat`, `v8_context_snapshot.bin` from a Windows extraction may not help if the files themselves are bundled differently.
- **Better path:** Find the native npm/web version. Most Electron apps ship a headless CLI or web UI.

### Qt Apps
- Open-source builds often depend on system Qt → breaks on older distros
- Enterprise/promercial builds bundle Qt in `/opt/<app>/bin/` → works everywhere
- Check `dpkg -I` for `Depends:` — if it only lists `libc6`, `libstdc++6`, etc., it's self-contained

### Finding Real Binary Paths
```bash
# After installing a .deb, find where the actual executable lives
dpkg -L <package> | grep -E 'bin/|opt/'
# Or check what the .desktop file actually runs
grep "^Exec=" /usr/share/applications/<app>.desktop
# Then verify the binary exists
ls -la <path-from-dpkg>
```

## Pitfalls

- Wine `xdg-mime default wine.desktop` makes ALL .exes open in Wine — remove when done: `xdg-mime unset default application/x-ms-dos-executable`
- Wine Staging from WineHQ repos (11.x) is more compatible than distro Wine (9.x) but still struggles with modern Electron
- `dri: failed to create dri2 screen` under Wine = NVIDIA driver not exposing DRI, not fixable with env vars
- Qt ABI is strict — a Qt 6.8 app cannot run on Qt 6.4 system libraries
- `dpkg -L` shows package contents; `dpkg -I` shows metadata/dependencies — use both
- Small snapshot/icudtl.dat files from a Windows installer are often correct — Wine just can't load them
- Don't upgrade system Qt or Mesa to force compatibility — breaks other packages
- **When user asks for open-source/free version, go to GitHub releases — NOT the commercial download page.** Commercial builds (e.g., `fincept.in/downloads/`) are paid/Enterprise and may bundle Qt or have different licensing. Always check GitHub first for the AGPL/open-source release.
- **AppImage is the right fallback for Qt version mismatches.** AppImages bundle their own Qt runtime and work on any distro. If a `.deb` fails with `Qt_6.X not found`, check for an AppImage release before trying older `.deb` versions.
- **Qt WebEngine OAuth often fails on Linux.** Embedded browser sign-in (Google, GitHub, etc.) frequently returns HTML error pages instead of completing the OAuth flow. If the app has a web-based alternative, recommend that instead of fighting Qt WebEngine.
- **Check `dpkg -I <file>.deb | grep Depends` for Qt deps:** If NO `qt6-*` packages are listed, the `.deb` expects system Qt to be new enough. On older distros (Ubuntu 24.04 = Qt 6.4), this WILL fail. Look for AppImage or build from source.

## Verification

A compatibility pass is complete when:
- Native alternative was checked first
- If Wine was tried, the failure mode was identified (GPU, Qt, or PE loader)
- The actual installed binary path was found via `dpkg -L`
- No system libraries were upgraded to force compatibility
- The user has a working install (native, container, or self-contained .deb)

Session-specific examples in `references/open-design-wine-failure.md`, `references/fincept-terminal-qt-mismatch.md`, `references/fincept-appimage-success.md`, and `references/cisco-packet-tracer-appimage.md`.

## See Also

- **linux-hardware-troubleshooting** — when a kernel module/driver isn't loaded and hardware isn't detected (Acer Nitro/Predator fan/thermal/RGB)
- **linux-mint-customization** — desktop-level config (themes, applets, keybindings)
