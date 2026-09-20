# OpenDesign Wine Failure (2026-09-04)

## Problem
OpenDesign v0.21.1 Windows installer (`open-design-0.21.1-win-x64-setup.exe`) was installed via Wine Staging 11.16 on Linux Mint (Ubuntu 24.04). The installer ran but the app crashed at startup with:
- `Invalid file descriptor to ICU data received` (icudtl.dat was 333KB instead of 10MB+)
- `Error loading V8 startup snapshot file` (snapshot_blob.bin was 334KB instead of 100MB+)
- `Failed to load chrome_100_percent.pak` / `resources.pak`
- After manually copying these files from a 7z extraction: `libEGL warning: pci id for fd XX: 10de:25a2, driver (null)` and `dri: failed to create dri2 screen`

## Root Cause
1. **Corrupted install**: Wine's NSIS extraction truncated large binary files (icudtl.dat, snapshot_blob.bin, .pak files). The 7z extraction confirmed the files were small in the installer payload itself — but the installed versions were even smaller than what 7z produced.
2. **GPU binding failure**: Wine's wined3d tried to create an EGL context on the NVIDIA RTX 3050 (mobile) but the proprietary driver exposed `driver (null)` to Wine's libEGL. Every env var hack (LIBGL_ALWAYS_SOFTWARE, GALLIUM_DRIVER=llvmpipe, MESA_LOADER_DRIVER_OVERRIDE=i915, DRI_PRIME=0/1, __EGL_VENDOR_LIBRARY_FILENAMES) failed because:
   - Electron's GL backend explicitly selects a hardware device, rejecting software rendering
   - The Intel i915 GPU (renderD129) was available but Wine defaulted to NVIDIA (renderD128)
   - Wine Staging 11.16 still can't bridge this gap on Optimus laptops

## What Didn't Work
- `WINEDEBUG=fixme-all` (suppressed noise but didn't fix anything)
- `wine explorer /desktop=OD,1920x1080` (virtual desktop — no effect on GPU binding)
- `WINEDLLOVERRIDES="mscoree,mshtml="` (irrelevant for Electron)
- `WINEDLLOVERRIDES="dxgi=n,b"` (no DXVK installed to translate D3D→Vulkan)
- `QT_QPA_PLATFORM=xcb` (not a Qt app)
- `VK_ICD_FILENAMES=""` (disabled Vulkan entirely, made it worse)
- `MESA_GL_VERSION_OVERRIDE=4.5COMPAT` (Mesa rejected the format)
- `GALLIUM_DRIVER=llvmpipe` (rejected: "Not allowed to force software rendering when API explicitly selects a hardware device")
- `DRI_PRIME=0` and `DRI_PRIME=1` (Wine still picked the wrong GPU)
- `MESA_LOADER_DRIVER_OVERRIDE=i915` (Wine's EGL ignored it)
- Copying icudtl.dat, v8_context_snapshot.bin, .pak files from 7z extraction (files were correct size but Wine still couldn't load them — PE loader issue)

## What Worked
**Native npm launcher**: `npm install -g open-design-ade` then `open-design-ade` starts the Next.js web UI directly on Linux at http://localhost:7456 — no Wine, no Electron, no GPU hacks.

## Lesson
Electron 41+ apps on Wine are a dead end on NVIDIA Optimus laptops. The PE loader can't map large binary blobs, and wined3d can't get a working EGL context from the proprietary NVIDIA driver. Always check for a native CLI/web version before attempting Wine.
