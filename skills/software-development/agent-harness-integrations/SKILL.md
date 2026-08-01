---
name: agent-harness-integrations
description: "End-to-end setup of third-party agent harness config layers (ECC, rules, skills, hooks) onto local toolchains: Claude Code, OpenCode, Hermes, Cursor, Codex, Zed, etc. Use when installing, repairing, or bridging agent-harness ecosystems."
metadata:
  short-description: "Install and verify ECC/agent harness configs across local toolchains."
---

# Agent Harness Integrations

## Purpose

Cover cross-tool setup of agent harness operating systems (principally **ECC v2.0.0**), spanning install, build prerequisites, verification, and unsupported-target workarounds.

## Supported harness targets

Claude Code (`claude` / `claude-project`), OpenCode (`opencode`), Cursor (`cursor`), Codex (`codex`), Gemini (`gemini`), Antigravity (`antigravity`), Zed (`zed`), Codebuddy (`codebuddy`), JoyCode (`joycode`), Qwen (`qwen`), Trae (`trae`), Kiro (`kiro`).

Hermes has **no official ECC target**; route through OpenCode-compatible config or symlink the expected `~/.opencode` tree.

## Canonical install flow

1. Clone the repo.
2. Run `npm install` from the repo root.
3. Run the harness-specific installer.
4. Verify with `node scripts/ecc.js doctor`; repair drift with `node scripts/ecc.js repair`.
5. Confirm visible modules with `node scripts/ecc.js list-installed`.

## Windows notes

Prefer `install.ps1 --profile <name>` or `node scripts/install-apply.js --profile <name>`.
If file locks occur after install, kill lingering `node.exe` and rerun the apply step.
Use `node scripts/ecc.js status` for a less-fragile health summary than `doctor`.

### Behavior / output shape

This is a fix-and-deliver task, not a tutoring session. Follow these rules:

- Suppress narration. Do not explain what you are about to do, what you just did, or what failed along the way unless it blocks delivery. "Why are you explaining" / "just give me the answer" overrides any tendency to summarize intermediate steps.
- Report only: (1) blockers that prevent completion, and (2) the final verified state with concrete handles (file paths, endpoints, IDs, exit codes).
- For MCP / harness wiring specifically: edit configs directly, verify with a single real round-trip, then stop.

## OpenCode build requirement

OpenCode installs fail if `.opencode/dist/` payloads are missing.
Run `node scripts/build-opencode.js` before any OpenCode-specific install.

## Uninstall / reinstall guidance

- Preview removals with `node scripts/uninstall.js --dry-run`.
- Full uninstall: `node scripts/install-apply.js --profile full --remove --target <name>`.
- Don’t mix plugin-install and manual-install for the same harness; pick one.

## Verification checklist

- `node scripts/ecc.js list-installed` shows the target and profile.
- `node scripts/ecc.js doctor` reports `0 warnings, 0 errors`. 
- For OpenCode, confirm `~/.opencode` exists after install.

## Third-Party npm AI Plugin Integration (OpenCode + Hermes)

Some AI plugins ship as npm packages that integrate as both OpenCode plugins and Hermes plugins. Example: `@dietrichgebert/ponytail` (YAGNI lazy-mode enforcer).

### Install Flow

1. **Install globally via npm:**
   ```bash
   npm install -g @org/plugin-name
   ```

2. **Register as OpenCode plugin** — add to `~/.config/opencode/opencode.jsonc`:
   ```json
   "plugin": ["@org/plugin-name"]
   ```
   The `"plugin"` field accepts npm package names or local paths to `.mjs` plugin files.

3. **Add plugin skills to OpenCode skills path** (if the plugin ships skills):
   ```json
   "skills": {
     "paths": [
       "...existing paths...",
       "C:/Users/<user>/Documents/Projects/<repo>/skills"  // local clone if skills aren't exposed by the npm package
     ]
   }
   ```

4. **Install for Hermes** — use the GitHub repo shorthand:
   ```bash
   hermes plugins install Owner/repo
   # or: hermes plugins install Owner/repo/path/to/plugin  (with subdirectory)
   ```

5. **Enable the Hermes plugin:**
   ```bash
   hermes plugins enable plugin-name
   # Takes effect on next session.
   ```

6. **Document in workflow repo** — update README.md ecosystem list and add a pipeline step in INTEGRATION.md (if using `hermes-workflow` or similar).

### Detection
- OpenCode picks up plugins at startup — no restart needed within a session, but new session required for Hermes.
- Verify OpenCode: check `~/.config/opencode/opencode.jsonc` has the `"plugin"` entry.
- Verify Hermes: `hermes plugins list` should show the plugin (if enabled) or `hermes plugins list --all` to see installed ones.

### Local clone approach (when npm package doesn't expose a plugin entry point)
If the npm package's `package.json` `"main"` points to the plugin file, OpenCode can reference it directly via npm. If not, clone the repo and reference the `.mjs` file:
```json
"plugin": ["./.opencode/plugins/plugin-name.mjs"]
```
(From the project root where the relative path resolves.)

---

## Hermes ↔ OpenCode Infrastructure Sync

When configuring both Hermes and OpenCode on the same machine to share local models, MCP servers, API keys, and skills:

| Resource | Hermes | OpenCode |
|----------|--------|----------|
| **Local models (Ollama)** | `hermes config set providers.<name>.base_url http://localhost:11434/v1` | `opencode.jsonc` → `provider.<name>.options.baseURL` |
| **MCP servers** | `~/.hermes/config.yaml` → `mcp_servers:` | `opencode.jsonc` → `"mcp":` (flattened, no `servers` wrapper) |
| **Skills** | `config.yaml` → `skills.external_dirs` | `opencode.jsonc` → `skills.paths` (forward slashes on Windows) |
| **API keys** | `.env` file | `~/.local/share/opencode/auth.json` (edit directly when CLI login fails) |

### OpenCode config.jsonc schema details

**MCP servers** go directly under `"mcp"`, NOT under a `"servers"` wrapper:
```json
"mcp": {
  "my-server": {
    "type": "local",
    "command": ["npx", "-y", "@package/server"],
    "environment": { "KEY": "value" }
  }
}
```
- Use `"environment"` not `"env"`
- Use `"command"` array not separate command+args
- Omit `"servers"` key entirely — causes schema validation error

**Custom providers** (local Ollama, FreeLLMAPI, LM Studio):
```json
"provider": {
  "ollama": {
    "name": "Ollama Local",
    "api": "openai",
    "options": { "baseURL": "http://localhost:11434/v1" }
  }
}
```
Then use: `opencode run 'prompt' --provider ollama`

**Skills paths** (share Hermes skills with OpenCode):
```json
"skills": {
  "paths": ["C:/Users/<user>/AppData/Local/hermes/skills/autonomous-ai-agents"]
}
```

### Hermes local model provider setup
- Override the built-in `ollama` provider's base URL via: `hermes config set providers.ollama.base_url http://localhost:11434/v1`
- Enable model discovery: `hermes config set providers.ollama.discover_models true`
- Set default: `hermes config set providers.ollama.default_model <model-name>`
- Shows up in `hermes model` picker as a selectable provider option
- Also works with custom provider names like `local-ollama`

### Pitfalls

**OpenCode auth.json direct edit format:**
When `opencode providers login --provider <name>` fails (e.g. OpenCode Zen interactive prompt doesn't accept piped stdin), write the credential directly to `~/.local/share/opencode/auth.json`:
```json
{
    "openrouter": { "type": "api", "key": "sk-or-..." },
    "opencode":   { "type": "api", "key": "sk-T50..." }
}
```
Verify with `opencode auth list`. The CLI picks up changes immediately — no restart needed.

**OpenCode custom provider models must be declared explicitly:**
Unlike Hermes which auto-discovers models via `/v1/models`, OpenCode only discovers models for its built-in providers. For custom providers (Ollama, FreeLLMAPI, etc.), declare models explicitly in the `models` object or `opencode models` won't show them:
```json
"provider": {
  "ollama": {
    "name": "Ollama",
    "api": "openai",
    "options": { "baseURL": "http://localhost:11434/v1" },
    "models": {
      "qwen2.5-coder:3b": {
        "limit": { "context": 32768, "output": 8192 }
      }
    }
  }
}
```

**OpenCode skills path memory crash on Windows:**
`opencode skills` can crash with `ASSERTION FAILED: MemoryExhaustion` when loading 30+ skill paths simultaneously on Windows. This is a JavaScriptCore memory limit in the OpenCode CLI, not a config error — the paths are still usable, only the listing command is fragile. Mitigation: limit `skills.paths` to the most relevant categories (autonomous-ai-agents, workflow, software-development, decide, do, setup) rather than the full Hermes tree.

## Reference

See `references/ecc-install-notes.md` for ECC-specific profiles, modules, and Hermes bridging details.
