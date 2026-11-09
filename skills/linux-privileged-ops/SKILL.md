---
name: linux-privileged-ops
description: Use when a task needs root and sudo demands a password.
version: 1.0.0
author: Attila
license: MIT
platforms: [linux]
---

# Linux privileged operations (pkexec + Polkit)

An agent session cannot type the user's password, and `sudo` prompts for one. Privileged work on this Linux box therefore runs as ONE root script through `pkexec`: the OS draws an authentication dialog, the user authorizes it, the script runs as root. The agent never sees or handles the password. Applies to installs, kernel modules, systemd units, permissions — anything root.

## When to Use

- Installing packages, drivers, or kernel modules that need root
- Creating or enabling systemd units, udev rules, modprobe blacklists
- Any write under `/etc`, `/opt`, `/usr`, `/lib/modules`
- A command the terminal tool refuses as non-root

## Procedure

1. Probe first: `sudo -n true`. If it fails, take the pkexec route immediately — never ask the user to paste a password into chat.
2. Write ONE script containing every privileged step (installs, unit files, enables, restarts, self-test), ending with a machine-checkable DONE marker (`echo INSTALL_DONE`) so completion is detectable in the log.
3. `chmod +x` the script before launching.
4. Ensure a Polkit authentication agent is running — the agent is what draws the dialog. Check with a self-match-safe pattern: `pgrep -af "[p]olkit-gnome"` (Mint may ship gnome/mate/kde variants). If absent, start `/usr/bin/polkit-gnome-authentication-agent-1` as a background process; autostart entries can exist while the process is dead.
5. Launch `pkexec /path/to/script.sh > /tmp/<name>.log 2>&1` with `background=true`, and in the SAME turn ask the user (clarify) to authorize the dialog that just appeared — the dialog carries no context of its own, the question is the explanation.
6. Poll the log for the DONE marker, then verify the effects from an unprivileged read (files present, `systemctl is-enabled`/`is-active`, observable state). A finished script is not a verified change.

## Pitfalls

- pkexec on a non-executable script fails with a bare "Permission denied" and nothing else — `chmod +x` first.
- Batch ALL root steps into one script per authorization. Every separate pkexec is another password prompt; users accept one, not four. If a new need appears mid-task, fold it into one consolidated re-run instead of spawning a second dialog per step.
- The Polkit dialog shows only the program name — the clarify question must state what the script does and why.
- Unprivileged `systemctl` operations on system units hit Polkit too — same route, same script.
- `pgrep -f`/`pkill -f` self-match the agent's own compound shell (the pattern text rides in its command line) — bracket-escape the pattern; load the `process-control` skill for the full rule.
- Never request, accept, or echo the user's password (including via `sudo -S` with pasted input). The OS dialog is the only legitimate path.
