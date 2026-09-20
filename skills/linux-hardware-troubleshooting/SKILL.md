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

### 5. Blacklist conflicting modules

Some modules conflict (e.g., `acer_wmi` vs `linuwu_sense`):

```bash
# Check if conflicting module is loaded
lsmod | grep <conflicting>

# Blacklist it
echo "blacklist <conflicting>" | sudo tee /etc/modprobe.d/blacklist-<conflicting>.conf
sudo rmmod <conflicting> 2>/dev/null || true
```

## Common Patterns

### systemd service depends on kernel module

If a daemon needs a kernel module:
- Service running ≠ module loaded
- Check service logs for "module not found" errors
- Restart service AFTER module is loaded: `sudo systemctl restart <service>`

### Kernel updates break manually-built modules

After `apt upgrade` installs a new kernel:
- Old .ko files won't load (version mismatch)
- Must `make clean && make && sudo make install` for new kernel
- DKMS modules auto-rebuild; manual builds don't

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
- After a kernel upgrade, all manually-built modules must be rebuilt — check `uname -r` vs the .ko's target
- Conflicting modules (e.g., stock `acer_wmi` vs replacement `linuwu_sense`) need blacklisting

## Verification

A hardware troubleshooting pass is complete when:
- The required kernel module is loaded (`lsmod | grep <module>`)
- Dependent services detect hardware correctly (logs show proper detection, not UNKNOWN)
- Module persists across reboots (`make install` done, or DKMS configured)
- No conflicting modules are loaded

Session-specific examples in `references/damx-linuwu-sense.md`.
