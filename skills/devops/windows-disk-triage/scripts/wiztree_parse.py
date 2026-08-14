#!/usr/bin/env python3
"""Parse a WizTree CSV export: top-level dir sizes, biggest files, recent big files.

Usage:
  python wiztree_parse.py <wiztree.csv> [YYYYMMDD]

Second arg = only list files >=100MB modified on/after that date (default: 7 days ago).
WizTree export is ~880MB / 5M rows for a full 476GB drive; this takes ~60s.
"""
import csv, collections, re, sys
from datetime import date, timedelta

GB = 2**30
BS = chr(92)  # backslash

csv_path = sys.argv[1] if len(sys.argv) > 1 else "wiztree.csv"
since = sys.argv[2] if len(sys.argv) > 2 else (date.today() - timedelta(days=7)).strftime("%Y%m%d")

dirs = collections.Counter()   # top-level dir -> bytes
files = []                     # (bytes, mtime_ymd, path)
recent = []

with open(csv_path, encoding="utf-8-sig", errors="replace") as f:
    for row in csv.reader(f):
        if len(row) < 7 or row[0] == "File Name":
            continue            # skips banner + header rows
        try:
            size = int(row[1])
        except ValueError:
            continue
        name = row[0].strip('"')
        mtime = row[3][:10].replace(" ", "") if len(row) > 3 else ""  # 'YYYY MM DD' -> 'YYYYMMDD'
        if name.endswith(BS):   # directory row (NOT attr flags — those vary)
            m = re.match(r"^[A-Za-z]:" + re.escape(BS) + r"([^" + re.escape(BS) + r"]+)" + re.escape(BS) + r"?$", name)
            if m and not m.group(1).startswith("$"):
                dirs[m.group(1)] += size
        else:
            files.append((size, mtime, name))
            if size > 100 * 2**20 and mtime >= since:
                recent.append((size, mtime, name))

print("=== TOP-LEVEL DIRS ===")
for k, v in dirs.most_common(20):
    print("%9.2f GB  %s" % (v / GB, k))
print("\n=== BIGGEST 45 FILES ===")
for size, mtime, name in sorted(files, reverse=True)[:45]:
    print("%9.2f GB  %s  %s" % (size / GB, name, mtime))
print("\n=== FILES >100MB MODIFIED SINCE %s ===" % since)
for size, mtime, name in sorted(recent, reverse=True)[:40]:
    print("%9.2f GB  %s  %s" % (size / GB, name, mtime))
print("\nsum(all files) = %.1f GB" % (sum(s for s, _, _ in files) / GB))
