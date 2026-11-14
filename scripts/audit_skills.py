#!/usr/bin/env python3
"""Audit the skills tree: valid frontmatter, unique names, no secrets.

Exit 0 = clean, 1 = problems found. Run before committing skill changes.
"""
import os
import re
import sys
from collections import defaultdict

if __package__:
    from .validate_repo import load_yaml_text
else:
    from validate_repo import load_yaml_text

ROOT = os.path.join(os.path.dirname(__file__), "..", "skills")

# Credential patterns that must never appear in a public skill file.
SECRET_PATTERNS = [
    r"sk-(?:proj|svcacct|or-v1)-[a-zA-Z0-9_-]{20,}",  # common prefixed provider keys
    r"sk-ant-[a-zA-Z0-9_-]{20,}",      # Anthropic API keys
    r"sk-[a-zA-Z0-9]{32,}",            # legacy generic sk- keys
    r"ghp_[A-Za-z0-9]{30,}",           # GitHub PAT
    r"gho_[A-Za-z0-9]{30,}",           # GitHub OAuth
    r"ghu_[A-Za-z0-9]{30,}",           # GitHub user-to-server token
    r"ghs_[A-Za-z0-9]{30,}",           # GitHub server-to-server token
    r"ghr_[A-Za-z0-9]{30,}",           # GitHub refresh token
    r"github_pat_[A-Za-z0-9_]{20,}",   # GitHub fine-grained PAT
    r"glpat-[A-Za-z0-9_-]{20,}",       # GitLab PAT
    r"npm_[A-Za-z0-9]{36,}",           # npm access token
    r"sk_(?:live|test)_[A-Za-z0-9]{16,}",  # Stripe secret/test key
    r"AKIA[0-9A-Z]{16}",               # AWS access key
    r"(?i)(?:aws[_-]?secret[_-]?access[_-]?key|secret[_-]?access[_-]?key)\s*[:=]\s*['\"]?[A-Za-z0-9/+]{40}['\"]?",
    r"AIza[0-9A-Za-z_-]{35}",          # Google API key
    r"am_sk_[A-Za-z0-9]{8,}",          # Capafy
    r"xox[baprs]-[A-Za-z0-9-]{10,}",   # Slack
    r"hf_[A-Za-z0-9]{30,}",            # HuggingFace
    r"xai-[A-Za-z0-9_-]{20,}",          # xAI
    r"r8_[A-Za-z0-9]{20,}",             # Replicate
    r"pplx-[A-Za-z0-9_-]{20,}",         # Perplexity
    r"AIza[0-9A-Za-z_-]{20,}",          # Google API keys (short test keys too)
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"Bearer\s+[A-Za-z0-9._~+/=-]{24,}",  # bearer tokens

    r"postgres(?:ql)?://[^\s:@]+:[^\s@]+@",  # credentialed DB URLs
    r"mongodb(?:\+srv)?://[^\s:@]+:[^\s@]+@",
]

def is_documented_regex(fragment: str, line: str) -> bool:
    """Ignore a documented pattern only when the matched text itself is regex syntax."""
    context = re.search(r"\b(?:grep|regex|pattern)\b", line, re.IGNORECASE)
    syntax = re.search(r"\(\?[=!<:]|\\[sSdDwWbB]|\\\[|\[[^\]]+\](?:[+*?]|\{\d)", fragment)
    return bool(context and syntax)


def has_private_key_payload(text: str, offset: int) -> bool:
    """Require actual base64 material after a PEM marker, not a header-only example."""
    tail = text[offset:].replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\r", "\r")
    end = re.search(r"-----END [A-Z ]*PRIVATE KEY-----", tail)
    body = tail[:end.start()] if end else tail
    size = 0
    for line in body.splitlines():
        candidate = line.strip().strip("`\"',")
        if re.fullmatch(r"[A-Za-z0-9+/=]{16,}", candidate):
            size += len(candidate)
        elif candidate and not (":" in candidate or "..." in candidate or candidate.startswith("[")):
            break
    return size >= 64


def find_secret_hits(rel: str, text: str) -> list[str]:
    hits = []
    for pat in SECRET_PATTERNS:
        for match in re.finditer(pat, text):
            frag = match.group(0)
            if frag == "***REMOVED***" or "..." in frag or frag == "AKIAIOSFODNN7EXAMPLE":
                continue
            line_start = text.rfind("\n", 0, match.start()) + 1
            line_end = text.find("\n", match.end())
            line = text[line_start:line_end if line_end != -1 else len(text)]
            if "://" in frag:
                userinfo = frag.partition("://")[2].rsplit("@", 1)[0]
                user, _, password = userinfo.partition(":")
                user, password = user.strip("[]<>").lower(), password.strip("[]<>").lower()
                if user in {"user", "username", "postgres", "example", "test"} and password in {
                    "password", "pass", "postgres", "example", "test", "changeme", "***", "redacted"
                }:
                    continue
            if is_documented_regex(frag, line):
                continue
            if pat.endswith("PRIVATE KEY-----") and not has_private_key_payload(text, match.end()):
                continue
            hits.append(f"{rel}: matches {pat}")
    return hits


def main() -> int:
    frontmatter_issues = []
    secret_hits = []
    names = defaultdict(list)
    total = 0

    if not os.path.isdir(ROOT):
        print("ERROR: skills root missing; audit incomplete")
        return 2

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
        secret_hits.extend(find_secret_hits(rel, text))
        m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if not m:
            frontmatter_issues.append(f"{rel}: no frontmatter block")
            continue
        try:
            fm = load_yaml_text(m.group(1))
            if not isinstance(fm, dict):
                raise ValueError("frontmatter is not a mapping")
        except Exception:
            frontmatter_issues.append(f"{rel}: invalid or duplicate-key YAML frontmatter")
            continue
        for field in ("name", "description"):
            if not isinstance(fm.get(field), str) or not fm[field].strip():
                frontmatter_issues.append(f"{rel}: {field} must be a non-empty string")
        if isinstance(fm.get("name"), str) and fm["name"].strip():
            names[fm["name"].strip().casefold()].append(rel)

    dups = {n: paths for n, paths in names.items() if len(paths) > 1}
    print(f"skills={total} unique_names={len(names)} "
          f"frontmatter_issues={len(frontmatter_issues)} "
          f"duplicate_names={len(dups)} secret_hits={len(secret_hits)}")

    for issue in frontmatter_issues:
        print("FRONTMATTER", issue)
    for name, paths in sorted(dups.items()):
        print(f"WARN duplicate name (use a qualified path): {name}: {', '.join(sorted(paths))}")
    for hit in secret_hits[:20]:
        print("SECRET", hit)

    # ponytail: dup names are warn-only — vendored upstream collections legitimately
    # mirror curated skills; tighten only if the count starts growing.
    return 1 if frontmatter_issues or secret_hits else 0


if __name__ == "__main__":
    sys.exit(main())
