# Cinnamon Spices Submission Checklist

Pre-PR validation checklist derived from the cinnamon-spices-desklets repo requirements.

## File Structure Required by CI

```
UUID/
├── info.json          # uuid, name, description, version, author (= GitHub username)
├── screenshot.png     # Desktop preview
├── README.md          # Install instructions (optional but recommended)
├── CHANGELOG.md       # Optional
└── files/
    └── UUID/
        ├── metadata.json      # uuid, name, description, maxInstances, cinnamonVersion
        ├── desklet.js         # Main GJS implementation
        ├── stylesheet.css     # St widget styles
        ├── icon.png           # 256×256 icon
        ├── settings-schema.json  # Optional: user-configurable settings
        └── po/                # Optional: translations
            └── UUID.pot
```

## info.json Schema

```json
{
  "uuid": "name@author",
  "name": "Human Readable Name",
  "description": "Short description",
  "version": "1.0.0",
  "author": "github_username",
  "license": "GPL-2.0",
  "website": "",
  "categories": ["fun", "multimedia"]
}
```

- `author` MUST be your GitHub username (the repo uses this for authorship tracking)
- `uuid` format: `name@author` (lowercase, no spaces)

## metadata.json Schema

```json
{
  "uuid": "name@author",
  "name": "Human Readable Name",
  "version": "1.0.0",
  "description": "Short description",
  "maxInstances": 1,
  "cinnamonVersion": "5.0",
  "author": "github_username"
}
```

- `maxInstances`: 1 for single-instance desklets, -1 for unlimited

## Pre-PR Checklist

- [ ] `info.json` author field matches your GitHub username
- [ ] `screenshot.png` shows the desklet on a realistic desktop
- [ ] `icon.png` is 256×256, readable at small sizes
- [ ] `metadata.json` `maxInstances` set correctly
- [ ] `desklet.js` passes `node --check`
- [ ] All files exist in both root (`info.json`, `screenshot.png`, `README.md`) and `files/UUID/`
- [ ] No duplicate desklet folders in the repo
- [ ] Fork is up to date with upstream before PR

## CI Validation

The `validate-spice` script checks:
- Required files exist
- UUID directory structure is correct
- `info.json` and `metadata.json` are valid JSON with required fields
- `files/` contains ONLY the UUID directory (nothing else)

Run locally before pushing:
```bash
cd cinnamon-spices-desklets
./validate-spice UUID
```

## Common Rejection Reasons

1. **Missing screenshot.png** — every spice needs a preview
2. **Missing icon.png** — required for the website listing
3. **Author mismatch** — `info.json` author must equal your GitHub username
4. **Extra files in files/** — only the UUID directory is allowed inside `files/`
5. **Invalid JSON** — syntax errors in info.json or metadata.json
6. **UUID mismatch** — folder name must match `uuid` field in both JSON files

## Submission Workflow

```bash
# Fork on GitHub first (one-time), then:
git clone https://github.com/YOUR_USER/cinnamon-spices-desklets.git
cd cinnamon-spices-desklets

# Copy desklet to repo root
cp -r ~/path/to/your-desklet@user .

# Commit and push
git add desklet@user
git commit -m "Add <Name> desklet

<Description>

UUID: desklet@user
Author: YOUR_USER
License: GPL-2.0"
git push origin master

# Open PR
gh pr create --repo linuxmint/cinnamon-spices-desklets \
  --base master --head YOUR_USER:master \
  --title "Add <Name> desklet" \
  --body "<Description>\n\n## UUID\n<uuid>\n\n## Author\nYOUR_USER\n\n## License\nGPL-2.0"
```

## Pitfall: Check for Existing Desklet First

Before scaffolding a new desklet directory, check whether one already exists:

```bash
find ~ -maxdepth 4 -type d -name "*<partial-name>*" 2>/dev/null
find ~/.local/share/cinnamon/desklets -maxdepth 2 -type d
```

If the user already has files (desklet.js, metadata.json, stylesheet.css), copy the existing folder into the repo and only add missing files (screenshot.png, icon.png) — do not overwrite their work.

## Pitfall: Git Auth

`git push` may fail with `could not read Username` if gh auth is not configured for git:

```bash
gh auth setup-git
```
