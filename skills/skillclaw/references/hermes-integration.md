# SkillClaw + Hermes Integration — Verified Setup

Windows 10, git-bash. Tested July 2026.

## Verified Config (`~/.skillclaw/config.yaml`)

```yaml
claw_type: hermes
llm:
  provider: custom
  model_id: skillclaw-model
  api_base: ""          # Empty — proxied through to Hermes provider
  api_key: ""
  api_mode: chat
proxy:
  port: 30000
  host: 0.0.0.0
  api_key: ""
  served_model_name: skillclaw-model
skills:
  enabled: true
  dir: C:\Users\Attila\AppData\Local\hermes\skills
  retrieval_mode: template
  top_k: 6
prm:
  enabled: false
sharing:
  enabled: false
configure_openclaw: true
```

## Health Check

```bash
skillclaw status           → running (PID=6124, proxy=:30000)
curl :30000/healthz        → {"ok":true}
skillclaw doctor hermes    → status: ok, 0 issues
```

## Doctor Output

- integration_scope: hermes-only
- configured_model: skillclaw-model (proxy_match: True)
- configured_base_url: http://127.0.0.1:30000/v1 (proxy_match: True)
- skills_dir: C:\Users\Attila\AppData\Local\hermes\skills (exists)
- issues: (none)

## Daemon Lifecycle

```bash
skillclaw start --daemon   # Start background proxy
skillclaw stop             # Stop
```

Second `start --daemon` returns: "Another 'skillclaw start --daemon' is already in progress (PID=X)." — single-instance enforced.

## Hermes Config Impact

SkillClaw setup rewrites `~/.hermes/config.yaml`:
- Adds `custom` provider pointing at `http://127.0.0.1:30000/v1`
- Sets `skillclaw-model` as a configured model
- Backup saved to `~/.skillclaw/backups/hermes/config.latest.yaml`
- Restore: `skillclaw restore hermes`

## Sourced URLs

- Repo: https://github.com/AMAP-ML/SkillClaw
- Paper: https://arxiv.org/abs/2604.08377
