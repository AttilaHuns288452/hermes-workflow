# Periwinkle Pass 2026-08 — freelance-rate-calculator

Follow-up to `premium-calculator-overhaul.md`. No calculator math touched; pure premium reskin from generic blue `#2563eb` → periwinkle `#5e6ad2`.

## Why

User brief: "make it as leest fele premium" — "least feel premium" / most premium feel. Previous overhaul used `blue-600` everywhere = generic. Periwinkle `#5e6ad2` is the user's pinned accent (memory: `#2563eb retired`). Editorial + glass > flat blue.

## What shipped (commit `0a7f31b`, build 18/18)

- `app/globals.css` — `@theme` primaries `50:#eef2ff 100:#e0e7ff 500:#5e6ad2 600:#4f46e5 700:#4338ca`, `--background:#f8f9ff --foreground:#0f1229`, `::selection` periwinkle, `glass-nav` (78% white + blur16 saturate), `.card` `rgba(15,18,41,0.06)` + `rounded-[20px]` + inset, `.premium-input:focus` ring `14%`, slider thumb `20px #5e6ad2` + `hover scale 1.12`, grain `0.035`.
- `app/layout.tsx` — `themeColor #5e6ad2`, `bg-[#f8f9ff]`, `glass-nav h-[60px] max-w-6xl`, FC badge `w-8 h-8 rounded-xl bg-[#5e6ad2] shadow`, nav links `rounded-full hover:bg-[#eef2ff] text-[#5e6ad2]`, hidden `Try it →` pill `bg-[#0f1229]`.
- `app/page.tsx` — hero `bg-[#0f1229]` 3 blobs periwinkle/90px + grid `36px 0.06` + grain `0.04` + vignette, headline editorial 56px `tracking -0.03em` gradient `a5b4fc→white→c7d2fe`, peek card `rotate 1.5deg` 360px lg only, guides `rounded-[20px] border-[#eef2ff] hover:border-[#c7d2fe] shadow 12/32`, timeline connector `#c7d2fe→#e0e7ff` dot `#a5b4fc -28px`, dark `#0f1229→#1a1d3d` why-card `rounded-[28px]`, FAQ `rounded-[20px]` chevron periwinkle, CTA `from-[#5e6ad2] to-[#3730a3] rounded-[28px]`.
- `components/RateCalculator.tsx` — `sliderFill #5e6ad2→#818cf8 / #eef2ff`, borders `#eef2ff`, inputs `bg-[#f8f9ff]/60`, pills periwinkle.
- `components/ResultCard.tsx` — hero `from-[#5e6ad2] via-[#4f46e5] to-[#3730a3]`, bar `to-[#4338ca]`, right card `from-[#eef2ff] to-[#e0e7ff] border-[#c7d2fe]`.

## Windows git-bash mass-replace trick

`sed -i 's/...'` fails on git-bash (unknown option to s). Use `node -e` splits instead:

```js
const fs=require('fs');
let t=fs.readFileSync('components/RateCalculator.tsx','utf8');
[['text-blue-600','text-[#5e6ad2]'],['bg-blue-600','bg-[#5e6ad2]']].forEach(([a,b])=>t=t.split(a).join(b));
fs.writeFileSync('components/RateCalculator.tsx',t);
```

Check stragglers with `grep -n "blue-" components/*.tsx` — last two were `hover:bg-blue-100` and `from-blue-50`.

## Verification

```
✓ next build — 18/18, TypeScript clean, sitemap generated
✓ dev server PORT=3100 → curl 200
✓ commit 0a7f31b → push origin/master → Vercel auto-deploy
```

Skipped: new deps, chart lib, framer-motion, font swap. Add when motion spec demands.
