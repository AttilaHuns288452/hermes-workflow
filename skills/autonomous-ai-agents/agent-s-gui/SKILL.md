---
name: agent-s
description: "Simular Agent S — computer-use GUI agent. Runs GUI automation via gui_agents package or agent_s CLI."
version: 1.0.0
triggers:
  - computer use
  - gui agent
  - gui automation
  - agent s
  - simular
  - desktop automation
---

# Agent S — Computer-Use GUI Agent

## Where It Lives
- Repo: `~/Documents/Projects/agent-s`
- CLI: `agent_s` (in Hermes venv)
- Package: `gui_agents` (installed editable)

## Available Stages

| Stage | Purpose | Entrypoint |
|-------|---------|------------|
| S1 | Basic screenshot + action | `gui_agents.s1.core.AgentS` → `GraphSearchAgent`, `UIAgent` |
| S2 | Screenshot + action + observation | `gui_agents.s2` |
| S2.5 | Enhanced action pipeline | `gui_agents.s2_5` |
| S3 | Full agent loop with planning (CLI entry point) | `gui_agents.s3.cli_app:main` |

## Usage

### CLI (S3 agent loop)
```bash
# Entry point: gui_agents.s3.cli_app:main (registered in setup.py)
agent_s --help

# Required arguments:
agent_s \\
  --provider openai --model gpt-4o \\
  --ground_provider openai --ground_url https://api.openai.com/v1 \\
  --ground_model gpt-4o --grounding_width 1920 --grounding_height 1080 \\
  --task "Open Chrome and go to gmail.com"
```

### Python (programmatic — S1 GraphSearchAgent)
The correct import path (NOT `gui_agents.s1.S1Agent` — that class doesn't exist):
```python
from gui_agents.s1.core.AgentS import GraphSearchAgent, UIAgent
from gui_agents.s1.aci.WindowsOSACI import WindowsACI  # or MacOSACI/LinuxACI
from gui_agents.s1.cli_app import run_agent

aci = WindowsACI()
engine_params = {"engine_type": "openai", "model": "gpt-4o"}
agent = GraphSearchAgent(engine_params, aci, action_space="pyautogui", observation_type="mixed")
agent.reset()
run_agent(agent, "Click the login button")
```

### Quick screenshot-only (no agent loop, uses pyautogui directly)
```python
import pyautogui
screenshot = pyautogui.screenshot()
screenshot.save("screenshot.png")
```

## Pitfalls
- **CLI hangs on first run** — first import/download caches model data; subsequent runs are fast. Run `agent_s --help` once to warm up.
- **Import path**: `from gui_agents.s1.core.AgentS import GraphSearchAgent, UIAgent` (NOT `gui_agents.s1 import S1Agent` — that class doesn't exist).
- **Requires vision-capable API key** — S3 needs both a main model AND a grounding model with image understanding. Free/open models usually lack the grounding accuracy.
- **Windows requires system Python with gui_agents installed** (Hermes venv works if `pip install -e` was run in the project dir).
- **Electron/headless apps may not render** when launched from a terminal subprocess — use `pyautogui` + `pywinauto` (from `gui_agents.s1.aci.WindowsOSACI`) for window detection instead.
- Don't run while actively using the mouse — agent takes control.
- See `references/agent-s-cli-help.md` for full CLI options.
