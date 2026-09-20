# DAMX + Linuwu-Sense — Acer Nitro AN515-57 on Linux

## Symptom

NitroSense key (keycode 425) doesn't launch Div Acer Manager Max (DAMX). The `damx-daemon.service` is running but reports:

```
ERROR - linuwu_sense module not found. Please install the linuwu_sense driver first.
WARNING - Unknown laptop type detected
```

## Root Cause

The `linuwu_sense` kernel module (which provides fan/thermal/RGB controls for Acer Nitro/Predator laptops) was not loaded. The daemon runs but can't detect hardware without it.

Additionally, the pre-built `.ko` file was for a different kernel version and failed to load with:

```
linuwu_sense: Unknown symbol sparse_keymap_entry_from_scancode (err -2)
linuwu_sense: Unknown symbol sparse_keymap_report_event (err -2)
linuwu_sense: Unknown symbol sparse_keymap_setup (err -2)
```

## Fix

```bash
cd ~/Documents/Apps/DAMX-1.0.2/Linuwu-Sense

# Rebuild for current kernel (7.0.0-31-generic)
make clean && make

# Load missing dependency
sudo modprobe sparse-keymap

# Insert module
sudo insmod src/linuwu_sense.ko

# Restart daemon to pick up module
sudo systemctl restart damx-daemon

# Persist across reboots
sudo make install
```

## After Fix

```
Detected laptop type: NITRO
Base path: /sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/nitro_sense
Available features: battery_limiter, backlight_timeout, battery_calibration,
                    thermal_profile, fan_speed, usb_charging
```

## Key Technical Details

- **Module location:** `/home/attila/Documents/Apps/DAMX-1.0.2/Linuwu-Sense/src/linuwu_sense.ko`
- **Daemon:** `/opt/damx/daemon/DAMX-Daemon` (systemd service: `damx-daemon.service`)
- **GUI:** `/opt/damx/gui/DivAcerManagerMax`
- **Kernel module dependency:** `sparse-keymap` (must be loaded first)
- **Conflicting module:** `acer_wmi` (blacklisted by `make install`)
- **Nitro key binding:** xbindkeys binds keycode 425 → launches `/opt/damx/gui/DivAcerManagerMax`
- **Kernel:** 7.0.0-31-generic (Ubuntu 24.04 HWE)
- **Laptop:** Acer Nitro AN515-57

## Lessons

1. A running systemd service ≠ its kernel module is loaded
2. `insmod` is volatile; `make install` persists across reboots
3. Kernel modules may have dependencies (`sparse-keymap`) that must be loaded first
4. Pre-built `.ko` files from GitHub may be for a different kernel — always `make clean && make` for current kernel
5. `dmesg | grep "Unknown symbol"` tells you exactly what's missing
