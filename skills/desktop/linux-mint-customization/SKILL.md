---
name: linux-mint-customization
description: Use when styling Mint Cinnamon. Apply native settings.
version: 0.1.0
author: Attila, Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [linux, mint, cinnamon, desktop, themes, gsettings]
    related_skills: []
---

# Linux Mint Customization Skill

Apply a coherent, reversible visual refresh to Linux Mint Cinnamon with native
per-user settings first. This skill prefers themes, icons, cursors, wallpapers,
and panel settings already installed; it does not install third-party packages,
run root commands, or edit theme files unless the user explicitly asks.

## When to Use

- The user wants Linux Mint/Cinnamon to look cleaner, more beautiful, themed, or consistent.
- The user asks to change desktop themes, icons, cursor, wallpaper, panel size, or effects.
- A current Cinnamon appearance needs inspection before making a small visual change.
- The user wants fastfetch / neofetch ASCII logo colors to match the current Mint theme.

Don't use for:

- Installing a whole desktop environment or replacing the window manager.
- System-wide package changes when a per-user setting solves the request.
- GUI clicking when a native `gsettings` change is clearer and safer.
- Creating new Cinnamon desklets — use `cinnamon-desklet-development` instead.

## Prerequisites

- Linux Mint with Cinnamon and a live graphical session.
- The `gsettings` command available through `terminal`.
- A user-approved aesthetic direction; if absent, use a restrained dark, neutral,
or blue-accent profile and state the assumption.
- `computer-use` is optional for a post-change desktop capture; it is not needed
for the configuration itself.

## Quick Reference

Inspect current appearance with `terminal`:

```text
terminal(command="gsettings get org.cinnamon.desktop.interface gtk-theme; gsettings get org.cinnamon.desktop.interface icon-theme; gsettings get org.cinnamon.desktop.interface cursor-theme; gsettings get org.cinnamon.desktop.wm.preferences theme; gsettings get org.cinnamon.theme name; gsettings get org.cinnamon panels-height; gsettings get org.cinnamon.desktop.background picture-uri", timeout=30)
```

Apply a minimal dark-blue profile with `terminal` (only after checking that the
named themes and wallpaper exist):

```text
terminal(command="gsettings set org.cinnamon.desktop.interface gtk-theme 'Mint-Y-Dark-Blue'; gsettings set org.cinnamon.desktop.interface icon-theme 'Papirus-Dark'; gsettings set org.cinnamon.desktop.interface cursor-theme 'Bibata-Modern-Ice'; gsettings set org.cinnamon.desktop.wm.preferences theme 'Mint-Y-Dark-Blue'; gsettings set org.cinnamon.theme name 'Mint-Y-Dark-Blue'; gsettings set org.cinnamon panels-height \"['1:36']\"; gsettings set org.cinnamon.desktop.background picture-uri 'file:///usr/share/backgrounds/linuxmint-wallpapers/theftiba_blue.jpg'", timeout=30)
```

Verify every changed key with `gsettings get`; do not infer success from a zero
exit code alone.

## Procedure

1. **Confirm the target desktop.**
   Use `terminal` to read `/etc/os-release`, `XDG_CURRENT_DESKTOP`,
   `DESKTOP_SESSION`, `DISPLAY`, and screen resolution. Completion criterion:
   the result identifies Linux Mint/Cinnamon and a graphical display, or the
   workflow stops with the missing prerequisite named.

2. **Snapshot the current appearance.**
   Read the current GTK theme, icon theme, cursor theme, window-manager theme,
   Cinnamon theme, panel height, wallpaper URI, and wallpaper options with
   `gsettings get`. Completion criterion: every setting that may be changed is
   recorded in the tool output before the first write.

3. **Inventory installed choices.**
   Use `terminal` to enumerate names under `/usr/share/themes`, `/usr/share/icons`,
   user theme/icon directories, and `/usr/share/backgrounds/linuxmint-wallpapers`.
   If a candidate is absent, choose an installed alternative instead of guessing.
   Completion criterion: each requested theme, icon, cursor, and wallpaper has a
   verified installed name or is removed from the change set.

4. **Choose one coherent palette.**
   Match the GTK, window-manager, and Cinnamon theme family; use an icon theme
   that has complete coverage; choose a cursor with adequate contrast; choose a
   wallpaper that supports text readability. Prefer the smallest useful set of
   changes. Completion criterion: the proposed values are listed once and do not
   mix a light widget theme with a dark panel without a deliberate reason.

5. **Apply only per-user settings.**
   Use one `terminal` call containing explicit `gsettings set` commands. Do not
   use `sudo`, edit `/usr/share`, pipe downloaded scripts into a shell, or install
   external themes during the first pass. For array-valued Cinnamon settings,
   preserve the exact GSettings syntax, for example `['1:36']`. Completion
   criterion: the command exits successfully and no system-owned file changed.

6. **Read back every target.**
   Run `gsettings get` for each key written, including the wallpaper URI and panel
   height. Completion criterion: each returned value exactly matches the intended
   value; if any differs, stop and report that key rather than retrying blindly.

7. **Perform a desktop capture when visual QA is useful.**
   Use `computer_use(action="capture", app="desktop", mode="vision")` or `mode="som"`.
   Keep the capture background-first. Completion criterion: a fresh screenshot is
   available, or the tool reports that visual capture is unavailable; the textual
   GSettings readback remains the source of truth for applied values.

8. **Handle stale applications conservatively.**
   Some already-open applications may retain their old GTK appearance. Suggest a
   logout/login only if the user still sees stale styling; never force a session
   restart or close applications as part of the first pass. Completion criterion:
   the user has a reversible next step and no unsaved application work is risked.

## Renderer and Desktop-App Diagnosis

When a user reports that an app is showing or repeating the desktop wallpaper, identify the app before treating it as a wallpaper engine. Inspect its process, X11/Wayland window, package metadata, configuration, and recent logs. A transparent or empty app surface can reveal Cinnamon's wallpaper and look like duplication even when the app is not rendering content.

For wallpaper failures, treat `gsettings set` plus readback as configuration evidence only, not visual proof. A/B test a known-good system wallpaper, then capture the compositor. If the system image renders but the user image does not, try a conventional per-user wallpaper location such as `~/.local/share/backgrounds/`, and synchronize Cinnamon's `picture-uri` with GNOME's `picture-uri` and `picture-uri-dark`; verify the result visually.

For desklet cleanup, setting `org.cinnamon enabled-desklets` to `[]` may not unload already-running actors. Close any open Cinnamon Desklets settings window, reapply the setting, and capture again; only use a normal Cinnamon reload or logout/login if the user approves and unsaved work is safe.

For third-party apps installed through Flatpak, prefer the app's own settings UI and logs over hand-editing JSON. For Sober, verify onboarding/bundle state before diagnosing a renderer: an uncompleted onboarding flow can leave an empty surface over the desktop. If content still fails after onboarding, use the documented graphics-backend fallback from Sober Settings rather than guessing flags.

Visual verification uses the MiMo visual subagent first. If that route is unavailable or blocked, use the current main model as the fallback and label that fallback; an optional visual worker must not stall the task.

## Aesthetic Defaults

- **Dark blue / periwinkle:** `Mint-Y-Dark-Blue` for GTK, window manager, and
  Cinnamon; `Papirus-Dark` icons; `Bibata-Modern-Ice` cursor; a blue wallpaper.
- **Neutral Mint:** keep the current Mint theme family, choose a matching Mint
  icon variant, and change only the wallpaper and panel density.
- **Light clean:** use a light Mint theme and a dark cursor; do not pair a bright
  wallpaper with low-contrast white text.

These are starting points, not mandatory values. Existing installed choices win
against a guessed name.

## Pitfalls

- A downloaded cursor theme (folder with `cursors/` + `index.theme`) installs
  per-user at `~/.icons/<Name>` (dir name matching `Name=` in index.theme),
  then `gsettings set org.cinnamon.desktop.interface cursor-theme '<Name>'`
  with readback. No sudo, no `/usr/share/icons`; some apps adopt it only
  after restart.
- **Special keys the GUI shortcut editor cannot see.** Cinnamon's Settings →
  Keyboard → Shortcuts only binds keys that have a standard X11 keysym. A
  non-standard key (macro key, media-key variant, vendor key) often has no
  keysym, so the shortcut editor ignores it or refuses to record it. When the
  GUI cannot capture the key, do not keep retrying the editor — capture the
  raw X keycode via `xev` (or `evtest` on the keyboard event device) and bind
  it with `xbindkeys` using the `c:<keycode> + m:0x0` syntax. The recipe is
  in `references/non-standard-key-bindings.md`.
- GTK, Cinnamon, window-manager, icon, and cursor settings are separate. Changing
  one does not guarantee a consistent desktop.
- `Mint-L-*` and `Mint-Y-Dark-*` are different families; do not mix them casually.
- The `org.cinnamon.theme` schema may expose fewer keys than other Cinnamon
  schemas. Run `gsettings list-keys <schema>` before using an unfamiliar key.
- Panel height is commonly an array-like string such as `['1:40']`; preserve the
  panel ID when changing it.
- A wallpaper filename being plausible is not proof that it exists. Verify the
  file before setting its URI.
- Do not add a dock, Conky, extensions, or third-party theme repositories merely
  because they are popular. Add them only when the user requests that layer.
- A successful `gsettings set` confirms the command ran, not that the desktop
  visually refreshed. Always read back the key and capture when visual feedback
  matters.
- If a key is missing or a theme is unavailable, adapt from the inventory; do not
  loop the same failing command.
- **Panel applet text color (clock/calendar labels) lives in the theme, not the
  applet.** TextApplets render via `set_applet_label()` with no color of their
  own — the color comes from the theme's `.applet-label` rule in
  `<theme>/cinnamon/cinnamon.css`. To recolor panel text, edit that rule in the
  per-user theme copy (`~/.themes/<Name>/cinnamon/cinnamon.css`, no sudo) and
  reload with `Alt+F2` → `r`. One rule covers every TextApplet at once (stock
  and third-party calendars alike), so prefer it over per-applet styling.
- **Theme sets `#panel { color: #D4AF37; }` (or similar) — your `.applet-label`
  override won't work.** ID specificity (`#panel`) beats class specificity
  (`.applet-label`), so the theme's panel color wins even if you set
  `.applet-label { color: #ffffff; }`. Fix: use a more specific selector:
  `#panel .applet-label { color: #ffffff; }`. Check the theme's `cinnamon.css`
  for `#panel { color: ... }` rules (often near the end of the file in a
  "shell-level" section) and override with `#panel .applet-label` or
  `#panel .applet-box .applet-label` as needed. Same pattern applies to any
  applet text/icon the theme colors at the `#panel` level.

## Verification

A customization pass is complete only when all of these are true:

- The target is a live Linux Mint Cinnamon session.
- The pre-change values were inspected.
- Every selected theme, icon, cursor, and wallpaper exists before use.
- Only the requested per-user settings were changed.
- Every changed key was read back and matches the intended value.
- A fresh desktop capture was attempted when the task is visual.
- No root command, package install, forced restart, or unsaved-work risk was
  introduced without explicit user approval.

Session-specific examples and reusable diagnostics are in
`references/linux-mint-cinnamon-theming.md` and
`references/desktop-renderer-diagnosis.md`.
