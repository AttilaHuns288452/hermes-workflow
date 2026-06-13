# Codebuff / Freebuff — Setup & Usage

> Freebuff is the free, ad-supported version of Codebuff — an AI coding assistant CLI.
> GitHub: https://github.com/CodebuffAI/codebuff

## Quick Install

```bash
npm install -g freebuff    # free version (ads)
npm install -g codebuff    # paid version (subscription)
```

The npm package is a small wrapper (JS) that downloads the real binary (~142 MB) on first run.

## Binary Location

| Platform | Path |
|---|---|
| Windows | `~/.config/manicode/freebuff.exe` |
| macOS/Linux | `~/.config/manicode/freebuff` |

Config/metadata: `~/.config/manicode/freebuff-metadata.json`
Settings: `~/.config/manicode/settings.json`

## Authentication

Freebuff uses **GitHub OAuth** — browser-based login only.

```bash
freebuff login
```

This outputs a URL like `https://freebuff.com/login?auth_code=XXXX` that must be opened in a browser. There is **no token-based or headless auth** — a browser is required.

1. Run `freebuff login`
2. Open the generated URL in a browser
3. Click **"Continue with GitHub"**
4. Log in with GitHub credentials
5. Authorize the Freebuff OAuth app
6. The CLI detects the auth and proceeds

**Known limitation:** GitHub Personal Access Tokens (PATs) cannot be used as passwords for the GitHub web login form. Only the actual account password works for OAuth flows.

## Running

```bash
cd /path/to/project
freebuff
```

This opens a full-screen TUI built with OpenTUI. It requires a PTY/pseudo-terminal — pipe/subprocess won't work well. Use `pty=true` if running programmatically.

### Key Commands

| Command | Purpose |
|---|---|
| `/help` | Keyboard shortcuts & tips |
| `/new` | Start fresh conversation |
| `/history` | Past conversations |
| `/bash` | Bash mode |
| `/init` | Create starter `knowledge.md` |
| `/feedback` | Share feedback |
| `/theme:toggle` | Light/dark mode |
| `/logout` | Sign out |
| `/exit` | Quit |

### Features

- **File mentions**: `@filename` to reference files
- **Agent mentions**: `@AgentName` to invoke agents
- **Bash mode**: `!command` or `/bash`
- **Knowledge files**: `knowledge.md` in project root
- **Chat history**: Resume with `freebuff --continue`

## Free Tier Details

| Feature | Limit |
|---|---|
| **Model** | DeepSeek V4 Flash |
| **Sessions/day** | 5 |
| **Session time** | ~42 minutes |
| **Ads** | Shown in CLI (supports free tier) |
| **Web research** | Built-in |
| **Browser use** | Built-in |

Full Codebuff (paid) offers more models, longer sessions, no ads.

## Windows-Specific Notes

- The TUI uses full-screen alternate buffer. Reset terminal after exit with `reset` if it leaves garbage.
- First run downloads and extracts a 142 MB `.tar.gz` via Node.js — this is normal and takes ~10-30s depending on connection.
- Runs fine under git-bash / MSYS2 terminal.
- The menus use keyboard navigation (arrows, Enter, Escape, / for commands).
- Use `--cwd <dir>` to set working directory without `cd`.

## Usage Pattern from Hermes

When invoked from within a Hermes session (autonomous):

```bash
# Start in background PTY
terminal(command="cd /path && freebuff", pty=true, background=true)

# Poll for startup
process(action="poll", session_id="...")

# Send a prompt once the TUI is loaded
process(action="submit", session_id="...", data="your prompt here")

# Wait for result, then check the edited files
process(action="wait", session_id="...", timeout=120)
```

The TUI may require bracketed paste mode for multi-line input. Single-line prompts work with `submit`.
