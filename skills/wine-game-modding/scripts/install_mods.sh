#!/usr/bin/env bash
# Install mod archives by plain file moves — no mod-manager tooling.
# Usage: GAME=<game-root> install_mods.sh <folder-with-archives> [modules-dir]
#   archives with SubModule.xml   -> Modules/<mod>/   (every module in the archive)
#   archives with bin/            -> game bin/ (loader dlls)
#   archives with a top Modules/  -> merged into game (file-replacement packs)
set -uo pipefail
GAME="${GAME:?set GAME to the game root}"
MODS="${2:-$GAME/Modules}"
[ -d "$1" ] || { echo "usage: GAME=<game-root> $0 <folder-with-archives> [modules-dir]"; exit 1; }
shopt -s nullglob
for a in "$1"/*.zip "$1"/*.7z "$1"/*.rar "$1"/*.ZIP "$1"/*.7Z "$1"/*.RAR; do
  t=$(mktemp -d)
  case "${a,,}" in
    *.zip) unzip -qo "$a" -d "$t" >/dev/null 2>&1 || 7z x -y -o"$t" "$a" >/dev/null 2>&1 ;;
    *)     7z x -y -o"$t" "$a" >/dev/null      || true ;;
  esac
  if [ -z "$(ls -A "$t" 2>/dev/null)" ]; then
    echo "SKIP (unreadable): $a"; chmod -R u+w "$t" 2>/dev/null; rm -rf "$t" 2>/dev/null; continue
  fi
  # read-only Windows attrs break rm/cp; normalize first
  chmod -R u+w "$t" 2>/dev/null
  if find "$t" -name SubModule.xml | grep -q .; then
    while IFS= read -r sm; do
      # never install a husk: 7z extracts RAR3 as 0-byte files ("Unsupported Method")
      [ -s "$sm" ] || { echo "SKIP (empty SubModule.xml — extract this RAR via libarchive): $a"; continue; }
      d=$(dirname "$sm"); name=$(basename "$d")
      [ "$d" = "$t" ] && name=$(basename "${a%.*}")   # SubModule at archive root -> name after archive
      chmod -R u+w "$MODS/$name" 2>/dev/null
      rm -rf "$MODS/$name" 2>/dev/null
      mkdir -p "$MODS/$name"; cp -r "$d/." "$MODS/$name/"
      echo "MOD: $name"
    done < <(find "$t" -name SubModule.xml)
  elif [ -d "$t/bin" ]; then
    cp -rn "$t/bin/." "$GAME/bin/" 2>/dev/null || cp -r "$t/bin/." "$GAME/bin/"
    echo "BIN: $(basename "$a")"
  elif m=$(find "$t" -mindepth 1 -maxdepth 2 -type d -name Modules | head -1) && [ -n "$m" ]; then
    cp -r "$m/." "$GAME/Modules/"
    echo "TREE: $(basename "$a")"
  else
    echo "SKIP (no SubModule.xml, no bin/, no Modules/): $a"
  fi
  chmod -R u+w "$t" 2>/dev/null
  rm -rf "$t" 2>/dev/null
done
