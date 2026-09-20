# Reference Library Preservation

When the user wants to permanently remove an external drive but keep reference skill libraries locally.

## Signal

User says: "I want to remove the external drive" / "copy to local" / "make the external drive unnecessary"

## Workflow

### 1. Discover the external drive

```bash
lsblk -f | grep -v "loop\|tmpfs"
mount | grep -iE "ext4|ntfs|vfat|exfat|usb"
```

Do NOT assume drive letters. Find the actual mount point (e.g., `/media/attila/SP PHD U3`).

### 2. Create local reference destination

```bash
mkdir -p ~/Documents/SkillReferences
```

### 3. Copy with rsync (not mv)

```bash
rsync -av --progress /path/to/external/repo1 ~/Documents/SkillReferences/
rsync -av --progress /path/to/external/repo2 ~/Documents/SkillReferences/
```

Use `rsync -av` to preserve:
- Timestamps
- Permissions
- Symlinks
- Git history (`.git/` directories)
- Repository structure

### 4. Verify the copy

```bash
# Count skills per repo
for repo in ~/Documents/SkillReferences/*/; do
    echo "$(basename $repo): $(find $repo -name SKILL.md | wc -l) skills"
done

# Check for broken symlinks
find ~/Documents/SkillReferences -type l ! -exec test -e {} \; -print
```

### 5. Checksum verification (optional)

For critical repositories, compare checksums:

```bash
# Generate checksums on source
find /path/to/external/repo -type f -exec md5sum {} \; | sort > /tmp/source_checksums.txt

# Generate checksums on destination
find ~/Documents/SkillReferences/repo -type f -exec md5sum {} \; | sort > /tmp/dest_checksums.txt

# Compare
diff /tmp/source_checksums.txt /tmp/dest_checksums.txt
```

### 6. Update Hermes references

Search for external drive paths in:
- `~/.hermes/config.yaml`
- `~/.hermes/skills/` (skill files referencing old paths)
- `~/.hermes/scripts/` (scripts referencing old paths)
- `~/.hermes/tmp/` (indexes referencing old paths)
- `~/.hermes/lightrag_index/` (search index)
- `~/.hermes/memories/` (memory files)

Replace with `~/Documents/SkillReferences/` where appropriate.

### 7. Rebuild indexes

```bash
# Rebuild LightRAG (if it referenced the old path)
python3 ~/.hermes/scripts/lightrag_build_index.py

# Rebuild reference search index (if it existed)
# Search the new local path instead of external
```

### 8. Test search

```bash
python3 ~/.hermes/scripts/lightrag_find.py "test query"
```

### 9. Simulate disconnection

Verify everything works WITHOUT the external drive:
- Active skills load
- Reference search works
- LightRAG works
- CodeGraph works
- No broken symlinks
- No references to `/media/` or `/mnt/` in active config

### 10. Report

Only declare complete when:
- All repos are copied and verified
- Hermes can search/use references without the external drive
- No critical skill references the external drive
- Git history is preserved (where present)

## Pitfalls

- **Documentation files**: Migration notes and restore documentation may reference the external drive path. This is OK — they are historical records, not operational dependencies.
- **LightRAG index**: May contain skill descriptions that mention `/media/` (e.g., skill names like `/media/youtube-content`). These are NOT drive references — they are just skill names. Only actual `/media/attila/SP PHD U3` paths are problematic.
- **Reference repos vs active skills**: Do NOT activate all reference skills. Keep them as a searchable library. The 244 active skills should remain the operational set.
- **Do NOT delete the external drive**: The external drive becomes a backup. Never delete or modify source repositories.
