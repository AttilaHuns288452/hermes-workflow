# Desklet Reload Debugging Recipe

Session-tested on Linux Mint Cinnamon 6.6 (Sep 2026, luxury-vinyl@attila).
Symptom class: desklet shows stale visuals, or goes invisible after a code edit.

## 0. Confirm the running build is newer than your last edit — FIRST

When the user reports "still the same" after a fix, do not ship another
patch blind. Compare session start vs file mtime plus the newest log line:

```bash
ps -o lstart= -p $(pgrep -f "cinnamon --replace" | head -1)   # session start
stat -c %y ~/.local/share/cinnamon/desklets/<uuid>/desklet.js # last edit
grep -a "<uuid>" ~/.xsession-errors | tail -2                 # last load
```

If the session started before the last edit and the log shows no fresh
`Loaded desklet <uuid>`, the old module is still live — every further edit
is untestable until Cinnamon restarts (step 4). Say so and stop patching.

## 1. Confirm what's on disk vs. what's running

```bash
grep -c "<suspect-string>" ~/.local/share/cinnamon/desklets/<uuid>/desklet.js
gsettings get org.cinnamon enabled-desklets   # is the uuid even enabled?
find /home/$USER /usr/share/cinnamon -maxdepth 6 -iname "*<short-name>*"  # second copies?
```

## 2. Read the log — it names the cause

```bash
grep -ai "<uuid>" ~/.xsession-errors | tail -5
```

| Log line | Meaning |
|---|---|
| `Loaded desklet <uuid> in 15 ms` | current file loaded fine |
| `Failed to evaluate 'main' function on desklet: <uuid>/<id>` + `[Error: ...]` | constructor threw; bracketed reason is exact (e.g. `No property spacing on StBoxLayout`) |
| `Reloading desklet: <uuid>/<id>` with no `Loaded` after | reload path died mid-flight; instance is half-unloaded |
| No new lines at all after a gsettings toggle | manager didn't react; go to step 4 |

## 3. Fix-and-reload loop (non-disruptive first)

```bash
node --check ~/.local/share/cinnamon/desklets/<uuid>/desklet.js
# remove all instances, wait, re-add (proven add path logs "Loaded desklet"):
CUR=$(gsettings get org.cinnamon enabled-desklets)
STRIPPED=$(echo "$CUR" | python3 -c "import sys,ast; l=ast.literal_eval(sys.stdin.read()); print([e for e in l if '<uuid>' not in e])")
gsettings set org.cinnamon enabled-desklets "$STRIPPED"; sleep 3
gsettings set org.cinnamon enabled-desklets "$(echo "$STRIPPED" | python3 -c "import sys,ast; l=ast.literal_eval(sys.stdin.read()); l.append('<uuid>:<id>:<x>:<y>'); print(l)")"
sleep 6; grep -ai "<uuid>" ~/.xsession-errors | tail -3
```

D-Bus reload (one shot, known-flaky):
```bash
gdbus call --session --dest org.Cinnamon --object-path /org/Cinnamon \
  --method org.Cinnamon.ReloadXlet "<uuid>" "desklet"
```
If it answers `TypeError: type is undefined`, the unload path broke and the
old module stays cached — stop retrying reload variants, they share the
machinery (`LookingGlass.ReloadExtension` throws identically).

## 4. Nuclear option (needs user approval — screen flickers)

`cinnamon --replace` in background, or logout/login. This clears the GJS
module cache, which is the only cure for a stale-cached UUID. Windows survive
a replace; unsaved work in settings dialogs may not — close them first.

## 5. Verify visually

`vision_analyze` may be down (bad key) — fall back to the user:
```bash
gnome-screenshot -f /tmp/<uuid>-verify.png
```
Deliver as `MEDIA:/tmp/<uuid>-verify.png` and ask what they see.

## Traps hit this session

- `St.BoxLayout({spacing: N})` throws; use `style: "spacing: Npx;"`.
  Old code worked only because it passed spacing via style string.
- `Clutter.Canvas` repaint API is `invalidate()`, not `queue_draw()`.
- Identical error repeating after the fix is proof of stale cache, not proof
  the fix is wrong — check `grep -c` on disk before doubting the patch.
