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

## Reference

See `references/ecc-install-notes.md` for ECC-specific profiles, modules, and Hermes bridging details.
