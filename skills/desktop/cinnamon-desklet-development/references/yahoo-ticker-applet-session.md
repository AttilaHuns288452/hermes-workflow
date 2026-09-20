# Yahoo Ticker applet session (2026-09-05) — yahoo-ticker@attila

Minimal Yahoo Finance **applet** (~230 lines) built after finding `yfquotes@thegli`
(1,792 lines, v7 quote + crumb + curl fallback) was overkill for
"price + ▲/▼ only". Lessons for future ticker/data applets:

## Confirm xlet type first

User asked for a "desklet", then corrected to "applet". Users conflate the
two constantly. Before scaffolding, confirm: desktop widget (desklet) vs
panel widget (applet) — one question saves a full rewrite.

## Lightweight Yahoo fetch (no crumb, no curl)

`GET https://query1.finance.yahoo.com/v8/finance/chart/<SYM>?interval=1d&range=1d`
with a browser User-Agent needs no crumb/cookies for price + previous close.
Fallback to `query2.` host on failure. Parse:
`meta.regularMarketPrice`, `prev = meta.previousClose || meta.chartPreviousClose`,
`change = price - prev`. Futures/crypto tickers: `GC=F` (gold), `CL=F` (oil),
`BTC-USD`, `ETH-USD`. Short labels via map (`GC=F→GOLD`, `CL=F→OIL`, strip `-USD`).
Reach for the heavy v7+crumb+curl stack (see yfquotes source) only when you
need pre/post-market, 52w stats, or have crumb failures.

## Soup2/Soup3 compat (both exist in the wild) — SUPERSEDED, see below

> Later the same session this whole approach was abandoned: requests failed
> silently (no log error, panel stuck at `…`). Kept for history only.

```javascript
const IS_SOUP3 = Soup.MAJOR_VERSION !== 2;
// Soup3: session.send_and_read_async(msg, prio, null, (s, res) => {
//   let bytes = s.send_and_read_finish(res);
//   if (msg.get_status() !== 200) return null;
//   return ByteArray.toString(bytes.get_data()); });
// Soup2: session.queue_message(msg, (s, m) => {
//   if (m.status_code !== 200) return null;
//   return (typeof m.response_body.data === "string")
//     ? m.response_body.data : ByteArray.toString(m.response_body.data); });
```

## Rotating TextApplet pattern

Panel too narrow for 8 quotes: `Applet.TextApplet` shows ONE compact quote
(`BTC 79,707.12 ▼`), `GLib.timeout_add_seconds` rotates the index, click
opens `AppletPopupMenu` with all rows. Timer hygiene: refresh reschedules
itself (`SOURCE_REMOVE` + re-add in `_refresh`); rotation is a separate
`SOURCE_CONTINUE` timer; `on_applet_removed_from_panel` removes both and
bumps a `_fetchTag` so in-flight Soup callbacks from a dead instance no-op.

## Single-source trend color

Price label + arrow label must share color: one `_trendColor(trend)` function
(up/down/flat settings keys) read by both paint paths — never separate color
keys per element, or they drift.

## Testing xlet JS without Cinnamon

`node --check` = syntax only. For logic: keep helpers pure top-level
functions (`fmtPrice`, `trendOf`, `labelOf`), then extract-and-eval them from
the shipped file and assert:

```bash
node -e '
const src = require("fs").readFileSync("applet.js", "utf8");
const grab = (re) => src.match(re)[0];
// ponytail: ONE eval — separate eval() calls do NOT share const bindings
// (second eval throws ReferenceError), so concatenate helpers + asserts.
eval([
  grab(/const LABELS = \{[^}]*\};/),
  grab(/function fmtPrice[\s\S]*?\n\}/),
  grab(/function trendOf[\s\S]*?\n\}/),
  `const assert = require("assert");
   assert.strictEqual(fmtPrice(79707.12), "79,707.12");
   assert.strictEqual(trendOf(-1), "down");
   console.log("OK");`
].join("\n"));'
```

Live HTTP parity was proven with the python stocks skill against the same
endpoint before shipping. Never hand-edit `enabled-applets`/`enabled-desklets`
— install files, user enables via UI (see desktop-customization-safety).

## Update later the same session — what actually shipped

### Soup to Yahoo dies silently → fetch via stdlib python subprocess

The Soup code above loaded clean (88 ms, zero log errors) yet every request
failed silently: rows sat at `…`, no arrows. Same-machine curl/python got
HTTP 200, so the fault was libsoup's handshake, not Yahoo. Fix: ship a
stdlib `fetch.py` in the applet dir (argv symbols → JSON
`[{symbol, price, change}]` on stdout) and call it with `Gio.Subprocess`:

```javascript
let proc = new Gio.Subprocess({
    argv: ["python3", APPLET_DIR + "/fetch.py"].concat(symbols),
    flags: Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_SILENCE
});
proc.init(null);
proc.communicate_utf8_async(null, null, (p, res) => {
    try {
        let [ok, stdout] = p.communicate_utf8_finish(res);
        cb((ok && stdout) ? JSON.parse(stdout) : null);
    } catch (e) { cb(null); }
});
```

Rule: when Soup fails with no error, don't debug the handshake — one python
subprocess per refresh interval (minutes) is cheap, and it runs the exact
code already proven live via terminal. `global.log` total failures so the
next silent break leaves a trace in `~/.xsession-errors`; show an offline
state in the UI instead of eternal placeholders.

### Full-strip panel via Pango markup (rotation removed per user feedback)

User rejected rotation — panel now shows ALL quotes at once, each in its
trend color, inside one `TextApplet` label via `Clutter.Text` markup:

```javascript
let text = this._applet_label.get_clutter_text();
text.set_markup(quotes.map(q =>
    '<span foreground="' + symColor + '">' + esc(q.label) + "</span> " +
    '<span foreground="' + trendColor + '">' + esc(fmtPrice(q.price)) + " " + ARROW + "</span>"
).join("    "));
```

The label auto-sizes with content: adding symbols widens the applet with
zero layout code. `esc()` (`&<>`) is mandatory — symbols come from a
user-editable settings key straight into a markup parser. The now-dead
`rotate-seconds` setting was deleted, not left orphaned.

### Yahoo crumb note

`/v1/test/getcrumb` intermittently 401s while bare v8 chart requests return
200. Never treat crumb failure as fatal — request bare first, add
cookie/crumb complexity only for endpoints that demand it (v7 quote).

### Reload applets by remove/re-add

Cinnamon caches xlet JS by UUID — edits don't reach a loaded instance
(same staleness as desklet pitfall 10). Remove the applet from the panel
and re-add it (`Alt+F2` → `r` also works); a settings tweak alone never
reloads code.
