# Luxury Vinyl Desklet — Implementation Reference

Complete working example of a Cinnamon desklet combining Cairo drawing,
Clutter animation, MPRIS D-Bus integration, and settings binding.

## Overview

The Luxury Vinyl desklet (`luxury-vinyl@attila`) renders a realistic black
vinyl record that spins when music plays. It detects MPRIS-compatible media
players (Spotify, VLC, Firefox, etc.) via D-Bus and responds to playback
state changes.

**Location:** `~/.local/share/cinnamon/desklets/luxury-vinyl@attila/`

## Key Implementation Details

### Cairo Drawing (Realistic Vinyl)

The record is drawn on a `Clutter.Canvas` with these layers (back to front):

1. **Outer glow** — subtle gold radial gradient (rgba 0.79, 0.66, 0.3)
2. **Record body** — dark radial gradient (#1e1e1e → #050505)
3. **Grooves** — concentric circles with increasing alpha (0.025 → 0.06)
4. **Center label** — dark gold-brown radial gradient
5. **Gold rings** — outer and inner label rings
6. **Spindle hole** — tiny black circle with highlight
7. **Reflection** — top-left white radial gradient (alpha 0.035)
8. **Outer edge** — subtle gray stroke

```javascript
// Key Cairo pattern for GJS compatibility:
const grad = new Cairo.RadialGradient(x0, y0, r0, x1, y1, r1);
grad.addColorStopRGBA(0, 0.12, 0.12, 0.12, 1);  // float values, NOT hex
ctx.setSource(grad);
ctx.arc(cx, cy, radius, 0, 2 * Math.PI);
ctx.fill();
```

### MPRIS Player Detection

Uses `NameOwnerChanged` D-Bus signal to detect players starting/stopping:

```javascript
this._nameWatcherId = Gio.DBus.session.signal_subscribe(
    "org.freedesktop.DBus",
    "org.freedesktop.DBus",
    "NameOwnerChanged",
    "/org/freedesktop/DBus",
    null,
    Gio.DBusSignalFlags.NONE,
    (connection, sender, object, iface, signal, params) => {
        const name = params.get_child_value(0).get_string()[0];
        if (name.startsWith("org.mpris.MediaPlayer2.")) {
            this._findPlayer();
        }
    }
);
```

### Smooth Rotation Animation

```javascript
_startAnimationLoop() {
    const frameInterval = 33; // ~30 FPS
    this._animationTimeout = GLib.timeout_add(GLib.PRIORITY_DEFAULT, frameInterval, () => {
        if (this._isPlaying) {
            this._rotationAngle += 0.4 * this._rotationSpeed;
            if (this._rotationAngle >= 360) {
                this._rotationAngle -= 360;
            }
            this._vinylActor.set_rotation_angle(Clutter.RotateAxis.Z_AXIS, this._rotationAngle);
        }
        return GLib.SOURCE_CONTINUE;
    });
}
```

### Settings Binding with Guard

The desklet uses Pattern B (guard callback) because settings are bound
before UI construction:

```javascript
_setupSettings() {
    this.settings = new Settings.DeskletSettings(this, UUID, this.instance_id);
    this.settings.bind('record-size', 'recordSize', this._onSettingsChanged);
    // ... more bindings
}

_onSettingsChanged() {
    if (!this._vinylCanvas) return;  // guard: UI not built yet
    // ... apply changes
}
```

### Volume Control via Scroll

```javascript
_onScroll(event) {
    const direction = event.get_scroll_direction();
    let delta = (direction === Clutter.ScrollDirection.UP) ? 0.05 : -0.05;
    // Get current volume, clamp to [0,1], set new volume
    Gio.DBus.session.call(
        this._playerName, MPRIS_PATH, DBUS_PROP_IFACE, "Set",
        new GLib.Variant("(ssv)", [MPRIS_IFACE, "Volume", new GLib.Variant("d", newVol)]),
        null, Gio.DBusCallFlags.NONE, -1, null, null
    );
}
```

## Lessons Learned

1. **Cairo colors in GJS** — Must use `addColorStopRGBA()` with float 0.0–1.0 values. Hex strings and CSS `rgba()` strings do NOT work.

2. **Settings bind fires immediately** — `settings.bind()` calls the callback right away. Either build UI first, or guard the callback with `if (!this._actor) return;`.

3. **MPRIS player detection** — Subscribe to `NameOwnerChanged` on the session bus. Players come and go; always handle disconnection gracefully.

4. **Clutter rotation** — Use `set_pivot_point(0.5, 0.5)` for center rotation. Wrap angle at 360 to prevent float overflow.

5. **D-Bus cleanup** — Always unsubscribe signals in `on_desklet_removed`. Leaked signals cause errors when desklet is removed.

6. **Syntax checking** — `node --check desklet.js` catches basic syntax errors but NOT GJS-specific API issues. Runtime testing requires Cinnamon.

## File Structure

```
luxury-vinyl@attila/
├── desklet.js           # Main implementation (589 lines)
├── metadata.json        # UUID, name, description
├── settings-schema.json # Size, speed, track info, colors
├── stylesheet.css       # Label styles
└── README.md            # Install/uninstall
```

## Settings Schema

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| record-size | spinbutton | 300 | Record diameter (100–800px) |
| rotation-speed | scale | 1.0 | Speed multiplier (0.1–3.0×) |
| show-track-info | switch | true | Show track label |
| track-info-font-size | spinbutton | 11 | Label font size (8–20px) |
| track-info-color | colorchooser | #c9a84c | Label text color |
| track-info-bg-color | colorchooser | #1a1a1a | Label background |

## Interaction

| Action | Behavior |
|--------|----------|
| Left click | Play/Pause |
| Mouse wheel up | Volume +5% |
| Mouse wheel down | Volume -5% |
| Hover | Reveal prev/next controls |
| Leave | Hide controls |

## Debugging

- Check `~/.xsession-errors` for runtime errors
- Restart Cinnamon: `Alt+F2` → `r` → Enter
- Enable via Desklets settings UI (don't manually edit `enabled-desklets`)
