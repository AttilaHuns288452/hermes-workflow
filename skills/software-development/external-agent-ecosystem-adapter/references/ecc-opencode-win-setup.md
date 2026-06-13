# ECC OpenCode Adapter Notes (Windows)

## Verified commands

```bash
# Build OpenCode plugin payload (required before install)
cd ~/Documents/Projects/ECC && node scripts/build-opencode.js

# Install full profile to OpenCode home
cd ~/Documents/Projects/ECC && node scripts/install-apply.js --target opencode --profile full
```

## Verification

```bash
node ~/Documents/Projects/ECC/scripts/ecc.js list-installed
node ~/Documents/Projects/ECC/scripts/ecc.js doctor
node ~/Documents/Projects/ECC/scripts/ecc.js repair
```

## Observed quirks

- `install-apply.js --help` can leak help text if:
  - arguments are not quoted consistently,
  - the build step was skipped and the adapter rejects the payload,
  - Windows cmd shell misroutes POSIX flags.
- Preferred invocation: `bash -lc 'cd ... && node scripts/install-apply.js --target <id> --profile <name>'`.
