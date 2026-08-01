---
name: tradingagents
description: TradingAgents multi-agent LLM financial trading framework — configured to run via OpenRouter + DeepSeek V4 Flash through the existing Hermes free model chain.
version: 1.0.0
triggers:
  - tradingagents
  - multi-agent trading
  - stock analysis agents
  - financial analysis agents
---

# TradingAgents — Multi-Agent Trading Framework

## Location
- Repo: `~/Documents/Projects/TradingAgents`
- CLI: `python -m cli.main` (or `tradingagents` if pip-installed as a script)
- App centerpiece: registered as `tradingagents`

## Existing-API Adaptation

TradingAgents was designed for Claude Code / paid LLMs. It's been adapted to use your **existing free model chain via OpenRouter**:

| Setting | Value | Why |
|---------|-------|-----|
| `llm_provider` | `openrouter` | Routes through your existing OpenRouter setup |
| `deep_think_llm` | `deepseek/deepseek-chat-v3-0324:free` | Same model Hermes uses for coding |
| `quick_think_llm` | `deepseek/deepseek-chat-v3-0324:free` | Same model for quick tasks |
| `TRADINGAGENTS_TEMPERATURE` | `0.0` | Reduces run-to-run variation |

## `.env` Setup

The `.env` at `~/Documents/Projects/TradingAgents/.env` is pre-configured with `TRADINGAGENTS_*` overrides pointing to OpenRouter + DeepSeek. You just need to fill in:

```
OPENROUTER_API_KEY=sk-or-v1-...    # same key Hermes uses
```

## Usage

### CLI (interactive)
```bash
cd ~/Documents/Projects/TradingAgents
python -m cli.main
```

Select your ticker, date, and provider. The `TRADINGAGENTS_*` env vars pre-fill the OpenRouter selection so you only pick the ticker and date.

### Python (programmatic — Hermes workflow)
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openrouter"
config["deep_think_llm"] = "deepseek/deepseek-chat-v3-0324:free"
config["quick_think_llm"] = "deepseek/deepseek-chat-v3-0324:free"
config["max_debate_rounds"] = 1
config["temperature"] = 0.0

ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("NVDA", "2026-07-24")
print(decision)
```

## Centerpiece
Click the **TradingAgents** card → launches CLI in a terminal window. Click **Open** to re-focus the terminal.

## Pitfalls
- OpenRouter free-tier models have rate limits — complex analyses may hit 429s.
- If the free DeepSeek model is unavailable, set `llm_provider: "openai_compatible"` with `backend_url` pointing at FreeLLMAPI (`http://localhost:3001/v1`).
- Decision logs live at `~/.tradingagents/memory/trading_memory.md`.
- Checkpoint resume is disabled by default (set `TRADINGAGENTS_CHECKPOINT_ENABLED=true` to enable).
