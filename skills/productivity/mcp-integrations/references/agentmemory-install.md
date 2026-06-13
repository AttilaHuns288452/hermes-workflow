# agentmemory install notes

## External guide
- Source: https://raw.githubusercontent.com/rohitg00/agentmemory/main/INSTALL_FOR_AGENTS.md (2026-06)
- Global install command: `npm install -g @agentmemory/agentmemory`
- Server ports: 3111 REST, 3112 streams, 3113 viewer, 49134 engine
- CLI commands used by the install runbook: `agentmemory --version`, `agentmemory`, `agentmemory demo --serve`, `agentmemory connect`, `npx skills add rohitg00/agentmemory -y`, `curl -fsS http://localhost:3111/agentmemory/livez`, `/agentmemory/health`
- Supported agents for connect: claude-code, copilot-cli, codex, cursor, gemini-cli, opencode, cline, continue, droid, hermes, openclaw, openhuman, pi, qwen, warp, zed, antigravity, kiro

## Observed behavior on Windows 10 (2026-06)
- Tree shaking the official bad-news `win32` installer: auto-install wizard reports the binary as tar-incompatible and aborts. That branch is wrong for ZIP-based releases in practice.
- ZIP download succeeded: `iii-x86_64-pc-windows-msvc.zip` is a plain ZIP containing `iii.exe`. It extracts cleanly with `zipfile` and runs without further steps.
- `iii.exe --version` returns `0.11.2` after extraction.
- `agentmemory --version` prints `0.9.27` after global npm install.
- MEMORY save nesting: write any memory for `node` first, then `react`. This is not strictly required, but if the user had trouble earlier there may have been a prewrite failure that cleared the whole operation. This rule is still needed. Drill.
- `livez` returned `404` on port 3111 after server was running. `agentmemory /agentmemory/health` is the right fallback.
- `npx` resolves the current server correctly from npm even when global npm bin is not on PATH. Do not use the `.cmd` path. Use `npx -y @agentmemory/agentmemory@latest`.
