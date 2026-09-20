# MyOldOS Restore — Field Notes (2026-09-02 backup → Linux Mint 22.3)

Concrete observations from one real restore. The umbrella SKILL.md holds the durable workflow; this file holds session-specific detail.

## Backup Layout

Mount: `/media/attila/SP PHD U3/MyOldOS` — `fuseblk (ro)`, dirname contains a space (`SP PHD U3`), always quote. 16 dirs: `00_MANIFEST 01_HERMES 02_OMNIROUTE 03_AI_MODELS 04_VSCODE 05_PROJECTS 06_DATABASES 07_DOCUMENTS 08_CONFIG 09_CREDENTIALS_SECURE 10_GIT 11_DEVELOPMENT 12_WINDOWS_COMPATIBILITY 13_RESTORE_SCRIPTS 14_INSTALLERS_AND_REFERENCES 15_VERIFICATION` + `HERMES_OMNIROUTE_VALIDATION.md`.

## Sizes

- `01_HERMES/` ~11G (full `data/` copy incl. caches); `05_PROJECTS/` ~7.1G (~60 repos); `06_DATABASES/` ~4.0G (16 verified SQLite DBs).
- `state.db` ~3.3G, `.codegraph_codegraph.db` ~880M — need ~25G+ free headroom; target disk had 379G available.
- `07_DOCUMENTS/`, `11_DEVELOPMENT/`, `14_INSTALLERS_AND_REFERENCES/` were empty at backup time.

## Key Docs

- Order of truth: `00_MANIFEST/MIGRATION_MANIFEST.md` → `13_RESTORE_SCRIPTS/HERMES_IMPORT.md` → `OMNIROUTE_IMPORT.md` → `LINUX_SETUP.md` → `01_HERMES/HERMES_MIGRATION_MANIFEST.md`, `02_OMNIROUTE/OMNIROUTE_MIGRATION.md`, `03_AI_MODELS/AI_MODELS_MIGRATION.md`, `06_DATABASES/DATABASE_MIGRATION.md`, `09_CREDENTIALS_SECURE/CREDENTIALS_INDEX.md`, `10_GIT/GIT_MIGRATION.md`, `12_WINDOWS_COMPATIBILITY/WINDOWS_TO_LINUX.md`, `15_VERIFICATION/BACKUP_VERIFICATION.md`.
- OmniRoute config lives in Hermes `config.yaml` providers section; `02_OMNIROUTE/data/` held only `server.log` + `watchdog.cmd`. Port 20128, `curl` 404 = healthy.
- AI: Ollama 0.32.14 installed, zero models on disk → re-pull `qwen2.5-coder:7b`, `qwen2.5-coder:1.5b`, `qwen3:8b`. Cloud models via commandcode/nous/openrouter need no file copy.
- VS Code: 119 extensions in `vscode-extensions.txt` (several `-win32-x64` suffixed → skip on Linux), settings at `04_VSCODE/settings/settings.json`.

## Gaps Hit (reconstruct, don't fail)

- `10_GIT/gitconfig_roaming` absent (only `GIT_MIGRATION.md`) → rebuild `~/.gitconfig` from the doc's settings (`user.email=attilasabiniano@gmail.com`, `user.name=AttilaHuns288452`, LFS filters, `credential...helper=gh auth git-credential`).
- `gh_auth/hosts.yml` had `user:` but no `oauth_token` → `gh auth login` required. `gh_auth/config.yml` aliases (`co: pr checkout`) copied fine.
- No `.ssh/`, no GPG keys on Windows → generate `ed25519` on Linux only if needed.
- MySQL 9.2 installed but not running at backup → no dump; flagged MANUAL ACTION REQUIRED.
- `09_CREDENTIALS_SECURE/config.yaml` (36K) duplicates `01_HERMES/data/config.yaml` — providers commandcode + nous, default `poolside/laguna-s-2.1:free`.
- `01_HERMES/data/` contains live `-shm`/`-wal` sidecars and regenerable caches (`audio_cache`, `cache`, `bootstrap-cache`) — stop Hermes before copying DBs, skip caches.

## Linux Target Correction

Manifest claimed `$HOME/.local/share/hermes/` (nonexistent); live home was `$HERMES_HOME=/home/attila/.hermes` with fresh `state.db` (1 session, 23 msgs). Restored into `$HERMES_HOME`, never the manifest's hardcoded path. Fresh box already had Node v26.8.1 + Python 3.11.16 + Git 2.43; missing Java/Docker/VS Code/Ollama/gh/ripgrep → native installs.
