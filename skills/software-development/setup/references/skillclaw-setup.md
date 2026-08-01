# SkillClaw Setup on Windows (Hermes Integration)

[SkillClaw](https://github.com/AMAP-ML/SkillClaw) is a skill injection proxy that sits between an agent CLI and its LLM provider, injecting relevant skills into the context window.

## Setup Walkthrough

```bash
# 1. Clone
cd ~/Documents/Projects
git clone https://github.com/AMAP-ML/SkillClaw.git

# 2. Venv + install (extras optional)
cd SkillClaw
python -m venv .venv
source .venv/Scripts/activate
pip install -e ".[evolve,sharing,server]"
```

## Config: Write Directly (skip interactive wizard)

The interactive `skillclaw setup` wizard reads from `stdin` via `input()`, which hangs in Hermes' PTY/background mode. Write `~/.skillclaw/config.yaml` directly instead.

Key settings for Hermes integration:

```yaml
claw_type: hermes
llm:
  provider: custom
  model_id: skillclaw-model
  api_base: ""
  api_key: ""
proxy:
  port: 30000
  host: 0.0.0.0
  served_model_name: skillclaw-model
skills:
  enabled: true
  dir: C:\Users\Attila\AppData\Local\hermes\skills
prm:
  enabled: false
sharing:
  enabled: false
configure_openclaw: true       # MUST be true for claw_type to stick
```

## Pitfall: `configure_openclaw: false` Overrides `claw_type`

In `config_store.py`, when `configure_openclaw` is `false`, the code hard-forces `raw_claw_type = "none"` regardless of what `claw_type` is set to. This means the ClawAdapter logs `claw_type=none — skipping auto-configuration` and never applies the Hermes proxy config. Always set `configure_openclaw: true` when configuring a non-OpenClaw agent.

## Starting

```bash
skillclaw start --daemon
```

The ClawAdapter automatically:
1. Detects `claw_type: hermes`
2. Writes the proxy config into `~/.hermes/config.yaml` (model, base_url, api_key)
3. Backs up the original Hermes config to `~/.skillclaw/backups/hermes/`

## Verification

```bash
skillclaw status                    # running (PID=..., proxy=:30000)
skillclaw doctor hermes             # status: ok, proxy_match: True
```

Doctor checks: `status: ok`, `proxy_match: True`, `configured_model: skillclaw-model`, `configured_base_url: http://127.0.0.1:30000/v1`.

## Stopping / Restarting

```bash
skillclaw stop
skillclaw start --daemon
```

## Reverting Hermes Config

If needed: `skillclaw restore hermes`. Backups at `~/.skillclaw/backups/hermes/config.<timestamp>.yaml`.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `claw_type=none — skipping auto-configuration` in log | `configure_openclaw: false` | Set to `true` |
| Hermes model config not updated after start | Daemon ran before config was fixed | `stop && start --daemon` |
| `proxy_match: False` in doctor | Hermes config wasn't written | Restart daemon, check ClawAdapter log lines |
