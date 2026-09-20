# Applet Development Session (2026-09-04)

Building a cheatsheet/reference applet for Linux Mint networking commands.

## What was built

A Cinnamon panel applet (`netref@attila`) that provides:
- Windows → Linux Mint networking command reference
- Searchable list with real-time filtering
- Copy to clipboard on click
- Scrollable list with fixed search bar
- 194 commands across 15 sections

## Key learnings

### 1. Cinnamon 6.6+ requires `_addStyleClass`

Without this method, the applet fails to load:
```
[netref@attila]: applet._addStyleClass is not a function
[netref@attila]: Failed to load applet: netref@attila/32
```

**Fix:**
```javascript
NetRef.prototype = {
    __proto__: Applet.IconApplet.prototype,
    _addStyleClass: function(styleClass) {
        this.actor.add_style_class_name(styleClass);
    },
    // ...
};
```

### 2. Popup closes when clicking search entry

`St.Entry` in a `PopupMenu.PopupBaseMenuItem` triggers `activate()` on click, closing the popup.

**Fix:** Override `activate()`:
```javascript
activate: function(event) {
    this.search_entry.grab_key_focus();
}
```

### 3. Popup relayouts when items are hidden/shown

Using `actor.show()/hide()` causes constant relayout, pushing the search bar around.

**Fix:** Use `destroy_all_children()` + re-add matching items:
```javascript
_filterItems: function(searchText) {
    this.itemsBox.destroy_all_children();
    for (let item of this._allItems) {
        let matches = /* ... */;
        if (matches) {
            let menuItem = this._createMenuItem(item);
            this.itemsBox.add(menuItem.actor);
        }
    }
}
```

### 4. ScrollView without scrollbar policy overflows invisibly

**Fix:** Always set:
```javascript
this.scrollView = new St.ScrollView({
    style: 'max-height: 450px;',
    hscrollbar_policy: St.PolicyType.NEVER,
    vscrollbar_policy: St.PolicyType.AUTOMATIC
});
```

### 5. Cheaty-style architecture works well for reference applets

The `cheaty@centurix` applet pattern:
- Load `sheet.json` from `refdocs/<SheetName>/sheet.json`
- Store enabled sheets in settings `cheatsheets` array
- `SheetMenuItem` → `SectionMenuItem` → `ItemMenuItem` → click to copy
- `St.Clipboard.get_default().set_text()` for copy
- `Main.notify()` for confirmation

### 6. JSON generation via Python

For large command databases, generate `sheet.json` with Python:
```python
import json
sheet = { "name": "...", "sections": { ... } }
with open('sheet.json', 'w') as f:
    json.dump(sheet, f, indent=4)
```

This avoids JSON syntax errors from hand-writing (control characters, etc.).

## File structure

```
~/.local/share/cinnamon/applets/netref@attila/
├── metadata.json
├── applet.js
├── icon.svg
├── stylesheet.css
├── settings-schema.json
└── refdocs/
    └── Networking/
        ├── sheet.json      # 194 commands, 15 sections
        └── icon.svg
```

## sheet.json format

```json
{
    "name": "Networking Commands",
    "description": "...",
    "author": "attila",
    "version": "2.0",
    "sections": {
        "Section Name": {
            "Item Name": {
                "description": "What it does",
                "code": "linux-command",
                "alternatives": {
                    "alt1": { "code": "alt-command" }
                }
            }
        }
    }
}
```

## SearchableListWidget pattern

For applets that need search, use a dedicated widget:
- Fixed `St.Entry` at top
- `St.ScrollView` with `max-height` below
- `St.BoxLayout` inside scrollview for items
- Store all items in `_allItems` array
- On search change: `destroy_all_children()` + re-add matches
- Each item is a `PopupMenu.PopupBaseMenuItem` with `code` property
- On `activate`: call copy callback

## Common Windows CMD → Linux mappings

| Windows | Linux |
|---|---|
| `ipconfig` | `ip addr` |
| `ipconfig /all` | `nmcli device show` |
| `ipconfig /release` | `sudo dhclient -r` |
| `ipconfig /renew` | `sudo dhclient` |
| `ipconfig /flushdns` | `sudo systemd-resolve --flush-caches` |
| `ping` | `ping` (same, but `-c` instead of `-n`) |
| `tracert` | `traceroute` |
| `pathping` | `mtr` |
| `nslookup` | `dig` |
| `arp -a` | `ip neigh` |
| `route print` | `ip route` |
| `netstat -ano` | `ss -tulnp` |
| `netstat -an` | `ss -tunp` |
| `netstat -e` | `ip -s link` |
| `netstat -r` | `ip route` |
| `hostname` | `hostname` |
| `getmac` | `ip link show` |
| `ncpa.cpl` | `nm-connection-editor` |
| `netsh winsock reset` | `sudo systemctl restart NetworkManager` |
| `netsh interface set interface disable` | `sudo ip link set eth0 down` |

## Lessons learned

1. **Start with the simplest fix first** — the `_addStyleClass` issue was a one-line fix, not a rewrite
2. **Test incrementally** — check `~/.xsession-errors` after each change
3. **Use Python for large JSON** — avoids syntax errors
4. **Search should not close popup** — override `activate()`
5. **Filtering should rebuild, not hide** — prevents relayout issues
6. **Always set scrollbar policy** — otherwise items overflow invisibly
7. **Mark sudo commands explicitly** — add `(requires sudo)` to descriptions
8. **Include every variant** — `ipconfig`, `ipconfig /all`, `ipconfig /release`, etc. all need separate entries