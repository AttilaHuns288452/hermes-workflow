# Linux Mint Cinnamon Theming Reference

## Observed working pass

A Linux Mint 22.3 Cinnamon session on a 1920x1080, 144 Hz display started with:

- GTK theme: `Mint-Y-Dark-Blue`
- Icon theme: `Mint-L-Blue`
- Cursor theme: `Bibata-Modern-Classic`
- Window-manager theme: `Mint-Y`
- Cinnamon theme: `Mint-Y-Dark-Aqua`
- Panel: `['1:40']` at the bottom
- Wallpaper: `/usr/share/backgrounds/linuxmint-wallpapers/jpanchal_cpu.jpg`

Installed alternatives included `Mint-Y-Dark-Blue`, `Papirus-Dark`,
`Bibata-Modern-Ice`, and `/usr/share/backgrounds/linuxmint-wallpapers/theftiba_blue.jpg`.

## Known-good minimal profile

The following per-user values were applied successfully through `terminal`:

```text
gsettings set org.cinnamon.desktop.interface gtk-theme 'Mint-Y-Dark-Blue'
gsettings set org.cinnamon.desktop.interface icon-theme 'Papirus-Dark'
gsettings set org.cinnamon.desktop.interface cursor-theme 'Bibata-Modern-Ice'
gsettings set org.cinnamon.desktop.wm.preferences theme 'Mint-Y-Dark-Blue'
gsettings set org.cinnamon.theme name 'Mint-Y-Dark-Blue'
gsettings set org.cinnamon panels-height "['1:36']"
gsettings set org.cinnamon.desktop.background picture-uri 'file:///usr/share/backgrounds/linuxmint-wallpapers/theftiba_blue.jpg'
```

Readback matched each intended value. The workflow did not require root access,
package installation, or edits to system-owned theme files.

## Reuse notes

- Inspect the current values and installed names first; this profile is an
  example, not a universal default.
- Keep GTK, Cinnamon, and window-manager themes in the same family.
- Use `gsettings list-keys` before adding a key not present in the current schema.
- Capture the desktop after the change when visual QA matters, but use exact
  `gsettings get` readback to verify configuration state.
