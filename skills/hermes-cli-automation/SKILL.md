---
name: hermes-cli-automation
description: Use when adding MCP servers or skills to Hermes.
---

# Hermes CLI Automation

Operating the Hermes CLI from inside an agent session: no TTY, no human at the prompt, and a tool result that must be real. Covers non-interactive registration of MCP servers and skills, and end-to-end verification in the app. For the full CLI command reference see the bundled `hermes-agent` skill; for per-server config quirks (Composio, Figma, Firecrawl, env-block secrets) see `mcp-integrations`.

## The confirmation-prompt rule (always-on)

Every `hermes ... add/install/create` subcommand can end in an interactive confirm. With no TTY the prompt reads EOF and the command CANCELS — while still exiting with plausible-looking output. Always pipe an answer, and always read the LAST line for `✓ Saved` vs `Cancelled` — exit code alone never proves the save landed.

- `printf 'Y\n' | hermes mcp add ...` works — both prompts ("Enable all N tools?" and "Save config anyway?") consume stdin.
- `hermes skills install <url>` does NOT accept piped input (TTY-bound confirm, exits `Installation cancelled`). Skip the installer: `curl -fsSL <raw SKILL.md url>` and write it directly to `~/.hermes/skills/<name>/SKILL.md` — the exact destination the installer uses — then confirm with `hermes skills list`.
- Registering BEFORE the backend works: `hermes mcp add` fails its connect probe, then asks "Save config anyway? [y/N]" and saves the entry DISABLED. There is no `hermes mcp enable` subcommand (the CLI offers only serve/add/remove/list/test/configure/login/reauth/picker/catalog/install) — flip it with `hermes config set mcp_servers.<name>.enabled true`, then `hermes mcp test <name>` once the backend is up.
- Disabling is config-only too: there is no `hermes mcp disable`. Use `hermes config set mcp_servers.<name>.enabled false` and confirm `hermes mcp list` shows `✗ disabled`.
- **A pipeline hides the real exit status.** `printf 'Y\n' | hermes mcp add ... | tail -3 || hermes config set ...` never runs the fallback: the last command in the pipe (`tail`) exits 0, so `||` sees success while the command that mattered failed. Run the recovery as its own call, or branch on the output text (`✓ Saved` vs `Cancelled`/error line).

## Registering a third-party MCP server (worked procedure)

1. **Read the repo's install docs.** Fetch raw files and release assets with `curl` into `/tmp` — `web_extract` is for HTML pages; raw file endpoints and binaries need curl. Check what the server actually exposes (the tool count in a README is a hypothesis).
2. **Probe the server standalone BEFORE registering.** Pipe JSON-RPC `initialize` + `tools/list` into the launch command: `scripts/probe_mcp_stdio.py -- <command> [args...]`. The tool count is your baseline; a server that won't answer standalone will never pass `hermes mcp test`.
3. **Python/PyPI server on a PEP 668 host:** isolated venv, never system python —
   `uv venv ~/.local/share/mcp-servers/<name>/.venv && uv pip install --python ~/.local/share/mcp-servers/<name>/.venv/bin/python <pypi-pkg>`
   Register with the venv interpreter in module form (works even when the package ships no console script):
   `printf 'Y\n' | hermes mcp add <name> --command <venv>/bin/python --args -m <pkg_module>`
   Pitfall: `--args` must be the LAST option (argparse `nargs=*` swallows trailing options into args); `--env` goes before it. There is no `--stdio` flag — anything unknown trailing after `--args` becomes junk server argv and kills the handshake.
3b. **Node/npm server:** register an absolute interpreter + absolute entry script (`--command /usr/bin/node --args /path/to/pkg/entry.mjs`), never the package's bin shim or a bare `npx`:
    - A fresh install whose bin was never linked (`npx <pkg>` → `<bin>: not found` despite a clean install) is a packaging bug — `npm i -g <pkg>` usually links the bin, but pointing at the entry script directly works regardless of linking.
    - A shebang bin (`#!/usr/bin/env node`) dies silently when the MCP spawn's PATH lacks the interpreter dir — the spawn env is not the login shell env; absolute paths sidestep it.
    - Cold-start `npx` downloads can exceed the 30s connect window — pre-warm the package (run the command once) or install globally before registering; raise `--connect-timeout` for heavyweight servers.
3c. **Repo-vendored server (the repo itself is the package):** clone to a durable location (`~/Documents/Projects/<name>`), `uv sync` in the repo, and register `<repo>/.venv/bin/python` with `--env PYTHONPATH=<repo-root>` (plus `--env PYTHONUNBUFFERED=1` for py servers). `hermes mcp add` has no `--cwd` flag, so PYTHONPATH is what makes a repo-local module importable from the gateway's spawn directory.
4. **Verify in layers** — each layer catches a different failure:
   - `hermes mcp list` → saved + enabled (tool count shown)
   - `hermes mcp test <name>` → handshake + tool discovery. **`Tools discovered: 0` is a failure, not a pass:** a server that connects and exposes nothing still pays its connect time every session. Fix the backend or disable it.
   - real end-to-end: `hermes chat -q "call <tool> with <simple args> and report one line"` — proves a fresh session can invoke a tool. Newly registered MCP tools do NOT appear in the session that registered them; 'registered' is not 'working' until a fresh session calls one. Cheaper equivalent when you don't want to spend a fresh agent turn: `scripts/mcp_call_tool.py <tool> '<json-args>' -- <command> [args...]` invokes one tool over raw JSON-RPC against the launch command.
   - run that end-to-end call from a FOREIGN cwd (e.g. `/tmp`): a server that resolves its config or `.env` relative to cwd passes from the repo directory and fails from the gateway's spawn directory. Prefer a tool whose result reports its own resolved config (models, endpoints) — that output is the proof.
5. **Companion skill from the repo (if shipped):** install via direct file write (see prompt rule), but land it adapted, not copied — run the `workflow/external-skill-import` transforms first (rewrite install placeholders like `{{PY}}` / `/path/to/<tool>` to this machine's real paths across the whole tree, translate the source runtime's tool names and brand prose). Confirm via `hermes skills list`, then rebuild LightRAG.
6. **GUI-side extensions** (desktop app modules, e.g. live-deploy bridges): download the release asset with curl, hand the user the in-app menu steps. GUI menus and any sign-in wall are the user's click — never guess credentials.

Notes: `resources/list` may legitimately return empty even when the project advertises resources — `tools/list` count is the metric that matters. Some servers log to stderr on every JSON-RPC request; that is normal, parse stdout line-wise.

## Verification (runnable check)

`scripts/probe_mcp_stdio.py` — pipes `initialize`/`tools/list`/`resources/list` into any stdio MCP command and prints counts + sample tool names. Use it before registration (step 2) and any time a registered server misbehaves; exit 1 means the launch command itself is wrong (missing package, bad args, PATH) — fix that before touching config.

For a silent `Connection closed` (no error, empty child stderr) follow `references/mcp-stdio-debugging.md` — the escalation chain ends in `scripts/mcp_sdk_roundtrip.py`, which runs Hermes's own MCP client stack against the same command to separate server faults from launch faults.
