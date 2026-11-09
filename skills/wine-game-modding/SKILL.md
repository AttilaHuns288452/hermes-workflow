---
name: wine-game-modding
description: Use when modding Windows games under Wine or fixing mods.
version: 1.0.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [gaming, wine, modding, bannerlord, nexus]
    related_skills: [linux-gui-automation]
---

# Wine Game Modding

## When to Use
- Installing or updating mods for a Windows game that runs under Wine on Linux.
- Recovering a mod list/pack from an old drive, wiped Windows profile, or dead mod-manager deployment.
- A game launcher or mod manager misbehaves under Wine (crash on Play, missing verifier, bad load order).

Not for: native Linux game modding, or emulator/VM game setups.

Install, recover, and repair mods for Windows games running under Wine (fixing their launchers included). The authoritative state is always the game's own config and log files on disk — a launcher that opens, or a mod folder that looks populated, is not proof.

## Procedure

### 1. Inventory before touching anything
Locate the game dir, the Wine prefix, the launch script, the modules/mods dir, and the game's log dir (e.g. `<prefix>/drive_c/ProgramData/<Game>/logs`). Read the newest log first: it shows how the game currently behaves and what it already loads.

If a mod manager ever ran (Vortex etc.), its deployment manifests (`vortex.deployment*.json` next to the game) are the authoritative mod list: package names, versions, and per-file sources.

### 2. Recover only what is actually recoverable
- Mod managers with a "symlink activator" deploy method fill the game dir with symlinks into a staging folder. `test -e` a sample per module: all-dead links means the staging folder is gone and the content is unrecoverable on that drive. Stop hunting; rebuild the mod list from the deployment manifest.
- Package names in manifests follow `<name>-<modid>-<version>-<epoch>[.rev]`: `modid` = first pure-numeric segment (≤5 digits), `epoch` = trailing 10-digit timestamp. The epoch equals the mod site's file upload date and is the strongest key for re-finding the exact file later.

### 3. Download the mods
See `references/nexus-download-automation.md` for the Nexus Mods free-account flow: browser-driven, exact-version matching, resumable.

### 4. Install archives with extraction verification
Use `scripts/install_mods.sh` (set `GAME=` to the game root). It installs every module tree found in an archive, merges `bin/` payloads into the game, and merges bare `Modules/` file packs. Then verify: every installed module must have a **non-empty, parseable** SubModule.xml (or the game's equivalent manifest).

Pitfalls:
- p7zip without the RAR codec prints "Unsupported Method" yet exits 0 with partial or empty files — a silent husk. Extract RAR via libarchive instead (`uv run --with libarchive-c python`): `entry.extract()` does not exist; write `entry.get_blocks()` yourself to a normalized path (`\`→`/`, reject `..`).
- Windows-built zips may store backslash path separators; `unzip`/`7z` flatten them into literal filenames so module discovery silently finds nothing. Extract those with python `zipfile`, replacing `\` with `/` in entry names.
- Some archives ship several modules — install every dir containing SubModule.xml, not the first hit.
- Files from Windows archives/dirs can be read-only; `chmod -R u+w` before `rm -rf` or a `set -e` installer aborts mid-run.
- Resolve dll/module file lookups case-insensitively (Windows references like `Foo.dll` vs on-disk `foo.dll`) and prefer the platform folder the game actually runs (e.g. `bin/Win64_Shipping_Client/` over `bin/Gaming.Desktop.*/`) when same-named copies exist with different sizes.
- Re-installing over an already-installed module silently reverts any manual fix (patched manifest, added dll). Make fixes durable by patching and repacking the SOURCE ARCHIVE, then re-installing from it; a module-level patch is temporary state.

### 5. Fix module dependency declarations
After install, cross-check every module manifest's dependency ids against the **enabled** modules' ids (run `scripts/audit_module_deps.py`; also treat a dependency on an installed-but-disabled module as broken). Mods routinely declare legacy ids (a library renamed over the years), brand-new library dependencies their older versions never had, or a module the user has toggled off. A dependency id the launcher cannot resolve crashes the launcher's start path with a bare NullReferenceException (the version lookup returns null and gets dereferenced) and can break the game too. Fix: patch the dependency id to the installed module's real id, install the missing library, or enable the depended-on module. Re-run the audit after every install AND every enable/disable change. A dependency id resolves to a module (`SubModule.xml` `<Id>`), never to DLLs: a library archive merged as a `bin/` payload registers no module id, so any dep on it stays broken even though its DLLs sit right there — when the audit flags a dep, check whether the providing archive was installed bin-only and re-install its module tree (or patch the dep out).

### 5b. Audit each module's manifest against its own disk contents
Run `scripts/audit_module_deps.py`, then check every `<SubModule><DLLName>` against the module's `bin/`: (a) a declared DLL that exists only with different CASE is a load failure under Wine — symlink/copy to the exact declared name; (b) a module that declares a LIBRARY submodule it does not ship (e.g. `MCMv5.dll` listed inside a small mod) crashes the loader — delete those `<SubModule>` blocks, the library lives in its own module. Both defects look like random crashes later, so check them before any bisect.

### 6. Enable, order, verify
- Load order: library mods first, then vanilla modules, then gameplay mods; topologically sort the rest by declared dependencies (a mod must load after everything it depends on). The ORDER OF THE LAUNCH ARGUMENT is what the engine uses — a config file in canonical order is not enough if the argument builder ranks vanilla first. Library mods (Harmony, ButterLib, UIExtenderEx, MCM) ship `ModulesToLoadAfterThis` pointing at the vanilla modules, which is WRONG for the argument: force libraries ahead of vanilla and ignore their `after` metadata, or ButterLib opens a "strongly recommended to terminate the game" dialog on every launch.
- Launch the game from the user's own session (desktop entry or their terminal) — never from an agent background terminal. Agent workers run in a memory-capped scope and the game gets killed mid-session once it grows past the cap; ship a `.desktop` entry as part of the setup.
- A crash demanding one insane allocation ("could not get new memory", tens of GB) at data-load time is a single incompatible mod's data, not RAM pressure. Bisect without the launcher UI: toggle enabled flags in the game's config, direct-launch, read the newest log; ~log2(n) launches pinpoints it. Keep the LAUNCH METHOD constant across bisect rounds — the launcher passes an explicit module list on the command line while a raw-exe direct launch boots vanilla-only unless the launch script reconstructs that argument from the saved config, so mixing paths confounds the toggle with the launch path. Confirm the culprit by re-enabling it through the same path that produced the clean rounds. Between rounds, kill the wine debugger and close any leftover "Program Error" crash dialogs — a stale dialog from the previous round reads as a fresh failure in screenshots and sends you chasing the wrong crash.
- Multiple broken mods can coexist: the game dies on the FIRST one it hits, masking the rest. After each clean boot, check for NEW exception signatures (type-load errors, Harmony patch failures) that appeared post-main-menu — each round reveals at most one or two more culprits. Disable and retest until zero exceptions; the game reaching the main menu is NOT success if Harmony patches fail after it.
- With 70+ mods the game can sit at the module-scanning log phase (SubModule.xml loads) for 2+ minutes before advancing. A log "stuck" at ~150-200 lines with the game process consuming CPU is slow loading, not a hang — wait 2 minutes past the last check before killing it.
- Verify with the game's own log: the `Command Args` line is ground truth for what the game was told to load (it must contain the module-list argument), mod-DLL `Loading assembly` lines prove mods are in the load, and there must be zero exceptions. A log full of SubModule.xml scans alone proves nothing — the game scans every installed module regardless of the loadout. Never report success from the absence of an error dialog alone.
- Mod ACTIVATION can only be verified from a session that entered a game: at the main menu the log shows module scans ("Loading xml file: .../SubModule.xml") and vanilla assemblies only; mod code loads when a campaign or save session starts. "Mods scanned" is not "mods running".
- When the user reports the mods "do nothing": FIRST read that session's game log and check the `Command Args` line plus mod-assembly lines — if the launcher's module-list argument is absent or no mod assemblies loaded, the game booted vanilla-only and nothing is wrong with the mods themselves (fix the launch command, no reinstall needed). Only if mods genuinely loaded: ask whether they continued an OLD SAVE. Data mods (troops, cultures, items, starting states) are baked into the save at campaign creation and cannot retroactively apply; a new campaign is the only honest test. Next suspect is mods erroring in-game so their features silently no-op — read that session's error log before reinstalling anything.
- Deliver an experiential check alongside the log check: name one concrete in-game thing to look at (a settings menu the mod adds, one visible feature) so the user can see the mods work. Log counts alone do not land.
- Launcher confirmation dialogs that list every mod dll ("You're loading unverified code from: ...") read to users as a wall of errors. Explain it once as a normal modded-launch warning, and prefer shipping a launcher-free direct-play .desktop entry whose script reconstructs the launcher's module-list command-line argument from the saved loadout (the raw exe applies NO mods without it) so everyday play never shows it; keep the launcher entry for editing the mod list.

### 7. Diagnose a crash before bisecting
Drive the game from a harness, never by hand, or every round costs a screenshot argument. A working Bannerlord harness (`~/Games/bl_test.py` pattern): kill leftovers -> write the enabled set -> launch the user's .desktop entry -> poll 5s for (game window, "Safe Mode" window, crash dialog, process alive) -> after the window appears WAIT ~30s more before declaring success (crashes surface immediately after the menu paints) -> report + screenshot.

Two dialogs poison automated verification:
- **"Safe Mode"** ("Game shut down unexpectedly on previous session. Would you like to enable safe mode?") appears on EVERY launch after a crash. Closing the window == "No" and the game continues normally. A harness that treats it as a crash reports 100% failure after the first real crash — the single most expensive false signal in this workflow.
- The crash reporter windows are titled **`*_*`** (class `watchdog.exe`) and **"The application faced a problem"**. Both are split-window dialogs whose Yes/No cannot be clicked reliably through XTest under Wine; close them with `wmctrl -ic <id>` instead of clicking, and close stale ones BEFORE each launch.

The log line that ends at the last `SubModule.xml` scan is NOT the fault. Real faults to grep for:

| Log text | Meaning | Fix |
|---|---|---|
| `Error while getting types and loading ... Loader Exceptions: Method 'X' in type 'Y' from assembly 'Z' ... does not have an implementation` | Module Z compiled against a different game build (interface member absent) — fatal | Drop or rebuild that module |
| `Requested memory size is <tens of GB>` after `Loading packages $BASE/Modules/<X>/` | X's item/asset XML allocates absurd memory on this build | Drop X |
| `Shader cache version of the external module (X) is invalid` then death | X ships `Shaders/<api>/compressed_shader_cache.sack` built for another build | Move the `.sack` out of the module |
| `Couldn't find .dll: ...Platform.PS.dll / Platform.GDK.dll / DedicatedServer.dll` | Console/dedicated-server submodules absent on a GOG desktop build — benign | Ignore |
| `Better exception window unhandled exception: Patching exception` + `Undefined target method` | Harmony patch target missing on this build — non-fatal but noisy | Drop the offending module |
| `Method not found: 'Boolean TaleWorlds.Localization.TextObject.op_Inequality(...)'` | Mod compiled against a newer game; 1.2.9 has no TextObject equality operators | Drop the module (see below) |
| `Method not found: '... TextObject.get_Empty()'` | 1.2.9 ships `TextObject.Empty` as a FIELD, not a property | Drop the module |
| NullReferenceException whose first frame is a game `Extensions.*` helper, called from a mod behavior on `OnHourAdvanced` | Mod passes a null/default argument into a game extension method | Drop the module |

**Only live stack traces are trustworthy for blame.** Static DLL-vs-assembly metadata scans (dnfile, MemberRef/TypeRef comparison) report the game's OWN modules (`Native`, `Sandbox`, `StoryMode`) as broken because generic type names (`Extensions`, `EventManager`) collide across namespaces — treat those results as noise. The reliable loop is: run the game, let the failing code path execute, read the first mod-owned frame in the log, drop that module, repeat. A mod can pass every declared-version and dependency check and still be compiled against a newer API; the manifest is not evidence.

**`StopGameOnFocusLost=True` in `BannerlordConfig.txt` pauses the campaign the moment the window loses focus.** Any automated verification that leaves the game unfocused will see the clock frozen and misread it as a hang or a pause the harness can't clear. Set it to `False` before long-running checks, and confirm progress from the log's `Before Daily Tick:` lines (they carry the in-game date) rather than screenshots.

A module that is incompatible on one axis is usually incompatible on several; once a mod's manifest pins a game version newer than the installed one, look for a version pinned to YOUR build on the mod page before dropping it, and expect the 2026-era uploads of old mods to have no compatible build at all.
When the game dies under wine (`Unhandled exception 0x...`), read the game's own crash output first — it lives beside the normal game log in the logs dir: `watchdog_log_*.txt` holds the ExceptionRecord (ExceptionCode + faulting address) plus a managed stack tail, and the run's `crashes/<timestamp>/dump.dmp` is the raw dump. Exception codes: `0xe0434352` is the CLR's unhandled-managed-exception marker, `0xC0000005` is a native access violation; one crash can report both (the game's watchdog dumps the native fault while wine surfaces the managed one) — trust the game's ExceptionRecord over the wine console line. The ordinary game log's final line is only the last flushed line before death, not the faulting operation: never diagnose from it alone.

## Related files
- `references/nexus-download-automation.md` — free-account Nexus download automation.
- `references/bannerlord.md` — Bannerlord-specific state, launcher repair, managed-code reverse-engineering recipe, and crash-signature table.
- `scripts/install_mods.sh` — archive installer (reusable for any game via `GAME=`).
- `scripts/audit_module_deps.py` — dependency-id cross-check (run after every install/enable change).