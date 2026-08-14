#!/usr/bin/env python3
"""Parse a WizTree CSV export: top-level dir sizes, biggest files, recent big files.
Usage: python wizparse.py <wiztree.csv> [min_date=YYYYMMDD]   (min_date filters ">100MB modified since")
"""
import csv, collections, re, sys

GB = 2**30
BS = chr(92)  # backslash
path = sys.argv[1]
since = sys.argv[2] if len(sys.argv) > 2 else '20260101'

dirs = collections.Counter()
files = []
recent = []
with open(path, encoding='utf-8-sig', errors='replace') as f:
    for row in csv.reader(f):
        if len(row) < 7 or row[0] == 'File Name':  # banner + header
            continue
        try:
            size = int(row[1])
        except ValueError:
            continue
        name = row[0].strip('"')
        mtime = row[3] if len(row) > 3 else ''
        if name.endswith(BS):  # directory row (attr column is unreliable)
            m = re.match(r'^[A-Za-z]:' + re.escape(BS) + r'([^' + re.escape(BS) + r']+)' + re.escape(BS) + r'?$', name)
            if m:
                dirs[m.group(1)] += size
        else:
            files.append((size, mtime, name))
            if size > 100 * 2**20 and mtime.replace(' ', '')[:8] >= since:
                recent.append((size, mtime, name))

print("=== TOP-LEVEL DIRS ===")
for k, v in dirs.most_common(20):
    print("%9.2f GB  %s" % (v / GB, k))
print("\n=== BIGGEST 45 FILES ===")
for size, mtime, name in sorted(files, reverse=True)[:45]:
    print("%9.2f GB  %s  %s" % (size / GB, name, mtime[:10]))
print("\n=== FILES >100MB MODIFIED SINCE %s ===" % since)
for size, mtime, name in sorted(recent, reverse=True)[:40]:
    print("%9.2f GB  %s  %s" % (size / GB, name, mtime[:10]))
print("\nsum(all files) = %.1f GB" % (sum(s for s, _, _ in files) / GB))
