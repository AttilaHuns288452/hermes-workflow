---
name: skillclaw
description: "Self-evolving skills for Hermes — auto-evolves, deduplicates, and improves skills from real session data across sessions, agents, and devices."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Skill-Evolution, Auto-Evolve, Cross-Session, Background, Agent-Improvement]
    related_skills: [ecc-bridge, hermes-agent]
---

# SkillClaw Integration

SkillClaw auto-evolves skills from real session data. Runs as a local proxy on port 30000.

## When to Use

- User asks about skill evolution or auto-improvement
- Skills need deduplication, patching, or quality improvement
- Cross-session skill refinement desired
- User wants skills to auto-improve with no manual effort

## Quick Start

```bash
# Start the SkillClaw daemon
skillclaw start --daemon

# Verify health
skillclaw status
skillclaw doctor hermes

# Inspect current skills
skillclaw skills list-remote
```

## Location

Installed at: `~/Documents/Projects/SkillClaw/`
Client proxy: port 30000 (configured via `skillclaw setup`)
Skills directory: `~/.hermes/skills` (shared with Hermes)

## Hermes Integration Details

- `skillclaw setup` configures Hermes as the CLI agent
- `skillclaw start --daemon` runs the local proxy
- `skillclaw doctor hermes` verifies integration health
- `skillclaw restore hermes` undoes integration changes
- Skills auto-evolve in the background with no extra effort

## Architecture

Two components:
1. **Client Proxy** — local API proxy that intercepts agent requests and records session artifacts
2. **Evolve Server** (optional) — reads session data and evolves/creates skills in the background

## Model Configuration

Settings in `~/.skillclaw/config.yaml`:
- Provider: OpenAI-compatible API
- Model: auto-evolution engine model (configured during `skillclaw setup`)
- Shared storage: optional (OSS/S3/local) for multi-device/team setups
