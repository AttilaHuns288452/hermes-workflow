---
name: buildable-plugin
description: Local-first AI app-builder brain — archetypes, golden templates, UI/UX playbooks, review loops. Wraps the buildable CLI tool for app planning, design, generation, and review. Complements existing design/plan/review skills with structured archetype-driven tooling.
tags: [app-builder, archetypes, templates, UI-UX, planning, review, prototype]
platforms: [linux, macos, windows]
---

# Buildable Plugin — Hermes Integration

## Overview

[Buildable](https://github.com/suntay44/buildable-plugin-skills) is a local-first AI app-builder brain that packages product intelligence known to hosted builders (Lovable, Replit Agent) into a local CLI tool. It provides **55 archetypes**, **15 golden templates**, **8 micro-blocks**, UI/UX playbooks, and a review loop — all zero runtime dependencies.

**Location:** `~/Documents/Projects/buildable-plugin-skills/`
**CLI:** `buildable` (linked via npm)

## How It Complements Existing Skills

| Existing Hermes Skill | Buildable Role | Relationship |
|---|---|---|
| `software-development/plan` | `buildable plan` with 55 archetypes | Buildable provides structured archetype-driven planning (not freeform). Use for app/feature planning. |
| `creative/claude-design` / `creative/sketch` | `buildable design` + `buildable generate` | Buildable handles full-stack app generation from templates. Use creative Hermes skills for one-off artifacts; Buildable for full app builds. |
| `creative/popular-web-designs` | Buildable golden templates (15 runnable) | Buildable templates are production-ready starters (Next.js/TS/Tailwind). Popular-web-designs are design-only HTML/CSS. Complementary. |
| `opencode-power-pack/code-reviewer` / `requesting-code-review` | `buildable review` | Buildable review checks generated code against app spec (local-first guardrails, accessibility, state coverage). Human code review still needed. Complementary. |
| `creative/excalidraw` / `creative/p5js` | Buildable design playbooks | Buildable handles structural design decisions. Excalidraw/p5js handle visual exploration. |

## CLI Commands

```bash
# Check installation
buildable check

# Plan an app (creates .buildable/phase-plan.md/json/toon)
buildable plan "Build me a lightweight CRM" [--with-auth] [--file <path>]

# Design a UI/UX brief
buildable design "Add a dashboard page" [--dark] [--write]

# Generate app code from plan
buildable generate "Build the CRM dashboard" [--out <dir>] [--augment]

# Review generated code against spec
buildable review [path] [--build] [--strict]

# List available archetypes and templates
buildable list

# Get a preview screenshot
buildable preview [path]

# Start MCP bridge (for desktop Claude clients)
buildable mcp

# Run evaluations
buildable eval [--compare]
```

## Workflow Integration

Use Buildable when building full applications. The workflow is:

1. **`buildable plan`** — Classify the app idea, select archetype+templates, emit phase plan
2. **`buildable design`** — Produce UI/UX brief with tokens (light+dark palettes)
3. **`buildable generate`** — Create project files from golden templates
4. Hermes creative skills — Polish UI with `popular-web-designs`, `claude-design`, `sketch`, `excalidraw`
5. **`buildable review`** — Audit against spec (local-first, accessibility, responsive, state coverage)
6. `requesting-code-review` — Standard code review pass
7. Obsidian note + Graphify index — Document the project

## Reference Skills (Built-in Buildable Sub-skills)

The buildable-plugin repo ships these skill definitions for Claude Code/Codex integration:

| Skill | Purpose |
|---|---|
| `planner` | Prompt classification, archetype selection, phase plan + app spec |
| `web-builder` | Next.js/TS/Tailwind app generation from Buildable specs |
| `mobile-builder` | Expo/React Native app generation from Buildable specs |
| `reviewer` | Prototype review against app spec + quality rubric |

These are internal to Buildable's plugin system and loaded automatically when you use the CLI.

## MCP Bridge (Desktop Clients)

For desktop Claude clients, add to `~/.hermes/config.yaml`:

```yaml
mcpServers:
  buildable:
    command: buildable-mcp
    args: []
    env:
      BUILDABLE_WORKSPACE: "$HOME/Documents/Projects"
```

## Conflict Resolution

When a task involves app building:
- Use **Buildable** for the structured workflow (plan → design → generate → review)
- Use **existing Hermes skills** for polish, one-off artifacts, and human review
- They are complementary — activate both
