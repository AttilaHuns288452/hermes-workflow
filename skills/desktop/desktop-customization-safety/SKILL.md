---
name: desktop-customization-safety
description: Use when changing a desktop. Preserve user-owned state.
version: 1.0.0
author: Hermes curator
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [desktop, customization, safety, preservation, cinnamon, gsettings]
    related_skills: [linux-mint-customization]
---

# Desktop Customization Safety

Safely customize an existing desktop without destroying user-arranged objects,
visibility preferences, or working-session state. This is a preservation layer
for theme, icon, wallpaper, panel, widget, desklet, extension, and mode-switch
work. It complements platform-specific customization skills; it does not
replace them.

## Core rule

A desktop customization is not allowed to silently convert a user's existing
layout into a clean slate. Preserve first, change only what was requested, and
verify the preserved state afterward.

User-owned desktop objects include, at minimum:

- desklets, widgets, applets, panels, docks, launchers, and pinned items;
- desktop icon visibility and placement;
- wallpaper identity and per-mode fallback choices;
- theme, icon, cursor, font, and accessibility settings not named for change;
- open applications and unsaved work.

A request for a new visual style does not authorize removing or resetting any
of these objects. “Clean,” “minimal,” or “premium” describes appearance, not
permission to delete state.

## Workflow

### 1. Identify the target and scope

Confirm the desktop environment and session before writing settings. Identify
whether the requested change is a theme, icon set, wallpaper, panel, widget,
or mode-controller change. Separate requested changes from existing state that
must survive.

For Linux Mint Cinnamon, inspect the relevant schemas with `gsettings list-keys`
and confirm a graphical session. For another desktop, use its native settings
interface or configuration store; do not assume Cinnamon keys apply elsewhere.

### 2. Snapshot before any write

Record every setting that could be affected, including array-valued settings.
At minimum, snapshot:

- theme, GTK/window theme, icon theme, cursor, fonts, panel dimensions;
- wallpaper URI and rendering options;
- desklet/widget/applet/extension lists;
- desktop icon visibility and volume/network/computer preferences;
- mode-controller state files if a script will switch identities.

A snapshot must contain the exact serialized value, not a paraphrase. If the
value cannot be read, stop before changing it.

### 3. Apply the smallest reversible change

Use per-user settings and existing installed assets first. Do not use `sudo`,
modify `/usr/share`, install unrelated packages, overwrite a user theme, or
pipe downloaded code into a shell merely to change appearance. Do not clear a
list to simplify a transition. Do not add Home, Trash, docks, widgets, or
launchers unless explicitly requested.

Mode controllers must be idempotent: switching Finance/Space or light/dark
must not mutate unrelated desktop state. A controller should set only its own
identity keys and leave user-owned object lists alone.

### 4. Preserve explicit user invariants

For this user, Cinnamon desklets are protected state:

- never write `org.cinnamon enabled-desklets=[]`;
- never replace the enabled desklet list during theme, wallpaper, or icon work;
- preserve the exact list and positions from the pre-change snapshot;
- keep Nemo Home and Trash desktop icons hidden with
  `org.nemo.desktop home-icon-visible=false` and
  `org.nemo.desktop trash-icon-visible=false`.

If a prior operation already changed these values, restore the exact snapshot or
a verified prior value. Never guess a replacement list or turn on Home/Trash to
make a desktop look complete.

The recovered Cinnamon-specific details for this user's setup are in
`references/cinnamon-state-preservation.md`.

### 5. Read back every changed and protected key

A successful setter only proves that a command ran. Read each changed key back,
then read the protected desklet and desktop-icon keys again. A minimum Cinnamon
check is:

```bash
gsettings get org.cinnamon enabled-desklets
gsettings get org.nemo.desktop home-icon-visible
gsettings get org.nemo.desktop trash-icon-visible
```

Compare the desklet value byte-for-byte with the snapshot where practical. If a
mode switch changes it, treat that as a regression and fix the controller before
continuing.

### 6. Verify visually without disrupting work

Capture the desktop after a visual change when practical. Confirm that:

- the requested theme/icon/wallpaper change is visible;
- preserved desklets remain visible;
- Home and Trash remain absent when requested;
- no new desktop icons, panels, or widgets appeared;
- open applications and unsaved work were not closed or interrupted.

Do not force a logout, Cinnamon restart, or application closure for cosmetic
refreshing. Suggest a safe reload only when the user can protect unsaved work;
use it only after the configuration readback is correct.

## Recovery procedure

If a customization accidentally clears or changes protected state:

1. stop further theme/mode changes;
2. read the current values and compare them with the snapshot;
3. restore the exact snapshot using the native settings tool;
4. read back every restored key;
5. perform a non-destructive visual capture;
6. remove the destructive write from the controller so the regression cannot
   recur.

If no snapshot exists, search reliable local history or a configuration backup
for the exact prior value. Do not infer a desklet list from installed packages:
installed is not the same as enabled, and positions are user state.

## Pitfalls

- “Disable all extra widgets” is not a safe default on an existing desktop.
- `enabled-desklets=[]` is destructive even if the desklet packages remain
  installed; package presence does not restore placement or enablement.
- Setting `home-icon-visible=true` or `trash-icon-visible=true` for a themed
  desktop violates the user's explicit preference.
- Theme/icon changes can be correct in GSettings while stale application windows
  still show old assets; verify without closing work.
- A mode script that reapplies a full profile on every switch can accidentally
  reset unrelated arrays. Keep profile writes narrowly scoped.
- A visual screenshot is evidence of appearance, not a substitute for reading
  back serialized settings.

## Completion checklist

- [ ] Target desktop/session identified.
- [ ] Pre-change values snapshotted exactly.
- [ ] Requested scope separated from protected user state.
- [ ] Only per-user, reversible changes made.
- [ ] Desklet/widget/applet lists preserved.
- [ ] Home/Trash visibility matches the user's preference.
- [ ] Every changed and protected key read back.
- [ ] Visual capture attempted when appearance matters.
- [ ] No forced restart, package install, root command, or unsaved-work risk.
