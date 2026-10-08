# Waydroid on an X11 desktop: bring-up and black-window debugging

## Bring-up chain (user session, no root)

All three run as background processes; the env names the weston socket explicitly:

1. `weston -Bx11-backend.so --width=1280 --height=720 --socket=wayland-altrox`
2. `XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-altrox waydroid session start`
3. `XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-altrox waydroid show-full-ui`

`waydroid status` saying RUNNING proves the container, NOT that any UI is attached.
Android surfaces render INSIDE the weston host window — there are no per-app X11
windows to look for.

## Black/blank window decision table

| Symptom | Cause | Fix |
|---|---|---|
| Gray patterned wallpaper + "Unlock your desktop" drag knob | weston idle locker over live surfaces | drag the knob right to the window edge (synthetic xdotool drag) |
| Only weston's own desktop/watermark, no Android | session grabbed the wrong socket or started before weston was ready | `waydroid session stop`, restart session with the env above, re-run show-full-ui |
| Android clock + lock screen, no home screen | Android's own lock screen | swipe up: drag bottom-center to ~45% height |
| `waydroid shell <cmd>` prints nothing | shell/logcat need root; piped output eats the error | confirm with `--details-to-stdout`; collect root evidence in ONE user-run `sudo` line |
| `waydroid log` hangs | follow mode | wrap in `timeout 5` |

## Synthetic gestures

Window rect comes from `wmctrl -lG` (`x y w h` per line); add the origin to
gesture coordinates:

    xdotool mousemove <cx> <cy> mousedown 1 mousemove --sync <cx+d> <cy> mouseup 1

Knob unlock: drag from window center to the right edge. Android unlock: drag from
bottom-center up to ~45% height.

## Screenshot verification (agent-side, no root)

`waydroid shell screencap` needs root and the container media dir is not host-readable;
host-side capture is the reliable path:

1. `gnome-screenshot -f /tmp/shot.png` (works where scrot/maim/ImageMagick are absent).
2. Window rect: `wmctrl -lG | grep -i weston` (match the compositor window).
3. Crop that rect with PIL and save the crop.
4. Pixel mean/variance on the crop proves rendering changed before spending a vision
   call; a uniform low-variance crop is blank.
5. `vision_analyze` the CROP, never the full desktop — vision describes sidebars/docks
   and misses the target window otherwise.
