# Applet Packaging & Distribution (2026-09-04)

How to package a Cinnamon applet for sharing with others.

## When to Use

- You've built an applet and want to share it with friends
- You want a one-click install experience
- You don't want to submit to Cinnamon Spices (or want to share before/without it)

## Package Structure

```
etref-package/
├── README.md              # Documentation
├── install.sh             # One-click installer
├── info.json              # Package metadata
└── files/
    └── netref@attila/     # The actual applet folder
        ├── applet.js
        ├── metadata.json
        ├── settings-schema.json
        ├── stylesheet.css
        ├── icon.svg
        └── refdocs/
            └── Networking/
                └── sheet.json
```

## The install.sh Script

```bash
#!/bin/bash
# NetRef Applet - One-click installer
set -e

echo "=== NetRef Applet Installer ==="

# Find the files directory (works from inside package or parent)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -d "$SCRIPT_DIR/files/netref@attila" ]; then
    SOURCE_DIR="$SCRIPT_DIR/files/netref@attila"
elif [ -d "$SCRIPT_DIR/netref@attila" ]; then
    SOURCE_DIR="$SCRIPT_DIR/netref@attila"
else
    echo "ERROR: Cannot find netref@attila files."
    echo "Make sure you extracted the package first."
    exit 1
fi

echo "Found applet files at: $SOURCE_DIR"

# Install
APPLET_DIR="$HOME/.local/share/cinnamon/applets/netref@attila"
mkdir -p "$HOME/.local/share/cinnamon/applets"

if [ -d "$APPLET_DIR" ]; then
    echo "Removing old version..."
    rm -rf "$APPLET_DIR"
fi

echo "Installing..."
cp -r "$SOURCE_DIR" "$APPLET_DIR"

echo ""
echo "=== Installation complete! ==="
echo ""
echo "Next steps:"
echo "  1. Right-click your panel → Applets → Add"
echo "  2. Find 'NetRef - Networking Command Reference'"
echo "  3. Add it to your panel"
echo ""
echo "Or restart Cinnamon: Alt+F2 → type 'r' → Enter"
```

**Key points:**
- Auto-detects whether run from inside the package or from a parent directory
- Removes old version if present
- Uses `set -e` to fail fast on errors
- Tells user what to do after install

## Creating the Archive

```bash
# From the package directory:
cd ~/Applications
zip -r netref-package.zip netref-package
tar -czf netref-package.tar.gz netref-package
```

## Distribution Methods

| Method | How | Best For |
|---|---|---|
| **Discord** | Drag & drop zip into DM | Quick sharing |
| **Google Drive** | Upload → share link | Large files |
| **Email** | Attach zip | Direct sharing |
| **Telegram** | Send as file | Quick sharing |
| **GitHub Releases** | Tag release → attach zip | Permanent, versioned |
| **curl \| bash** | Host URL + one-liner | Power users |

## curl|bash One-Liner

Requires hosting the zip somewhere with a direct URL:

```bash
curl -L <URL>/netref-package.zip -o netref.zip && unzip netref.zip && cd netref-package && bash install.sh
```

**GitHub Releases setup:**
1. Create a repo on GitHub
2. Push your package
3. Create a release (tag like `v1.0.0`)
4. Attach `netref-package.zip` as a release asset
5. Get the download URL: `https://github.com/<you>/netref/releases/latest/download/netref-package.zip`
6. Share the one-liner

**Note:** curl|bash doesn't work with local files — the zip must be hosted somewhere accessible via HTTP(S).

## What Your Friend Needs

- Linux Mint with Cinnamon (any recent version)
- No internet needed after download
- No dependencies to install
- `unzip` (usually pre-installed)

## Lessons Learned

1. **Auto-detect paths** — `install.sh` should work whether run from inside the package or from a parent directory
2. **Use `set -e`** — fail fast instead of continuing with errors
3. **Tell user next steps** — don't assume they know how to enable the applet
4. **curl|bash needs hosting** — local files can't use this pattern; upload to GitHub Releases or similar
5. **Zip is more universal than tar.gz** — Windows/Mac can open zip without extra tools
6. **Keep the package small** — 17 KB is easy to share anywhere
