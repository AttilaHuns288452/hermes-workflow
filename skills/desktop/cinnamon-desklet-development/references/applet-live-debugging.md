# Applet live debugging: Eval bridge, color pitfalls, pixel forensics

Companion to SKILL.md. Proven on Cinnamon 6.x (Sept 2026, X11) while building
a Yahoo-Finance panel ticker. All techniques run from a shell, no IDE needed.

## 1. Live introspection via org.Cinnamon.Eval

Any running applet instance can be read and driven without reload:

```bash
gdbus call --session --dest org.Cinnamon --object-path /org/Cinnamon \
  --method org.Cinnamon.Eval '
  const a = imports.ui.appletManager
    .getRunningInstancesForUuid("my-applet@user")["0"];
  a._cSym + " | " + a._cUp + " | quotes=" + a._quotes.length' 
```

For longer probes, write the JS to /tmp/probe.js and eval it:

```bash
gdbus call --session --dest org.Cinnamon --object-path /org/Cinnamon \
  --method org.Cinnamon.Eval \
  'eval(String(imports.byteArray.toString(
    imports.gi.Glob.file_new_for_path... load via Gio.file_new_for_path("/tmp/probe.js").load_contents(null)[1])))'
```

(Correct loader: `imports.gi.Gio.file_new_for_path(p).load_contents(null)[1]`
wrapped in `imports.byteArray.toString(...)`. Use it to force `_refresh()`,
call `_applySettings()`, or paint a controlled test label.)

## 2. Settings truth vs code truth

- Live values: `~/.config/cinnamon/spices/<uuid>/<uuid>.json`
  (NOT `~/.cinnamon/configs/` — stale copies may exist; the spices path wins.)
- Cross-check: `dconf dump /org/cinnamon/ | grep -A20 <uuid>`
- Confirm loaded code version: `grep '<uuid> v' ~/.xsession-errors`
  (add a `global.log(UUID + " v" + version + " init")` stamp on every
  version bump; xlet code is cached — remove + re-add the applet or
  `Alt+F2 → r` after edits.)

## 3. Pitfall: colorchooser stores rgb(), Pango markup rejects it

`type: "colorchooser"` persists values as `rgb(229,165,10)` / `rgba(...)`
strings. A single invalid `foreground` attribute makes the WHOLE
`set_markup()` call fail — label goes silently invisible; the only trace is
`Clutter-WARNING ... Failed to set the markup...` in `~/.xsession-errors`.

Fix once, at the single place colors are read — normalize to `#rrggbb`:

```js
_readColors: function() {
    const norm = v => {
        let m = /rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/.exec(v || "");
        if (m) return "#" + [1,2,3].map(i =>
            Math.max(0, Math.min(255, +m[i])).toString(16).padStart(2, "0")).join("");
        return /^#[0-9a-f]{6}$/i.test(v || "") ? v : "#ffffff";
    };
    this._cSym = norm(this.symbol_color); // etc.
},
```

Verify: `grep -c "Failed to set the markup" ~/.xsession-errors` must be 0
for your uuid after init, and the label must be visible after restart.

## 4. Observed quirk: leading-span attribute drop (re-verify, don't assume)

On the tested build, the FIRST `<span>`'s `foreground` was ignored and it
inherited a later span's color (proven by screenshot pixel means: first
symbol-name rendered in the up-trend gold). Workaround that held:
prepend a zero-width guard span `<span foreground="...">\u200b</span>`
(single backslash in the GJS file — a doubled `\\u200b` paints literally)
and set the label actor's base style color to the symbol color as fallback.
Treat as build-specific: re-prove with a screenshot before shipping the hack.

## 5. Pixel forensics when you can't trust your eyes

`DISPLAY=:0 gnome-screenshot -f /tmp/panel.png`, then PIL + numpy:

- Word segmentation: threshold bright text pixels, connected-component blobs
  along the bar row → per-word mean RGB vs configured colors.
- NCC template matching: render DejaVuSans-Bold at candidate size to a
  template, normalized cross-correlation over the strip — but letter glyphs
  alone (e.g. "META") also match "GOLD"'s substrings at small sizes, so
  only trust matches that include the price digits / wider context.
- Freeze the subject first: timer repaints move pixels between screenshot
  and Eval reads (`_refreshId = 0` via Eval bridge), restore after.

## 6. Yahoo fetch ladder (GJS Soup fails silently — use a helper)

GJS Soup requests to Yahoo can die with no error and no data (blank label).
A stdlib `fetch.py` via `Util.spawn_async` was the reliable path:

1. Bare `https://query1.finance.yahoo.com/v8/finance/chart/<SYM>` (200, no
   cookie/crumb needed) → fallback `query2.` on non-200.
2. Only if both fail: curl with browser UA + `--cookie-jar` (v7/v8 crumb flow).
3. Labels: `GC=F→GOLD`, `CL=F→OIL`, strip `-USD`.
