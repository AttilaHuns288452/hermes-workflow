#!/usr/bin/env python3
"""Scan public repository text files for credential-shaped values.

Reads Git-tracked and non-ignored working-tree files. Does not follow symlinks,
make network requests, or print matched credential values.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

if __package__:
    from .audit_skills import SECRET_PATTERNS, find_secret_hits
else:
    from audit_skills import SECRET_PATTERNS, find_secret_hits

ROOT = Path(__file__).resolve().parents[1]
MAX_TEXT_FILE_BYTES = 10 * 1024 * 1024
SAMPLE_BYTES = 8192


def _looks_like_text(sample: bytes) -> bool:
    if b"\0" in sample:
        return False
    decoded = sample.decode("utf-8", errors="replace")
    if not decoded:
        return True
    printable = sum(char.isprintable() or char in "\r\n\t\f" for char in decoded)
    return printable / len(decoded) >= 0.95


def list_repo_files(root: Path) -> list[Path]:
    """Return tracked and non-ignored working-tree paths without using the network."""
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    paths = {Path(os.fsdecode(item)) for item in result.stdout.split(b"\0") if item}
    return sorted(paths, key=lambda path: path.as_posix())


def _safe_label(value: str) -> str:
    for pattern in SECRET_PATTERNS:
        value = re.sub(pattern, "[REDACTED]", value)
    return value.replace("\n", "?").replace("\r", "?")


def scan_paths(root: Path, paths: list[Path]) -> tuple[list[str], list[str], int, int]:
    """Return (hits, errors, scanned_text_files, skipped_paths)."""
    root = root.resolve()
    hits: list[str] = []
    errors: list[str] = []
    scanned = 0
    skipped = 0

    for relative in paths:
        if relative.is_absolute() or ".." in relative.parts:
            errors.append("invalid repository path")
            continue
        path = root / relative
        path_text = relative.as_posix()
        label = _safe_label(path_text)
        try:
            has_symlink_component = any(
                root.joinpath(*relative.parts[:index]).is_symlink()
                for index in range(1, len(relative.parts) + 1)
            )
            if has_symlink_component:
                skipped += 1
                continue
            if not path.exists():
                skipped += 1
                continue
            resolved = path.resolve(strict=True)
            if not resolved.is_relative_to(root):
                errors.append(f"{label}: resolves outside repository")
                continue
            if not resolved.is_file():
                continue
            with resolved.open("rb") as stream:
                sample = stream.read(SAMPLE_BYTES)
                if not _looks_like_text(sample):
                    skipped += 1
                    continue
                size = resolved.stat().st_size
                if size > MAX_TEXT_FILE_BYTES:
                    errors.append(f"{label}: oversized text file; scan incomplete")
                    continue
                data = sample + stream.read()
        except OSError:
            errors.append(f"{label}: unreadable; scan incomplete")
            continue

        scanned += 1
        text = data.decode("utf-8", errors="replace")
        hits.extend(find_secret_hits(label, text))

    return hits, errors, scanned, skipped


def main() -> int:
    try:
        paths = list_repo_files(ROOT)
    except (OSError, subprocess.CalledProcessError):
        print("ERROR: unable to enumerate repository files; scan incomplete")
        return 2

    hits, errors, scanned, skipped = scan_paths(ROOT, paths)
    print(
        f"public_paths={len(paths)} text_scanned={scanned} "
        f"nontext_symlink_or_missing_skipped={skipped} incomplete={len(errors)} secret_hits={len(hits)}"
    )
    for error in errors:
        print("INCOMPLETE", error)
    for hit in hits[:50]:
        print("SECRET", hit)
    if len(hits) > 50:
        print(f"SECRET {len(hits) - 50} additional hit(s) omitted; inspect locations locally")

    if errors:
        return 2
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
