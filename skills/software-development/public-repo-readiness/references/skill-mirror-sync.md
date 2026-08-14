# Skill Mirror Sync — tested recipe (hermes-workflow, 2026-08)

Syncs a live Hermes skills install (`C:\Users\<user>\AppData\Local\hermes\skills`) into a repo mirror (`skills/`), adding missing skills and replacing changed ones. Byte-verified end-to-end; used for a 302-local → 351-mirror sync (193 added, 65 refreshed) with zero content mismatches.

## Procedure

1. Fresh clone: `git clone --depth 1 <url> /tmp/hw` (bash). If patching files under `/tmp`, verify with `git status` afterward — see Pitfall 4 in SKILL.md.
2. Run the sync script below with `python` (Windows paths).
3. Re-run the script's verify section: remaining mismatches must be ONLY `__pycache__/*.pyc` (excluded on purpose — and gitignored).
4. Junk sweep: `find skills -type d -name '.temp' -o -type d -name '*.bak'` → `git rm -r` + gitignore `.temp/`, `__pycache__/`, `*.pyc` (a capafy `.temp/confirmed-selections.json` rode in once; a `codex.bak` dir too).
5. Count: `find skills -name SKILL.md | wc -l` → update README (hero, badge `Skills-NNN`, quick-start comment, stats block) + SETUP step header + blurb. The `sed` count-fix missed the em-dash line (`📦 508    Skills`) — patch that one manually.
6. `git add -A && git commit && git push`.

## The sync script

```python
import os, shutil, hashlib

LOCAL = r"C:\Users\<user>\AppData\Local\hermes\skills"
REPO  = os.environ["TEMP"] + r"\hw\skills"   # git-bash /tmp == %TEMP%

def skill_map(root, skip_prefixes=("external",)):
    m = {}
    for dirpath, dirnames, filenames in os.walk(root):
        if "__pycache__" in dirpath or any(x in dirpath for x in skip_prefixes):
            continue
        if "SKILL.md" in filenames:
            m[os.path.relpath(dirpath, root)] = dirpath
    return m

def tree_hash(d):
    h = hashlib.sha256()
    for dp, dn, fn in os.walk(d):
        for f in sorted(fn):
            p = os.path.join(dp, f)
            h.update(os.path.relpath(p, d).encode()); h.update(b"\0")
            try: h.update(open(p, "rb").read())
            except OSError: pass
    return h.hexdigest()

local = skill_map(LOCAL)
repo  = skill_map(REPO)  # repo may have a vendored external/ subtree — skip it in the map
missing = sorted(set(local) - set(repo))
differ  = [s for s in sorted(set(local) & set(repo)) if tree_hash(local[s]) != tree_hash(repo[s])]

# CRITICAL: deepest-first for differ — rmtree of a parent skill dir wipes its
# nested skill dirs, so copying parent-before-nested makes the nested copy
# land in a deleted tree (FileExistsError on the nested makedirs).
order = sorted(differ, key=lambda r: -r.count(os.sep)) + missing
for rel in order:
    src, dst = local[rel], os.path.join(REPO, rel)
    if rel in differ and os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

# verify: every local skill byte-identical in repo
mismatch = [r for r in local
            if r not in skill_map(REPO) or tree_hash(local[r]) != tree_hash(os.path.join(REPO, r))]
print(f"missing={len(missing)} differ={len(differ)} mismatches={len(mismatch)}")
print("\n".join(mismatch[:20]))  # expect only __pycache__-only diffs
```

## Pitfalls hit in practice

- **First sync attempt failed** with `FileExistsError` on `frontend-design\design-prototype-transplant` — parent `frontend-design` was copied after its nested skill dirs; rmtree+copy ordering fixed it.
- **`dirs_exist_ok=False` (default) crashes** when a repo dir partially exists from an interrupted prior run — pass `dirs_exist_ok=True`.
- **Run 1 crashed midway, run 2's counts differed** — always trust the final verify pass, not the "copied N" counter.
- **Nested skills** (`frontend-design/design-prototype-transplant`, `autonomous-ai-agents/agency-agents`) are real skill dirs with their own SKILL.md — a per-dir map handles them; a flat top-level-only map silently skips ~100 skills.
- **Repo-only extras** (legacy skills removed locally, e.g. `apple/*`, `creative/excalidraw`) — leave them; deleting risks removing intentional content. Prune only on explicit request.
- **Binary scan catches what text grep misses**: a committed `__pycache__/*.pyc` (24 KB) carried the username — `git ls-files | grep -E '\.pyc$|__pycache__'` + delete + gitignore.
