#!/usr/bin/env python3
"""Parse supabase/migrations/*.sql into tables/columns/CHECKs/FKs/RPCs/policies.

Usage: python parse_migrations.py [migrations_dir]   (default: supabase/migrations)
Prints one block per migration: TABLE cols, CNST lines, ALTER adds, FN signatures, POLICIES.
Pitfall: no backslashes inside f-string expressions (py<3.12) — use the S() helper.
"""
import os, re, sys

S = lambda s: re.sub(r"\s+", " ", s)

def strip_comments(sql):
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.S)
    return re.sub(r"--.*", "", sql)

def main(mig_dir):
    for fn in sorted(os.listdir(mig_dir)):
        if not fn.endswith(".sql"):
            continue
        clean = strip_comments(open(os.path.join(mig_dir, fn), encoding="utf-8", errors="replace").read())
        print("\n### %s" % fn)
        for m in re.finditer(
            r"create\s+table(?:\s+if\s+not\s+exists)?\s+(?:public\.)?(\w+)\s*\((.*?)\)\s*;",
            clean, re.S | re.I,
        ):
            tbl, body = m.group(1), m.group(2)
            parts, depth, cur = [], 0, ""
            for ch in body:  # split top-level commas (skip parens: CHECK/FK clauses)
                depth += (ch == "(") - (ch == ")")
                if ch == "," and depth == 0:
                    parts.append(cur); cur = ""
                else:
                    cur += ch
            parts.append(cur)
            cols, cnsts = [], []
            for p in parts:
                p = p.strip()
                pm = re.match(r"^(\w+)\s", p)
                if pm:
                    cols.append(pm.group(1))
                if re.match(r"^(constraint|check|unique|primary\s+key|foreign\s+key)", p, re.I):
                    cnsts.append(S(p)[:160])
            print("TABLE %s: %s" % (tbl, cols))
            for c in cnsts:
                print("  CNST: %s" % c)
        for m in re.finditer(
            r"alter\s+table(?:\s+if\s+exists)?\s+(?:public\.)?(\w+)\s+add\s+column(?:\s+if\s+not\s+exists)?\s+(\w+)\s+([^;]+?)(?:,|\s*;)",
            clean, re.S | re.I,
        ):
            print("  ALTER %s ADD %s %s" % (m.group(1), m.group(2), S(m.group(3))[:80]))
        for m in re.finditer(
            r"create\s+(?:or\s+replace\s+)?function\s+(?:public\.)?(\w+)\s*\(([^)]*)\)",
            clean, re.S | re.I,
        ):
            print("  FN %s(%s)" % (m.group(1), S(m.group(2))))
        for m in re.finditer(
            r'create\s+policy\s+(\w+)\s+on\s+(?:public\.)?(\w+)\s+for\s+(\w+)\s+to\s+(\w+)\s+using\s*\((.*?)\)(?:\s+with\s+check\s*\((.*?)\))?\s*;',
            clean, re.S | re.I,
        ):
            print("  POLICY %s ON %s FOR %s TO %s USING %s WC=%s" % (
                m.group(1), m.group(2), m.group(3), m.group(4),
                S(m.group(5))[:80], S(m.group(6))[:60] if m.group(6) else "-",
            ))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "supabase/migrations")
