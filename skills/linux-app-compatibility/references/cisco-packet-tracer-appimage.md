# Cisco Packet Tracer AppImage on Linux (2026-09-05)

## Problem
Cisco Packet Tracer 9.0.0 AppImage launches but no window appears. Process runs (`packettracer`, `PacketTracer`, `QtWebEngineProcess`) but the GUI never renders.

## Root Cause
The AppImage's `AppRun` → `pt-manage.sh activate` runs interactive TUI prompts:
- `tui-eula.sh` — displays EULA via `less` + `select` (waits for user input)
- `tui-activation.sh` — activation prompt

These hang indefinitely when stdin is not a terminal (e.g., launched from a desktop shortcut or background process).

## What Worked
**Method 1: Set `DEBIAN_FRONTEND=noninteractive`**
```bash
DEBIAN_FRONTEND=noninteractive /usr/local/bin/packettracer
```
The `interactive()` function in `pt-manage.sh` checks this variable and skips the TUI prompts.

**Method 2: Run the inner binary directly**
```bash
/tmp/.mount_packet*/opt/pt/bin/PacketTracer
```
Skips the AppImage wrapper entirely. Works but misses mime-type/icon registration.

## How to Diagnose
```bash
# Check if PT processes are running but no window
ps aux | grep -i packet | grep -v grep

# Check for the mount directory
ls /tmp/.mount_packet*/

# Look at the AppRun script to understand the launch chain
cat /tmp/.mount_packet*/AppRun
cat /tmp/.mount_packet*/pt-manage.sh

# Check if EULA was accepted (creates a marker file)
ls -la ~/.local/.packettracer/
```

## Window Management
If PT launches but the window is hidden behind other apps:
```bash
# List PT windows
xdotool search --name "Cisco Packet Tracer"

# Bring to front
wmctrl -i -a <window_id_hex>

# Or raise via xdotool
xdotool search --name "Cisco Packet Tracer" windowactivate
```

## Key Insight
AppImages that bundle their own runtime (Qt, Electron, etc.) often have interactive setup scripts that assume a terminal. When launched from a GUI desktop, these hang. `DEBIAN_FRONTEND=noninteractive` is the universal bypass for Debian/Ubuntu-derived distros.

## Lesson
For AppImage-based educational software on Linux:
1. Try `DEBIAN_FRONTEND=noninteractive` first
2. If that fails, run the inner binary directly
3. Check `~/.local/.<app>/` for activation/EULA marker files
4. Use `wmctrl`/`xdotool` to manage window stacking
