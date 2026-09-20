# Fincept Terminal Qt Mismatch (2026-09-04)

## Problem
Fincept Terminal v4.4.1 (open-source build) installed from a `.deb` package failed to launch with:
```
/usr/bin/FinceptTerminal: /lib/x86_64-linux-gnu/libQt6Core.so.6: version `Qt_6.8' not found
```

## Root Cause
The open-source v4.4.1 `.deb` was built against Qt 6.8, but Ubuntu 24.04 ships Qt 6.4.2. The binary requires symbols like `Qt_6.8` that don't exist in the system's `libQt6Core.so.6`.

## Diagnosis
```bash
# Check what Qt version the app needs
strings /usr/bin/FinceptTerminal | grep "Qt_6\."

# Check what the system has
strings /usr/lib/x86_64-linux-gnu/libQt6Core.so.6 | grep "Qt_6\."
# Output: Qt_6.0, Qt_6.1, Qt_6.2, Qt_6.3, Qt_6.4 (no 6.8)

# Check the .deb's dependencies (reveals it doesn't bundle Qt)
dpkg -I fincept-terminal-4.4.1.deb | grep Depends
# Output: libc6, libstdc++6, libgcc-s1, libgl1, libegl1, ... (no qt6-* packages listed)
# This means the .deb EXPECTS system Qt to be new enough — it's not.
```

## What Didn't Work
- Upgrading system Qt 6.4 → 6.8: not available in Ubuntu 24.04 repos, would require a PPA or manual install that breaks other packages
- Using `LD_LIBRARY_PATH` to point to a newer Qt: no newer Qt available on the system

## What Worked
**Enterprise build (v5.0.2)**: Downloaded from `https://fincept.in/downloads/FinceptTerminal-5.0.2-linux-x64.deb`. This build bundles its own Qt runtime inside `/opt/fincept-terminal/bin/` and only depends on `libc6`, `libstdc++6`, `libgcc-s1`, `libgl1`, `libegl1`, etc. — no `qt6-*` packages. The binary is at `/opt/fincept-terminal/bin/FinceptTerminal`, not `/usr/bin/FinceptTerminal`.

## Key Insight
Open-source builds of Qt apps often depend on system Qt (breaks on older distros). Enterprise/commercial builds bundle Qt in `/opt/<app>/bin/` (works everywhere). Always check `dpkg -I <file>.deb | grep Depends` — if it doesn't list `qt6-*` packages, it's self-contained.

## Real Binary Path Pattern
Many `.deb` packages install to `/opt/<app>/bin/` and create a wrapper in `/usr/bin/` or `/usr/share/applications/`. The wrapper's `Exec=` line may not match the actual binary:
```bash
# Find the real binary
dpkg -L fincept-terminal | grep -E 'bin/|opt/'
# Output: /opt/fincept-terminal/bin/FinceptTerminal

# Check what the .desktop file runs
grep "^Exec=" /usr/share/applications/fincept-terminal.desktop
# Output: Exec=FinceptTerminal %U (resolves to /opt/fincept-terminal/bin/FinceptTerminal via PATH or symlink)
```
