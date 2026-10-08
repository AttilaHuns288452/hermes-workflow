# Montage / sizzle re-edit recipe

For re-cutting a long demo film into a 45–60s product montage. Entry rules live in SKILL.md "Short montage variant"; this file is the build recipe and brief checklist.

## Build recipe

1. **Curate from the existing build's asset library.** Re-exec the original generator's templates (up to its build marker) instead of rebuilding assets; keep prior delivered files read-only. Pick the strongest 2–4 moments per role plus 8–12 flash-worthy screens — selection beats quantity.
2. **Beat grid = 0.5s at 120 BPM.** All scene starts land on grid; derive shot durations first, then fit the music (loops per section length) to the cut list — cuts are the master, music the follower. Downbeats at section starts.
3. **Screen presentation:** full-bleed tinted backdrop + one centered phone screen per shot (looser than a walkthrough's board layout); `object-fit:cover; object-position:top` on tall source screens; highlight rects per shot in visible-box % (see SKILL.md cover-fraction mapping).
4. **Label overlay per shot:** kicker (section) + name (2–4 words) at a fixed frame corner, plus the role pill opposite. Short label animations (0.25s), mounted OUTSIDE the camera wrapper.
5. **Motion vocabulary (see SKILL.md):** entries only — each phone slides in opaque from a rotating side (right → left → bottom → top down the cut list), captions slide in with overshoot, role titles whip in skewed from the left, dividers ken-burns. No exit tweens at cuts (boundary blink), no fade-only stretches.
6. **Section dividers:** centered role name (kicker) + scope line (the duality statement for a dual-role section). Divider itself sits on the beat grid.
7. **Close card:** brand name + one-line positioning, hold ~2s, tween stage to black (fade-to-black on the last beat). A multi-phone reveal (each phone slides in from its own direction, assembling) is the approved close for role-based montages. If the product has a one-liner, it is the close card's hero line, paired with the brand card at open — the promise/payoff bookend.
8. **Audio:** calm bed at the chosen BPM, whooshes on section cuts only; nothing louder than −1.5 dBFS peak; no narration track at all.

## Brief checklist (the panelist's test)

| Check | Pass condition |
|---|---|
| Runtime | 45–60s, ffprobe-verified |
| Pacing | shots 1.0–2.5s, every cut on a beat, no filler movement |
| Role clarity | roles appear in product-usage order, pill + divider label each |
| Dual-role representation | both sub-roles staged in-role (clinical + management), label names the duality |
| Feature density | final flash covers the headline features at ~1s each |
| Polish | boundary-blink scan clean at every cut (0 background-only frames), labels legible + non-overlapping (vision), fade-to-black close |
| Motion | no two consecutive shots animate alike, entry directions rotate, captions/titles move — no fade-only stretch (checked numerically, not just by eye) |
| Identity | vision-verified screen at every role-critical shot (right navbar variant) |
