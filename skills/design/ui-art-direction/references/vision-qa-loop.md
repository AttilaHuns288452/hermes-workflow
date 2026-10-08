# Vision QA loop with ground-truth arbitration

How to run screenshot → vision critique → fix → re-verify on UI work without chasing vision-model hallucinations.

## Capture

- Headless chromium via node one-liner (Playwright at `/home/attila/.hermes/hermes-agent/node_modules/playwright`, `NODE_PATH` set). Desktop at the user's judging width (1920×1080 — density/type judged there; 1440×900 acceptable) + mobile 390×844; after any type-scale change spot-check the narrow (320/390) and wide (1366/1920) ends. Full-page PNGs to a workspace dir.
- Localhost dev servers: fine from terminal/node; `browser_exec` blocks localhost as a "private address" — don't route screenshot work through it.
- **Settle rule**: wait 600-1200ms after load (or for entrance animations to finish) before `screenshot()`. Mid-entrance content is faded/offset and vision calls it invisible/missing.
- When saving grayscale analysis copies, keep the RGB original as the delivered file (a `.convert('L')` copy that overwrites the original reads as "no color").
- After any fix that changes page height, re-crop analysis strips from the fresh full-page shot — a stale crop boundary shifts content out of frame and reads as a missing section / false FAIL.

## Critique

- Full-critique prompts get a brutal-editor frame: enumerate named items (sections/rows/columns), each verdict states the problem concretely plus the exact fix and severity; explicitly forbid whole-code rewrites ("do NOT rewrite the code; list concrete fixes").
- For spot checks, ask targeted questions (3-5 named items), not "does this look good". Request yes/no + one line per item.
- Defect-only variant for polish/modernization passes (enhancement suggestions are noise): "list only concrete, objectively verifiable visual problems; do not suggest enhancements or redesigns; one line per problem: [element] — [problem]".
- Send rounds until the verdict is literally "ship/shippable" at BOTH breakpoints; "close" or "minor nits" means another round. Fix by impact (blockers first), then re-review.
- Vision verdicts by reliability:
  - **Usually trust, one cheap probe first**: text truncation/clipping, missing/duplicated copy, layout gaps, hierarchy, alignment, spacing rhythm. These carry false-alarm classes of their own (below); a single grep/DOM probe settles each before any edit.
  - **Verify before acting**: any color/contrast/"blends in"/"invisible" claim.
- False-alarm classes recurring even on "trusted" claim types — check before fixing:
  - **Glyph misreads at downscale**: a symbol reads as a different character to the model (a proportional "≈" reads as "="). Grep the actual string in source/DOM; the typo must exist before it is a bug.
  - **Lazy images in full-page shots**: below-the-fold `loading="lazy"` images never enter the viewport during a full-page capture, so they render as gray placeholders in the PNG while the live page loads them fine. "Missing images" from a full-page shot are usually this.
  - **Crop boundaries**: a strip cut mid-section reads as "content cut off" or a cramped edge. Check the un-cropped full-page shot before believing an edge verdict.
  - **Scroll boundaries**: an element partially hidden at a scroll container's bottom edge in a full-page shot reads as "clipped" or "covered by the composer". Scroll the container to its end and re-measure the element rect before treating it as overflow.
  - **Probing the wrong convention**: a negative claim ("nav has no active state") is only as good as the probe's assumed styling convention. Read how the element is actually styled (its class pattern / framework primitive like NavLink isActive) before concluding absence.
  - **Misalignment is measurable**: compare `getBoundingClientRect()` tops of the suspect rows; identical tops = claim wrong (auto-layout like `mt-auto` holds alignment the eye misses at downscale).
- **Taste coin-flip rule**: if vision flags the same block in opposite directions across rounds ("center the heading", then "heading sits low" after centering), the model is expressing taste, not reporting a bug. Decide once by the page's own convention (what sibling sections do) and move on; do not churn the loop.

## Arbitration (the step that saves the session)

For every color/contrast/visibility claim, probe ground truth before editing design:

```js
// computed color of a suspect surface
getComputedStyle(el).backgroundColor
// is the element actually rendered where vision says?
JSON.stringify(el.getBoundingClientRect())
// truncation check on VISIBLE nodes only
[...document.querySelectorAll('*')].filter(n => n.offsetWidth > 0 && n.innerText.includes('TEXT'))
```

- If computed styles/pixels contradict the vision verdict, REJECT the critique, keep the design, and state the numbers in the report.
- If numbers confirm it, fix and re-verify with the same probe (numbers again), not just a re-look.
- For truncation: find every node containing the string, filter `offsetWidth > 0`, measure `scrollWidth > clientWidth` on the visible one. A zero-width match = hidden duplicate; a fix there is a no-op for the user.

## Closing the loop

- Re-shoot settled screenshots after fixes; run project QA gates; one final targeted vision check on the fixed items only.
- Deliver proof: gate counts (e.g. panel-qa 51/51, route-crawl 40/40), final screenshot path (also copied to `~/Downloads/`), and which vision claims were confirmed vs rejected. The loop converges when the reviewer's verdict is "ship" on both desktop and mobile.
