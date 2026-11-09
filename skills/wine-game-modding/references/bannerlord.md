# Mount & Blade II: Bannerlord (Wine)

Working setup: GOG 1.2.11 copy at `~/Games/Mount & Blade 2 - Bannerlord`, Wine prefix `~/Games/bl-prefix`, launcher script `~/Games/bannerlord.sh` (no arg = vanilla launcher with the Mods tab; `direct` = skip launcher). Tooling lives in `~/Games/`: `install-mods.sh`, `gen_launcher_data.py`, `gen_dllcheck.py`.

## LauncherData.xml (`~/Documents/Mount and Blade II Bannerlord/Configs/`)
- `<SingleplayerData><ModDatas><UserModData><Id><LastKnownVersion><IsSelected>` = enabled mods + entry order. `<Id>` is the MODULE ID from SubModule.xml `<Id value>`, NOT the folder name (folder `Jarl's Grafted Armory` = id `BerserkerKingCloak`) — selection/toggle scripts must match ids, and a launcher save rewrites generator-written folder-name entries into id-based ones. **The game does NOT read this file on its own**: the launcher translates it into a `_MODULES_*id1*id2*...*_MODULES_` command-line argument and without that argument `Bannerlord.exe /singleplayer` boots vanilla-only (only the 25 vanilla assemblies load — mods "do nothing" with zero errors, and new campaigns show no mod content). A direct-launch script must rebuild the argument from the selected ids in file order every boot:
  ```bash
  MODULES_ARG=$(python3 -c '
  import re, sys
  x = open(sys.argv[1], encoding="utf-8-sig").read()
  ids = [re.search(r"<Id>([^<]+)</Id>", b).group(1)
         for b in re.findall(r"<UserModData>(.*?)</UserModData>", x, re.S)
         if "<IsSelected>true</IsSelected>" in b]
  print("_MODULES_*" + "*".join(ids) + "_MODULES_")
  ' "$HOME/Documents/Mount and Blade II Bannerlord/Configs/LauncherData.xml")
  exec wine ./Bannerlord.exe /singleplayer "$MODULES_ARG"
  ```
  Pass the whole `_MODULES_*...*_MODULES_` string as ONE shell argument (module ids can contain spaces, e.g. `Better Npcs`). `bannerlord.sh direct` does exactly this. Verify in the game log's `Command Args` line and via mod-DLL `Loading assembly` lines (the log dir is CRLF — `tr -d '\r'` before grepping).
- `<DLLCheckData><DLLData>` items `<DLLName><DLLVerifyInformation><LatestSizeInBytes><IsDangerous>` = the launcher's dll-verify cache. `gen_dllcheck.py` fills it from every SubModule's DLLName reference (name + byte size of the `bin/Win64_Shipping_Client/` copy, case-insensitive). Entries matching name+size skip the verify step entirely.
- `gen_launcher_data.py` regenerates the whole loadout (libraries → vanilla → mods, topological by DependedModules). Do not re-run it after hand-curating a loadout. Never edit LauncherData.xml while the launcher is running: it saves its own state on exit and overwrites yours.

## Vanilla launcher Play-button failure modes
- GOG/cracked copies ship no `ModVerifier/ModVerifier.exe`; the verify step logs "File not found" and fails. A pre-filled DLLCheckData cache skips it.
- The signature Play crash is `Exception occurred inside invoke: ExecuteStartGame` / "Object reference not set": caused by a `<DependedModule>` whose Id matches no module the launcher will resolve — missing entirely, or installed but deselected (the version lookup misses it and the comparison dereferences null). Fix the dep id, install the missing module, or enable the depended-on module.
- With any non-certified dll enabled, Play shows "You're loading unverified code from: ... Are you sure?" — that dialog is normal for modded installs; continue through it.

## Reverse-engineering a misbehaving Windows launcher (managed code)
First capture the process console output (the wine stdout of the launcher): the in-app log typically shows only a reflection wrapper ("Exception has been thrown by the target of an invocation") while the real inner exception + stack trace prints to the console. Read that before any IL.

When no log explains a launcher failure, read the .NET IL: `uv run --with dnfile --with dncil python`, dump method bodies from the launcher assemblies (here `TaleWorlds.MountAndBlade.Launcher.Library.dll`, `TaleWorlds.ModuleManager.dll`), resolve metadata tokens to member names (MethodDef/MemberRef/Field/TypeRef + the #US string heap). Reading the actual control flow pinned both the verify-cache shape and the dependency crash above; error messages alone did not.

Bisecting mod crashes needs no launcher UI: flip `<IsSelected>` entries in LauncherData.xml and direct-launch (the launch script rebuilds the `_MODULES_` argument from the file each boot, so toggles take effect), checking the newest game log each round.

## Crash logs
The game writes its own crash records into the ProgramData logs dir: `logs/watchdog_log_*.txt` (ExceptionRecord + managed stack tail, e.g. `at Bannerlord.Program.dump_callback(...)`) and `crashes/<timestamp>/dump.dmp`. These carry the faulting exception and address; the rgl_log tail and the wine console line do not.

## Crash signature → root cause table
Read the rgl_log near the crash point and match the error text. Each signature means a different fix:

| Log signature | Meaning | Fix |
|---|---|---|
| `could not get new memory` + `Requested memory size is NNN bytes` (tens of GB) | One mod's item/asset data causes an insane allocation | Bisect mods; disable the culprit |
| `Loader Exceptions: Method 'X' in type 'Y' does not have an implementation` | Mod DLL targets a game-version API that no longer exists | Update mod or disable |
| `Error while getting types and loading` + `Could not load type 'X'` | Assembly references a type missing from current game version (often via Harmony `PatchAll`) | Update mod or disable |
| `Undefined target method for patch method static ...` | Harmony patch targets a method that doesn't exist | Update mod or disable |
| `Type initializer for 'X' threw an exception` | Static constructor crash (missing dependency, bad config) | Check mod deps or disable |
| `Exception occurred inside invoke: ExecuteStartGame` | Dep declaration points at missing/disabled module | Fix dep id or enable the module |

Multiple broken mods often coexist — the game dies on the first, masking the rest. After each fix, retest; new signatures appear post-main-menu as Harmony patches execute.

## Batch-toggling mods for bisect
Regex-match the `<UserModData>` blocks in LauncherData.xml to flip `<IsSelected>` in bulk:
```python
import re
cfg = open(path, encoding="utf-8-sig").read()
# disable one mod:
cfg = re.sub(r'(<Id>ModId</Id>\s*<LastKnownVersion>[^<]*</LastKnownVersion>\s*)<IsSelected>true</IsSelected>', r'\1<IsSelected>false</IsSelected>', cfg)
# enable only a known-good set:
good = {"Native", "SandBoxCore", ...}
def replacer(m):
    block = m.group(0)
    mid = re.search(r'<Id>([^<]+)</Id>', block)
    if not mid: return block
    return re.sub(r'<IsSelected>(?:true|false)</IsSelected>',
                  f'<IsSelected>{str(mid.group(1) in good).lower()}</IsSelected>', block)
cfg = re.sub(r'<UserModData>.*?</UserModData>', replacer, cfg, flags=re.S)
```
After writing, verify the selected list matches intent: `re.findall(r'<Id>([^<]+)</Id>\s*<LastKnownVersion>[^<]*</LastKnownVersion>\s*<IsSelected>true</IsSelected>', cfg)`.

## BLSE is bin-only in this copy
ButterLib's SubModule.xml declares `<DependedModule Id="BLSE.AssemblyResolver"/>`, but BLSE ships here only as `bin/Win64_Shipping_Client/Bannerlord.BLSE.*` DLLs (no `Modules/` entry), so the dep can never resolve. Fix: install the module-tree copy of the BLSE archive, or remove the dep line.