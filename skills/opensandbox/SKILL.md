---
name: opensandbox
description: Use when agent code must run in an isolated Docker sandbox.
version: 1.0.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [sandbox, docker, isolation, code-execution]
    related_skills: [docker-management, hermes-cli-automation]
---

# OpenSandbox (self-hosted agent sandboxes)

Docker-backed sandbox runtime: create a container, run commands, read/write files, destroy it. Same API scales to Kubernetes, but this box runs the Docker runtime only. Upstream: github.com/opensandbox-group/OpenSandbox (Apache-2.0).

## When to Use

- Running model-generated or untrusted code without touching the host.
- Reproducible throwaway environments (a specific base image, clean FS per task).
- Parallel/one-off eval or CI-style executions where `terminal` on the host would be too dirty.
- Not for: interactive GUI work, or anything needing the user's real files (no host bind mounts configured).

## Layout on this machine

| Piece | Path |
|---|---|
| venv (server + SDK + CLI + MCP) | `~/.local/share/opensandbox/.venv` |
| server config | `~/.sandbox.toml` (api_key inside; copy in `~/.opensandbox_api_key`) |
| server service | systemd user unit `opensandbox.service` → `127.0.0.1:8080` |
| CLI | `osb` (wrapper at `~/.local/bin/osb`) |
| MCP launcher | `~/.local/share/opensandbox/bin/opensandbox-mcp` (wrapper) |
| Hermes MCP entry | name `opensandbox`, 19 tools, stdio |
| smoke test | `~/.local/share/opensandbox/smoke_test.py` |

## Install (rebuild on another machine)

```
uv venv --python 3.12 ~/.local/share/opensandbox/.venv
uv pip install --python ~/.local/share/opensandbox/.venv/bin/python \
    opensandbox opensandbox-mcp opensandbox-cli opensandbox-server
~/.local/share/opensandbox/.venv/bin/opensandbox-server init-config ~/.sandbox.toml --example docker
```

Then: set `api_key` in the TOML and mirror it to `~/.opensandbox_api_key` (chmod 600); run the server
as a systemd **user** unit with `Environment=PYTHONPATH=` and
`ExecStart=<venv>/bin/opensandbox-server --config %h/.sandbox.toml`, `Restart=on-failure`; wrap both
`osb` and the MCP entrypoint in shell scripts that `unset PYTHONPATH` before exec'ing the venv binary;
register the MCP server per `hermes-cli-automation` (`--args` last). Verify with the smoke test below
before wiring anything to it.

Hermes MCP tools: `sandbox_create`, `sandbox_connect`, `sandbox_kill`, `sandbox_list`, `sandbox_get_info`, `sandbox_renew`, `sandbox_get_metrics`, `sandbox_healthcheck`, `sandbox_get_endpoint`, `command_run`, `command_interrupt`, `file_read`, `file_write`, `file_delete`, `file_search`, `file_create_directories`, `file_delete_directories`, `file_move`, `file_replace_contents`.

## Use

MCP (preferred inside Hermes): `sandbox_create(image="python:3.12")` → `command_run(sandbox_id, command)` → `file_write`/`file_read` → `sandbox_kill`. The MCP server keeps its own sandbox registry in the stdio process, so create and kill must happen inside ONE session/process; a second process uses `sandbox_connect`.

CLI:
```
osb sandbox create --image python:3.12 --timeout 30m -o json
osb command run <id> -o raw -- python -c "print(1+1)"
osb sandbox list -o json
osb sandbox kill <id>
```

SDK: `~/.local/share/opensandbox/.venv/bin/python` then `from opensandbox import Sandbox; sb = await Sandbox.create("alpine")`.

## Pitfalls

1. **PYTHONPATH poisons every entrypoint.** The Hermes shell exports a py3.14 site-packages; any OpenSandbox binary then imports the wrong pydantic and dies with `ImportError: cannot import name 'ArgsKwargs' from 'pydantic_core._pydantic_core'`. The `osb` and `opensandbox-mcp` wrappers `unset PYTHONPATH`; when calling the venv directly prefix `PYTHONPATH=`. The systemd unit sets `Environment=PYTHONPATH=` for the same reason.
2. Server refuses to start without auth: either `api_key` in `~/.sandbox.toml` (current setup) or `OPENSANDBOX_INSECURE_SERVER=YES`. Rotating the key means editing the TOML, updating `~/.opensandbox_api_key`, then `hermes config set` the MCP env + restart both.
3. First `sandbox_create` on an unseen image pulls it — allow ≥60 s (`ready_timeout_seconds`). The execd image `opensandbox/execd:v1.1.0` is already pulled.
4. Newly registered MCP tools do not exist in the session that registered them: `/reload-mcp` or a new session.
5. Ops: `systemctl --user restart opensandbox`, `journalctl --user -u opensandbox -n 50`. Port range for sandbox publishing is 40000-60000 (`[docker] port_range_*`).
6. Sandboxes run as root inside their container on the host kernel. `drop_capabilities`, `no_new_privileges`, `pids_limit` are already set, but this is isolation for generated code, not a hostile multi-tenant boundary — for that use the Kubernetes/Firecracker path.
7. Egress control default is `mode = "dns"` with sidecar image `opensandbox/egress:v1.1.7`; leave network unconstrained unless a task needs per-sandbox policies (the sidecar adds a third host port per sandbox).
8. **Bind mounts are denied by default and the config comment lies.** `[storage] allowed_host_paths = []` reads like "empty means all allowed"; the server enforces the opposite (`HOST_PATH_NOT_ALLOWED, Allowed prefixes: []`). List real prefixes, restart the service, then mount with a volumes file:
   ```json
   [{"name":"work","host":{"path":"/abs/project"},"mountPath":"/work","readOnly":true}]
   ```
   `osb sandbox create --image node:20 --volumes-file v.json`. The MCP `sandbox_create` schema has no volumes field, so use the CLI or SDK for mounted trees.
9. Clean-room test recipe: mount the project read-only, run `npm ci && npm test` (or `uv run pytest`) in the sandbox, then `osb sandbox kill`. Dependencies reinstall every time unless the tree carries its own `node_modules`/venv or you snapshot the sandbox.

## Verify

```
PYTHONPATH= python3 ~/.local/share/opensandbox/smoke_test.py   # -> SMOKE: PASS
```

Covers create → command_run (asserts output) → file write/read → kill over the real MCP stdio path.
