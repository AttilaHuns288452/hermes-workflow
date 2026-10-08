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

## Registering a third-party MCP server (worked procedure)

1. **Read the repo's install docs.** Fetch raw files and release assets with `curl` into `/tmp` — `web_extract` is for HTML pages; raw file endpoints and binaries need curl. Check what the server actually exposes (the tool count in a README is a hypothesis).
2. **Probe the server standalone BEFORE registering.** Pipe JSON-RPC `initialize` + `tools/list` into the launch command: `scripts/probe_mcp_stdio.py -- <command> [args...]`. The tool count is your baseline; a server that won't answer standalone will never pass `hermes mcp test`.
3. **Python/PyPI server on a PEP 668 host:** isolated venv, never system python —
   `uv venv ~/.local/share/mcp-servers/<name>/.venv && uv pip install --python ~/.local/share/mcp-servers/<name>/.venv/bin/python <pypi-pkg>`
   Register with the venv interpreter in module form (works even when the package ships no console script):
   `printf 'Y\n' | hermes mcp add <name> --command <venv>/bin/python --args -m <pkg_module> --stdio`
   Pitfall: `--args` must be the LAST option (argparse `nargs=*` swallows trailing options into args); `--env` goes before it.
4. **Verify in layers** — each layer catches a different failure:
   - `hermes mcp list` → saved + enabled (tool count shown)
   - `hermes mcp test <name>` → handshake + tool discovery
   - real end-to-end: `hermes chat -q "call <tool> with <simple args> and report one line"` — proves a fresh session can invoke a tool. Newly registered MCP tools do NOT appear in the session that registered them; 'registered' is not 'working' until a fresh session calls one.
5. **Companion skill from the repo (if shipped):** install via direct file write (see prompt rule), confirm via `hermes skills list`.
6. **GUI-side extensions** (desktop app modules, e.g. live-deploy bridges): download the release asset with curl, hand the user the in-app menu steps. GUI menus and any sign-in wall are the user's click — never guess credentials.

Notes: `resources/list` may legitimately return empty even when the project advertises resources — `tools/list` count is the metric that matters. Some servers log to stderr on every JSON-RPC request; that is normal, parse stdout line-wise.

## Verification (runnable check)

`scripts/probe_mcp_stdio.py` — pipes `initialize`/`tools/list`/`resources/list` into any stdio MCP command and prints counts + sample tool names. Use it before registration (step 2) and any time a registered server misbehaves; exit 1 means the launch command itself is wrong (missing package, bad args, PATH) — fix that before touching config.
