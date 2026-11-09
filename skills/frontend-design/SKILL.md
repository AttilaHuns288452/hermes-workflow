---
name: frontend-design
description: Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Helps with aesthetic direction, typography, and making choices that don't read as templated defaults.
license: Complete terms in LICENSE.txt
---

# Frontend Design

Approach this as the design lead at a design studio known for giving every client a distinct visual identity that is not mistaken for anyone else's. This client has already rejected proposals that felt cliché or templated, and is paying for a distinctive point of view: make deliberate, opinionated choices about palette, typography, and layout that are specific to this brief, and take aesthetic risk if justified.

## Ground your designs in the subject matter

If the brief does not identify what the product or subject matter is, identify it yourself before designing, and confirm with the client. You can come up with one concrete subject, the design's audience, and the design's primary job, as a proposal. If there's any information in your memory about the client's preferences or context about what they're building, use that as a hint. The subject's industry, subject matter, materials, and vernacular are where distinctive visual choices come from — a design for a toy for girls aged 8–11 will be very aesthetically different from a dashboard for financial analysts. Build with the brief's real content and subject matter throughout.

## Design principles

For web designs, the hero is the first thing viewers will see. Open with the most characteristic thing in the subject's world, in the form that is most appropriate: a headline, an image, an animation, a live demo, an interactive moment, or other treatments. Be deliberate with your choice: a big number with a small label, supporting stats, and a gradient accent is the default treatment, so only use it if that's truly the best option.

Typography carries the personality of the page. You don't need a different typeface for display or headline text and body content: use one family or two, and if two, make them clearly distinct.

Choose your typefaces deliberately, not the default families you would reach for on any other project, and set a clear type scale following the default guidance of The Elements of Typographic Style with intentional weights, widths, and spacing. When type is used as a headline or visual element, use the type treatment itself as an active part of the design, not a neutral delivery vehicle for the content.

Default to line lengths of less than 80 characters. Serif typefaces can have slightly longer line lengths; give serif body text slightly more line-height than a sans-serif.

Avoid these default typographic treatments; they are the commonest tells of a generated page:
- Accenting just a single word or phrase in a headline, like putting one word in italic/bold or a different color.
- Using all caps for labels.
- Adding unnecessary typographic labels above content.

Visual structure is information. Structural devices like outlines, borders, numbering, eyebrows, dividers, labels, etc., encode useful information about the content rather than decorate it. Many generic designs use numbered markers (01 / 02 / 03), but that's only appropriate if the content actually is a sequence — like a stepped process or a timeline. Before adding numbered markers, check the content really is a sequence.

Use non-user-triggered motion sparingly and deliberately, only to draw attention. A single orchestrated moment — one page-load sequence or one reveal — lands better than scattered effects; fade-and-slide-up entrances on each section and hover transitions on every card are the generic default and read as AI-generated. Motion that answers a person's action (opening, expanding, confirming) is welcome when it shows what changed.

Consider written content carefully. Often a design brief may not contain real content, and it's up to you to come up with copy and placeholder content. Copy can make a design feel as templated as the design itself. See the below section on writing for more guidance.

## Process: plan, review against the brief, build, critique

For calibration, AI-generated design right now clusters around some traits:
1. a warm cream background (near #F4F1EA) with a high-contrast serif display and a terracotta or warm-clay accent (often near #D97757 — Anthropic's own Claude-interaction accent, so on a user's brief it reads as a tell);
2. a near-black background with a single bright acid-green or vermilion accent;
3. a broadsheet-style layout with hairline rules, zero border-radius, and dense newspaper-like columns;
4. the SaaS-card kit: content chopped into identical rounded cards, one border-radius on everything regardless of hierarchy, the same soft grey shadow (rgba(0,0,0,.1)) under each, and gradient washes as decoration;
5. template chrome that appears whatever the subject: a tracked-out ALL-CAPS eyebrow label above every heading; meta strings joined with middle dots ('A · B · C'); labels built as 'WORD — fragment' with a spaced em dash; tinted near-black (#0B0B0B, #111) standing in for black; a monospace face for small data labels; a '→' appended to link and button text.

All traits are legitimate for some briefs, but they are defaults rather than choices, and they appear regardless of subject. Where the brief pins down a visual direction, follow it exactly — the brief's own words always win, including when it asks for one of these looks. Where it leaves an axis free, don't spend that freedom on one of these defaults. As with a hired human designer, there's often a careful balance between doing what you're good at and taking each project as a chance to experiment and learn.

Work in two passes. First, brainstorm a short design plan based on the client's design brief: create a compact token system with color, type, layout, and principles.
- Color: describe the core base palette as 4–6 named hex values.
- Type: the typefaces and their roles.
- Layout: a layout concept, using one-sentence prose descriptions and ASCII wireframes to ideate and compare. Include alignment guidance; should the content be left aligned, center aligned, justified?
- Principles: the high-level guidance for what makes this page unique.

Then review that plan against the brief before building: if any part of it reads like the generic default you would produce for any similar page (work through a similar prompt to see if you arrive somewhere similar) rather than a choice made for this specific brief — revise that part, say what you changed and why. Only after you've confirmed the relative uniqueness of your design plan should you start to write the code, following the revised plan.

Once the page is built, run a final pass with the `ux-psychology` skill whenever the page has a job to do beyond looking good (landing, pricing, onboarding, checkout, dashboard): it names the 3-5 behavioral principles at play, the concrete markup/copy changes for them, and the dark patterns to avoid.

When writing the code, be careful of structuring your CSS selector specificities. It's easy to generate CSS classes that cancel each other out (especially with a type-based selector like .section and an element-based selector like .cta). This can happen often with padding/margin between sections.

## Restructuring existing UI without breaking small viewports

When a polish pass wraps existing blocks in new layout containers, check the narrowest supported viewport (320px) after every structural change — container regressions are invisible at desktop widths and only surface as horizontal page overflow on phones.

- A CSS grid with no explicit `grid-cols-*` gets one implicit `auto` column that sizes to the MAX-CONTENT of its children — and a horizontal-scroller child (overflow-x-auto carousel, flex row of `flex-none` chips) reports its full scroll-track width as that max-content, stretching the column past the viewport. Always set explicit columns (`grid-cols-1`, `md:grid-cols-2`, …); `grid-cols-1` is `minmax(0,1fr)`, which lets children shrink and scroll as designed.
- Rows of `flex-none` fixed-width controls (day toggles, button groups) stop fitting below their summed width. Give them `flex-1 min-w-0` at base with the fixed size in an `md:` variant, or make the row `grid grid-cols-N`.
- Measure mechanically: `document.documentElement.scrollWidth - clientWidth` at the target width is the check. When it trips, walk `getBoundingClientRect()` for elements exceeding the viewport, then clone suspect subtrees into a `width:min-content` probe to find the forcing node — the widest visible element is usually a victim stretched by its parent, not the cause.
- A `flex` TRACK must not clip its own children: `overflow-hidden` on the moving strip hides every item past the first, because the track's clip box is its own width and translated items can never re-enter it. The fixed WRAPPER is the only legal clip in a slider/carousel/marquee.
- `grid-auto-rows: 1fr` equalizes every row to the tallest row's CONTENT — one wrapped multi-line chip inflates a uniform tile grid into portrait tiles (measured 48×113 on "square" day cells). Clamp the row's content (line-clamp, one compact chip + "+N") or use fixed row tracks; verify tile aspect by measuring `getBoundingClientRect()`, not by eye.
- When view/tab switches conditionally render blocks into a shared flex row, controls physically move between views (a legend rendered before the tablist in one mode and after the heading in another shifts the whole toolbar). Keep every control in a FIXED slot across all views and swap only the CONTENT of one slot (e.g. one legend container whose entries vary per view); verify by measuring the control's rect in every view — identical coordinates, or the user reads it as "things move to different places when I flip".
- A spanning grid item written `grid-row: 1 / -1` (or any `-1` end) resolves `-1` only against the EXPLICIT track list. On a grid whose rows are implicit, the span collapses to one row and that item's full height inflates the single row, leaving a large void beside/below the neighbors (a sticky side rail pinned this way can push the main column down by hundreds of px). Use `grid-row: 1 / span N` when rows are implicit, or define explicit rows. The tell is a big y-gap between two siblings that should stack tightly — measure the first two children's `getBoundingClientRect().y`, don't read the stylesheet.
- Runtime-injected DOM furniture (a side rail, a detail panel, a wrapper class added in `init`) must survive minimal test stubs as well as the real DOM: stub elements lack `querySelectorAll`, `style.setProperty`, and a default `input.value`, and one throw on a cosmetic call fails a test that has nothing to do with your change. Guard those calls with `typeof` checks or wrap the furniture block in `try/catch` so decoration can never take the render down.

When improved copy would break a test suite that matches accessible names, bridge with `aria-label` on the control (visible copy stays new, accessible name keeps the contract) instead of reverting the copy or editing the suite to match. Change the suite's expectation only when the accessible name itself needed to change.

## Form-spawn convention (standing user preference)

Every "add" / "+" / create action opens a modal dialog — never inject a form block into the page (inline form spawns were rejected as "feels weird", twice). Audit every create/add flow for this during a rebuild or polish pass — an inline spawn that already shipped is still a violation. Use ONE dialog language app-wide (scrim, rounded card, title, ✕ close, Escape, click-outside) and wrap each form's EXISTING markup in it rather than rewriting the form: field ids/labels/placeholders are QA contract strings. Make the trigger button's label static — the modal owns dismissal (a label that toggles to "Close" is state noise and breaks substring locators). Portal the dialog to `document.body` when the app's fixed chrome would paint above a plain `fixed` scrim. Small chip-adders (one input + add button inside an already-modal form) stay inline; the rule targets form SPAWNS.

## Polishing an existing product to a "premium" bar

When the user calls a surface "boring", "plain", "awkward" or asks to "give flavor / make it aesthetic", they want a designed treatment at the level of the app's best surface — not merely a fixed defect. Work comparison-first: screenshot the surface they praise and the one they criticize at the same viewport, extract the good surface's language (label style, icon treatment, card anatomy, density, spacing scale), and bring the laggard up to it before inventing anything new. Presentability levers that read as premium without breaking an established system: textured/toned header bands on cards, icon chips instead of bare icons, content grouping that fills dead space with real data, compact stat cards with strong numbers, and consistent action-button styling across sibling sections.

Hierarchy discipline on a rebuilt page: the page's own title must be the largest type on screen — a supporting/source block that outranks it inverts the page identity (users read the page as the wrong kind of page). Compress provenance/context blocks into strips, not heroes. And one filled primary action per viewport: when two or three filled CTAs compete (global chrome aside), demote the secondary ones to ghost/tertiary even when they are major features — a report opener or export is secondary to the page's actual task. Card rows share a baseline: reserve two title lines (`min-height` on the title) so one wrapped heading never pushes its description out of alignment with its siblings.

When the user asks to REMOVE something ("remove this button", "replace that section") they also want (1) a one-line reason for the removal and (2) a replacement from the same domain scope — never leave a hole where the element was. Ask "what real information lives in this system that belongs here?" and build the replacement from that data (a care-history list instead of a payment queue on a clinical dashboard); the reason and the replacement are part of the deliverable, not optional commentary.

## Restraint and self-critique

Spend your boldness in one place. Let one element be the memorable thing, keep everything around it quiet and disciplined, and cut any decoration that does not serve the brief. Build to a quality floor without announcing it: responsive down to mobile, visible keyboard focus, reduced motion respected, visually accessible, harmonious color palettes. Critique your own work as you build, taking screenshots to review if your environment supports it — a picture is worth 1000 tokens. Consider Chanel's advice: before leaving the house, take a look in the mirror and remove one accessory. Human creatives have memory and always try to do something new, so if you have a space to quickly jot down notes about what you've tried, it can help you in future passes.

## More on writing in design

Words appear in a design for one reason: to make it easier to understand and use. They are design content, not decoration. Bring the same intentionality and minimalism to copywriting that you would bring to spacing and color. Before writing anything, ask what the design needs to say, and how it can best be said to help the person navigate the experience.

Write from the end user's perspective. Name things by what users will understand in simple language, not by how the system is built. A user manages notifications, not webhook config. Describe what something is or does in plain terms rather than selling it. Being specific and legible to new users is always better than being clever.

Use active voice as default. A CTA says exactly what happens when it is used: "Save changes," not "Submit." An action keeps the same name through the whole flow, so the button that says "Publish" produces a toast that says "Published." The vocabulary of an interface is the signposting for someone navigating the product. Cohesion and consistency are how people learn their way around.

Treat failure and emptiness as moments for direction, not mood. Explain what went wrong and how to fix it, in the interface's voice rather than a person's. Errors don't apologize, and they are never vague about what happened. An empty screen is an invitation to act.

Keep the tone conversational: plain verbs, sentence case, no filler, with tone matched to the brand and the audience. Let each written element do exactly one job.
