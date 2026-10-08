---
name: linux-gui-automation
description: Use when a Linux GUI has no CLI/API. Drive with xdotool.
---

# Linux GUI Automation (xdotool + verified clicks)

When no CLI or API exists (desktop-app extension menus, installers, IDE
dialogs), drive the X11 GUI with xdotool and PROVE every click landed. The
governing rule: **click coordinates come from pixels in the image; state
readings come from vision.** Never the reverse.

## Procedure

1. Find the target window: `xdotool search --name '<title fragment>'`; get its
   screen origin with `xdotool getwindowgeometry` (Position = window origin).
2. Capture with `gnome-screenshot -f /tmp/x.png` (full 1920x1080 = 1:1 pixel
   mapping). Get click coordinates DETERMINISTICALLY: PIL crop → grayscale →
   dark-pixel count per row/column to locate text rows, button edges, menu
   items.
3. Click, then verify BEFORE the next action: fresh screenshot + read the
   GUI's own state change (new window title, changed button label, appeared
   panel). Silence is not success — a missing error is not a click.
4. Convert crop coordinates to screen coordinates: add the window origin from
   step 1. Menu/dialog clicks always use screen coordinates.

## Pitfalls

- `xdotool type` swallows every remaining argument in the chain
  (`type text key Return` types nothing and eats "text"): run
  `xdotool type '…'` and `xdotool key Return` as separate invocations.
- Vision models downscale full screenshots and transpose rows in dense
  tabular UIs — unreliable for coordinates. Use vision to answer "what is on
  screen" and pixel scans to answer "where do I click".
- Transient windows (menus, file dialogs) close on the next click elsewhere —
  capture the screenshot while they are open, and finish one dialog before
  touching another window.
- Crop offsets from a PREVIOUS screenshot go stale the moment a window moves —
  re-read geometry before every crop-based vision call.
- A locked screensaver silently eats clicks. On Cinnamon:
  `cinnamon-screensaver-command -d` unlocks without a password.

## App-extension bridges (GUI-only integrations)

When a desktop app's functionality is exposed through a GUI-loaded extension
(e.g. Packet Tracer's MCP-BUILDER module bridging to a local MCP server), the
integration has GUI-only lifecycle rules:

- Extension registration is persisted **only on a clean app exit**. A crash or
  session kill drops it — after any unclean shutdown, verify the extension is
  still registered/loadable BEFORE debugging the server side. Re-adding goes
  through the app's own extension/script-module dialog; file-picker "Open"
  buttons often grey out until a full path is TYPED into the name field
  (clicking the file's icon in the list may not resolve it).
- Extension→server connection runs on a **~30-60s retry loop**. "Not
  connected" in the first minute is NORMAL: retry the status call before
  rebuilding anything, and hold the server process alive long enough for one
  retry (a 1-second probe is too short to ever see the connection).
- The extension latches onto **one** bridge at a time. With several server
  processes alive (multiple agent sessions), status through a different
  process reports disconnected even when the app is fine — close stale
  sessions and test through the one in use.
- The extension's control-center window changes the transport (HTTP while
  open, file-based when closed) — its menu entry often appears only while the
  module runs.

## Verify

Final state must be read from the GUI's own indicator (window title, status
line, visible result) via screenshot + vision — not from the automation
script's output or the absence of errors.
