# Cinnamon State Preservation Reference

This reference records the verified recovery detail for the existing Linux Mint
Cinnamon desktop used with the Finance/Space identities.

## Protected preferences

- Keep `org.cinnamon enabled-desklets` unchanged during theme, wallpaper, icon,
  or performance-mode changes.
- Keep `org.nemo.desktop home-icon-visible=false`.
- Keep `org.nemo.desktop trash-icon-visible=false`.
- Do not add Home or Trash desktop icons as part of a visual profile.

## Exact recovered desklet state

The pre-change Cinnamon value recovered from session history was:

```text
['diskspace@schorschii:0:1700:25', 'simple-system-monitor@ariel:5:1325:25', 'yfquotes@thegli:7:1300:325']
```

The entries encode desklet ID, instance ID, and position. Preserve the exact
string from a current snapshot whenever possible; use this value only as the
verified recovery record for this desktop.

The corresponding user desklet packages were present at:

```text
~/.local/share/cinnamon/desklets/diskspace@schorschii
~/.local/share/cinnamon/desklets/simple-system-monitor@ariel
~/.local/share/cinnamon/desklets/yfquotes@thegli
```

## Minimal readback

```bash
gsettings get org.cinnamon enabled-desklets
gsettings get org.nemo.desktop home-icon-visible
gsettings get org.nemo.desktop trash-icon-visible
```

Expected result: the exact desklet list above, followed by `false` and `false`.

## Controller rule

A Finance/Space controller may change theme, icon theme, cursor, wallpaper,
panel styling, and its own performance state. It must not contain a write to
`org.cinnamon enabled-desklets`, and it must not set Nemo Home or Trash to
`true`. Read protected keys after applying any profile.
