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
   mapping); if that binary is absent, `ffmpeg -loglevel error -f x11grab
   -video_size 1920x1080 -i :0 -frames:v 1 -y /tmp/x.png` gives the same
   1:1 root grab with no extra package. Get click coordinates DETERMINISTICALLY: PIL crop → grayscale →
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
- **Prefer the app's keyboard accelerator over a menu-item coordinate, because
  menus GROW.** A menu whose item list gains rows as the document gains state
  (a "Save with Notes" entry appearing once a file has been published, a
  "Recent" submenu appearing after first use) shifts every item below the
  insertion point: the coordinate that hit "Publish" yesterday lands on the
  row beneath it today and opens an unrelated modal. Use the documented
  accelerator (`Alt+P`) and treat the click path as a last resort; when an
  accelerator then appears to do nothing, look for a modal over the window
  first (Escape) — a stray dialog from a previous mis-click silently eats
  every keystroke.
- **For a Wine/flatpak window, `xdotool getwindowpid` returns the IN-SANDBOX
  (Windows) pid, not a host pid.** Feeding it to `kill` fails or targets
  nothing, so you cannot map "which of these two identical windows belongs to
  which process" that way. Identify instances by something the app itself
  reports (a title suffix, a client/instance id in its own status panel) and
  act on that, not on the X11 pid.
- Crop offsets from a PREVIOUS screenshot go stale the moment a window moves —
  re-read geometry before every crop-based vision call. Window ids from
  `xdotool search` go stale the same way: a closed window's id can linger and
  `getwindowgeometry`/`windowactivate` then fail with BadWindow or hand you
  garbage coordinates — loop over all search hits and keep the first id whose
  `getwindowgeometry` succeeds.
- The user's own foreground work owns the desktop. When their app covers your
  target window, screenshots show THEIR app, not a broken target, and synthetic
  clicks risk landing in their dialogs. Do not fight for focus mid-task: verify
  through the target's own logs/state files, and hand the final click to the
  user with the exact button named. A MODAL in another app (dialog, popover,
  composer popup) holds keyboard focus even after `wmctrl -ia <target>` reports
  success — before ANY keystroke sequence, assert
  `xdotool getactivewindow getwindowname` matches the TARGET WINDOW's name (a
  foreign modal like "Add context" or "Open File" will be the active window
  instead) and re-assert after every step that can open or close a dialog.
- Coordinates reported by a cropped vision call are RELATIVE TO THE CROP ORIGIN,
  not the full screenshot — clicking them unshifted silently hits the wrong
  element (a miss just selects nothing). Add the crop origin to every
  vision-reported coordinate before `xdotool click`, and verify the click by
  re-capturing and reading the changed state.
- Never batch the screenshot write and the vision call reading that same file in
  one tool turn: the analyzer can read the previous image and report phantom
  defects against already-fixed code. Capture, then analyze in a later turn,
  then act.
- A fullscreen or always-raising app in the background STEALS focus on a plain `mousemove`, so the
  subsequent `click` lands on the wrong window and the screenshot shows that app instead of your
  target. Two fixes, both validated: (a) chain `xdotool windowactivate --sync <W> mousemove --sync X Y
  click 1` in ONE invocation with no sleep between move and click — an atomic chain lands the click
  before the background app can raise; and (b) for persistent stacking while you work, `wmctrl -i -r
  <W> -b add,above`, then remove it when done. A separate move → sleep → click is what loses the
  click to the background app.
- **Chain the VERIFICATION CAPTURE into that same invocation.** The agent's own host app is itself a
  fullscreen window that reclaims focus between tool calls, so a click that landed perfectly in call N
  is invisible by call N+1 — and a menu opened in call N has already closed. `windowmap → windowraise →
  windowactivate --sync → click → ffmpeg grab` in ONE command is the only sequence whose screenshot
  actually contains the effect of the click; splitting the capture into its own call yields a picture of
  the host app and reads as "the click missed", sending you into coordinate debugging that was never wrong.
- `gnome-screenshot -w` (window capture) renders GL/composited windows as a
  solid black frame while the app displays fine — always capture the full
  screen and crop to the window geometry (step 2); a black crop means wrong
  capture mode, not a broken app.
- A locked screensaver silently eats clicks AND corrupts captures: full-desktop
  screenshots show the lock-screen wallpaper with a clock, and vision then
  answers "this is not the expected page / wrong image was attached" — a misread
  that sends you debugging capture tooling or distrusting vision. Worse,
  `xdotool type`/`key` are NOT eaten: they land in the lock screen's PASSWORD
  FIELD and submit on Return, polluting a credential input. Check lock state
  BEFORE sending any keystrokes, not just clicks. Diagnosis order before
  touching tooling: `cinnamon-screensaver-command --query` (lock
  state) → `xdotool getactivewindow` vs the target → workspace check.
  `xdotool windowactivate` reports success while the locker still owns the
  screen, so activation output is not screen state. On Cinnamon:
  `cinnamon-screensaver-command -d` unlocks without a password.
- **`windowactivate` reports success on an ICONIFIED window while the screen
  still shows another app.** `xdotool getactivewindow` then returns your target
  id, so any "did it focus?" check passes, yet every click and capture still
  hits whatever is actually painted. Map it first: `xdotool windowmap <W> &&
  xdotool windowraise <W> && xdotool windowactivate --sync <W>`, then confirm
  with a capture — not with `getactivewindow`.
- **Normalize window geometry before trusting ANY coordinate.** Screenshot pixel
  coordinates only equal screen coordinates when the window is at 0,0 and
  unmoved since capture; a window sitting at an offset (or restored after being
  maximized) makes a remembered coordinate miss by exactly that offset and
  clicks land on whatever occupies those screen pixels. Either re-read
  `getwindowgeometry` and add the origin, or force the simple case with
  `xdotool windowsize <W> <screenW> <screenH> && xdotool windowmove <W> 0 0` so
  image space == screen space for the rest of the task.
- `pkill -f` regex-matches every process's FULL command line — including the shell running your own command. Bracket-guarding the pattern only protects the pattern text itself; any SIBLING argument containing the plain target word (`grep ... vinegar` next to `pkill -f 'vinega[r]'`) still self-matches and SIGKILLs the whole call mid-run. Make every occurrence in the command line bracket-guarded, or split kill and verify into separate calls; a self-killed call may have half-executed its earlier statements, so re-probe actual state before trusting either outcome.
- X keysym names are case-sensitive and a misspelled one fails SILENTLY:
  `xdotool key enter` prints "No such key name" and exits 0, so a chained
  command continues as if the key were sent. Use `Return`, `Escape`, `space`,
  `Tab`, and grep every `xdotool key` output for "Ignoring it" before trusting
  the keystroke.
- A browser window's X11 WM title is its ACTIVE TAB's title, so
  `xdotool search --name '<text from a background tab>'` finds nothing. List
  windows first (`xdotool search --onlyvisible --name '.*' getwindowname %@`),
  target the browser by pid/app, and switch tabs inside it before sending keys.
- A "…"/kebab button does not always open a popup menu — some expand sections in place below the row. After clicking, inventory what appeared ANYWHERE in the panel (fresh screenshot + vision listing all visible items), not just near the click; searching only around the click point reads "no menu opened" and sends you re-clicking a control that already worked.
- When the UI has no pixel-scannable label (icon-only buttons, toggles) and you must use vision-reported coordinates: ask explicitly for ORIGINAL full-screenshot pixel coordinates, click, verify the intended control CHANGED STATE, and on a miss re-ask with the FRESH screenshot — the first answer is often off by tens of pixels on small controls, and nudging guessed offsets hits the neighbor instead.
- A click-through of an app's settings UI is NOT read-only: opening a settings
  page can push its stored state to hardware, and a navigation click can land
  on a toggle when coordinates shift between pages. When the app has a
  daemon/socket/config control channel, read and set state there (see
  `linux-hardware-troubleshooting` for socket probing); if you must click
  through, capture the state before and normalize it after.
- **Never `xdotool windowkill` a child window of an app you care about.** It
  does not close the dialog; it destroys the resource, and the parent process
  can go down with it — losing unsaved work. Close dialogs by clicking their
  own Cancel/close control, or with `Escape` sent to that window.
- **`getactivewindow` naming the right window does not mean no modal exists.**
  An app can own several X windows at once, and a stray one (a shortcuts
  editor, a leftover file picker, a text alert) swallows keystrokes and clicks
  aimed at the main window while the focus check still passes. Enumerate them
  all before blaming coordinates:
  `xdotool search --onlyvisible --name '.' | while read w; do echo "$w $(xdotool getwindowname $w)"; done`
  — an unexpected extra title from the same app IS the bug.
- **When a synthetic click produces no state change, re-derive the target box
  from a FRESH capture instead of nudging the last coordinate.** Guess-and-nudge
  burns turns and lands on neighbouring controls. For a coloured primary
  button, scan the capture for the exact fill colour and click the centre of
  its bounding box; that is self-correcting against window moves that silently
  invalidated every earlier offset.
- **A few sampled pixels are not a UI state test.** Probing "is the centre of
  the screen dark" to decide whether a dialog is open gives false answers both
  ways and sends you debugging the wrong layer. Read a real signal: the window
  list, a title, or the text of the control you changed.

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
