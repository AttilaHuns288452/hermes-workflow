---
name: cinnamon-desklet-development
description: Cinnamon xlet development — desklets AND applets (GJS, Cairo, MPRIS, Clutter, PopupMenu).
triggers:
  - desklet
  - cinnamon desklet
  - desktop widget
  - cinnamon widget
  - mpris desklet
  - music visualization desklet
  - applet
  - cinnamon applet
  - panel applet
  - cheatsheet applet
  - reference applet
  - popup menu
  - popupmenu
  - St.ScrollView
  - St.Entry
---

# Cinnamon Xlet Development

Build native Cinnamon desklets AND applets using GJS (GNOME JavaScript),
Cairo for 2D drawing, Clutter for animation, D-Bus for system integration
(MPRIS, notifications), and PopupMenu for panel applets.

## When to Use

- Creating a new Cinnamon desklet from scratch
- Creating a new Cinnamon applet (panel widget) from scratch
- Modifying an existing desklet's or applet's behavior or visuals
- Adding MPRIS media player detection to a desklet/applet
- Implementing custom Cairo drawing (vinyl records, gauges, visualizations)
- Adding Clutter-based animation (rotation, transitions, smooth motion)
- Building reference/cheatsheet applets with search and copy-to-clipboard
- Binding user settings via `Settings.DeskletSettings` or `Settings.AppletSettings`

Don't use for:

- Extensions (shell modifications) — different architecture
- Pure gsettings theming — use `linux-mint-customization` instead
- Converting a desklet to a web widget — different platform
- Feature-rich reference apps (command databases, translators, multi-panel tools) — desklets are too small; use a standalone HTML app instead (see Fallback below)

## Prerequisites

- Linux Mint Cinnamon (any modern version)
- `cinnamon --version` to verify the target version
- Desklets live in `~/.local/share/cinnamon/desklets/<uuid>/`
- UUID format: `name@author` (e.g., `luxury-vinyl@attila`)
- GJS is the JavaScript engine — `node --check` catches syntax errors but NOT GJS-specific API issues

## Applet File Structure

```
~/.local/share/cinnamon/applets/<uuid>/
├── metadata.json          # UUID, name, description, version, author
├── applet.js              # Main implementation (GJS class)
├── settings-schema.json   # User-configurable settings (optional)
├── stylesheet.css         # St widget styles (optional)
├── icon.png OR icon.svg   # Applet icon (SVG supported)
├── refdocs/               # Cheatsheet data (for reference applets)
│   └── <SheetName>/
│       ├── sheet.json     # Sheet data (name, description, sections, items)
│       └── icon.svg       # Sheet icon (optional)
└── README.md              # Install/uninstall instructions
```

### metadata.json (applet)

```json
{
    "uuid": "your-applet@yourname",
    "version": "1.0.0",
    "description": "What it does",
    "name": "Your Applet Name",
    "author": "yourname",
    "last-edited": 1725000000
}
```

### settings-schema.json (applet)

```json
{
    "keyOpen": {
        "type": "keybinding",
        "description": "Open the applet menu",
        "default": ""
    },
    "cheatsheetFolder": {
        "type": "filechooser",
        "description": "Cheatsheet folder",
        "default": "~/.local/share/cinnamon/applets/<uuid>/refdocs",
        "select-dir": true
    },
    "cheatsheets": {
        "type": "generic",
        "default": []
    }
}
```

### sheet.json (cheatsheet data)

```json
{
    "name": "Sheet Name",
    "description": "Sheet description",
    "author": "author",
    "version": "1.0",
    "sections": {
        "Section Name": {
            "Item Name": {
                "description": "What this command does",
                "code": "linux-command",
                "alternatives": {
                    "alt1": { "code": "alt-command-1" },
                    "alt2": { "code": "alt-command-2" }
                }
            }
        }
    }
}
```

## Applet Core Architecture

### The Applet Class (PopupMenu pattern)

Every applet extends `Applet.IconApplet` (icon in panel) or `Applet.TextApplet`:

```javascript
const Applet = imports.ui.applet;
const PopupMenu = imports.ui.popupMenu;
const Settings = imports.ui.settings;
const St = imports.gi.St;
const Main = imports.ui.main;

class MyApplet extends Applet.IconApplet {
    constructor(metadata, orientation, panelHeight, instanceId) {
        super(metadata, orientation, panelHeight, instanceId);
        this.set_applet_icon_path(ICON_PATH);
        this.set_applet_tooltip("Tooltip text");

        this.menuManager = new PopupMenu.PopupMenuManager(this);
        this.menu = new Applet.AppletPopupMenu(this, orientation);
        this.menuManager.addMenu(this.menu);

        // Build UI
        this._buildMenu();
    }

    on_applet_clicked(event) {
        this.menu.toggle();
    }

    on_applet_removed_from_panel() {
        // Cleanup: remove keyborders, destroy actors
        Main.keybindingManager.removeHotKey("hotkey-" + this.instance_id);
    }
}

function main(metadata, orientation, panelHeight, instanceId) {
    return new MyApplet(metadata, orientation, panelHeight, instanceId);
}
```

### Critical: Cinnamon 6.6+ requires `_addStyleClass`

Cinnamon 6.6+ calls `applet._addStyleClass(styleClass)` during load. If missing:
```
[netref@attila]: applet._addStyleClass is not a function
[netref@attila]: Failed to load applet: netref@attila/32
```

**Fix:** Add this method to your applet prototype:
```javascript
NetRef.prototype = {
    __proto__: Applet.IconApplet.prototype,

    _addStyleClass: function(styleClass) {
        this.actor.add_style_class_name(styleClass);
    },
    // ... rest of prototype
};
```

### Keybindings

```javascript
// In _init:
this.settings.bind("keyOpen", "keyOpen", this._setKeybinding);
this._setKeybinding();

// Method:
_setKeybinding: function() {
    Main.keybindingManager.addHotKey("myapplet-show-" + this.instance_id,
        this.keyOpen, Lang.bind(this, this._openMenu));
}

// Cleanup in on_applet_removed_from_panel:
Main.keybindingManager.removeHotKey("myapplet-show-" + this.instance_id);
```

### Copy to Clipboard

```javascript
copyToClipboard: function(text) {
    St.Clipboard.get_default().set_text(St.ClipboardType.CLIPBOARD, text);
    Main.notify('Applet Name', 'Copied: ' + text.substring(0, 40));
}
```

## Searchable List Widget (for Reference/Cheatsheet Applets)

When building a reference applet with search, use this pattern:

```javascript
function SearchableListWidget() {
    this._init.apply(this, arguments);
}

SearchableListWidget.prototype = {
    _init: function(copyCallback) {
        this._copyCallback = copyCallback;
        this._allItems = [];
        this._buildUI();
    },

    _buildUI: function() {
        this.mainBox = new St.BoxLayout({
            vertical: true,
            style: 'min-width: 380px; max-width: 500px;'
        });

        // Search bar (fixed at top)
        this.searchEntry = new St.Entry({
            name: 'searchEntry',
            hint_text: 'Search...',
            track_hover: true,
            can_focus: true,
            style: 'background-color: #1a1a1a; color: #e0e0e0; border: 1px solid #3c3c3c; border-radius: 4px; padding: 6px 10px; font-size: 12px; margin: 6px;'
        });
        this.searchEntry.clutter_text.connect('text-changed', Lang.bind(this, this._onSearchChanged));

        // Scrollable container
        this.scrollView = new St.ScrollView({
            style: 'max-height: 450px;',
            hscrollbar_policy: St.PolicyType.NEVER,
            vscrollbar_policy: St.PolicyType.AUTOMATIC
        });

        this.itemsBox = new St.BoxLayout({
            vertical: true,
            style: 'spacing: 4px; padding: 4px;'
        });
        this.scrollView.add_actor(this.itemsBox);

        this.mainBox.add(this.searchEntry);
        this.mainBox.add(this.scrollView);
    },

    _onSearchChanged: function(entry) {
        let searchText = entry.get_text().toLowerCase().trim();
        this._filterItems(searchText);
    },

    _filterItems: function(searchText) {
        this.itemsBox.destroy_all_children();
        for (let i = 0; i < this._allItems.length; i++) {
            let item = this._allItems[i];
            let matches = !searchText ||
                item.name.toLowerCase().includes(searchText) ||
                item.description.toLowerCase().includes(searchText) ||
                item.code.toLowerCase().includes(searchText);
            if (matches) {
                let menuItem = this._createMenuItem(item);
                this.itemsBox.add(menuItem.actor);
            }
        }
    },

    _createMenuItem: function(item) {
        let menuItem = new PopupMenu.PopupBaseMenuItem();
        menuItem.actor.add_style_class_name("sheet-item");

        let container = new St.BoxLayout({ vertical: true });

        let descLabel = new St.Label({ text: item.description, style_class: 'sheet-item-description' });
        descLabel.get_clutter_text().set_line_wrap(true);
        container.add_actor(descLabel);

        let codeLabel = new St.Label({ text: item.code, style_class: 'sheet-item-code' });
        container.add_actor(codeLabel);

        menuItem.addActor(container);
        menuItem.code = item.code;
        menuItem.connect('activate', Lang.bind(this, function() {
            if (this._copyCallback) this._copyCallback(item.code);
        }));
        return menuItem;
    },

    addItems: function(items) {
        this._allItems = items;
        this._filterItems('');
    },

    getActor: function() { return this.mainBox; }
};
```

### Pitfall: Popup closes when clicking search entry

`St.Entry` in a `PopupMenu.PopupBaseMenuItem` causes the popup to close on click.

**Fix:** Override `activate()` in your SearchMenuItem to prevent close:
```javascript
activate: function(event) {
    // Prevent popup from closing, keep search focused
    this.search_entry.grab_key_focus();
}
```

### Pitfit: Popup relayouts when items are hidden/shown

Using `actor.show()/hide()` causes constant relayout and pushes the search bar.

**Fix:** Use `destroy_all_children()` + re-add matching items instead.

### Pitfall: Max-height without scrollbar

If you don't set `vscrollbar_policy: St.PolicyType.AUTOMATIC`, items overflow invisibly.

**Fix:** Always use:
```javascript
this.scrollView = new St.ScrollView({
    style: 'max-height: 450px;',
    hscrollbar_policy: St.PolicyType.NEVER,
    vscrollbar_policy: St.PolicyType.AUTOMATIC
});
```

## Cheatsheet Applet Pattern (Cheaty-style)

Inspired by the `cheaty@centurix` applet, this pattern loads external cheat sheets from `refdocs/`:

### Architecture

```
OnClick → PopupMenu → SheetMenuItem (submenu) → SectionMenuItem → ItemMenuItem
                                                              ↓
                                                        Click → copyToClipboard()
```

### Key Components

1. **SheetMenuItem** — extends `PopupMenu.PopupSubMenuMenuItem`, loads `sheet.json`
2. **DescriptionMenuItem** — extends `PopupMenu.PopupBaseMenuItem`, stores `code`
3. **copyToClipboard** — triggered on item `activate`, uses `St.Clipboard`

### Loading sheet.json

```javascript
let sheetPath = REFDOCS + '/' + sheetName + '/sheet.json';
let sheetFile = Gio.file_new_for_path(sheetPath);
let [ok, data, etag] = sheetFile.load_contents(null);
if (ok) {
    let contents = JSON.parse(ByteArray.toString(data));
    // contents.sections = { "Section": { "Item": { description, code, alternatives } } }
}
```

### Settings: cheatsheets array

The applet stores which sheets are enabled in settings:
```json
{
    "cheatsheets": [
        { "enabled": true, "name": "Sheet Name", "description": "...", "author": "..." }
    ]
}
```

## Applet Installation & Testing

### Install

```bash
cp -r applet-folder ~/.local/share/cinnamon/applets/
```

Then enable via **Right-click panel → Applets → Add**.

### Debugging

- Cinnamon logs: `~/.xsession-errors`
- Confirm load/failure: `grep -ai <uuid> ~/.xsession-errors`
- Restart Cinnamon: `Alt+F2` → type `r` → Enter
- `node --check applet.js` catches syntax errors (but not GJS API issues)

### Applet Pitfalls

0. **Confirm desklet vs applet before scaffolding** — users say "desklet"
   when they mean panel "applet" and vice versa. One clarifying question
   (desktop widget vs panel widget) saves a full rewrite.

1. **`_addStyleClass` missing** — Cinnamon 6.6+ requires this method or applet won't load
2. **Popup closes on search click** — Override `activate()` to prevent close
3. **Popup relayout on filter** — Use `destroy_all_children()` + re-add, not `show()/hide()`
4. **No scrollbar** — Always set `vscrollbar_policy: St.PolicyType.AUTOMATIC` on ScrollView
5. **Keybinding not cleaned up** — Always `removeHotKey` in `on_applet_removed_from_panel`
6. **Settings not bound before use** — Build UI before binding settings (Pattern A)
7. **Wrong icon path** — Use absolute path, not relative
8. **SVG icon not rendering** — Some Cinnamon versions prefer PNG; test both
9. **Panel too narrow for full data** — two patterns: (a) rotating-TextApplet:
   ONE compact item via `set_applet_label`, rotated on a
   `timeout_add_seconds` timer, full list in the click popup; (b) full-strip:
   ALL items at once via
   `this._applet_label.get_clutter_text().set_markup()` with per-item
   `<span foreground>` colors — auto-resizes as items are added, escape
   user-editable strings (`&<>`) before markup. Timer hygiene: refresh
   reschedules itself, cleanup removes timers plus a fetch-tag guard for
   in-flight callbacks. **Soup to some hosts (Yahoo) fails silently with no
   log error** — don't debug the handshake, fetch via a stdlib python
   subprocess (`Gio.Subprocess` + `communicate_utf8_async`) running code
   already proven live. After edits, remove/re-add the applet (code is
   cached by UUID). See `references/yahoo-ticker-applet-session.md` for the
   full recipe (lightweight Yahoo v8 fetch, markup strip, node
   extract-and-eval tests).

## Fallback: Standalone HTML Application

When the feature set is too large for a desklet (command databases, translators,
multi-panel tools), build a single-file HTML app instead. Zero dependencies,
works offline, launches from a desktop shortcut.

### When to choose HTML over desklet

- More than ~10 entries in a database
- Need search, filtering, comparison views
- Multiple panels (translator + reference + history)
- User needs to copy/paste frequently
- GTK3/Qt not available (check: `python3 -c "import gi"` fails)

### Pattern

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>App Name</title>
<style>
  :root {
    --bg-primary: #1e1e1e;
    --bg-secondary: #252526;
    --bg-card: #2d2d2d;
    --text-primary: #e0e0e0;
    --text-secondary: #a0a0a0;
    --accent: #00bcd4;
    --accent-glow: rgba(0, 188, 212, 0.15);
  }
  /* ... dark theme matching Mint desktop ... */
</style>
</head>
<body>
  <!-- Search bar -->
  <!-- Content cards -->
  <!-- Toast notifications -->
<script>
  // Command database (array of objects)
  // Search/filter logic
  // Copy to clipboard (navigator.clipboard.writeText)
  // localStorage for favorites/history
  // Theme toggle (data-theme attribute)
</script>
</body>
</html>
```

### Desktop shortcut

```ini
# ~/.local/share/appdescriptions/<name>.desktop
[Desktop Entry]
Name=App Name
Exec=xdg-open /home/user/Applications/app.html
Icon=network-wired
Type=Application
Categories=Network;Utility;
```

### Clipboard copy (JavaScript)

```javascript
async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
  } catch (e) {
    // Fallback for older browsers
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  }
}
```

### Theme matching

To match the user's desktop theme:
1. Screenshot the desktop
2. Use vision_analyze to extract colors (panel, accent, text)
3. Apply as CSS variables (`--bg-primary`, `--accent`, etc.)
4. Support both dark/light with `[data-theme="light"]` selector
5. Persist choice in `localStorage`

See `references/html-app-fallback.md` for a complete working example.

## Desklet File Structure

```
~/.local/share/cinnamon/desklets/<uuid>/
├── metadata.json          # UUID, name, description, version, author
├── desklet.js             # Main implementation (GJS class)
├── settings-schema.json   # User-configurable settings (optional)
├── stylesheet.css         # St widget styles (optional)
├── icon.png               # Desklet icon (optional)
└── README.md              # Install/uninstall instructions
```

### metadata.json

```json
{
    "uuid": "your-desklet@yourname",
    "max-instances": 1,
    "name": "Your Desklet Name",
    "description": "What it does",
    "prevent-decorations": true,
    "version": "1.0.0",
    "author": "yourname",
    "last-edited": 1725000000
}
```

- `max-instances`: 1 for single-instance desklets, -1 for unlimited
- `prevent-decorations`: true to remove window borders
- `last-edited`: Unix timestamp

### settings-schema.json

Follow the GSettings schema format. Common types:
- `spinbutton` — numeric input with min/max/step
- `scale` — slider
- `switch` — boolean toggle
- `combobox` — dropdown selection
- `colorchooser` — color picker
- `generic` — hidden internal values (position, state)

Use `dependency` to conditionally enable settings based on a switch.

## Core Architecture

### The Desklet Class

Every desklet extends `Desklet.Desklet`:

```javascript
const Desklet = imports.ui.desklet;
const St = imports.gi.St;
const Clutter = imports.gi.Clutter;
const GLib = imports.gi.GLib;
const Gio = imports.gi.Gio;
const Cairo = imports.cairo;
const Settings = imports.ui.settings;

class MyDesklet extends Desklet.Desklet {
    constructor(metadata, desklet_id) {
        super(metadata, desklet_id);
        this.metadata = metadata;
        this.instance_id = desklet_id;
        
        // Initialize state
        this._setupSettings();
        this._setupUI();
        this._startLoop();
    }
    
    on_desklet_removed(deleteConfig) {
        // Clean up all resources: timeouts, D-Bus signals, actors
        if (this._timeout) {
            GLib.source_remove(this._timeout);
            this._timeout = null;
        }
        // Unsubscribe D-Bus signals
        // Destroy actors
    }
}

function main(metadata, desklet_id) {
    return new MyDesklet(metadata, desklet_id);
}
```

### Critical: Settings Binding Order

`settings.bind()` fires the callback IMMEDIATELY during binding. If your
callback touches UI actors, those actors must exist first. Two patterns:

**Pattern A — Build UI before settings:**
```javascript
this._setupUI();
this._setupSettings();  // callback can safely touch actors
```

**Pattern B — Guard the callback:**
```javascript
_setupSettings() {
    this.settings = new Settings.DeskletSettings(this, UUID, this.instance_id);
    this.settings.bind('key', 'prop', this._onSettingsChanged);
}

_onSettingsChanged() {
    if (!this._myActor) return;  // guard: UI not built yet
    // ... apply changes
}
```

Pattern A is cleaner. Pattern B is necessary when settings must be bound
before UI construction (e.g., size settings that affect initial layout).

## Cairo Drawing

Use `Clutter.Canvas` for custom drawing. Connect to the `draw` signal:

```javascript
this._canvas = new Clutter.Canvas();
this._canvas.connect('draw', (canvas, ctx, width, height) => {
    this._drawMyThing(ctx, width, height);
});
this._canvas.set_size(width, height);

this._actor = new Clutter.Actor();
this._actor.set_content(this._canvas);
```

### Cairo API Notes for GJS

- Use `Cairo.Operator.SOURCE` and `Cairo.Operator.OVER` (not raw integers)
- Use `addColorStopRGBA()` with float values (0.0–1.0), NOT hex strings or `rgba()` CSS strings
- `new Cairo.RadialGradient(x0, y0, r0, x1, y1, r1)` for radial gradients
- `ctx.setSourceRGBA(r, g, b, a)` with float values
- `ctx.arc(cx, cy, radius, 0, 2 * Math.PI)` for circles
- Call `ctx.fill()` or `ctx.stroke()` after defining paths

### Redrawing

To trigger a redraw after changing drawing parameters, call:
```javascript
this._canvas.invalidate();
```
// ponytail: Clutter.Canvas has invalidate(), NOT queue_draw() (that's Gtk).
// Call invalidate() once after initial layout too — guarantees first paint.

## Clutter Animation

For smooth animation, use `GLib.timeout_add` with a frame interval:

```javascript
_startAnimation() {
    const FPS = 30;
    const interval = 1000 / FPS;  // ~33ms
    
    this._timeout = GLib.timeout_add(GLib.PRIORITY_DEFAULT, interval, () => {
        if (this._shouldAnimate) {
            this._angle += 0.5;
            this._actor.set_rotation_angle(
                Clutter.RotateAxis.Z_AXIS, this._angle
            );
        }
        return GLib.SOURCE_CONTINUE;
    });
}
```

### Smooth Rotation

- Use `set_pivot_point(0.5, 0.5)` to rotate around center
- Keep angle in degrees (0–360), wrap around to avoid float overflow
- `Clutter.RotateAxis.Z_AXIS` for 2D rotation
- Only update rotation when state changes (playing/paused) to save CPU
- Rotation is a whole-actor transform: anything radially symmetric (concentric
  grooves, centered gradients) looks identical frame-to-frame, so the spin is
  invisible even while the angle advances. Paint at least one asymmetric cue on
  the rotating canvas — orbiting strobe dots near the rim, an off-center
  specular wedge, a marker dot, or text. Label text doubles as track display
  (readable when parked) and motion proof when spinning; invalidate that canvas
  on track change since it now owns the pixels.

## MPRIS Integration

MPRIS (Media Player Remote Interfacing Standard) is the standard Linux
interface for media player control. Access it via D-Bus.

### Key Constants

```javascript
const MPRIS_PATH = "/org/mpris/MediaPlayer2";
const DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties";
const MPRIS_IFACE = "org.mpris.MediaPlayer2.Player";
```

### Finding Players

Players register as `org.mpris.MediaPlayer2.<name>` on the session bus.
Subscribe to `NameOwnerChanged` to detect players starting/stopping:

```javascript
_setupMPRIS() {
    // Watch for player appearance/disappearance
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
    this._findPlayer();
}

_findPlayer() {
    Gio.DBus.session.call(
        "org.freedesktop.DBus",
        "/org/freedesktop/DBus",
        "org.freedesktop.DBus",
        "ListNames",
        null, null,
        Gio.DBusCallFlags.NONE, -1, null,
        (connection, res) => {
            try {
                const reply = connection.call_finish(res);
                const names = reply.get_child_value(0).get_strv();
                const player = names.find(n =>
                    n.startsWith("org.mpris.MediaPlayer2.")
                );
                if (player && player !== this._playerName) {
                    this._connectToPlayer(player);
                } else if (!player) {
                    this._disconnectPlayer();
                }
            } catch (e) {
                this._disconnectPlayer();
            }
        }
    );
}
```

### Subscribing to Property Changes

```javascript
_connectToPlayer(name) {
    this._disconnectPlayer();
    this._playerName = name;
    
    const handlerId = Gio.DBus.session.signal_subscribe(
        name,
        DBUS_PROP_IFACE,
        "PropertiesChanged",
        MPRIS_PATH,
        null,
        Gio.DBusSignalFlags.NONE,
        (connection, sender, object, iface, signal, params) => {
            this._onPropertiesChanged(params);
        }
    );
    this._signalHandlers.push(handlerId);
    this._updatePlaybackStatus();
    this._updateTrackInfo();
}

_onPropertiesChanged(params) {
    try {
        const iface = params.get_child_value(0).get_string()[0];
        if (iface !== MPRIS_IFACE) return;
        const changed = params.get_child_value(1);
        const values = changed.deep_unpack();
        
        if ("PlaybackStatus" in values) {
            this._updatePlaybackStatus();
        }
        if ("Metadata" in values) {
            this._updateTrackInfo();
        }
    } catch (e) {}
}
```

### Reading Properties

```javascript
_updatePlaybackStatus() {
    Gio.DBus.session.call(
        this._playerName,
        MPRIS_PATH,
        DBUS_PROP_IFACE,
        "Get",
        new GLib.Variant("(ss)", [MPRIS_IFACE, "PlaybackStatus"]),
        null, Gio.DBusCallFlags.NONE, -1, null,
        (connection, res) => {
            try {
                const reply = connection.call_finish(res);
                const variant = reply.get_child_value(0);
                const status = variant.get_child_value(0).get_string()[0];
                this._isPlaying = (status === "Playing");
            } catch (e) {
                this._isPlaying = false;
            }
        }
    );
}

_updateTrackInfo() {
    Gio.DBus.session.call(
        this._playerName,
        MPRIS_PATH,
        DBUS_PROP_IFACE,
        "Get",
        new GLib.Variant("(ss)", [MPRIS_IFACE, "Metadata"]),
        null, Gio.DBusCallFlags.NONE, -1, null,
        (connection, res) => {
            try {
                const reply = connection.call_finish(res);
                const variant = reply.get_child_value(0);
                const inner = variant.get_child_value(0);
                const data = inner.deep_unpack();
                
                let title = "";
                let artist = "";
                try {
                    title = data["xesam:title"]?.get_string()[0] || "";
                } catch (e) {}
                try {
                    artist = data["xesam:artist"]?.get_strv()[0] || "";
                } catch (e) {}
                
                this._trackInfo = { title, artist };
                this._updateTrackLabel();
            } catch (e) {
                this._trackInfo = { title: "", artist: "" };
            }
        }
    );
}
```

### Unwrapping D-Bus replies — `deep_unpack()` does NOT recurse into variants

On current Cinnamon GJS builds, `reply.deep_unpack()[0]` on a Properties
`Get` reply (type `(v)`) returns a still-boxed `Variant`, NOT the plain
value — verified live: `status=[object variant of type "s"]`, so a
`=== "Playing"` check never fires; Metadata dict values stay boxed too,
and passing one to `St.Label.set_text()` throws `Expected type string ...
got GObject_Boxed`. Unwrap in a loop everywhere a `Get` reply is read:

```javascript
// ponytail: this build's deep_unpack() leaves variant-boxed Get replies
// packed — loop until a plain value falls out.
_unwrap(reply) {
    let v = reply.deep_unpack()[0];
    while (v && typeof v.deep_unpack === "function") v = v.deep_unpack();
    return v;
}
// usage: const st = this._unwrap(conn.call_finish(res)); // "Playing"
```

Metadata needs per-value unwrapping (the dict itself is plain, its values
are boxed):

```javascript
const meta = this._unwrap(conn.call_finish(res)) || {};
const _v = (x) => {
    while (x && typeof x.deep_unpack === "function") x = x.deep_unpack();
    return x;
};
const _t = _v(meta["xesam:title"]);
const _a = _v(meta["xesam:artist"]);
this._track = {
    title: (typeof _t === "string") ? _t : "",
    artist: (Array.isArray(_a) && typeof _a[0] === "string") ? _a[0] : "",
};
```

Defensive: `label.set_text(String(s))` — St setters are type-strict and a
boxed value throws instead of coercing. The manual
`get_child_value(0).get_string()[0]` chains are longer AND version-fragile
(`get_string()` returns a bare string on some builds, making `[0]` silently
take the first character) — prefer the unwrap loop over both.

### Calling Player Methods

```javascript
_playerCall(method) {
    if (!this._playerName) return;
    Gio.DBus.session.call(
        this._playerName,
        MPRIS_PATH,
        MPRIS_IFACE,
        method,  // "PlayPause", "Play", "Stop", "Previous", "Next"
        null, null,
        Gio.DBusCallFlags.NONE, -1, null, null
    );
}
```

### Setting Properties (e.g., Volume)

```javascript
Gio.DBus.session.call(
    this._playerName,
    MPRIS_PATH,
    DBUS_PROP_IFACE,
    "Set",
    new GLib.Variant("(ssv)", [
        MPRIS_IFACE,
        "Volume",
        new GLib.Variant("d", newValue)
    ]),
    null, Gio.DBusCallFlags.NONE, -1, null, null
);
```

### Cleanup

Always unsubscribe D-Bus signals in `on_desklet_removed`:

```javascript
on_desklet_removed(deleteConfig) {
    if (this._nameWatcherId) {
        Gio.DBus.session.signal_unsubscribe(this._nameWatcherId);
    }
    for (const id of this._signalHandlers) {
        Gio.DBus.session.signal_unsubscribe(id);
    }
}
```

## Interaction Patterns

### Click Events — use the native hook, never consume button-press

The base `Desklet` class makes every desklet draggable (`DND.makeDraggable`)
and calls `on_desklet_clicked(event)` on button-release *after DND rules out
a drag*. Override it. Do NOT connect `button-press-event` and return
`EVENT_STOP` on left-click: the press never reaches the desklet actor, DND
never tracks the gesture, and the user can no longer move the desklet.

```javascript
// Native tap hook: taps toggle, drags move, no bookkeeping needed.
// ponytail: taps on child control buttons already acted on press —
// ignore their release here or one tap both acts AND toggles.
on_desklet_clicked(event) {
    if (event.get_button() !== 1) return; // 3 = menu, handled by base class
    const src = event.get_source();
    if (src && (this._prev.contains(src) || this._next.contains(src))) return;
    this._playerCall("PlayPause");
}
```

- No `button-press-event` handler on desklet content, ever (scroll/hover are fine).
- `event.get_source()` + `actor.contains(src)` identifies taps from nested controls.

### Scroll Events

```javascript
this._actor.connect('scroll-event', (actor, event) => {
    const direction = event.get_scroll_direction();
    if (direction === Clutter.ScrollDirection.UP) {
        // volume up
    } else if (direction === Clutter.ScrollDirection.DOWN) {
        // volume down
    }
    return Clutter.EVENT_STOP;
});
```

### Hover Reveal

```javascript
this._actor.connect('enter-event', () => {
    this._overlay.show();
});
this._actor.connect('leave-event', () => {
    this._overlay.hide();
});
```

## Installation & Testing

### Install

```bash
cp -r desklet-folder ~/.local/share/cinnamon/desklets/
```

Then enable via **Right-click desktop → Desklets → Add**.

### Uninstall

```bash
rm -rf ~/.local/share/cinnamon/desklets/<uuid>
```

Then remove from Desklets settings.

### Debugging

- Cinnamon logs: `~/.xsession-errors`
- Confirm load/failure: `grep -ai <uuid> ~/.xsession-errors` — success is
  `Loaded desklet <uuid> in 15 ms`; failure is
  `Failed to evaluate 'main' function on desklet: <uuid>/<instance_id>`
  (read the bracketed reason — it names the exact cause)
- Restart Cinnamon: `Alt+F2` → type `r` → Enter
- Enable desklet in settings UI, don't manually edit `enabled-desklets`
- Non-disruptive reload attempt: `gdbus call --session --dest org.Cinnamon --object-path /org/Cinnamon --method org.Cinnamon.ReloadXlet "<uuid>" "desklet"` (unreliable — see pitfall 10)
- `node --check desklet.js` catches syntax errors (but not GJS API issues)
- For runtime errors, check `~/.xsession-errors` after restarting Cinnamon
- Read the user's ACTUAL stored values (not just schema defaults):
  `~/.config/cinnamon/spices/<uuid>/<uuid>.json` (`value` fields) —
  revealed a case where the user had set gold `rgb()` colors while defaults
  were `#hex`, which explained a rendering failure defaults couldn't produce
- Full reload/debug recipe: `references/desklet-reload-debugging.md`
- Trace the MPRIS handshake before fixing it: temporary `log()` lines at
each step (bus scan → attach → status → track), restart, read the values
back from the log. Silent try/catch around D-Bus calls hides handshake
failures — one instrumented restart beats repeated unverified fix rounds
(each costs the user a disruptive restart).

## Common Pitfalls

1. **Settings callback fires before UI exists** — Use Pattern A (build UI first) or Pattern B (guard callback)
2. **Cairo color format** — Use float 0.0–1.0, not hex or CSS `rgba()`
3. **D-Bus signal leaks** — Always unsubscribe in `on_desklet_removed`
4. **Animation timeout leaks** — Always `source_remove` in cleanup
5. **MPRIS player disappears** — Handle `NameOwnerChanged` and `_disconnectPlayer()` gracefully
6. **`this` context in callbacks** — Use arrow functions `() => {}` to preserve `this`
7. **Clutter actor not reactive** — Call `set_reactive(true)` to receive events
8. **Rotation pivot** — Set `set_pivot_point(0.5, 0.5)` for center rotation
9. **`spacing` is not an `St.BoxLayout` constructor property** — passing
   `spacing:` in the constructor object throws `No property spacing on
   StBoxLayout`, which fails `main()` and leaves the desklet totally
   invisible with no UI at all. Use `style: "spacing: Npx;"` instead
   (spacing is an St style property, not a GObject property). Same trap
   applies to any non-GObject key in St/Clutter constructors — an invisible
   desklet plus `Failed to evaluate 'main'` in the log means a constructor
   prop first, code logic second.
10. **Cinnamon caches xlet JS modules by UUID** — editing `desklet.js` does
    not refresh a loaded instance, and neither D-Bus reload path is
    reliable: on some builds both `org.Cinnamon.ReloadXlet` and
    `LookingGlass.ReloadExtension` throw `TypeError: type is undefined`
    and can leave the desklet half-unloaded (invisible). After code edits,
    verify via log (Debugging below); when in doubt, logout/login or
    `cinnamon --replace` (user approval — screen flickers) rather than
    piling on more edits. Full recipe:
    `references/desklet-reload-debugging.md`.
11. **`color-mix()` is NOT supported in Clutter CSS** — Cinnamon uses a
    GTK3-era CSS parser that does not understand CSS Color Level 4 functions
    like `color-mix()`. Any rule containing it is silently dropped, so color
    changes via CSS variables never apply. Derive gradient stops
    arithmetically in JavaScript (mix RGB channels toward white/black by a
    float factor) and apply them via `actor.set_style()` directly on each
    element — never rely on CSS color functions.
12. **Settings belong in `metadata.json`, not `settings-schema.json`** —
    for DESKLETS. Cinnamon reads desklet settings from `metadata.json`
    (the `settings` array); `settings-schema.json` is a GSettings artifact
    that Cinnamon ignores for desklets. APPLETS are the opposite:
    `AppletSettings` + `settings-schema.json` is the working pattern
    (verified live — binds fire, values persist to
    `~/.config/cinnamon/spices/<uuid>/`). Always define your settings
    array in `metadata.json` for desklets, `settings-schema.json` for applets.
13. **CSS variables on a parent don't cascade to St children in this
    context** — Setting `--my-var` on a canvas via `set_style()` does NOT
    propagate to child actors. Each element (`platter`, `record`, `label`,
    `title`) needs its own `set_style()` call with the computed values.
    Apply colors directly per-element, not via CSS custom properties.
14. **Imports must be correct** — `PopupMenu` comes from `imports.ui.popupMenu`
    (not `Cinnamon.PopupMenu`). `Clutter` comes from `imports.gi.Clutter`.
    `Desklet.DeskletManager` does not exist — use
    `new PopupMenu.PopupMenuManager(this)`. Always verify imports against
    working desklet code; wrong imports fail silently at runtime.
15. **Rotation requires asymmetric visual cues** — A perfectly radially
    symmetric record (concentric grooves, centered gradients) looks identical
    every frame while spinning, making the animation invisible. Paint at
    least one asymmetric mark on the rotating canvas: an off-center specular
    wedge, orbiting strobe dots near the rim, or a marker dot. Label text
    doubles as track display (readable when parked) and motion proof (blurred
    while spinning). Invalidate the canvas on track change since it now owns
    those pixels.
16. **Pango markup `foreground` rejects `rgb()` — one bad span blanks the
    whole label** — `colorchooser` settings store `rgb(r,g,b)`/`rgba(...)`,
    but `ClutterText.set_markup()` only accepts `#hex`/named colors. A
    single unparseable span fails the ENTIRE call (log signature:
    `Failed to set the markup of the actor 'ClutterText' ... could not be
    parsed ... not 'rgb(...)'`) and the label keeps its previous (often
    empty) text — symptom is an invisible applet + "color settings do
    nothing", with zero JS errors. Fix once: a `normColor()` helper
    (`rgb()/rgba()`→`#rrggbb`, `#rgb`→`#rrggbb`, names pass through,
    else fallback) applied in a single `_readColors()` that runs at the top
    of the settings callback, so every paint path only ever sees valid
    colors. Same normalization protects `set_style()` color rules.

## Submission to Cinnamon Spices

Once the desklet works locally, submit it to the official repository so it appears on cinnamon-spices.linuxmint.com.

### Required files (per the cinnamon-spices-desklets repo)

```
UUID/
├── info.json          # uuid, name, description, version, author (= GitHub username)
├── screenshot.png     # Desktop preview (recommended: 400×300)
├── README.md          # Install instructions
└── files/
    └── UUID/
        ├── metadata.json      # uuid, name, description, maxInstances, cinnamonVersion
        ├── desklet.js         # Main GJS implementation
        ├── stylesheet.css     # St widget styles
        └── icon.png           # 256×256 icon
```

### Pre-submission checklist

- [ ] `info.json` author field matches your GitHub username
- [ ] `screenshot.png` shows the desklet on a realistic desktop
- [ ] `icon.png` is 256×256, readable at small sizes
- [ ] `metadata.json` `maxInstances` set correctly (1 for single-instance)
- [ ] `desklet.js` passes `node --check`
- [ ] All files exist in both root (`info.json`, `screenshot.png`, `README.md`) and `files/UUID/`

### Submission workflow

```bash
# 1. Fork linuxmint/cinnamon-spices-desklets on GitHub (one-time)
# 2. Clone your fork
git clone https://github.com/YOUR_USER/cinnamon-spices-desklets.git
cd cinnamon-spices-desklets

# 3. Copy your desklet folder to the repo root
cp -r ~/.local/share/cinnamon/desklets/<uuid> .
#    OR copy from your development folder
cp -r ~/dev/my-desklet@user .

# 4. Add and commit
git add <uuid>
git commit -m "Add <Name> desklet

<Description>

UUID: <uuid>
Author: YOUR_USER
License: GPL-2.0"

# 5. Push to your fork
git push origin master

# 6. Open PR to upstream
gh pr create --repo linuxmint/cinnamon-spices-desklets \
  --base master --head YOUR_USER:master \
  --title "Add <Name> desklet" \
  --body "<Description>\n\n## UUID\n<uuid>\n\n## Author\nYOUR_USER\n\n## License\nGPL-2.0"
```

### Pitfall: check for existing desklet before creating

Before scaffolding a new desklet directory, check whether one already exists:

```bash
find ~ -maxdepth 4 -type d -name "*<partial-name>*" 2>/dev/null
find ~/.local/share/cinnamon/desklets -maxdepth 2 -type d
```

If the user already has files (desklet.js, metadata.json, stylesheet.css), copy the existing folder into the repo and only add missing files (screenshot.png, icon.png) — do not overwrite their work.

### Pitfall: git auth

`git push` may fail with `could not read Username` if gh auth is not configured for git:

```bash
gh auth setup-git
```

### Post-submission

- CI runs `validate-spice` automatically
- The Cinnamon team reviews within days/weeks
- Once merged, the desklet appears on cinnamon-spices.linuxmint.com
- Users can install it from System Settings → Desklets

## Verification

A desklet is complete when:

- All required files exist (info.json, screenshot.png, README.md, metadata.json, desklet.js, stylesheet.css, icon.png)
- `node --check desklet.js` passes
- Settings bind and update UI without errors
- D-Bus signals subscribe and unsubscribe cleanly
- Animation loop runs only when needed (saves CPU)
- `on_desklet_removed` cleans up all resources
- Desklet appears in Desklets settings and can be added to desktop
- PR is open at linuxmint/cinnamon-spices-desklets

## References

- `references/luxury-vinyl-implementation.md` — Complete MPRIS vinyl record desklet with Cairo drawing, Clutter animation, and settings binding
- `references/desklet-reload-debugging.md` — Stale-code diagnosis recipe: log signatures, gsettings toggle, D-Bus reload pitfalls, screenshot verification
- `references/spices-submission-checklist.md` — Pre-PR validation checklist, file structure, and CI requirements
- `references/vinyl-player-session.md` — Vinyl record player desklet session (2026-09-04): color customization, settings, imports, submission
