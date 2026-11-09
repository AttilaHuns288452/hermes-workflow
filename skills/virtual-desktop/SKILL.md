---
name: virtual-desktop
description: Use when agents must click/type off the user's screen.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [gui, x11, automation, isolation]
    related_skills: [computer-use, linux-gui-automation, vm-guest-driving]
---

# Virtual Desktop (isolated GUI automation)

Run GUI apps and synthetic input on a private X display (`:99`) so nothing appears on, or steals input from, the user's real desktop (`:0`). Built for the "agent needs to click a button while I'm gaming" case.

## When to Use

- The user is playing or working and a task needs GUI clicks, typing, or app windows.
- You need screenshots of an app without capturing the user's screen.
- Testing a desktop app in a clean session.

Not for: GPU/3D work (Xvfb is software-rendered), anything that must act inside the user's already-open windows, or browser work (use headless `browser_exec`, which never opens a visible window).

## Tool

`vdesk` (in `~/.local/bin`) wraps Xvfb + xdotool + ffmpeg:

```bash
vdesk start                      # Xvfb :99 at 1920x1080x24
vdesk run xmessage -geometry 500x200+100+100 "hello"
vdesk windows                    # visible windows on :99
vdesk shot /tmp/v.png            # screenshot of the virtual screen
vdesk click 400 300              # move+click INSIDE :99 only
vdesk type "hello"               # type into the focused window
vdesk key ctrl+s                 # key combo
vdesk stop                       # kill display + every app on it
```

Override with `VDESK_DISPLAY` / `VDESK_GEOM`. State lives in `~/.vdesk` (xvfb pid + launched pids).

## Procedure

1. `vdesk status`; start it if down.
2. Launch the target app with `vdesk run <app> ...`. Give it a `-geometry` so its position is known.
3. `vdesk shot` and inspect the PNG (vision/size) before clicking. Coordinates are absolute in the virtual screen.
4. Click, type, screenshot again to confirm the state changed. Do not assume a click landed.
5. `vdesk stop` when finished; a leftover Xvfb holds memory and a port.

## Pitfalls

- Without a window manager, windows open unmanaged at their requested geometry. That is fine for clicks; if you need dialogs to stack normally, `vdesk run openbox` first (if installed).
- Xvfb has no GPU: Chromium/Electron apps may need `--disable-gpu`; games and Blender will not run there.
- `computer_use` (cua) targets the DISPLAY of the gateway process, which is `:0`. Do NOT use it expecting isolation. If you truly need the tool against `:99`, a second Hermes gateway would have to run with `DISPLAY=:99`; `vdesk` is the cheaper path.
- Never set `DISPLAY=:0` in an automation command. The whole point is that `:0` is the user's.
- Screenshots of `:99` may be black until an app maps a window; that is not a failure.
- `xdotool type` sends keys to the focused window; click the target first if focus is unclear.
