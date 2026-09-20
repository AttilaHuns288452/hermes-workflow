# Desktop Renderer Diagnosis

Reusable checks for Linux Mint Cinnamon when a wallpaper, live renderer, or desktop app appears blank, duplicated, or visually stale.

## 1. Identify the renderer

Do not infer behavior from the app name. Check:

```text
pgrep -af '<app-name>'
wmctrl -l -x
flatpak info <app-id>
```

Read only the relevant config and recent logs. A missing process, an onboarding loop, or an exited UI service means there is no rendered scene to debug yet.

## 2. Prove the background path visually

`gsettings set` and `gsettings get` prove the URI was stored, not that Cinnamon displayed it.

1. Select a known-good system wallpaper.
2. Capture the compositor.
3. If the system wallpaper works but the user image does not, copy the image to a conventional per-user background directory such as `~/.local/share/backgrounds/`.
4. Set all relevant keys explicitly:
   - `org.cinnamon.desktop.background picture-uri`
   - `org.gnome.desktop.background picture-uri`
   - `org.gnome.desktop.background picture-uri-dark`
   - `picture-options` where supported
5. Capture again and keep the working URI as the controller's canonical path.

## 3. Remove stale Cinnamon desklets

`gsettings get org.cinnamon enabled-desklets` can show `@as []` while actors from an already-open Desklets session remain visible. Close the Desklets settings window first, reapply the empty list, then capture. If the window is stale, close only that specific X11 window; do not restart unrelated applications.

## 4. Sober-specific interpretation

Sober is the Flatpak Roblox runtime, not a wallpaper engine. Its state and logs can distinguish first-run setup from graphics failure:

- `has_seen_onboarding=false` or `roblox_uid=0` indicates onboarding is incomplete.
- Repeated `wants_bundle_install=yes` followed by `ui service exited` means Sober has not reached Roblox rendering.
- A blank/transparent Sober surface can therefore show the Cinnamon wallpaper underneath.

Complete onboarding and the Roblox bundle installation first. If the renderer is still blank, use Sober Settings to try its documented OpenGL fallback (`use_opengl`) before editing configuration manually. Official reference: https://vinegarhq.org/Sober/Configuration/index.html

If hand-editing is unavoidable: `~/.var/app/org.vinegarhq.Sober/config/sober/config.json` is JSONC, not JSON (it opens with `//` comment lines), so `patch`/`write_file` refuse it on syntax validation. Edit it with a Python string replace instead and verify with `grep`:

```bash
python3 -c "p='<path>'; s=open(p).read(); open(p,'w').write(s.replace('\"use_opengl\": false','\"use_opengl\": true',1))"
grep use_opengl <path>
```

## 5. Verify stateful controllers

For a live/static controller with a watcher, verify the state twice after a transition. A watcher started before a script change can retain old logic and overwrite the new state. Recycle only the known watcher, start the current controller once, wait a few seconds, then verify:

- selected identity
- performance state
- override state
- renderer process
- actual wallpaper URI
- compositor capture
