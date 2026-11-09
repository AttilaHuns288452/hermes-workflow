---
name: linux-hardware-troubleshooting
description: Use when laptop hardware isn't detected on Linux.
version: 1.0.0
author: Attila
license: MIT
platforms: [linux]
---

# Linux Hardware Troubleshooting

Patterns for diagnosing and fixing laptop hardware that works in Windows but not Linux.

## When to Use

- A systemd service runs but reports hardware as UNKNOWN or detects no features
- A kernel module fails to load with "Unknown symbol in module"
- Hardware controls (fan, RGB, thermal) don't work after a kernel update
- Laptop-specific features (NitroSense, PredatorSense, etc.) need a replacement

## Diagnostic Flow

### 1. Service running but hardware not detected

Check what the daemon actually sees in its logs:

```bash
journalctl -u <service> --since "1 hour ago" | grep -iE "module|driver|detect|unknown|error"
```

Common: daemon started BEFORE module was loaded, or module build is for wrong kernel.

### 2. Module load fails with "Unknown symbol in module"

Find the missing symbol's module:

```bash
# Check what symbol is missing
dmesg | tail -20 | grep "Unknown symbol"

# Search for which module provides it
grep -r "<symbol>" /lib/modules/$(uname -r)/modules.dep
# or
modinfo <candidate-module> | grep <symbol>
```

Load dependency first, then retry:

```bash
sudo modprobe <dependency-module>
sudo insmod src/<target-module>.ko
```

### 3. Rebuild module for current kernel

When a .ko from a previous build fails to load:

```bash
cd <module-source>
make clean
make
sudo insmod src/<module>.ko
```

### 4. Persist across reboots (make install vs insmod)

`insmod` is volatile — survives until reboot. For persistence:

```bash
sudo make install   # copies .ko to /lib/modules/<ver>/, runs depmod, loads it
```

This also handles:
- Installing to correct `/lib/modules/$(uname -r)/kernel/drivers/...`
- Running `depmod -a` to update dependency maps
- Setting up module to load at boot (via `modules-load.d` or similar)

`make install` survives reboots but NOT kernel updates. When the fix must survive kernel updates too, register with DKMS (next section) instead of rebuilding by hand after every update.

### 5. Blacklist conflicting modules

Some modules conflict (e.g., `acer_wmi` vs `linuwu_sense`):

```bash
# Check if conflicting module is loaded
lsmod | grep <conflicting>

# Blacklist it
echo "blacklist <conflicting>" | sudo tee /etc/modprobe.d/blacklist-<conflicting>.conf
sudo rmmod <conflicting> 2>/dev/null || true
```

## Make the fix permanent: DKMS

A hand-built `.ko` dies at the next kernel update. To make a fix survive kernel updates, register the module with DKMS (`templates/dkms.conf` is a working starter):

```bash
sudo mkdir -p /usr/src/<module>-<ver>
sudo cp -r Makefile src dkms.conf /usr/src/<module>-<ver>/
sudo dkms add <module>/<ver>
sudo dkms build <module>/<ver> -k $(uname -r)
sudo dkms install <module>/<ver> -k $(uname -r)
```

Verify both halves:
- `dkms status` shows the module installed for the running kernel.
- The kernel-update hook exists (`ls /etc/kernel/postinst.d/dkms`) — without it `AUTOINSTALL` never fires and the "permanent" fix silently stops at the next kernel.

## Self-healing boot guard (durability asks)

When the user says "make sure it ALWAYS works at startup", configuration alone is not the deliverable — add a repair path and prove it. A oneshot unit running BEFORE the dependent daemon closes the two remaining gaps (DKMS failing once, daemon starting before the module):

- `templates/boot-guard.service` — `After=systemd-modules-load.service`, `Before=<daemon>.service`, `WantedBy=multi-user.target`.
- `templates/boot-guard.sh` — modprobe; on failure rebuild via `dkms install --force`, fallback `make install`; then `systemctl --no-block try-restart <daemon>`.

The daemon then cannot latch onto limited/unknown mode, because it never starts before the module is guaranteed loaded.

## Prove durability by simulating the failure

Never claim "survives a restart" from config inspection. Reproduce the failure state and let the boot path recover it:

```bash
sudo rmmod <module>                       # the state the machine boots into
sudo systemctl restart <guard>.service    # the boot path
sudo systemctl restart <daemon>.service
journalctl -u <daemon> --since '-1 min' | grep -E 'Detected features: [a-z]'
```

The pass condition is the daemon reporting full features after recovery, not the unit files looking right. Embed this test in the install script so it is re-runnable later.

## Verify and normalize through the control channel

Vendor hardware daemons usually expose a local unix socket with a trivial JSON protocol (probe request shapes `{"command": "<name>", "params": {}}` / `{"action": ...}` against `get_*`/`set_*` commands). Use it to READ state (`get_all_settings`) and to NORMALIZE settings a GUI click-through flipped. The daemon journal is the root-cause oracle: grep it for `module not found`, `Unknown laptop type`, `Detected features` before touching anything.

## Common Patterns

### systemd service depends on kernel module

If a daemon needs a kernel module:
- Service running ≠ module loaded
- Check service logs for "module not found" errors
- Restart service AFTER module is loaded: `sudo systemctl restart <service>`

### Kernel updates break manually-built modules

After `apt upgrade` installs a new kernel:
- Old .ko files won't load (version mismatch)
- One-off recovery: `make clean && make && sudo make install` for the new kernel
- The permanent fix is DKMS registration plus the boot guard (sections above); rebuilding by hand after every update is how the same bug comes back

### Checking what a kernel module provides

```bash
# See if module loaded
lsmod | grep <module>

# See module info
modinfo <module>

# See kernel messages from module load
dmesg | grep <module>
```

## Pitfalls

- Don't assume a running service means its hardware driver is loaded — always check `lsmod` and service logs
- `insmod` works but doesn't persist; `make install` is required for boot-time loading
- Module dependencies (like `sparse-keymap`) must be loaded BEFORE the dependent module
- A manually-built module dies at every kernel upgrade — check `uname -r` vs the .ko's target, then register with DKMS so the question never comes back
- A daemon that starts before its module loads latches onto limited/unknown mode and keeps it until restarted — fix ORDERING (`Before=<daemon>` in the guard unit), not just presence
- `systemctl restart X` (or `try-restart`) from inside a unit ordered `Before=X` deadlocks: X's start waits for the unit's completion while the unit waits for X's restart job. Use `systemctl --no-block`
- Clicking through a hardware app's settings GUI is NOT read-only: pages can push their stored state to the device on open, and navigation clicks can land on toggles when coordinates shift between pages. Set and verify state via the daemon's control channel, and normalize anything a click-through flipped
- Conflicting modules (e.g., stock `acer_wmi` vs replacement `linuwu_sense`) need blacklisting

## Verification

A hardware troubleshooting pass is complete when:
- The required kernel module is loaded (`lsmod | grep <module>`)
- Dependent services detect hardware correctly (logs show proper detection, not UNKNOWN)
- Module persists across kernel updates (`dkms status` installed + kernel hook present), not just across reboots
- When the user asked for durability, recovery from the simulated failure state is proven
- Any settings a verification click-through flipped are normalized
- No conflicting modules are loaded

Root work (installs, unit files, dkms) goes through the `linux-privileged-ops` skill: one script, one authorization. Worked example (Acer Nitro + DAMX/Linuwu-Sense): `references/damx-linuwu-sense.md`. Starter files: `templates/dkms.conf`, `templates/boot-guard.service`, `templates/boot-guard.sh`.
