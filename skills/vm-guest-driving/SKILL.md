---
name: vm-guest-driving
description: Use when driving or resizing a libvirt VM or qcow2 disk.
---
# Driving libvirt guests + qcow2 disk rebuilds

## Guest keyboard automation (no guest agent needed)
- Type into the guest with `virsh send-key win11 --codeset linux KEY_*` — hypervisor-level, focus-independent. Char-to-keycode mapper: `~/.hermes/cache/scratch/vtype.py` (recreate if pruned).
- Code names: `[` = `KEY_LEFTBRACE`, `]` = `KEY_RIGHTBRACE` (NOT KEY_LEFTBRACKET — virsh rejects it). Letters/digits/`KEY_SEMICOLON`/`KEY_APOSTROPHE`/`KEY_LEFTSHIFT` combos work as expected.
- UAC dialog: focused button is **No**. Accept with `KEY_LEFTALT KEY_Y` (Alt+Y accelerator), never blind Enter.
- PowerShell gotcha: `Resize-Partition C` / `Get-PartitionSupportedSize C` binds positionally to -DiskNumber and fails — always `-DriveLetter C`. Unclosed `(` leaves a `>>` continuation prompt — cancel with `KEY_LEFTCTRL KEY_C`.
- Never type passwords (lock/PIN screens stop the automation; hand those to the user).

## Seeing the guest screen
- `virsh screenshot win11 out.png` = guest framebuffer, unambiguous (better than host-window captures which composite with host apps).
- Black ~3KB PNG = guest display asleep or early boot; send any key to wake (`KEY_LEFTSHIFT`), then re-shoot.
- Host window capture: `xwd -root` + `xwdtopnm | pnmtopng` (netpbm; PIL can't read xwd, no ImageMagick on this box). Vision on dark-theme composites misidentifies which layer is the guest — prefer virsh screenshot.

## qcow2 resize/rebuild (BitLocker-locked guests)
- BitLocker blocks ALL offline fs work (libguestfs, ntfsresize) — the fs shrink must run inside Windows (`Resize-Partition -DriveLetter C -Size ([math]::Max((Get-PartitionSupportedSize -DriveLetter C).SizeMin,28GB))` shrinks to target or the minimum possible). `powercfg /h off` first frees hiberfil = more shrink room.
- Delete the tail Recovery partition (`Get-Partition|?{$_.Type -eq 'Recovery'}|Remove-Partition -Confirm:$false`) — it sits at the old disk tail and blocks truncation.
- Rebuild: `qemu-img create -f qcow2 new.qcow2 <G>G` + `virt-resize old new` (block copy, BitLocker-safe, writes a fresh valid GPT). Sum of partition sizes +16MB = minimum target. virt-resize creates a small 'surplus' partition if the output has slack — harmless.
- Swap files, `chown --reference` old file, boot-test BEFORE deleting the old image (virsh screenshot to sign-in screen = pass).
- Root-free volume ops through libvirtd: `virsh vol-delete --pool default <name>` works WITHOUT pkexec/sudo even though /var/lib/libvirt/images is root-owned (use it for cleanup; probe `virsh vol-list --pool default`).
- `virsh domblkinfo win11 sda` = capacity/allocation without root. Allocation << capacity on sparse qcow2 — judge host usage by allocation, not virtual size.

## PKExec on this box
Launch `/usr/bin/polkit-gnome-authentication-agent-1` first (DISPLAY=:0), and keep the screen clear — fullscreen windows hide the auth dialog (requests time out or get 'Request dismissed').