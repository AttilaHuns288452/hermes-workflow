---
name: storage-cleanup
description: Use when disk is low or user asks to clean or organize.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [devops, disk, cleanup, organization, linux]
    related_skills: [backup-verification, hermes-backup-workflow, linux-privileged-ops]
---

# Storage Cleanup & Folder Organization

## When to Use

Disk filling up (df shows high use%), "clean my files", "free space", "organize Downloads" or any cluttered folder. Also when trimming backups/snapshots or removing local LLM models.

Goal: free the most bytes at the least risk. Governing safety rule: **anything on disk may be referenced by absolute path elsewhere — a VM config, a render script, a symlink, a cron job. Delete caches freely; move or delete user data only after checking references.**

## Procedure

### 1. Survey before proposing anything
- `df -h /` for the headline number the user cares about.
- `du -h --max-depth=1 ~ | sort -rh | head -20`, then drill one level into the top offenders (same command on each dir).
- Ambiguous big dirs get one more drill before being classified (a 'cache' name can hold live models; a 'tmp' can hold today's backup artifact).

### 2. Tier the findings

**Tier A — regenerable caches: delete immediately, no approval.** The user prefers direct deletion; asking about caches is ceremony.
- Known-safe set: `~/.npm/_cacache ~/.npm/_npx`, `~/.cache/uv`, `~/.cache/pip`, `~/.cache/go-build`, `~/.cache/winetricks`, `~/.cache/.fr-*` (file-roller extraction leftovers), `~/.cache/codex-runtimes`.
- `flatpak uninstall --unused -y` is safe. Journal/log vacuum needs root on this box — skip unless asked (caches free more bytes per unit risk).
- Do NOT delete caches that are active tool state: Playwright browsers, HF/whisper model caches, anything a running service reads.

**Tier B — retention-controlled dirs (state snapshots, rotating backups):** trim to a sane count AND patch the producing script's keep-count in the same pass (`tail -n +N` / `KEEP=N`, keep its comment in sync). A trimmed retention dir refills on the next scheduled run.

**Tier C — user data (games, VM images/ISOs, local models, media, installers):** present a numbered decision table (item | size | one-line note) and let the user reply with row numbers. Local LLM models: `ollama list` for sizes, `ollama rm <names>`. Never delete Tier C on your own judgment.

### 3. Dedupe rule
`(1)`/`(2)`-suffixed files are usually re-exports with different bytes, not copies. `md5sum` both first; delete only byte-identical copies. For non-identical version pairs keep the newest (or both if they are deliverables) and say which.

### 4. Folder organization (when asked)
1. Before moving anything, find absolute references: `grep -rn '<name>/' ~/Documents/Projects ~/.hermes/scripts` (and any project dir that produced the file). Render/harness scripts hardcode asset paths.
2. Check symlink targets (`ls -la ~/.local/bin`) before moving tool directories — a `blender -> ~/Downloads/...` link silently breaks.
3. **VM disk images and install ISOs stay put**: the VM config references them by absolute path; moving one leaves the VM unbootable. If unsure which ISO a VM uses, leave every ISO in place.
4. A referenced file you still want moved: move it, `ln -s` back at the old absolute path, then verify the reference resolves (read magic bytes through the path).
5. Sort loose FILES by extension into type folders (Installers/Archives/Videos/Audio/Images/Documents/Web/Code/3D-Models/Keys); leave existing directories and path-pinned files at root.
6. Credentials (api key txt, oauth json, recovery codes) go in `Keys/`, then tell the user they are plaintext and belong in a password manager.
7. Finish with the folder map. The user checks Downloads first and expects to find things without asking — every new folder named in the reply.

## Output shape
Headline first ("21G → 60G free"), then freed-by-source table, then a notes list of what was kept and why (VM ISOs, tool installs referenced by symlink). The user approves Tier C by replying with row numbers — map numbers to items literally, and treat qualifiers like "the unused ones" as a per-item judgment call to state explicitly before deleting.