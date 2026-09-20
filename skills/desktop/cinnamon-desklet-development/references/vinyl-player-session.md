# Vinyl Record Player Desklet — Session Notes (2026-09-04)

Concrete implementation of a Cinnamon vinyl record player desklet with spinning record, tonearm, and MPRIS integration.

## UUID

`vinyl-player@AttilaHuns288452`

## What Was Built

- 200x200px desklet with spinning vinyl record
- Wood platter, black vinyl with grooves, center label, spindle, tonearm
- Play/Pause toggle on click
- 33/45 RPM speed selection via popup menu
- Color customization: font, platter, record, label colors
- Dark/Light/Custom scheme presets

## Key Technical Decisions

### Color Handling

**Problem**: `color-mix()` in CSS doesn't work in Clutter's CSS parser (GTK3-era). Color changes via CSS variables silently fail.

**Solution**: Derive gradient stops arithmetically in JavaScript:

```javascript
function shade(hex, t, towardWhite) {
    const c = hex.replace('#', '');
    const r = parseInt(c.substr(0, 2), 16);
    const g = parseInt(c.substr(2, 2), 16);
    const b = parseInt(c.substr(4, 2), 16);
    const w = towardWhite ? 255 : 0;
    return St.Color.to_string(St.Color.new_rgba(
        Math.round(r + (w - r) * f),
        Math.round(g + (w - g) * f),
        Math.round(b + (w - b) * f),
        1.0
    ));
}
```

Apply colors directly via `actor.set_style()` on each element — never rely on CSS color functions.

### Settings Location

**Problem**: `settings-schema.json` is a GSettings artifact that Cinnamon ignores for desklets.

**Solution**: Define settings in `metadata.json` (the `settings` array). Cinnamon reads this file.

### Rotation

- Use `rotation_angle_z` property for 2D rotation
- Set `set_pivot_point(0, 0.5)` for tonearm rotation
- Record and label rotate together; angle computed from elapsed time and RPM

### Imports

```javascript
const PopupMenu = imports.ui.popupMenu;  // NOT Cinnamon.PopupMenu
const Clutter = imports.gi.Clutter;
```

## Submission

PR opened: https://github.com/linuxmint/cinnamon-spices-desklets/pull/1900

## Files

```
vinyl-player@AttilaHuns288452/
├── info.json
├── screenshot.png
├── README.md
├── files/
│   └── vinyl-player@AttilaHuns288452/
│       ├── metadata.json
│       ├── desklet.js
│       ├── stylesheet.css
│       └── icon.png
```
