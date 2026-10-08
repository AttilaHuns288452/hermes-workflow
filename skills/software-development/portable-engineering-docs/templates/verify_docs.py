#!/usr/bin/env python3
"""verify_docs.py — reference-existence verifier skeleton.
Asserts every file path, symbol, migration file, and QA file referenced in the
docs exists at HEAD, then runs a stale-claim/secret scan of the generated
artifact. Exit 1 on any miss. Reproduce with modifications: set ROOT, globs,
and the per-project STALE patterns (architecture wording, versions, counts).
"""
import re, os, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent
ARTIFACT = ROOT / 'HANDBOOK.html'
md = '\n'.join(p.read_text() for p in (ROOT / 'docs').glob('*.md'))
fails = []

# 1. every backticked project path must exist somewhere in the tree
for raw in sorted(set(re.findall(r'`((?:src|app|lib|supabase|migrations|frontend)/[A-Za-z0-9_\-./]+)', md))):
    p = raw.rstrip('.,;:)')
    if not (ROOT / p).exists() and not list(ROOT.glob('**/' + p.split('/')[-1])):
        fails.append(f'MISSING PATH: {p}')

# 2. every cited function/symbol must appear in source (catches invented names)
src_text = ' '.join(p.read_text() for p in ROOT.rglob('*')
                    if p.suffix in ('.py', '.js', '.jsx', '.ts', '.sql') and 'node_modules' not in str(p))
for s in sorted(set(re.findall(r'`(fn_[a-z_]+|[a-z]+_[a-z_]{4,})`', md))):
    if s not in src_text:
        fails.append(f'MISSING SYMBOL: {s}')

# 3. cited migration files exist
for name in sorted(set(re.findall(r'`(\d{4}[a-z]?_[a-z0-9_]+\.sql)`', md))):
    if not list(ROOT.glob(f'**/migrations/{name[:-4]}*')):
        fails.append(f'MISSING MIGRATION: {name}')

# 4. secret / stale-claim scan of the generated artifact
h = ARTIFACT.read_text() if ARTIFACT.exists() else ''
for pat in [r'sk_[A-Za-z0-9]{8,}', r'whsk_', r'password123', r'SUPABASE_SERVICE_ROLE_KEY\s*=\s*["\']']:
    if re.search(pat, h):
        fails.append(f'SECRET/STALE PATTERN IN ARTIFACT: {pat}')

# 5. internal markdown links resolve
for f in (ROOT / 'docs').glob('*.md'):
    for m in re.finditer(r'\[[^\]]+\]\(([^)]+)\)', f.read_text()):
        u = m.group(1)
        if u.startswith(('http', '#', 'mailto')): continue
        if not os.path.exists(os.path.normpath(os.path.join(f.parent, u.split('#')[0]))):
            fails.append(f'BROKEN LINK: {f.name} -> {u}')

if fails:
    print('\n'.join(fails)); sys.exit(1)
print('ALL REFERENCES VERIFIED')
