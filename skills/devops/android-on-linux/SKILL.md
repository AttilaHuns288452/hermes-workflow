---
name: android-on-linux
description: Use when installing Android games or mods on Linux.
---

# Android games & mods on Linux

A mobile-only Android game (or a mod for one) must end up running on the Linux desktop.
Three phases: acquire the files, stand up an Android runtime, install per the mod's own
mechanics. The READ-ME that ships with a mod is the source of truth for phase 3 — fan
mods routinely deviate from normal install flows (bundle swaps, offline launches, file
renames). Never plan the install from the store page description alone.

## 1. Acquire the files

- Store pages (Game Jolt, itch) are JS SPAs: `curl` returns a shell with no download
  links, and headless Playwright clicks on their Download buttons silently do nothing —
  no modal, no network request, no download. Do not iterate on the button. Find the
  author's own install tutorial video (linked from the mod page or via search) and read
  its description, which usually carries the real file host (Google Drive, MediaFire):
  `curl -A "<browser UA>" "https://www.youtube.com/watch?v=<id>"` then
  `grep -oE '"shortDescription":"[^"]{0,3000}'`.
- Google Drive folder: `curl` the folder page and grep filenames to see contents. When
  per-file IDs don't sit next to names in the embedded blob, probe candidate IDs with
  `https://drive.usercontent.google.com/download?id=<id>&export=download` and identify
  each hit by `file` type/size. Files over the malware-scan threshold return an HTML
  confirmation form: extract `name="confirm" value=` and `name="uuid" value=` and
  re-request with `&confirm=<t>&uuid=<u>`.
- Play-Store-only titles (no direct file host): confirm the listing first
  (`curl -A "<browser UA>" "https://play.google.com/store/apps/details?id=<pkg>"` —
  HTTP 200 with the app name means Play inside the runtime is the install path) and
  don't grind on APK mirrors (apkpure/apkcombo/uptodown are bot-walled with 403s and JS
  gates). Google sign-in is the user's own action — never handle their credentials.
- Extract and read the shipped READ-ME (and any helper files the manual references)
  before staging anything. Archive top-level layout often encodes the install (wrapper
  folder vs. bare content) — compare against the vanilla game's on-device directory
  layout before copying, never normalize paths.

## 2. Android runtime (root required)

- Probe before planning: `lsmod | grep binder`, module presence under
  `/lib/modules/$(uname -r)/`, `id` groups (sudo/docker/kvm),
  `command -v pkexec qemu-system-x86_64`, `/dev/dri/*` GPUs, and whether the Waydroid
  apt repo is reachable.
- Root delivery from the agent terminal is the fragile step. `sudo -n` needs a password;
  pkexec's polkit dialog does NOT reliably reach the user (an unseen auth agent can
  swallow the request — it dies as "Request dismissed", and a background-launched pkexec
  is killed at the launcher's timeout with the same symptom). Working pattern: write ONE
  idempotent setup script to /tmp and have the user run
  `sudo bash /tmp/<script>.sh 2>&1 | tee /tmp/<log>` in their own terminal, then monitor
  the log. Never background or poll an interactive auth flow; offer SUDO_PASSWORD in
  ~/.hermes/.env only as an opt-in alternative.
- Waydroid is the Linux-native runtime (LXC container). Script contents, in order:
  `modprobe binder_linux` and persist via /etc/modules-load.d; add the Waydroid apt repo
  keyed to `${UBUNTU_CODENAME:-$VERSION_CODENAME}` from /etc/os-release (Mint reports its
  own codename and the repo rejects it — use the Ubuntu base codename); `waydroid init
  -s GAPPS -f`; `systemctl enable --now waydroid-container`.
- ARM-only APKs need a translation layer on x86_64 via casualsnek/waydroid_script. Its
  CLI is subcommand-based: `main.py -a 11 install libhoudini` (Intel CPUs) or
  `install libndk_translation` (AMD) — the token goes AFTER `install`; `-i` is not a
  valid flag and argparse rejects it. Script deps (InquirerPy etc.) must live in a
  dedicated venv because Hermes's pip is shadowed: `uv venv ~/waydroid-venv`,
  `uv pip install -r /opt/waydroid_script/requirements.txt`, then run main.py as
  `sudo ~/waydroid-venv/bin/python ...`. Re-run after every `waydroid init` (image
  re-download wipes it).
- UI on an X11 session: nested weston with an explicit socket, then session and UI
  pointed at that socket:
  `weston -Bx11-backend.so --width=1280 --height=720 --socket=wayland-altrox` (background),
  `XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-altrox waydroid session start`,
  then `show-full-ui` with the same env. If show-full-ui exits silently with no window,
  `waydroid session stop` and start it again (the session grabs the compositor socket at
  start time). A blank window needs `references/waydroid-x11-bringup.md` before any
  GPU/rendering theory — the cause is usually a lock screen.

## 3. Install per the mod's mechanics

Copy mod files exactly where the manual says. For PvZ Heroes bundle-replacement mods see
`references/pvzh-mod-install.md`.

## 4. Verification gate

Prove the game reaches its main menu from the Android UI (screenshot), not just that
files copied. Execute per-mod launch quirks (e.g. offline first launch) before the
screenshot counts as proof. Agent-side capture without root: `gnome-screenshot -f` a
full-desktop PNG, get the Android window rect from `wmctrl -lG`, crop that rect with
PIL, and vision-check the CROP (vision misreads full-desktop shots — sidebars and docks
get described instead of the window). Crop pixel mean/variance is a free "did anything
render / did the screen change" check before spending a vision call. Full recipe:
`references/waydroid-x11-bringup.md`.

## Pitfalls

- `pkill -f <pattern>` self-matches the agent terminal's wrapper shell (its argv contains
  the whole command text) and SIGTERMs your own call. Use `pkill -x <procname>` or
  `pgrep` + explicit PID.
- Online first launch can make the game re-download vanilla data over the mod files;
  offline-launch rules in a mod's manual are load-bearing, not superstition.
- A mod's install flow changes between versions — re-read the shipped READ-ME per
  version instead of reusing the previous version's steps.
- A blank nested-compositor window is usually that compositor's own idle lock screen
  (weston: gray wallpaper + "Unlock your desktop" drag knob), not a rendering failure —
  the locker covers live surfaces so the screenshot looks black. Drag the knob right
  before touching GPU/dmabuf diagnosis.
- `waydroid shell`/`waydroid logcat` need root and fail SILENTLY when their output is
  piped (the error line gets eaten) — the trailing "Use '--details-to-stdout'" hint is
  the tell. `waydroid log` follows forever; always bound it with `timeout`.