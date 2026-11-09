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
4. **A "started" message is not evidence a backgrounded server is up.** `background: true` is NOT detachment — a server launched without `setsid`/`nohup` dies with the terminal tool's process group, including when an unrelated later foreground call times out (the child is collateral). Detach with `(setsid … &)`; only the step 5 health check proves liveness, and re-probe it after any suspected death.
5. `kill -TERM` first; escalate to `kill -9` only if the process survives, and only on the PID identified in step 1.

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