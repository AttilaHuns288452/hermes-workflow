# HyperFrames lint internals (verified against hyperframes@0.8.1)

Found by sourcing the installed CLI bundle on Windows (git-bash). The npm
cache hashed dir differs per machine — discover it, don't hardcode:

```
ls ~/AppData/Local/npm-cache/_npx/*/node_modules/hyperframes/dist/cli.js
```

`dist/cli.js` is one big bundled file (~10 MB). Grep for rule codes
(`"code: \"rule_name\""`) or font internals (`FONT_ALIAS_MAP2`,
`extractUsedFontFamilies`, `collectAliasedFonts`) and read the enclosing
function. Docs/contract rule codes drift between versions — several codes in
the frame-worker contract (`clip_missing_data_attrs`, `timeline_not_paused`,
`timeline_not_registered`, `css_transition_used`,
`exit_animation_on_non_final_scene`) do NOT exist verbatim in 0.8.1.

## Font rule mechanics

- `extractUsedFontFamilies(styles)` lowercases family names, strips quotes and
  `!important`, drops generic families (`sans-serif` etc.) — so
  `font-family: "Inter"` becomes the key `inter`.
- `font_family_without_font_face` (error) fires for used families that are
  NOT in: declared `@font-face` families, `FONT_ALIAS_KEYS2` (keys of
  `FONT_ALIAS_MAP2`), or Google-Fonts-imported families. Inter and the other
  bundled families are in the alias set → bare `Inter` lints clean with no
  @font-face. The fixHint explicitly allows `src: local('Exact Font Name')`
  for OS-bundled system fonts — a declaration alone satisfies the check.
- `FONT_ALIAS_MAP2` canonical bundled families (keys, lowercased):
  inter, montserrat, outfit, nunito, oswald, league gothic, archivo black,
  space mono, ibm plex mono, jetbrains mono, eb garamond, playfair display,
  source code pro, noto sans jp, roboto, open sans, lato, poppins, plus
  aliases mapping system faces onto them (`cambria`/`times`/`times new
  roman` → eb-garamond; `segoe ui` → inter).
- `system_font_will_alias` (info/warning, not error) fires when a used family
  maps to a different bundled family — a heads-up, not a gate.
- `google_fonts_import` (warning) fires for `<link>`/`@import` to
  fonts.googleapis.com — prefer the bare bundled family name instead.

## Track rule mechanics

- `overlapping_clips_same_track`: clips sharing a `data-track-index` must not
  overlap in time; boundary-touch counts as overlap. Full-duration visible
  layers that never leave the frame each need their own track index
  (e.g. bg=0, kicker=1, tiers=2, cta=3, glow=4, wordmark=5, tagline=6,
  dim-overlay=10). Assigning the same track to several always-on layers fails
  even when GSAP staggers their visual appearances.

## Lint CLI behavior

- `npx hyperframes lint` exits 0 even with errors — read the `✗` / `⚠` lines.
- It lints `compositions/frames/*.html` even before they are wired into the
  assembled `index.html` (contrary to the worker contract's claim that lint
  only covers the assembled project).
- Lint findings in OTHER files (`index.html` missing staged assets, sibling
  frames) are pre-existing — leave them; fix only your own frame file.