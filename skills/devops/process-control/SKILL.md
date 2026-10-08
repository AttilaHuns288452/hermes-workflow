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
2. **Split kill and verify into separate tool calls.** A verification command that mentions the process pattern self-matches and reports the agent's own shell as the running process.
3. **Identify before you kill.** Name-based kills can hit a same-named process that is not the one bound to the port in question; the port holder is the identity that matters.
4. **A "started" message is not evidence a backgrounded server is up.** Processes started without `setsid`/`nohup` die with the terminal tool's process group; only the step 5 health check proves liveness.
5. `kill -TERM` first; escalate to `kill -9` only if the process survives, and only on the PID identified in step 1.