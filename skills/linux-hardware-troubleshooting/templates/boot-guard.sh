#!/bin/bash
# Boot self-healing guard for a vendor kernel module + its daemon.
# Replace <module>, <module>/<ver>, <module-src-dir>, <daemon>.service.
set -u
KVER=$(uname -r)

if ! modprobe <module> 2>/dev/null; then
  echo "<module> missing for $KVER - repairing"
  dkms install <module>/<ver> -k "$KVER" --force >/dev/null 2>&1 \
    || make -C <module-src-dir> install >/dev/null 2>&1
  modprobe <module> 2>/dev/null
fi

# --no-block is REQUIRED: a blocking restart deadlocks against this unit's
# Before=<daemon> ordering (the daemon's start waits for us, we wait for its
# restart job). One line without it and the boot hangs in "activating".
systemctl --no-block try-restart <daemon>.service 2>/dev/null

if lsmod | grep -q '^<module>'; then
  echo "GUARD_OK"
else
  echo "GUARD_FAILED"
  exit 1
fi
