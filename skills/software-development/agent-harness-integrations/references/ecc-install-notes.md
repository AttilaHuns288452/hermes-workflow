# ECC Install Notes

## Profiles

Common profiles: `full`, `core`, `minimal`, `operator-workflows`.

## Key commands

Run from repo root (`~/Documents/Projects/ECC`).

- Install: `node scripts/install-apply.js --target <name> --profile <profile>`
- Build OpenCode payload: `node scripts/build-opencode.js`
- Status: `node scripts/ecc.js list-installed`
- Doctor: `node scripts/ecc.js doctor`
- Repair: `node scripts/ecc.js repair`
- Uninstall preview: `node scripts/uninstall.js --dry-run`
- Uninstall: `node scripts/install-apply.js --profile full --remove --target <name>`

## Hermes bridging

Hermes has no ECC adapter.
Use OpenCode as the closest official surface:
- store ECC output under `~/.opencode`
- reference those files from Hermes project rules/configs as needed

## Windows tips

- If installer reports ENOENT near `node.exe`, kill lingering Node and rerun
- Use `node scripts/install-apply.js` rather than shell scripts for reliability on Windows
