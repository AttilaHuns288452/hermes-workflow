# Non-Standard Key Bindings on Cinnamon

Reusable recipe for binding a key that the Cinnamon shortcut editor cannot see
(no standard X11 keysym) to a desktop command.

## When to use this

- The user wants a physical key (macro key, vendor key, unusual media key) to
  launch a command, but System Settings → Keyboard → Shortcuts ignores it.
- `xev` reports a `keycode` but no recognizable keysym, or the keysym is
  outside the standard set.
- Prefer the native GUI shortcut editor first; fall back to this recipe only
  when the key is genuinely invisible to the editor.

## Recipe

### 1. Find the key's X keycode

Run `xev` and press the key once. Capture the `keycode N` value from the
`KeyPress` line:

```bash
xev -event keyboard 2>&1 | grep -E "KeyPress|keysym|keycode|state"
```

If the key is on a different input device, target that device:

```bash
evtest /dev/input/by-path/<device>-event-kbd 2>&1
```

Record the keycode. Do not guess it.

### 2. Write an xbindkeysrc entry

`xbindkeys` binds at the X keycode level, bypassing the keysym layer:

```bash
cat > ~/.xbindkeysrc <<'EOF'
"/path/to/command"
  c:<KEYCODE> + m:0x0
EOF
```

- `c:<KEYCODE>` is the raw X keycode from step 1.
- `m:0x0` means no modifier.
- The command must be quoted. Use the absolute path to the binary or script.

### 3. Test before committing

Start xbindkeys in foreground (no daemon) and simulate the key with `xdotool`:

```bash
xbindkeys -n -v &
sleep 1
xdotool key <KEYCODE>
sleep 1
pgrep -f "<command-unique-substring>" && echo "binding works" || echo "binding failed"
pkill xbindkeys
```

If the command does not launch, check `~/.xbindkeysrc` syntax and the command
path. Do not assume the binding is live without an actual launch check.

### 4. Make it survive logout/reboot

Create a Cinnamon autostart entry:

```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/xbindkeys.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=xbindkeys (custom key bindings)
Comment=Run xbindkeys to load custom key bindings
Exec=xbindkeys
Hidden=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
OnlyShowIn=Cinnamon;
EOF
```

`Exec=xbindkeys` (daemon mode, no `-n`/`-q` flags) is what autostart expects.
`-q` is not a valid xbindkeys flag and will silently fail.

### 5. Start it now

```bash
xbindkeys
```

Verify with `pgrep -x xbindkeys`.

## Verification

- The binding launches the intended command when the physical key is pressed.
- `xbindkeys` is running (`pgrep -x xbindkeys`).
- `~/.config/autostart/xbindkeys.desktop` exists and `Exec=xbindkeys`.
- The command path in `~/.xbindkeysrc` is absolute and exists.

## Pitfall

- Do not write `keycode N` in `~/.xbindkeysrc` — the correct syntax is
  `c:N + m:0x0`. The old `keycode` form is rejected with "unknown key in RC
  file" and "Error in allocation of keys".
- Do not use `xbindkeys -q` — it is not a valid flag.
- If the key is actually a keysym that cinnamon can see, prefer the GUI shortcut
  editor over xbindkeys; xbindkeys is the fallback for truly invisible keys.
- If the key belongs to a separate HID device (macro pad, controller), bind on
  that device's event node, not the main keyboard's.
