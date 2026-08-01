# Hermes CLI Entry Point Hang (Windows)

## Symptom

`hermes chat -q "hello"` hangs with no output (times out after 30-60s).
`hermes doctor` also hangs.
But `hermes --version`, `hermes status`, `hermes mcp list` all work fine.
The Python agent works fine in the current Hermes session (same provider/model).

## Diagnostics Performed

```bash
# 1. Basic install check
hermes --version     # Hermes Agent v0.18.2 — OK
hermes status --all  # Shows provider, API keys, sessions — OK
hermes mcp list      # Shows all MCP servers — OK

# 2. MCP server connectivity
hermes mcp test codegraph     # Connected, 8 tools — OK
hermes mcp test open-design   # Connected, 7 tools — OK
hermes mcp test opendesign    # Connected, 7 tools — OK
# hermes mcp test composio    # TIMEOUT after 10s

# 3. Model provider via curl
curl -s --max-time 10 https://opencode.ai/zen/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash-free","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'
# Returns 200 with valid response — OK

# 4. Model provider via Python OpenAI SDK
python -c "
from openai import OpenAI
client = OpenAI(api_key='', base_url='https://opencode.ai/zen/v1')
resp = client.chat.completions.create(model='deepseek-v4-flash-free', messages=[{'role':'user','content':'hi'}], max_tokens=10)
print('OK:', resp.choices[0].message.content)
"
# Works with empty key!

# 5. Python agent initialization (bypassing CLI)
python -c "
from cli import HermesCLI
cli = HermesCLI(model=None, toolsets=['web', 'terminal', 'file'])
print('model:', cli.model, 'provider:', cli.provider)
"
# Works fine — model=deepseek-v4-flash-free, provider=opencode

# 6. Run CLI main directly (bypassing entry point)
python -c "
from cli import main
main(query='say hello', quiet=True, max_turns=1)
"
# WORKS — exit 0

# 7. Run via CLI module entry point
python -m hermes_cli.main chat -q "hello" -Q --yolo
# HANGS — same as `hermes chat -q`

# 8. Trace with verbose imports
python -v -m hermes_cli.main chat -q "hi" -Q --yolo 2>&1 | grep -E "import.*cli" | tail -5
# Last import: 'cli' — shows the hang is past the import stage
```

## Root Cause Analysis

The failure mode: **the compiled PE binary entry point** (`venv/Scripts/hermes`) and **`python -m hermes_cli.main`** both go through `hermes_cli.main.main()` → `cmd_chat()` → `cli.main()`. But calling `cli.main()` directly from `python -c` skips the CLI wrapper and works.

The hang is in the CLI wrapper layer — between arg parsing and the first LLM call. Verified vectors:

1. **Unknown toolsets in config** — `platform_toolsets.cli` in `config.yaml` references `messaging`, `moa`, `mcp-codegraph` which don't exist in v0.18.2. Removing them fixes the startup: `hermes chat -q "..." -Q --yolo` works cleanly after cleanup.
2. **prompt_toolkit + git-bash on Windows** — In non-`-Q` mode, `prompt_toolkit` tries to init `Win32Output` but git-bash (MSYS2) has `TERM=xterm-256color` with no real Win32 console buffer → `NoConsoleScreenBufferError`. This blocks the `Application.__init__()` call. The `-Q` flag skips prompt_toolkit entirely and works.
3. **OpenCode API key is invalid** — The stored `OPENCODE_ZEN_API_KEY` returns 401. Empty-key (no-auth) works via curl; the invalid key path stalls on auth retry.

## Resolved

- Unknown toolsets removed from config → `hermes chat -q "test" -Q --yolo` now works
- `hermes doctor` runs but hangs at "Running 26 connectivity checks in parallel" — this is 26 parallel HTTP pings to provider endpoints. One slow endpoint blocks the timeout. All checks before that line (security, Python env, config, packages, auth, directory structure) pass correctly.

## Configuration Issues Noted

- `OPENCODE_ZEN_API_KEY=sk-T50...uMpj` is invalid (401 AuthenticationError)
- `platform_toolsets.cli` lists `mcp-codegraph`, `messaging`, `moa` — none exist in v0.18.2
- Both `open-design` and `opendesign` MCP servers point to the same binary (duplicate)
- `composio` MCP connection times out (>10s)

## Fixes to Try

1. **Remove unknown toolsets** from config to eliminate warnings
2. **Get a valid OpenCode Zen API key** from https://opencode.ai/auth, or
3. **Switch to OpenRouter** as primary provider (key is already valid)
4. **As workaround**, use direct Python entry point:
   ```bash
   alias hermes='cd /c/Users/Attila/AppData/Local/hermes/hermes-agent && python -c "from cli import main; main()"'
   ```
