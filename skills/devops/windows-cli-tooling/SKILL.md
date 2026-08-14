---
name: windows-cli-tooling
description: Install, locate, and verify CLIs on Windows git-bash.
---

# Windows CLI Tooling (git-bash / MSYS)

Environment facts and install patterns for `C:\Users\YOUR_USERNAME` (Windows, git-bash shell, uv + npm + gh + node present, pipx absent).

## Pitfall: git and bash disagree on `/tmp` (MSYS path divergence)

`git clone <url> /tmp/foo` **succeeds** but the files are NOT where bash `ls /tmp/foo` looks:

- git (msys build) resolves `/tmp` → `C:\tmp\foo`
- bash `ls`/`readlink` resolve `/tmp` → `C:\Users\YOUR_USERNAME\AppData\Local\Temp`

Symptoms: `ls: cannot access '/tmp/foo'` right after a successful clone; `git -C /tmp/foo <cmd>` works while `ls` fails.

Fix:
```bash
git -C /tmp/foo rev-parse --show-toplevel   # prints the REAL path git used
cygpath -w /tmp                              # show what bash thinks /tmp is
```
Avoid the class entirely: clone to an explicit Windows path (`C:/Users/YOUR_USERNAME/.agent-reach/src`) instead of `/tmp`.

## Pattern: `uv tool install` is the pipx replacement here

pipx is NOT installed; `uv` is (at `~/AppData/Local/hermes/bin/uv`). For any standalone Python CLI:

```bash
uv tool install <pypi-name>          # from PyPI
uv tool install C:/path/to/repo      # from a local checkout
uv tool install https://github.com/owner/repo/archive/main.zip  # from a repo zip
```

- Binaries land in `~/.local/bin/` which IS on PATH — no venv activation needed.
- **Pitfall:** a tool's own dependencies are NOT exposed as commands. E.g. `agent-reach` bundles `yt-dlp` as a dependency, but there is no `yt-dlp` command until you also run `uv tool install yt-dlp`.

## Pattern: Node CLIs via npm global

```bash
npm install -g mcporter
```
→ installs to `~/AppData/Roaming/npm/`, already on PATH.

## Verify with live smoke tests, not just the installer's doctor

Installers/doctors check config presence, not live reachability. After setup, prove each channel with one real call (real URL, real query). A probe failing on the FIRST test artifact is often the artifact (geo-blocked/dead video, etc.) — retry once with a different target before concluding the tool is broken.

## Config file conventions (Windows)

| Tool | Config path |
|------|-------------|
| yt-dlp | `~/.config/yt-dlp/config` |
| mcporter | `~/.mcporter/mcporter.json` (`mcporter config add <name> <url> --scope home`) |
| agent-reach | `~/.agent-reach/` (config, tools, cookies) |

## Pattern: Scheduled tasks flashing CMD windows (hidden-VBS fix)

Symptom: random CMD window pops on the desktop. Culprit: a Task Scheduler task running `cmd.exe /c script.cmd` with `<LogonType>InteractiveToken</LogonType>`. The window stays visible as long as the cmd runs — a `curl -m 5` health check inside makes it linger ~5s whenever the target is slow/down (so it looks "random").

Diagnose:
```bash
# all cmd/bat-launched tasks
powershell.exe -NoProfile -Command "Get-ScheduledTask | Where-Object {\$_.Actions.Execute -match 'cmd|bat'} | Select-Object TaskName, @{n='Action';e={(\$_.Actions | ForEach-Object {\$_.Execute + ' ' + \$_.Arguments}) -join '; '}} | Format-Table -AutoSize -Wrap"
# recent runs (match flash timestamps)
powershell.exe -NoProfile -Command "Get-ScheduledTask | Where-Object {\$_.State -ne 'Disabled'} | Get-ScheduledTaskInfo | Where-Object {\$_.LastRunTime -gt (Get-Date).AddHours(-12)} | Sort-Object LastRunTime -Descending | Select-Object -First 12 TaskName, LastRunTime | Format-Table -AutoSize"
```

Fix — keep the .cmd, wrap it in a hidden VBS launcher, repoint the task:
```vbs
' script_hidden.vbs
Dim sh
Set sh = CreateObject("WScript.Shell")
sh.Run "cmd /c ""C:\path\to\script.cmd""", 0, False
```
```bash
schtasks /change /tn "Task Name" /tr "wscript.exe \"C:\path\to\script_hidden.vbs\""
schtasks /run /tn "Task Name"   # test-fire; confirm no window appears
schtasks /query /tn "Task Name" /xml | grep -E "<Command>|<Arguments>"   # verify
```
- `schtasks /change` may print a run-as-password warning — harmless for InteractiveToken tasks while logged in.
- `start` calls INSIDE the .cmd inherit the hidden state as long as what they launch also hides itself (VBS with `Run ..., 0, False` is safe).

## Reference

- `references/agent-reach-setup.md` — full Agent Reach install recipe (uv tool + yt-dlp + mcporter/Exa + doctor fixes + channel status) from the 2026-08-13 setup.
