---
name: run-windows-apps-linux
description: "Use when running a Windows .exe app on Linux."
---

# run-windows-apps-linux

When a user wants to run a Windows desktop app on Linux, **do not reach for Wine by default** — Wine is the last resort, not the first tool.

## The ladder (apply in order)

### 1. Native path exists? Use it FIRST.

Modern Electron/Node.js apps ship a Linux-native engine that the Electron wrapper just calls. Before Wine, check:

- **npm package**: `npm search <app>` or `npm install -g <app>-ade` / `<app>-cli`. Many Electron apps publish a native launcher.
- **Docker image**: `docker search <app>` / check GitHub for `docker-compose.yml`.
- **Official download**: check releases page for `.deb`, `.AppImage`, `.rpm`, or `tar.gz` Linux builds.
- **Web/Cloud version**: some apps (OpenDesign, Figma) have a fully functional web UI at `https://<app>.com/cloud`.

```bash
npm install -g open-design-ade  # starts local daemon + web UI on :7456
```

If a native path exists → use it, done. No Wine, no GPU hacks.

### 2. No native path? Wine — but know the failure modes.

If you must use Wine, expect these issues on modern hardware (especially NVIDIA Optimus laptops):

#### V8 snapshot / ICU crash
```
FATAL:gin/v8_initializer.cc:690 Error loading V8 startup snapshot file
ERROR:base/i18n/icu_util.cc:232 Invalid file descriptor to ICU data
```
**Fix**: extract the app's resources directly from the installer via 7z:
```bash
7z x installer.exe -o/tmp/od_extract
7z x '/tmp/od_extract/$PLUGINSDIR/payload-base.7z' -o/tmp/od_base
# Copy missing files to install dir:
cp /tmp/od_base/icudtl.dat ~/.wine/drive_c/.../App/\ Design/
cp /tmp/od_base/v8_context_snapshot.bin ~/.wine/drive_c/.../App/\ Design/
cp /tmp/od_base/*.pak ~/.wine/drive_c/.../App/\ Design/
```

#### .pak resource files missing
```
ERROR:ui/base/resource/resource_bundle.cc:1100 Failed to load .../chrome_100_percent.pak
```
Same fix — extract from installer payload.

#### GPU / EGL / OpenGL failure (Wine's wined3d can't create a GL context)
```
libEGL warning: egl: failed to create dri2 screen
err:d3d:wined3d_caps_gl_ctx_create Failed to find a suitable pixel format
```
**Root cause**: Wine's wined3d tries to use the NVIDIA GPU directly, but the Mesa DRI driver is `driver (null)` — Wine can't find a working GL context. Common on Optimus laptops.

**Workarounds (try in order):**
```bash
# 1. Force Intel iGPU
DRI_PRIME=1 MESA_LOADER_DRIVER_OVERRIDE=i915 wine app.exe

# 2. Virtual desktop (fixes off-screen windows)
wine explorer /desktop=App,1920x1080 app.exe

# 3. GDI rendering (no GL)
WINE_D3D_BACKEND=gdi wine app.exe
```

**Honest ceiling**: Electron 40+ apps with GPU process requirements often **will not work** under Wine on Optimus hardware. The Electron GPU process spins up a Vulkan/D3D context that Wine's translation layers can't provide. If the above three workarounds fail, stop — tell the user the native path is the right answer.

#### Set Wine as default .exe handler
```bash
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/wine.desktop << 'EOF'
[Desktop Entry]
Name=Wine
Exec=wine %f
Type=Application
MimeType=application/x-ms-dos-executable;application/x-msdownload;
EOF
xdg-mime default wine.desktop application/x-ms-dos-executable application-x-msdownload
```

## Key pitfalls

### Game installs with mod managers (Vortex) — Bannerlord case study (verified 2026-09-24)

- **Symlink husks:** game dirs managed by Vortex contain thousands of ABSOLUTE symlinks into `.NTFS-3G/C:/Users/.../Vortex/...` staging. If the staging dir is gone (wiped Windows profile), every mod file incl. mod loaders (BLSE) is a dead husk — game cannot run modded. Check `find <dir> -type l | wc -l` + test-resolve BEFORE trusting an install. Fix: delete dead links, move Modules lacking SubModule.xml aside, run vanilla.
- **External NTFS mounts are read-only via udisks** (`fuseblk ro`). Wine needs writes next to the exe → one-time `rsync -a` to native fs (~1h for 50GB USB). Don't fight the mount.
- **pgrep self-match:** `pgrep -f 'rsync …'` matches its own wrapper bash → phantom STILL_RUNNING loops. Use `pgrep -x rsync`.
- **xwd captures of GL/Vulkan windows can be all-black even when rendering fine.** Ground truth: `nvidia-smi --query-compute-apps` VRAM, ps CPU >100%, game Documents dir created. Convert captures with ffmpeg (`ffmpeg -i x.xwd x.png`); PIL cannot read .xwd.
- **pkill/pgrep -f of the game name kills your own shell wrapper** — target exact pids; comm is 15 chars (`pgrep -x 'TaleWorlds.Moun'`).
- **Bannerlord recipe that worked (Wine 11.18 Staging, RTX 3050):** dedicated prefix + `winetricks -q vcrun2022 dotnet48 dxvk` (dotnet48 ~20 min, looks stalled — don't retry), run `TaleWorlds.MountAndBlade.Launcher.exe` or `Bannerlord.exe /singleplayer` from bin/Win64_Shipping_Client. Window title contains full exe path (wmctrl grep '[Bb]anner').

### General

- **Don't loop on Wine workarounds**. If V8/ICU is fixed and GPU still fails after 3 attempts, the native path is the answer — say so.
- **Electron apps are Node.js underneath**. Look for the npm package / Docker image before accepting Wine as the path.
- **Installer extraction**: NSIS installers pack payloads in `$PLUGINSDIR/payload-base.7z` and `payload-overlay.7z` — extract with `7z x`.
- **Off-screen Wine windows**: use `wine explorer /desktop=Name,WxH app.exe` to force a managed desktop.
- **Process cleanup**: `wineserver -k` then `pkill -f 'App Name'` between attempts; stale processes cause false failures.

## References

- `references/electron-wine-failures.md` — transcript of Electron 41 + Wine Staging 11.16 failure modes on RTX 3050 Optimus