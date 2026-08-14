#!/usr/bin/env python3
"""Parse a WizTree CSV export (see windows-disk-cleanup SKILL.md for how to produce it).

Usage:
  python parse_wiztree_csv.py [export.csv] [YYYYMMDD]

Prints: top-level dir sizes, biggest files, files >100MB modified since YYYYMMDD (optional),
and a junk-pattern report.
"""
import csv
import collections
import re
import sys

GB = 2**30
BS = chr(92)
p = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\YOUR_USERNAME\AppData\Local\Temp\wiztree.csv"
since = sys.argv[2] if len(sys.argv) > 2 else ""  # YYYYMMDD

junk_pats = [(re.compile(x, re.I), lbl) for x, lbl in [
    (r'(Cache|Code Cache|GPUCache|CachedData|CacheStorage)$', 'browser/app cache'),
    (r'(CrashDumps|Minidump)(\\)?$|(^|[\\])WER([\\]|$)', 'crash dumps'),
    (r'DeliveryOptimization', 'delivery optimization'),
    (r'^C:' + re.escape(BS) + r'temp' + re.escape(BS), r'C:\temp'),
    (r'Config\.Msi|\$WinREAgent|\$WINDOWS\.~BT', 'upgrade leftovers'),
    (r'^C:' + re.escape(BS) + r'\$Recycle', 'recycle bin'),
    (r'Prefetch', 'prefetch'),
    (r'\.cache|huggingface|codex-runtimes', 'user caches'),
    (r'DXCache|GLCache|ShaderCache', 'shader caches'),
]]

dirs = collections.Counter()
files = []
recent = []
junk = collections.Counter()

with open(p, encoding='utf-8-sig', errors='replace') as f:
    for row in csv.reader(f):
        if len(row) < 7 or row[0] == 'File Name':
            continue
        try:
            size = int(row[1])
            attr = int(row[5])
        except ValueError:
            continue
        name = row[0].strip('"')
        if name.endswith(BS):  # directory row
            m = re.match(r'^[A-Za-z]:' + re.escape(BS) + r'([^' + re.escape(BS) + r']+)' + re.escape(BS) + r'?$', name)
            if m and not m.group(1).startswith('$'):
                dirs[m.group(1)] += size
            for pat, lbl in junk_pats:
                if pat.search(name):
                    junk[lbl] += size
                    break
        else:
            files.append((size, name))
            if since and size > 100 * 2**20 and len(row) > 3:
                d = row[3].replace(' ', '')[:8]
                if d >= since:
                    recent.append((size, name))

print("=== TOP-LEVEL DIRS ===")
for k, v in dirs.most_common(20):
    print("%9.2f GB  %s" % (v / GB, k))
print("\n=== BIGGEST 30 FILES ===")
for s, n in sorted(files, reverse=True)[:30]:
    print("%9.2f GB  %s" % (s / GB, n))
if recent:
    print("\n=== FILES >100MB SINCE %s ===" % since)
    for s, n in sorted(recent, reverse=True)[:30]:
        print("%9.2f GB  %s" % (s / GB, n))
print("\n=== JUNK PATTERNS (dirs only) ===")
for lbl, v in junk.most_common():
    print("%9.2f GB  %s" % (v / GB, lbl))
