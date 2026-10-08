---
name: lan-share
description: Use when sharing files with a Windows laptop over Ethernet.
---

# lan-share — direct-cable Linux↔Windows Samba sharing

Tool: `~/.local/bin/lan-share` (subcommands: `start|status|stop|reset|selftest`, bare = interactive). Also for maintaining this setup or debugging direct-cable SMB between laptops.
Design: detect (nmcli ethernet device, never hardcode names) → plan minimal changes → apply (state ledger `~/.lan-share/state` records ONLY tool-made changes) → layered tests → print Windows instructions. Env overrides: LAN_SHARE_IP, LAN_SHARE_PEER, LAN_SHARE_NAME, LAN_SHARE_DIR.

## Pitfalls (all hit live, 2026-09-26)

1. **smbclient `put` where source path == target file (same file through the share) transfers 0 bytes silently and returns exit 0.** smbd truncates the destination first, then the client streams the now-empty same file. Stage test payloads OUTSIDE the share dir, and compare with `cmp` — never trust smbclient exit codes alone.
2. **`ufw status` prints Action `ALLOW`; only `ufw status verbose` prints `ALLOW IN`.** Grepping 'ALLOW IN' against compact output silently matches nothing → false "firewall blocks" reports. Grep `ALLOW` or use verbose consistently.
3. **Nested `sudo` inside a script fails in non-tty contexts** ("a terminal is required to read the password"). Run such tools via top-level `sudo tool …`, resolve the real user via `$SUDO_USER` for share/state/home paths, and make read-only checks degrade to "unknown" instead of a false state (never report "ufw inactive" when the probe failed).
4. **nmbd hangs at startup with `interfaces = <iface>` when that iface has no address** (cable unplugged): "No local IPv4 non-loopback interfaces available" → systemd timeout. Don't restrict Samba to the cable interface; enforce isolation with `hosts allow = 127. <subnet>.` in [global] plus a `ufw allow in on <iface>` rule — same guarantee, hotplug-safe.
5. Backup before ANY smb.conf edit must `mkdir -p` the backup dir first and abort on cp failure — a printed "Backup:" line for a file that was never written is worse than no backup.

## Facts for this machine

- Linux side: `192.168.50.1/24` on the NM ethernet profile (auto-detected), share `[LAN-Share]` → `~/LAN-Share`, guest+force user attila. Pre-existing `[Shared]` → `~/Shared` untouched.
- Windows side per classmate: `192.168.50.2/255.255.255.0`, no gateway/DNS, `netsh advfirewall firewall set rule group="File and Printer Sharing" new enable=Yes`, share folder with Everyone Read/Write. Access Linux via `\\192.168.50.1\LAN-Share` (auth as `attila` + Samba password unless AllowInsecureGuestAuth=1). Never enable SMB1.
- Full smb.conf backups accumulate in `~/.lan-share/backups/`.