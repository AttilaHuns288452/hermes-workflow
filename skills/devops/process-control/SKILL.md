---
name: process-control
description: Use when managing dev servers or background processes.
---

# Process control

Agent tool calls run inside a compound shell whose full command line is visible to `pkill -f` / `pgrep -f`. Pattern-based process management kills the agent's own shell or self-matches its own verification text.

## Restart procedure (dev server)

1. Identify the holder: `ss -ltnp | grep :3000` (or `fuser -v 3000/tcp`).
2. Free the port: `fuser -k 3000/tcp`.
3. Confirm the port is gone (same probe as step 1, in a SEPARATE tool call).
4. Start detached: `(setsid node server.js > /tmp/srv.log 2>&1 &)` — log to a file you will read.
5. Readiness = a real HTTP check (`curl -s localhost:3000/api/health`); on failure read the log first.

## Always-on rules

1. **Kill by port, never by pattern.** `pkill -f PATTERN` matches the agent's own compound shell whenever the pattern text appears anywhere in the same command line: in the restart command joined with `&&`, in file paths, or in a later `pgrep -af` verification whose arguments repeat the pattern. A bracket escape (`[n]ode server\.js`) only stops the pattern from matching itself; it does not protect literal occurrences of the plain text elsewhere in the command.
2. **Split kill, launch, and verify into separate tool calls — and never write the plain target text into a `pkill -f` pattern.** Splitting is necessary but NOT sufficient: a lone `pkill -f 'serve -l 4688'` still SIGTERMs the agent's own shell, because the pattern literal sits in its own argv and `pkill -f` matches full command lines. Escape a character inside the pattern (`pkill -f 'serve -l 46[8]8'`) or, better, kill by port (`fuser -k 3000/tcp`). A combined kill+restart call dies before the new server starts (the launch text self-matches), and a verification command that repeats the plain text reports the agent's own shell as the running process.
3. **Identify before you kill.** Name-based kills can hit a same-named process that is not the one bound to the port in question; the port holder is the identity that matters.
4. **A "started" message is not evidence a backgrounded server is up.** `background: true` alone does not detach from the terminal tool's process group: when an unrelated later foreground call times out, the child can be killed as collateral. Prefer `background=true` (it tracks the pid and can notify on exit) and health-check in a SEPARATE call. A `(setsid cmd > log 2>&1 &)` subshell is the way to spawn a browser or other long-lived child from inside a command, and the current terminal tool accepts it when it is a plain subshell in the middle of a compound command — earlier blanket notes that it is refused are version-specific, so probe rather than assume. Only the step 5 health check proves liveness, and re-probe it after any suspected death.
5. `kill -TERM` first; escalate to `kill -9` only if the process survives, and only on the PID identified in step 1.
6. **A deleted working directory deadlocks every later call.** The terminal wrapper restores the session cwd with `cd <saved path> || exit 126` *before* your command runs, so after you delete the directory a job was launched from (or your own), every call fails on that `cd` — even `mkdir` never executes, and the error just names the missing path. Recreate the directory from a non-shell tool (`execute_code` with `os.makedirs`) so the wrapper's `cd` succeeds; retrying the shell cannot fix it. Never `rm -rf` the directory a background session was started in while the shell session is still live.

## High CPU triage (leaked headless browsers)

1. Rank by usage: `ps -eo pid,ppid,pcpu,pmem,etimes,args --sort=-pcpu | head -20`. `pcpu` is the average over the process LIFETIME, so a room-temperature background job and a 20-second spawn burst print the same number — always read `etimes` alongside it.
2. Get the offender's real identity from its argv, not its binary name. Every Chromium-family process matches `grep -i chrom`: the user's Brave, the Hermes desktop Electron wrapper, and any Playwright chromium. `--user-data-dir=<path>` and `--type=<role>` are what separate them.
3. `--type=gpu-process` at hundreds of percent together with `--use-angle=swiftshader` / `--enable-unsafe-swiftshader` means software-GL rasterization: one headless page will eat every core it is given. That is a leak amplifier, not a graphics bug to go fix.
4. Kill the tree by its unique profile path, never by binary name: TERM then KILL on the same pattern, then remove the profile dir. `pkill -TERM -f 'user-data-dir=/tmp/cdp-pro[f]'` → `sleep 3` → `pkill -KILL -f 'user-data-dir=/tmp/cdp-pro[f]'` → `rm -rf /tmp/cdp-prof`. Bracket a character so the pattern cannot match the agent's own shell.
5. Verify in a LATER call: `pgrep -af 'cdp-pro[f]'` empty, the debugging port free (`ss -tlnp | grep 9333`), and `uptime` trending down. Load average is a 1/5/15-minute average — it lags the kill by about a minute, so read the trend rather than the first reading.
6. Assume the leak is self-inflicted until proven otherwise. A persistent headless chromium on `/tmp/<something>-prof` with `--remote-debugging-port=N` is a browser-automation backend (`browser_exec`, a scraper, an agent session), and its owner exited without closing the browser. Check what launched it (`ps -o ppid` → `systemd --user` means orphaned) before blaming the user's own browser.
7. **A shell whose command line merely MENTIONS the profile path is not the browser.** Matching kill targets by cmdline substring (`if udir in raw`) reaches shells that launched the browser (`(chromium ... &)`), including the agent's own tool shell — a reaper written that way SIGTERMs the process running the test. Walk the real parent/child closure instead: build a `pid -> ppid` map from `/proc/<pid>/stat` (field 2 after the `)` split) and expand transitively from the browser roots. `pkill -f` on a bracketed profile path is the same class of shortcut and has the same blast radius.

## Idle-browser reaper (auto-close, not just alert)

A reporting watchdog leaves the user to kill it by hand every time. A reaper is safe only when it can prove all three of: ownership, idleness, and age. `~/.hermes/scripts/cdp_browser_reaper.py` is the working instance (cron every 5 min, `--no-agent`, `deliver local`, prints only when it reaps). Guard set:

1. **Scope the class, not one vendor.** Match `--headless` plus a `chrome` argv; accept both `--headless=new` and bare `--headless`. Housekeeping: skip `~/.hermes/browser-profile` — that is the gateway's long-lived Brave, idle by design, and reaping it breaks browser tools.
2. **Idleness = no live client on the debug port.** Read the port from `--remote-debugging-port=N`, or from `DevToolsActivePort` in the profile when the flag is `0`. A driver holds an ESTABLISHED socket whose LOCAL port is N: `ss -tnp state established | grep ":N\s"`. If the probe itself errors, return busy — never kill blind.
3. **Two-strike, with an age floor.** First idle sighting writes a marker file and spares the process; the next tick with the marker still present kills. Require `> 120s` old before the first count — a driver that just launched has not connected yet. Two-strike at 5-min ticks gives a ~10 min idle floor at near-zero false-positive risk.
4. **Liveness checks must exclude zombies.** `os.path.exists('/proc/<pid>')` stays true for a zombie, so a test asserting death fails on a successfully killed process. Read `/proc/<pid>/stat` and require the state letter != `Z`.
5. **Verify with both directions in one self-check**: spawn a real headless browser, confirm tick 1 spares it, tick 2 reaps it and its port closes; spawn a second with a held socket to the port and confirm it survives two ticks. `~/.hermes/scripts/test_cdp_browser_reaper.py` does exactly this.

## Work that must outlive the session (and may kill its own app)

A one-shot maintenance job whose job is to stop, compact or restart the gateway/desktop that hosts the agent cannot be launched from the agent's own process tree: it dies with its target. Detaching harder inside the same session does not change that ownership.

Use a transient **systemd user** unit so the user manager owns it:

```
systemd-run --user --collect --unit=<name> --on-active=90s /bin/bash /path/to/job.sh
systemctl --user list-timers --all | grep <name>      # confirm it is armed
systemctl --user stop <name>.timer                    # cancel before it fires
```

- `--on-active` gives the current turn time to finish and deliver its message before the app closes.
- `--collect` unloads the unit after exit; otherwise failed units pile up.
- The script must log to a file and be safe to re-run: the agent is gone by the time it executes, so the only evidence afterwards is that log plus the post-restart state.
- Verify the outcome from the log and a fresh process (sizes, integrity check), never from the fact that the unit was scheduled.