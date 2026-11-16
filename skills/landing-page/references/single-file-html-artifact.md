# Single-file HTML artifact: build and verify

A one-file landing page / hero / product page with no build step and no network
dependencies. Everything below is the order that avoids rework.

## 1. Design tokens first, in `:root`

Declare ink, paper, one accent, a serif/sans pair, a max width, and one easing
curve before any component rule. Every later value references a token. This is what
makes a later polish pass a one-line change instead of a hunt.

## 2. Structure the page in the standard landing order

Hero → spec strip → argument sections → proof → FAQ → closing CTA. Keep section
IDs on the elements the nav links to; every `section[id]` needs
`scroll-margin-top` at least the sticky nav height (see pitfall 1).

## 3. Draw the product instead of sourcing a photo

An inline `<svg>` with `<defs>` gradients reads as a premium product render at
zero asset cost and never 404s. Follow the physical anatomy of the object — a
wristwatch has the buckle on the 6 o'clock strap and the adjustment holes on the
12 o'clock strap; getting that inverted is the first thing a reviewer notices.

## 4. Verify, do not assume

Run these probes after the markup is written, then again after every fix. Each one
caught a real defect that the others missed.

```js
// hero actually painted (not held at opacity 0 by an entrance animation)
getComputedStyle(document.querySelector('.hero-visual')).opacity

// no horizontal overflow at mobile width
({ vw: innerWidth, scrollW: document.documentElement.scrollWidth })

// sticky nav does not cover an anchor target
(() => { const h = document.querySelector('#faq h2').getBoundingClientRect();
         const n = document.querySelector('.nav').getBoundingClientRect();
         return { clears: h.top >= n.bottom, gap: h.top - n.bottom }; })()

// tap targets >= 44px on every nav/footer link and button
[...document.querySelectorAll('.nav a, footer a, .btn')]
  .filter(a => { const r = a.getBoundingClientRect(); return r.height && r.height < 44; })
  .map(a => a.textContent.trim())

// reduced motion leaves nothing hidden
({ hidden: [...document.querySelectorAll('.reveal')]
    .filter(e => getComputedStyle(e).opacity === '0').length })
```

Then vision-check the render at desktop AND 390px. Distrust vision on "the [product]
is missing" until the opacity + viewport probe above has run.

## Pitfalls

1. **Sticky nav swallows every anchor jump.** One rule fixes all of them:
   `section[id], main[id] { scroll-margin-top: 84px }` (nav height + breathing
   room). Verify with the nav-vs-heading probe above, not by eye.

2. **SVG-adjacent work is where visual defects hide.** Two that render as
   "invisible" or "broken" rather than as errors:
   - A `linearGradient` applied as a **stroke** to a perfectly vertical or
     horizontal line paints nothing: the object bounding box has zero width, so
     the gradient has no box to map into. Use a solid colour, or wrap the shape in
     a rotated `<g>` and keep the gradient on a `fill`.
   - Malformed path data (`h34c8 0 14 6 14 14v-52…`) renders a notch or step that
     looks like a rendering bug. Keep product geometry to simple `M/h/v/z`
     rectangles and arcs, and re-read the path if an edge looks chipped.

3. **Entrance animations hide content from screenshots.** Elements start at
   `opacity: 0` and are released on intersection. A full-page capture right after
   load shows empty bands; release the reveals before capturing.

4. **Nav and footer links are the smallest tap targets on the page.** Body-level
   links inherit a ~20px line box; wrap them in `display: inline-flex; align-items:
   center; min-height: 44px` so a mobile audit passes.

5. **One external URL is still an external dependency.** A `data:` URI favicon is
   fine (the `xmlns` string inside it is not a request). A `<link rel="stylesheet"
   href="https://…">` or a Google Font import defeats the point of a single-file
   artifact — check with `grep -c 'https\?://'` and confirm every hit is inside a
   `data:` URI or a comment.

6. **Validate the tag tree before declaring done.** Python's `HTMLParser` with a
   void-element set (`meta, link, br, hr, img, input, source, path, circle, rect,
   line`) catches unclosed and mismatched tags in one pass and needs no dependency.

## Delivery

One `.html` file, no siblings required. Copy it to both the project directory and
`~/Downloads`, and hand the user a rendered preview image rather than a path alone.
