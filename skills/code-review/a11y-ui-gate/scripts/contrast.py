#!/usr/bin/env python3
"""WCAG contrast checker for UI token palettes.

Usage:
  python contrast.py                  # print the standard token-pair table below
  python contrast.py #5e6ad2 #ffffff  # ratio for one pair (fg bg), PASS/FAIL vs 4.5

Also simulates Tailwind `color-mix(in oklch, <fg> <pct>%, transparent)` soft
tokens (accent-soft etc.) composited over their base background, so you can
check text-on-soft-token contrast that is otherwise invisible in source code.
"""
import sys

def lum(hexc):
    c = hexc.lstrip('#')
    rgb = [int(c[i:i+2], 16) / 255 for i in (0, 2, 4)]
    lin = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

def ratio(fg, bg):
    l1, l2 = lum(fg), lum(bg)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)

def blend(fg, pct, bg):
    """Approximate color-mix(fg pct%, transparent) over bg in sRGB space."""
    f = [int(fg[i:i+2], 16) for i in (1, 3, 5)]
    b = [int(bg[i:i+2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(f[i] * pct + b[i] * (1 - pct)) for i in range(3))

def report(name, fg, bg):
    r = ratio(fg, bg)
    print(f"{name:<58}{r:>7.2f}  {'PASS' if r >= 4.5 else 'FAIL (<4.5)'}")

if __name__ == '__main__':
    if len(sys.argv) == 3:
        fg, bg = sys.argv[1], sys.argv[2]
        r = ratio(fg, bg)
        print(f"{fg} on {bg}: {r:.2f}:1 — {'PASS' if r >= 4.5 else 'FAIL'} (4.5 normal / 3.0 large)")
        sys.exit(0)

    # Edit this table to match the palette under review, then run.
    pairs = [
        ('accent #5e6ad2 on white',                 '#5e6ad2', '#ffffff'),
        ('accent #5e6ad2 on page bg #f8f9fb',       '#5e6ad2', '#f8f9fb'),
        ('muted-fg #575e6c on white',               '#575e6c', '#ffffff'),
        ('muted-fg #575e6c on page bg #f8f9fb',     '#575e6c', '#f8f9fb'),
        ('muted-fg #8a8f98 on card #121315 (dark)', '#8a8f98', '#121315'),
        ('muted-fg #8a8f98 on bg #0a0b0c (dark)',   '#8a8f98', '#0a0b0c'),
        ('accent #5e6ad2 on bg #0a0b0c (dark)',     '#5e6ad2', '#0a0b0c'),
        ('accent #5e6ad2 on card #121315 (dark)',   '#5e6ad2', '#121315'),
        ('white on accent #5e6ad2 (badge)',         '#ffffff', '#5e6ad2'),
    ]
    for name, fg, bg in pairs:
        report(name, fg, bg)

    print('\n-- text on color-mix soft tokens (simulated) --')
    for label, base, pct in [('accent-soft 10% over white', '#ffffff', 0.10),
                             ('accent-soft 14% over #121315', '#121315', 0.14)]:
        soft = blend('#5e6ad2', pct, base)
        report(f'accent text on {label} -> {soft}', '#5e6ad2', soft)
