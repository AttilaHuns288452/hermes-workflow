---
name: redesign-existing-projects
description: Upgrades existing websites and apps to premium quality. Audits current design, identifies generic AI patterns, and applies high-end design standards without breaking functionality. Works with any CSS framework or vanilla CSS.
---

# Redesign Skill

## Scope: what "improve" means to this user

"Improve", "improv", "polish", "make everything better", "fix those" on an existing project means a SIGNIFICANT, VISIBLE upgrade pass, not an audit plus small tweaks. Deliver: real bugs fixed at the root, awkward layouts restructured (column rebalances, density fixes at wide viewports, overflow repairs), motion/hover/responsive polish, everything verified (QA suites + visual re-check), and shipped (commit, push, deploy) without being asked twice. The user judges with his eyes: a passing check is not the finish line, so loop the visual pass until the page holds up.

Still out of scope unless asked: invented features, new pages/sections, new content or copy he did not request, new dependencies. "Significant" is depth of polish and layout surgery on what exists, not new capabilities. An explicit restriction ("only fix X", "do not touch anything else") is authoritative over this default.

Two recurring over-build failures to avoid: (1) speculative CTA buttons — a control exists only when the app's real flow has an action there; "remove that button, don't put buttons" is the reaction to invented affordances. (2) invented process machinery — approval queues, review states, leave-request workflows layered onto systems that have no such step. When a section's label names a workflow the app does not perform, rename it to a state that is real (e.g. "Awaiting payment" for unpaid bookings) or remove it; do not design process the domain does not have.

## How This Works

When applied to an existing project, follow this sequence:

1. **Scan** — Read the codebase. Identify the framework, styling method (Tailwind, vanilla CSS, styled-components, etc.), and current design patterns.
2. **Diagnose** — Run through the audit below. List every generic pattern, weak point, and missing state you find. Cross-check against the Scope Constraint — if an audit item recommends adding something new, skip it unless the user explicitly requested it.
3. **Fix** — Apply targeted upgrades working with the existing stack. Do not rewrite from scratch. Improve what's there. Changes should be visible and deliberate: hierarchy, spacing, and motion improvements the user will notice on sight, while the project's established design language (palette, type scale, motion vocabulary) stays intact.

## Palette retheme from a reference design

When the task is "match this deck/mock's palette" across a whole site (light-mode flip, brand recolor), the remap is one atomic pass, not page-by-page tweaking:

1. **Extract the target palette first** — from the reference's stated tokens, or by pixel-sampling the reference image (vision hex estimates run ±10 off). Lock the old→new mapping (each old hue gets exactly one target) before touching files.
2. **Inventory before editing** — grep every hex literal, named CSS color, inline SVG `fill`/`stroke`, favicon/logo files, and any design doc listing tokens. Embedded app-screen mockups (phone frames, dashboard SVGs) carry their OWN palette inside the page; they need a separate light/dark flip decision, not just the global swap.
3. **Apply the map in one pass**, then grep every old value again — zero leftovers is the exit criterion. Update the project's design doc (DESIGN.md, token comments) in the same commit; docs still describing the old palette mean the job is half done.
4. **Verify colors with computed styles + pixel scans, not vision hues** (see visual-pass step 3).
5. **Ship and live-verify with a cache-bust query** — static hosts serve stale builds for minutes after push, and a stale page false-fails the color audit.

## The visual pass loop

For a UI/UX improvement sweep, run this per page (or per page group when fanned out):

1. **Shoot** the page's key states at the widths the user judges at: 390x844 mobile, 1440x900 desktop, plus 1920x1080 when wide-layout density matters. Cover every persona the page serves (session usually lives in localStorage; reach logged-out views through the app's own Log out flow, because demo apps re-inject a session on reload).
2. **Vision-critique** each shot: "what would a senior designer call awkward, templated, sparse, misaligned, or broken here? Rank by impact."
3. **Confirm every claim against source or DOM geometry before editing** — for color claims specifically, a computed-style read plus a pixel scan of the region (vision misattributes hues on small/desaturated text and imports photo colors as UI colors) — then fix the top items.
4. **Re-shoot to confirm** the fix landed. Iterate a page at most twice, then move on.
5. After each batch: repo QA suites + build + the fit matrix. Ship only on green.

For sweeps across many pages, fan out page groups to subagents with disjoint file ownership (see the `subagent-playbook` skill), verify claimed edits via git diff before reporting success — interrupted children leave half-edits — and exclude in-flight workers' files from commits (`git add -A -- ':!path'`). Batch-parse every worker-edited file with esbuild/before the full build: interrupted mid-edit artifacts present as mismatched opener/closer tag types (opened `<header>`, closed `</div>`), unclosed JSX comment delimiters, and wrappers opened but never closed. When a parse error's line matches no visible diff, suspect an invisible character inside a comment block and bisect at byte level rather than line-hunting.

Pitfalls:
- Full-page screenshots stitch fixed overlays (bottom nav bars, floating action buttons, dev/demo pills) into the middle of the image. Vision reports them as "content guillotined", "nav overlapping content", "FAB colliding with the CTA". They are capture artifacts, not defects: verify against getBoundingClientRect or a viewport-height shot before patching anything they name.
- Vision misreads small SVG line icons as "broken image placeholder glyphs" and estimates hairline progress bars inconsistently (the same bar read as 35%, 50%, 65% across three calls). Check the source — aria-valuenow, the width expression — before "fixing" data displays.
- When a critique's premise contradicts the app's real state ("this logged-out page shows a personalized dashboard"), trust the critique and re-check the capture: the probe probably never reached the state it claims to show.
- When every fresh browser (and every engine, and the production build) renders correctly but the user's screenshot still shows the defect, the user's own tab is the last untested variable: dev-server restarts silently kill HMR, leaving their tab on stale half-migrated modules. Serve the production build on the same dev port and ask for one hard reload before debugging the code again — measure the user's own screenshot pixels when deciding which side is true.
- Horizontal overflow a suite reports is diagnosed with `references/mobile-overflow-debugging.md`, not by staring at screenshots.
- **A drag on a transform/translate carousel must `setPointerCapture`.** A `pointerup` handler bound to the strip never fires when the release lands outside it (exactly how people drag), so the offset strands and the slides sit permanently out of view — which reads to the user as "content not rendering". Capture the pointer on down; where the surface can strand, also add a timer that re-clamps the offset.
- **After the same user-reported defect survives two fixes, stop theorizing and go to evidence:** measure raw pixels of the user's own screenshot (no vision model), reproduce in their exact browser and viewport, and if the surface still cannot be made reliable, ship a can't-fail fallback render (plain stacked cards) plus a one-line telemetry dump of the runtime numbers. A third theory about a repro you cannot produce is how one surface eats a whole session.
- **Never freeze essential motion with the blanket reduced-motion kill.** `* { animation: none !important }` is a shorthand — it also forces `animation-duration: 0s !important` over inline styles — and fingerprinting-protection browsers (Brave) report `prefers-reduced-motion` regardless of the OS setting, so the freeze hits users who never asked for it. Keep reduced-motion a polish enhancement (instant swap), and when an animation must survive, route its duration through a custom property and set longhand `animation-duration: var(--dur) !important`.
- A `padding: A 0 B` shorthand in a component class (`.cols`, `.fine`) silently resets the layout class's horizontal gutters when both classes sit on one element. The bug is invisible on desktop where `max-width` centering still insets content; it only appears at viewports below the container's max-width. Verify gutters at a narrow viewport, and prefer longhand `padding-block`/`padding-inline` when layering a component class over a layout class.
- Fixed-width device mockups (phone frames, small cards) overflow a few pixels invisibly: a label + value flex row wider than the mock pushes the trailing value past the right edge, which vision reports only as "misaligned values". Compare each row child's rect edges against the mock's content box; widen the mock a notch and set `flex: none` on the value instead of shrinking type.
- Per-row accent borders (`border-l-*`) die under `divide-*` list utilities: the `> * + *` selectors carry (0,3,0) specificity and set the full `border-color`, crushing the left accent. Give rows explicit bottom borders instead of divide utilities whenever rows style their own border sides.

## Design Audit

### Typography

Check for these problems and fix them:

- **Browser default fonts or Inter everywhere.** Replace with a font that has character. Good options: `Geist`, `Outfit`, `Cabinet Grotesk`, `Satoshi`. For editorial/creative projects, pair a serif header with a sans-serif body.
- **Headlines lack presence.** Increase size for display text, tighten letter-spacing, reduce line-height. Headlines should feel heavy and intentional.
- **Body text too wide.** Limit paragraph width to roughly 65 characters. Increase line-height for readability.
- **Only Regular (400) and Bold (700) weights used.** Introduce Medium (500) and SemiBold (600) for more subtle hierarchy.
- **Numbers in proportional font.** Use a monospace font or enable tabular figures (`font-variant-numeric: tabular-nums`) for data-heavy interfaces.
- **Missing letter-spacing adjustments.** Use negative tracking for large headers, positive tracking for small caps or labels.
- **All-caps subheaders everywhere.** Try lowercase italics, sentence case, or small-caps instead.
- **Orphaned words.** Single words sitting alone on the last line. Fix with `text-wrap: balance` or `text-wrap: pretty`.

### Color and Surfaces

- **Pure `#000000` background.** Replace with off-black, dark charcoal, or tinted dark (`#0a0a0a`, `#121212`, or a dark navy).
- **Oversaturated accent colors.** Keep saturation below 80%. Desaturate accents so they blend with neutrals instead of screaming.
- **More than one accent color.** Pick one. Remove the rest. Consistency beats variety.
- **Mixing warm and cool grays.** Stick to one gray family. Tint all grays with a consistent hue (warm or cool, not both).
- **Purple/blue "AI gradient" aesthetic.** This is the most common AI design fingerprint. Replace with neutral bases and a single, considered accent.
- **Generic `box-shadow`.** Tint shadows to match the background hue. Use colored shadows (e.g., dark blue shadow on a blue background) instead of pure black at low opacity.
- **Flat design with zero texture.** Add subtle noise, grain, or micro-patterns to backgrounds. Pure flat vectors feel sterile.
- **Perfectly even gradients.** Break the uniformity with radial gradients, noise overlays, or mesh gradients instead of standard linear 45-degree fades.
- **Inconsistent lighting direction.** Audit all shadows to ensure they suggest a single, consistent light source.
- **Random dark sections in a light mode page (or vice versa).** A single dark-background section breaking an otherwise light page looks like a copy-paste accident. Either commit to a full dark mode or keep a consistent background tone throughout. If contrast is needed, use a slightly darker shade of the same palette — not a sudden jump to `#111` in the middle of a cream page.
- **Empty, flat sections with no visual depth.** Sections that are just text on a plain background feel unfinished. Add high-quality background imagery (blurred, overlaid, or masked), subtle patterns, or ambient gradients. Use reliable placeholder sources like `https://picsum.photos/seed/{name}/1920/1080` when real assets are not available. Experiment with background images behind hero sections, feature blocks, or CTAs — even a subtle full-width photo at low opacity adds presence.

### Layout

- **Everything centered and symmetrical.** Break symmetry with offset margins, mixed aspect ratios, or left-aligned headers over centered content.
- **Three equal card columns as feature row.** This is the most generic AI layout. Replace with a 2-column zig-zag, asymmetric grid, horizontal scroll, or masonry layout.
- **Using `height: 100vh` for full-screen sections.** Replace with `min-height: 100dvh` to prevent layout jumping on mobile browsers (iOS Safari viewport bug).
- **Complex flexbox percentage math.** Replace with CSS Grid for reliable multi-column structures.
- **Bare `grid` or `flex` wrapper with no explicit base columns.** An implicit `auto` track sizes to max-content of its content — including `overflow-x-auto` scrollers (carousels, chip rows) nested inside — and overflows narrow viewports. Always give `grid grid-cols-1` at base with `md:`/`xl:` column variants.
- **No max-width container.** Add a container constraint (around 1200-1440px) with auto margins so content doesn't stretch edge-to-edge on wide screens.
- **Cards of equal height forced by flexbox.** Allow variable heights or use masonry when content varies in length.
- **Uniform border-radius on everything.** Vary the radius: tighter on inner elements, softer on containers.
- **No overlap or depth.** Elements sit flat next to each other. Use negative margins to create layering and visual depth.
- **Symmetrical vertical padding.** Top and bottom padding are always identical. Adjust optically — bottom padding often needs to be slightly larger.
- **Dashboard always has a left sidebar.** Try top navigation, a floating command menu, or a collapsible panel instead.
- **Missing whitespace.** Double the spacing. Let the design breathe. Dense layouts work for data dashboards, not for marketing pages.
- **Buttons not bottom-aligned in card groups.** When cards have different content lengths, CTAs end up at random heights. Pin buttons to the bottom of each card so they form a clean horizontal line regardless of content above.
- **Feature lists starting at different vertical positions.** In pricing tables or comparison cards, the list of features should start at the same Y position across all columns. Use consistent spacing above the list or fixed-height title/price blocks.
- **Inconsistent vertical rhythm in side-by-side elements.** When placing cards, columns, or panels next to each other, align shared elements (titles, descriptions, prices, buttons) across all items. Misaligned baselines make the layout look broken.
- **Mathematical alignment that looks optically wrong.** Centering by the math doesn't always look centered to the eye. Icons next to text, play buttons in circles, or text in buttons often need 1-2px optical adjustments to feel right.
- **`auto-rows-fr` / equal-row stretching in dense grids (calendars, tile boards).** Every row becomes as tall as its tallest cell, so one multi-line wrapped chip turns square tiles into tall portraits across the whole grid. Clamp cell chips to 1–2 lines on mobile (compact time-only chip + a '+N' overflow instead of stacking full chips), and judge cell shape from `getBoundingClientRect` — the screenshot misreads tile aspect ratios.

### Interactivity and States

- **No hover states on buttons.** Add background shift, slight scale, or translate on hover.
- **No active/pressed feedback.** Add a subtle `scale(0.98)` or `translateY(1px)` on press to simulate a physical click.
- **Instant transitions with zero duration.** Add smooth transitions (200-300ms) to all interactive elements.
- **Missing focus ring.** Ensure visible focus indicators for keyboard navigation. This is an accessibility requirement, not optional.
- **No loading states.** Replace generic circular spinners with skeleton loaders that match the layout shape.
- **No empty states.** An empty dashboard showing nothing is a missed opportunity. Design a composed "getting started" view.
- **No error states.** Add clear, inline error messages for forms. Do not use `window.alert()`.
- **Dead links.** Buttons that link to `#`. Either link to real destinations or visually disable them.
- **No indication of current page in navigation.** Style the active nav link differently so users know where they are.
- **Scroll jumping.** Anchor clicks jump instantly. Add `scroll-behavior: smooth`.
- **Animations using `top`, `left`, `width`, `height`.** Switch to `transform` and `opacity` for GPU-accelerated, smooth animation.

### Content

- **Generic names like "John Doe" or "Jane Smith".** Use diverse, realistic-sounding names.
- **Fake round numbers like `99.99%`, `50%`, `$100.00`.** Use organic, messy non-contact data: `47.2%`, `$99.00`, `18 of 43`.
- **Placeholder company names like "Acme Corp", "Nexus", "SmartFlow".** Invent contextual, believable brand names.
- **AI copywriting cliches.** Never use "Elevate", "Seamless", "Unleash", "Next-Gen", "Game-changer", "Delve", "Tapestry", or "In the world of...". Write plain, specific language.
- **Exclamation marks in success messages.** Remove them. Be confident, not loud.
- **"Oops!" error messages.** Be direct: "Connection failed. Please try again."
- **Passive voice.** Use active voice: "We couldn't save your changes" instead of "Mistakes were made."
- **All blog post dates identical.** Randomize dates to appear real.
- **Seed/demo copy containing relative words on fixed timestamps.** Copy that says "tomorrow" or "next week" must derive its timestamp relative to now; a fixed date stamp goes incoherent within days and the fixture reads broken.
- **Same avatar image for multiple users.** Use unique assets for every distinct person.
- **Lorem Ipsum.** Never use placeholder latin text. Write real draft copy.
- **Title Case On Every Header.** Use sentence case instead.

### Component Patterns

- **Generic card look (border + shadow + white background).** Remove the border, or use only background color, or use only spacing. Cards should exist only when elevation communicates hierarchy.
- **Always one filled button + one ghost button.** Add text links or tertiary styles to reduce visual noise.
- **Pill-shaped "New" and "Beta" badges.** Try square badges, flags, or plain text labels.
- **Accordion FAQ sections.** Use a side-by-side list, searchable help, or inline progressive disclosure.
- **3-card carousel testimonials with dots.** Replace with a masonry wall, embedded social posts, or a single rotating quote.
- **Pricing table with 3 towers.** Highlight the recommended tier with color and emphasis, not just extra height.
- **Popups for single-field actions.** Reserve modal dialogs for multi-field create/edit forms (this user's preferred pattern — see Rules); keep simple actions (toggle, rename chip, reorder) inline. Slide-over panels or expandable sections suit detail views.
- **Destructive confirmation dialogs with the emphasis backwards.** The retain/keep action takes the solid primary button; the destructive action is the restrained one (outline or red text). A filled-red destructive button makes the destroy path the visually loudest choice.
- **Entry-form category chips with a different vocabulary than the display layer.** If the manual-entry chips say "Pasta (Restoration)" while the chart/filter labels say "Tooth Filling", manual entries mis-bucket invisibly. One taxonomy, identical strings, across entry forms and display.
- **Three row grammars for one pattern.** A list page that invents a different row layout per section reads mediocre even when each row is clean. Pick one row template (leading avatar/icon chip + stacked primary/secondary text + trailing action cluster, 44px targets, quiet tertiary styling for destructive actions — not solid red buttons) and apply it to every list on the page.
- **Avatar circles exclusively.** Try squircles or rounded squares for a less generic look.
- **Light/dark toggle always a sun/moon switch.** Use a dropdown, system preference detection, or integrate it into settings.
- **Footer link farm with 4 columns.** Simplify. Focus on main navigational paths and legally required links.

### Iconography

- **Lucide or Feather icons exclusively.** These are the "default" AI icon choice. Use Phosphor, Heroicons, or a custom set for differentiation.
- **Rocketship for "Launch", shield for "Security".** Replace cliche metaphors with less obvious icons (bolt, fingerprint, spark, vault).
- **Inconsistent stroke widths across icons.** Audit all icons and standardize to one stroke weight.
- **Missing favicon.** Always include a branded favicon.
- **Stock "diverse team" photos.** Use real team photos, candid shots, or a consistent illustration style instead of uncanny stock imagery.

### Code Quality

- **Div soup.** Use semantic HTML: `<nav>`, `<main>`, `<article>`, `<aside>`, `<section>`.
- **Inline styles mixed with CSS classes.** Move all styling to the project's styling system.
- **Hardcoded pixel widths.** Use relative units (`%`, `rem`, `em`, `max-width`) for flexible layouts.
- **Missing alt text on images.** Describe image content for screen readers. Never leave `alt=""` or `alt="image"` on meaningful images.
- **Arbitrary z-index values like `9999`.** Establish a clean z-index scale in the theme/variables.
- **Commented-out dead code.** Remove all debug artifacts before shipping.
- **Import hallucinations.** Check that every import actually exists in `package.json` or the project dependencies.
- **Missing meta tags.** Add proper `<title>`, `description`, `og:image`, and social sharing meta tags.

### Strategic Omissions (What AI Typically Forgets)

- **No legal links.** Add privacy policy and terms of service links in the footer.
- **No "back" navigation.** Dead ends in user flows. Every page needs a way back.
- **No custom 404 page.** Design a helpful, branded "page not found" experience.
- **No form validation.** Add client-side validation for emails, required fields, and format checks.
- **No "skip to content" link.** Essential for keyboard users. Add a hidden skip-link.
- **No cookie consent.** If required by jurisdiction, add a compliant consent banner.

## Proportional Scale System (type + spacing)

When spacing or type complaints alternate between passes (content feels too narrow, then text feels too big, then margins feel too wide), stop value-tuning and rebuild the relationship as one system. Procedure:

1. **Measure the design source first.** Extract the artboard width and representative text sizes (body, hero heading, section heading) from the prototype/export. The artboard is the objective anchor that ends taste debates: at the judging width the rendered relationship should match the source's ratio of text size to artboard width, within judgment.
2. **Assign one knob per dimension.** Gutters and containers scale with viewport as a ratio of the source (e.g. gutter ≈ 3-4% of artboard width per breakpoint). Type follows ONE fixed scale at every width. Container width and type size change independently — never as one multiplier.
3. **Normalize off-scale values.** Grep the tree for arbitrary text-[Npx] / hardcoded px heading sizes sitting beside scale utilities and fold them into the shared scale; a stray 26px next to a 30px step reads as broken hierarchy even when each value looks fine alone.
4. **Sweep candidates as evidence.** Render 2-4 system candidates at the widths the user judges at, montage the named focus areas, vision-vote the montage, then confirm any named defect in DOM geometry before patching.
5. **Run the fit matrix before shipping**: horizontal-overflow check at 320 / 390 / 768 / 1280 / 1440 / 1920 (documentElement.scrollWidth vs innerWidth), plus zero-overflow confirmation on every named route.

Pitfalls:
- Never add a viewport multiplier to type tokens (media-query bump, a --tscale var) so text "fills" a wide grid — when container and type both grow with width, the oscillation restarts, because the next pass shrinks one to compensate for the other. Type stays on one fixed hierarchy; the grid scales.
- Do not fix oversized type by shrinking the gutter set. The chosen gutters are the layout constant; re-tuning both dimensions in one pass guarantees the next review blames whichever you moved.
- An alternating complaint across passes is a system defect, not a taste miss. Name the shared cause, change one system once, judge it at the target widths, deploy, and do not re-tune per follow-up comment unless the comment names a new defect.
- `1fr` grid tracks and flex rows containing `shrink-0` blocks (price, badge, CTA) set a min-content floor that overflows narrow viewports: use `minmax(0, 1fr)` tracks and let row items wrap or shrink together. The same floor comes from a bare `grid`/`flex` container with no explicit base `grid-cols-1`: its implicit `auto` track sizes to max-content of everything inside, including `overflow-x-auto` scrollers — those clip visually but still contribute their full content width to the track.
- Assemble candidate montages at one fixed panel size — upscaling wide-short sections distorts type weight and swings the vote. Screenshot crop edges read as "clipped text"; confirm overlap/gap with getBoundingClientRect before treating it as a real defect.

## Upgrade Techniques

When upgrading a project, pull from these high-impact techniques to replace generic patterns:

### Typography Upgrades
- **Variable font animation.** Interpolate weight or width on scroll or hover for text that feels alive.
- **Outlined-to-fill transitions.** Text starts as a stroke outline and fills with color on scroll entry or interaction.
- **Text mask reveals.** Large typography acting as a window to video or animated imagery behind it.

### Layout Upgrades
- **Broken grid / asymmetry.** Elements that deliberately ignore column structure — overlapping, bleeding off-screen, or offset with calculated randomness.
- **Whitespace maximization.** Aggressive use of negative space to force focus on a single element.
- **Parallax card stacks.** Sections that stick and physically stack over each other during scroll.
- **Split-screen scroll.** Two halves of the screen sliding in opposite directions.

### Motion Upgrades
- **Smooth scroll with inertia.** Decouple scrolling from browser defaults for a heavier, cinematic feel.
- **Staggered entry.** Elements cascade in with slight delays, combining Y-axis translation with opacity fade. Never mount everything at once.
- **Spring physics.** Replace linear easing with spring-based motion for a natural, weighty feel on all interactive elements.
- **Scroll-driven reveals.** Content entering through expanding masks, wipes, or draw-on SVG paths tied to scroll progress.

### Surface Upgrades
- **True glassmorphism.** Go beyond `backdrop-filter: blur`. Add a 1px inner border and a subtle inner shadow to simulate edge refraction.
- **Spotlight borders.** Card borders that illuminate dynamically under the cursor.
- **Grain and noise overlays.** A fixed, pointer-events-none overlay with subtle noise to break digital flatness.
- **Colored, tinted shadows.** Shadows that carry the hue of the background rather than using generic black.

## Fix Priority

Apply changes in this order for maximum visual impact with minimum risk:

1. **Font swap** — biggest instant improvement, lowest risk
2. **Color palette cleanup** — remove clashing or oversaturated colors
3. **Hover and active states** — makes the interface feel alive
4. **Layout and spacing** — proper grid, max-width, consistent padding
5. **Replace generic components** — swap cliche patterns for modern alternatives
6. **Add loading, empty, and error states** — makes it feel finished
7. **Polish typography scale and spacing** — the premium final touch

## Rules

- Work with the existing tech stack. Do not migrate frameworks or styling libraries.
- Do not break existing functionality. Test after every change.
- **QA suites asserting accessible names are the contract.** Polish with visual classes where possible; when better visible copy would break a name assertion, bridge with `aria-label` (visible "+ Add dentist", `aria-label="Add New Dentist"`) instead of editing the assertion. If a polish pass dropped a contract string ("Estimated:"), restore the string rather than weakening the check.
- Layout and overflow fixes follow `references/mobile-overflow-debugging.md`.
- Before importing any new library, check the project's dependency file first.
- If the project uses Tailwind, check the version (v3 vs v4) before modifying config.
- If the project has no framework, use vanilla CSS.
- Keep changes reviewable and focused. Small, targeted improvements over big rewrites.
- **Button-triggered create/edit forms open as modal dialogs**, matching the app's existing dialog pattern (scrim, centered card, × close, Escape-to-close). Inline form spawns that inject a form into the page flow feel broken to this user — and this covers EVERY create button ("+ Add …", "Add …"), even single-field creations like one-name category adds. "Inline" applies only to non-creation actions (toggle, rename chip, reorder), which never spawn forms.
- **Carousel surfaces:** autoplay means NO prev/next arrows (dots are the manual control); landing/announcement strips use a continuous marquee ticker, not a step carousel; step carousels advance fast (~3s), never slow (~10s+). Marquee tickers are draggable: pause motion on pointer interaction and resume after a short inactivity (~5s), with pointer capture so a release outside the strip can't strand the offset.
- **View switchers (month/week/day, grid/list) keep every toolbar element in one stable slot across views.** Legends, counts, or headings rendered in different slots per view make the controls jump when the user switches; pin the shared chrome (segmented control, date nav, legend) to one wrapper and let only the content area change. The switcher itself fills its column as equal segments on mobile and collapses to a compact inline pill on desktop.
- **Plan first for new visual direction; act on execution sweeps.** When introducing a new design direction or producing proposals the user will review, list the planned changes concisely and get approval before code. When the request is itself an execution order ("improve everything", "fix those", "continue", "push and deploy"), proceed autonomously and ship after verification — this user prefers action and decisiveness over approval loops, and treats a stalled small-tweak pass as a failure.
