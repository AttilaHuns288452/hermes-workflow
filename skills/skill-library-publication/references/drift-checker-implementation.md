# Implementing a repo-vs-live drift checker

The comparison is cheap to get subtly wrong: a checker can report "OK" while
large parts of the publication were never written. These are the four traps that
have actually produced a false green, in the order you hit them.

## 1. Compare files, not just `SKILL.md`

A skill is a directory. Comparing only `SKILL.md` certifies a repo that is
missing every `references/`, `templates/` and `scripts/` file a skill added
since it was first published.

```python
def _same_bytes(a: pathlib.Path, b: pathlib.Path) -> bool:
    """Byte comparison, line-ending agnostic.

    git autocrlf rewrites CRLF<->LF on checkout, so a Windows-authored script is
    byte-different and content-identical. Without normalization the gate reports
    drift on files nobody changed.
    """
    x, y = a.read_bytes(), b.read_bytes()
    if x == y:
        return True
    return x.replace(b"\r\n", b"\n") == y.replace(b"\r\n", b"\n")
```

For each shared skill, walk both trees and report the two cases separately —
they need different fixes:

```python
repo_files = {p.relative_to(repo_dir) for p in repo_dir.rglob("*") if p.is_file()}
live_files = {p.relative_to(live_dir) for p in live_dir.rglob("*") if p.is_file()}
for f in sorted(live_files - repo_files):
    report(f"{skill}/{f} (missing)        # never published")
for f in sorted(repo_files & live_files):
    if not _same_bytes(repo_dir / f, live_dir / f):
        report(f"{skill}/{f} (differs)        # published, now stale")
```

Both cases must make the checker exit non-zero. Missing-only is not enough:
a file that exists but is stale is the more common state.

**Do not let the root `SKILL.md` be counted twice.** The `SKILL.md` comparison
above already reports a changed body as `stale`; a supporting-file walk over the
same directory reports it again as `(differs)`, so one changed skill shows two
findings and inflates every count you report. Skip the skill-root file in the
supporting pass and compare only the rest:

```python
for f in sorted(repo_files & live_files):
    if f.parent == pathlib.Path(".") and f.name == "SKILL.md":
        continue  # already reported as stale by the body comparison
    if not _same_bytes(repo_dir / f, live_dir / f):
        report(f"{skill}/{f} (differs)")
```

## 2. The live-root convention can silently empty the comparison

The repo root and the live root are usually NOT the same shape:

```
repo/                       live/
├── README.md               └── skills/
└── skills/                     └── <category>/<skill>/SKILL.md
    └── <category>/<skill>/SKILL.md
```

The repo dual-roots at `skills/`, the live side roots one level higher and
contains a `skills/` child. If you pass the live root's PARENT to a function that
expects the skills dir, every path gains a prefix, `shared_paths` comes out EMPTY,
the per-file loop iterates zero times, and the checker prints `OK` — a green
result produced by comparing nothing.

Guard it explicitly, because an empty intersection is indistinguishable from a
clean repo in the summary line:

```python
if repo_paths and live_paths and not shared_paths:
    print("NO SHARED PATHS: repo and live roots do not line up; check the root convention")
    return 2
```

## 3. Test fixtures must mirror the real root convention

A test that builds `live/<skill>/SKILL.md` and passes `live_root=live` when
`main()` resolves `live_root/skills` will pass the assertion only by accident,
or fail with a confusing `assert 0 == 1`. Build the fixture in the same shape as
production and pass the same level:

```python
def _drift_fixture(tmp_path, repo_extra=None, live_extra=None):
    repo, live = tmp_path / "repo", tmp_path / "live"
    for root in (repo, live):
        s = root / "skills" / "example"
        s.mkdir(parents=True)
        (s / "SKILL.md").write_text("---\nname: example\n---\n", encoding="utf-8")
    for root, extra in ((repo, repo_extra or {}), (live, live_extra or {})):
        for rel, data in extra.items():
            t = root / "skills" / "example" / rel
            t.parent.mkdir(parents=True, exist_ok=True)
            t.write_bytes(data)
    for n in ("README.md", "SKILLS_CATALOG.md", "INTEGRATION.md"):
        (repo / n).write_text("", encoding="utf-8")
    return repo, live

# live_root is the SKILLS ROOT, matching main()'s live_root / skills resolution
monkeypatch.setattr(repo_drift, "parse_args", lambda: type("Args", (), {
    "repo_root": repo, "live_root": live / "skills"
})())
```

Write both directions as separate tests so neither can regress alone:

1. a `references/deep.md` present only on the live side makes `main()` return 1
   and print `(missing)`;
2. the same file on both sides with CRLF vs LF returns 0.

A test that only covers the clean case proves nothing about the checker.

## 4. Sync with the same walk the checker uses

Sync and check must agree on what "the same file" means, or they oscillate.
Reuse one walk over the shared skills dir and copy every missing or differing
file, then re-run the checker. Expect more drift on the second pass — copying
files settles names and aliases that the next comparison sees differently — and
loop until a clean report rather than trusting one pass.

Report the counts you actually measured (`512 updated, 231 added across 572
shared skills`), not a summary adjective.
