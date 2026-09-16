#!/usr/bin/env python3
"""Audit the skills tree: valid frontmatter, unique names, no secrets.

Exit 0 = clean, 1 = problems found. Run before committing skill changes.
"""
import os
import re
import sys
from collections import Counter

ROOT = os.path.join(os.path.dirname(__file__), "..", "skills")

# Credential patterns that must never appear in a public skill file.
SECRET_PATTERNS = [
    r"sk-[a-zA-Z0-9_-]{20,}",          # generic sk- keys
    r"ghp_[A-Za-z0-9]{30,}",           # GitHub PAT
    r"gho_[A-Za-z0-9]{30,}",           # GitHub OAuth
    r"github_pat_[A-Za-z0-9_]{20,}",   # GitHub fine-grained PAT
    r"AKIA[0-9A-Z]{16}",               # AWS access key
    r"AIza[0-9A-Za-z_-]{35}",          # Google API key
    r"am_sk_[A-Za-z0-9]{8,}",          # Capafy
    r"xox[baprs]-[A-Za-z0-9-]{10,}",   # Slack
    r"hf_[A-Za-z0-9]{30,}",            # HuggingFace
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
]

frontmatter_issues = []
secret_hits = []
names = Counter()
total = 0

for dirpath, _dirs, files in os.walk(ROOT):
    if "SKILL.md" not in files:
        continue
    total += 1
    path = os.path.join(dirpath, "SKILL.md")
    rel = os.path.relpath(path, ROOT)
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError as e:
        frontmatter_issues.append(f"{rel}: unreadable ({e})")
        continue
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        frontmatter_issues.append(f"{rel}: no frontmatter block")
        continue
    fm = m.group(1)
    nm = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
    dm = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
    if not nm:
        frontmatter_issues.append(f"{rel}: missing name:")
    else:
        names[nm.group(1).strip()] += 1
    if not dm:
        frontmatter_issues.append(f"{rel}: missing description:")
    for pat in SECRET_PATTERNS:
        for hit in re.finditer(pat, text):
            # ignore obvious placeholders / examples
            frag = hit.group(0)
            if frag in ("***REMOVED***",) or "..." in frag:
                continue
            line_start = text.rfind("\n", 0, hit.start()) + 1
            line_end = text.find("\n", hit.end())
            line = text[line_start:line_end if line_end != -1 else len(text)]
            # scanning-pattern examples inside security skills are documentation
            # (a real PEM block starts at column 0, never inside backticks)
            if re.search(r"grep|regex|pattern|scan", line, re.IGNORECASE):
                continue
            if pat.endswith("PRIVATE KEY-----") and "`" in line:
                continue
            secret_hits.append(f"{rel}: matches {pat}")

dups = {n: c for n, c in names.items() if c > 1}
print(f"skills={total} unique_names={len(names)} "
      f"frontmatter_issues={len(frontmatter_issues)} "
      f"duplicate_names={len(dups)} secret_hits={len(secret_hits)}")

for issue in frontmatter_issues:
    print("FRONTMATTER", issue)
for n, c in sorted(dups.items()):
    print(f"WARN duplicate name (vendored upstream vs curated copy, allowed): {n} x{c}")
for hit in secret_hits[:20]:
    print("SECRET", hit)

# ponytail: dup names are warn-only — vendored external collections legitimately
# mirror curated skills; tighten only if the count starts growing.
failed = bool(frontmatter_issues or secret_hits)
sys.exit(1 if failed else 0)
