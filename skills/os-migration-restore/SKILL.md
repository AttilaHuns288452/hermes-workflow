---
name: os-migration-restore
description: "Use when restoring a Windows backup onto Linux."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, windows]
metadata:
  hermes:
    tags: [migration, restore, windows-linux, backup, environment, path-translation, verification]
---

# OS Migration Restore

Audit-first, manifest-driven restoration of a dev environment from a Windows backup (e.g. `MyOldOS`-style) onto a clean Linux system. Never blindly copy every file.

## When To Use

- Restoring `X:\MyOldOS`-style backups (numbered dirs `00_MANIFEST/` … `15_VERIFICATION/`) onto Linux.
- Any Windows → Linux dev-environment migration: Hermes state, providers, Git/SSH, databases, VS Code, projects, credentials.
- Rebuilding a machine where Windows paths, executables, and service wrappers do not translate directly.

## Persistence Principle

When the user says "continue", "don't stop until it's resolved", or "don't stop until its all resolved":

- **Keep working autonomously** through multi-step migration tasks
- **Don't stop to ask for confirmation** at each step — complete the entire workflow end-to-end
- **Only stop when the task is truly complete** or blocked by a technical issue that requires user intervention
- **Treat "continue" as a directive to finish the entire job**, not just the next step

This preference exists because migration work is inherently multi-step and stopping mid-flow wastes context and time.

## Workflow: Audit → Manifest → Deps → Data → Verify

1. **Locate the backup first.** External drives land under `/media/$USER/` or `/mnt/` with spaces and read-only `fuseblk (ro)` mounts. Find the mount containing `MyOldOS`, quote paths with spaces, and treat the backup as read-only until validation is complete.
2. **Audit the Linux system before touching anything.** Record distro/version, CPU/GPU/RAM, disks, mount points, free space, UEFI/boot, and which tools already exist (Git, SSH, Node, Python, Java, MySQL/Postgres, Docker, VS Code, Ollama, Hermes, OmniRoute). Write `~/migration-status-before-restore.md`. Do not overwrite yet.
3. **Read the migration manifests before restoring.** `00_MANIFEST/MIGRATION_MANIFEST.md` plus `RESTORE_ORDER.md`, Hermes/OmniRoute/AI/VS Code/database/Windows-compat docs. The manifest's restore order wins over assumptions; Windows paths in it never apply literally on Linux.
4. **Install Linux-native dependencies before application data.** System packages, Git, SSH, Node, Python, JDK/Maven/Gradle, DB servers, Docker, VS Code, Ollama, OmniRoute, Hermes — via native packages, never Windows `.exe` files.
5. **Restore credentials securely, then Git/SSH, then data.** Credentials → Git config/keys → dev toolchain → databases → local AI (re-pull, don't copy binaries) → OmniRoute → Hermes → VS Code → projects → documents → Windows-only software alternatives.
6. **Verify everything, keep the backup.** Migration is complete only when Hermes + routing + AI + databases + projects + credentials + VS Code all work. Keep the backup untouched; write `~/migration-final-report.md` with `VERIFIED / WARNING / FAILED / MANUAL ACTION REQUIRED`.

See `references/myoldos-restore-notes.md` for the concrete MyOldOS layout, sizes, and field observations from a real restore.

## Path Translation (never copy Windows paths literally)

| Windows | Linux |
|---|---|
| `C:\Users\<you>\AppData\Local\hermes\` | `$HERMES_HOME` (resolve from env, see below) |
| `C:\Users\<you>\Documents\Projects\` | `$HOME/Documents/Projects/` |
| `C:\Users\<you>\AppData\Roaming\GitHub CLI\` | `$HOME/.config/gh/` |
| `watchdog.cmd` / service wrappers | systemd unit or cron job |
| Windows `.exe` installers | native package / npm / Flatpak / AppImage |
| Cron `Workdir:` / script paths (`C:\Users\…`) | Linux `$HERMES_HOME` or project path; rewrite via `hermes cron edit` |


## Hermes Home Resolution (pitfall)

Migration manifests often hardcode a Linux target like `$HOME/.local/share/hermes/`, but the live Hermes home is `$HERMES_HOME` (canonical `~/.hermes/`, profiles under `~/.hermes/profiles/<name>/`). Always resolve the real home from the environment and restore state/DBs/skills/plugins/scripts/cron/memories/profiles there. Never hand-edit `config.yaml` by hand — use `hermes config set KEY VAL`; secrets belong in `.env`, settings in `config.yaml`.

## Credentials Discipline

- Never print secret values into chat/terminal output; never commit them to Git.
- `chmod 600` files, `chmod 700` dirs (`~/.ssh`, `~/.config/gh`).
- Expect gaps and reconstruct: a missing `gitconfig_roaming` file can be rebuilt from `GIT_MIGRATION.md` settings; a `gh` `hosts.yml` with only `user:` and no token means re-login (`gh auth login`), not a broken backup. Supabase/Vercel auth is often browser-bound — re-login on Linux.
- Convert Windows env-var config to `~/.bashrc` / `~/.config/environment.d/` exports.

## Database + Large-File Handling

- Prefer `sqlite3.backup()` copies and `PRAGMA integrity_check` on every `.db` (state, kanban, projects, response_store, codegraph, cron, board DBs). Never overwrite a restored DB with a fresh empty one.
- Expect `-shm`/`-wal` sidecars next to live DBs; stop Hermes (`hermes stop` / `pkill -f hermes`) before copying state DBs.
- Large files are normal (`state.db` multi-GB, codegraph near-GB). Check `df -h` headroom before copying `01_HERMES/` + `05_PROJECTS/`.
- MySQL dumps are usually absent when the server wasn't running at backup time — flag as `MANUAL ACTION REQUIRED` and re-dump from the source. Local AI models are re-pulled (`ollama pull …`), never copied; on 4GB-VRAM GPUs prefer small models (e.g. 1.5b) for vision tasks.

## Output Discipline for Operational Restores

Restores are operational work, not visual artifacts. Answer directly with commands run, real tool output, and file paths. **Do not emit `::preview` live widgets or HTML mockups for migration/restore tasks** unless the user explicitly asks for a visual artifact. Reserve preview widgets for design deliverables.

## LightRAG Migration (pitfall)

LightRAG indexes are NOT portable between Windows and Linux. The old index contains Windows-specific paths and a different format (graphml + json vs skill_index.json). Do NOT copy the old index. Instead:

1. Rebuild from current skills: `python3 ~/.hermes/scripts/lightrag_build_index.py`
2. Query test: `python3 ~/.hermes/scripts/lightrag_find.py "test query"`
3. The build script and find script are at `~/.hermes/scripts/lightrag_build_index.py` and `~/.hermes/scripts/lightrag_find.py` (Linux-native versions)

## Skill Migration (pitfall)

The old Windows backup may contain 800+ skills, but most are REFERENCE REPOS (external skill libraries like ECC, hermes-workflow), not the user's active skills. The actual active+optional count is typically ~200.

1. Count old active skills: `find /path/to/old/skills -name SKILL.md | wc -l`
2. Count old optional skills: `find /path/to/old/optional-skills -name SKILL.md | wc -l`
3. Compare with current: `find ~/.hermes/skills -name SKILL.md | wc -l`
4. Import only Linux-native optional skills (skip Windows-specific, obsolete, and already-existing)
5. Rebuild LightRAG after import

Do NOT import reference repos (ECC, hermes-workflow, etc.) — they are external libraries, not user skills.

## CLI Tool Local Model Setup (pitfall)

After migration, CLI tools like CommandCode and OpenCode won't auto-discover local Ollama models. They need manual BYOK setup:

- **CommandCode**: Run `commandcode /connect` interactively, add provider with URL `http://localhost:11434/v1` (no API key needed for local). Then `commandcode --list-models` to verify.
- **OpenCode**: Run `opencode providers login http://localhost:11434/v1` interactively. Then `opencode models` to verify.
- **Hermes**: Already has `discover_models: true` under `local-ollama`. Use `hermes config set local-ollama.default_model <name>` to switch defaults.

## Config Editing (pitfall)

`hermes config` will refuse to edit `config.yaml` for security. Use:
- `hermes config set KEY VAL` for individual settings
- Direct file edit for bulk changes
- `hermes config get KEY` to read current values
