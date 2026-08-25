"""Aggregate OpenCode token usage by calendar month from the local DB.

Usage:
    python usage_by_month.py            # monthly table (sessions, input/output/reasoning/cache tokens, cost)
    python usage_by_month.py 2026-08    # per-model breakdown for one month
"""
import sqlite3
import sys
import datetime
from collections import defaultdict

DB = r"C:\Users\Attila\.local\share\opencode\opencode.db"
WANT = sys.argv[1] if len(sys.argv) > 1 else None


def ym(t_epoch_ms):
    return datetime.datetime.fromtimestamp(t_epoch_ms / 1000).strftime("%Y-%m")


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        """SELECT time_created, tokens_input, tokens_output, tokens_reasoning,
                  tokens_cache_read, tokens_cache_write, cost, model
           FROM session"""
    ).fetchall()

    months = defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0])   # sess, in, out, reason, cr, cw, cost(int, ->float)
    models = defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0])
    for t, i, o, r, cr, cw, c, m in rows:
        i, o, r, cr, cw, c = i or 0, o or 0, r or 0, cr or 0, cw or 0, c or 0
        if not (i or o or r):                              # skip empty/aborted sessions
            continue
        k = ym(t)
        if WANT and k != WANT:
            continue
        target = models if WANT else months
        key = (m or "?") if WANT else k
        a = target[key]
        a[0] += 1; a[1] += i; a[2] += o; a[3] += r; a[4] += cr; a[5] += cw; a[6] += c

    def show(items, keyw):
        print(f"{keyw:9} {'Sess':>5} {'Input':>10} {'Output':>9} {'Reason':>9} {'CacheRd':>11} {'CacheWr':>8} {'Cost':>7}")
        for key in sorted(items):
            s, i, o, r, cr, cw, c = items[key]
            print(f"{key:9} {s:5d} {i:10,d} {o:9,d} {r:9,d} {cr:11,d} {cw:8,d} {c:7.2f}")
        t = [sum(items[k][j] for k in items) for j in range(7)]
        print(f"{'TOTAL':9} {t[0]:5d} {t[1]:10,d} {t[2]:9,d} {t[3]:9,d} {t[4]:11,d} {t[5]:8,d} {t[6]:7.2f}")

    show(models if WANT else months, "Model" if WANT else "Month")


if __name__ == "__main__":
    main()