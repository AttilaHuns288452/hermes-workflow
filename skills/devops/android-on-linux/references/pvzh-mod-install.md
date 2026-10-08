# PvZ Heroes mod install (bundle-replacement mods)

Applies to PvZH fan mods distributed as game-data bundle folders (e.g. Altrox). Base
package: `com.ea.gp.pvzheroes`.

Mechanics (per the mod's shipped READ-ME — re-verify per version):

- Prerequisites: file manager with Android/data access (or adb), vanilla PvZH fully
  loaded (finish the vanilla tutorial so the game downloads every bundle first), PvZH
  account linked as backup.
- Replace the bundle set: place the mod's `atlastagged/` + `autotagged/` folders into
  `/sdcard/Android/data/com.ea.gp.pvzheroes/files/cache/bundles/`, overwriting.
- Pin the mod by swapping the `versions` index so the game never re-downloads vanilla
  bundles over it: run the mod's `versions helper.html` in a browser (it reads the
  game's `versions` file and emits `versions.txt` tagged for the mod's bundles), move
  the generated file into `bundles/`, rename original `versions` -> `versions vanilla`,
  then `versions.txt` -> `versions`.
- Launch rule, EVERY session: start the game with internet OFF (airplane mode; in an
  emulator, cut the emulator's network) and restore network only at the main menu.
  Online launches let the game re-download vanilla bundles over the mod.
- Uninstall: rename `versions` -> `versions mod`, `versions vanilla` -> `versions`,
  launch online.

Gating quirks: the mod builds are gated to the same store regions as vanilla PvZH
(vanilla is not distributed in all countries), and ARM-only APKs need translation on
x86_64 (see SKILL.md phase 2).
