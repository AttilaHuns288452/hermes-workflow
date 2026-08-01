# agent_s CLI — Full Options

```
usage: agent_s [-h] [--provider PROVIDER] [--model MODEL]
               [--model_url MODEL_URL] [--model_api_key MODEL_API_KEY]
               [--model_temperature MODEL_TEMPERATURE]
               --ground_provider GROUND_PROVIDER
               --ground_url GROUND_URL
               [--ground_api_key GROUND_API_KEY]
               --ground_model GROUND_MODEL
               --grounding_width GROUNDING_WIDTH
               --grounding_height GROUNDING_HEIGHT
               [--max_trajectory_length MAX_TRAJECTORY_LENGTH]
               [--enable_reflection] [--enable_local_env] [--task TASK]
```

## Required Arguments
| Flag | Description |
|------|-------------|
| `--provider` | Provider name (openai, anthropic, gemini, azure_openai, vllm, open_router) |
| `--model` | Vision model name (e.g., gpt-4o, claude-sonnet-4) |
| `--ground_provider` | Grounding model provider (required) |
| `--ground_url` | Grounding API endpoint (required) |
| `--ground_model` | Grounding model name (required) |
| `--grounding_width` | Screenshot width after processor rescaling |
| `--grounding_height` | Screenshot height after processor rescaling |

## Optional Arguments
| Flag | Default | Description |
|------|---------|-------------|
| `--model_url` | — | Custom API endpoint for main model |
| `--model_api_key` | env var | API key for main model |
| `--model_temperature` | — | Temperature (o3 requires 1.0) |
| `--ground_api_key` | env var | API key for grounding model |
| `--max_trajectory_length` | — | Max screenshot turns in trajectory |
| `--enable_reflection` | off | Enable reflection agent |
| `--enable_local_env` | off | Enable local code execution (WARNING: runs arbitrary code) |
| `--task` | — | Task instruction for Agent-S3 |

## Quick-start with OpenRouter (open-source models)
```bash
agent_s \
  --provider anthropic \
  --model claude-sonnet-4-20250514 \
  --ground_provider openai \
  --ground_url https://api.openai.com/v1 \
  --ground_model gpt-4o \
  --grounding_width 1920 \
  --grounding_height 1080 \
  --task "Click the Start button next to each app in the centerpiece window"
```

## Notes
- First run is slow (import cache warmup). Run `--help` once to pre-warm.
- For simple screenshots, use `pyautogui` directly without the agent loop.
- Grounding model must support image input. Most free-tier models don't.
