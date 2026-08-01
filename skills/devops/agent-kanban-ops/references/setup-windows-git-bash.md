# agent-kanban setup on Windows / git-bash (operator notes)

Findings from wiring the `ak` CLI (1.15.0) against the hosted https://agent-kanban.dev
from a Hermes terminal session (git-bash on Windows).

## Setup order matters — register the machine BEFORE leader login

- `ak config set --api-url https://agent-kanban.dev --api-key <key>` — saves creds to
  `~/.config/agent-kanban/config.json`.
- `ak auth login --leader-agent --username <u> --name <n>` fails with
  `Machine not registered` (server-side, HTTP 400 on the session-create call) **if no
  machine exists yet**. The server binds agent sessions to a registered machine.
- Registering the machine happens via `POST /api/machines`, which the `ak start`
  daemon does on boot. If `ak start` can't run (see below), register manually:
  ```bash
  curl -sS -X POST "https://agent-kanban.dev/api/machines" \
    -H "Authorization: Bearer $AK_KEY" -H "Content-Type: application/json" \
    -d '{"name":"<machine>","os":"win32 x64","version":"1.15.0",\
         "runtimes":[{"name":"hermes","status":"ready","checked_at":"<ISO>"}],\
         "device_id":"<any-stable-hex>"}'
  ```
  Server upserts by `device_id` (same id returned on re-register). Then the leader
  login succeeds. Verify: `ak auth whoami` → `Type: leader / Runtime: hermes`.

## `ak start` daemon cannot run against hosted agent-kanban.dev

`ak start` → `POST /api/machines` → requires the response to include
`runner.onboarding` (origin + projectId + environmentId for the AMA runner).
The hosted service returns `"runner": null` for local machines, so the daemon exits
with `Machine registration did not return runner onboarding details`. Server-side
limitation — no CLI flag/env bypass exists in 1.15.0. The leader/board/task workflow
(`ak get board`, `ak apply -f task.yaml`, `ak task ...`) works fine without the
daemon; only local worker spawning is gated.

## `ak` command breaks in git-bash: "Could not locate hermes process in ancestry"

`ak auth login --leader-agent` / `ak get board` fail with
`Could not locate hermes process in ancestry` when invoked as bare `ak` from a
Hermes terminal. Root cause: the CLI detects its host runtime by walking the native
Windows process tree (a `process-tree.node` addon) from `process.ppid` up, matching
a regex (e.g. `hermes_cli\.main`) against each ancestor's command line. The npm
install ships an `#!/bin/sh` shim that **truncates the walk**: `sh.exe`/`bash.exe`/
`env.exe` script interpreters have no resolvable parent in the addon's view, so the
hermes process is never reached.

Empirically on this machine:
- `node dist/index.js ...` direct → walk reaches `hermes_cli.main serve` ✅
- `.cmd` file → `cmd.exe` layer keeps the chain ✅ (walk works through cmd.exe)
- `#!/bin/sh` / `#!/bin/bash` / `#!/usr/bin/env node` script → walk stops at the
  interpreter ❌

**Fix (tested components):** make bare `ak` delegate through `cmd.exe`, whose chain
stays intact. Replace the npm `ak` shim (or add an earlier-PATH wrapper):
```bash
cat > "$HOME/AppData/Roaming/npm/ak" <<'EOF'
#!/bin/sh
exec cmd //c "C:\\Users\\Attila\\AppData\\Roaming\\npm\\ak.cmd" "$@"
EOF
chmod +x "$HOME/AppData/Roaming/npm/ak"
```
Do NOT simply delete the shim and rely on `ak.cmd` fallback — git-bash does NOT
fall back to `.cmd` for a bare command name; the command becomes "not found".
Verified workaround meanwhile: `node "$(npm root -g)/agent-kanban/dist/index.js" ...`.

## Key hygiene

Machine API keys are long-lived and get echoed into terminal history/config files.
Mask with sed when displaying (`sed 's/ak_[A-Za-z0-9]*/ak_***/'`); recommend
rotation if a transcript containing the key is ever shared.

## Probing the ancestry walk (debug technique)

Dump what the CLI's native addon sees from your current process:
```bash
node -e "const {createRequire}=require('module');const path=require('path');\
const root='$(npm root -g)/agent-kanban/dist/index.js';\
const addon=createRequire(root)(path.join(path.dirname(root),'native','win32-x64','process-tree.node'));\
for(const p of addon.getProcessAncestry(process.ppid,32))console.log(p.pid,'|',(p.commandLine||'').slice(0,100));"
```
The addon lives at `<pkg>/native/win32-x64/process-tree.node` — other CLIs that
detect their host agent (AMA runner etc.) use the same mechanism.
