# Animated SVG Flowchart Patterns

## When to Use

Building a documentation/landing page for a system pipeline, decision flow, or architecture diagram that needs to look premium and animated without loading any JS library (GSAP, D3, etc.).

## Two Row Layout (e.g., /decide Flow)

860×320 viewport. 2 rows × 4 columns with dashed connector paths between nodes, a vertical connector linking the rows, and staggered fade-in per node group.

**Layout math:** 10px left margin → 120px node → 55px gap → 155px node → 55px gap → 155px node → 55px gap → 155px node (rest right padding). Y: row1=55, row2=155, height=70 per node.

**Delay timing:** `animation:fadeNode .5s {DELAY}s forwards` — row1: 0.2, 0.4, 0.6, 0.8; row2: 1.0, 1.2, 1.4, 1.6; arrows: 0.6 (vertical) and 1.0 (horizontal).

**Vertical connector** from center of row1 to center of row2: `d="M430 125 L430 155"`.

## Multi-Column Layout (e.g., Pipeline Flow)

860×530 viewport. 3 columns × up to 5 rows with node groups horizontally and vertically connected.

**Columns:** col1=275px wide at x=15, col2=275px wide at x=300, col3=275px wide at x=585.

**Rows:** row1 y=10, row2 y=74, row3 y=138, row4 y=202, row5 y=266. Node height=44px. Vertical gap=20px.

**Arrows:** horizontal (`M275 32 L300 32`), vertical (`M145 54 L145 74`). Arrowhead triangles at layer boundaries.

**Delay timing:** col1 rows 0.1, 0.3, 0.5, 0.7; col2 rows 0.9, 1.1, 1.3, 1.5; col3 1.7; final badge 1.9.

## Gradients

Define in `<defs>`. Four standard gradient IDs used across diagrams:

```html
<linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">  <!-- Blue: standard steps -->
  <stop offset="0" stop-color="#4a8cf4"/><stop offset="1" stop-color="#7c5cf5"/>
</linearGradient>
<linearGradient id="g2" x1="0" y1="0" x2="0" y2="1">  <!-- Red: guardrail -->
  <stop offset="0" stop-color="#e4686a"/><stop offset="1" stop-color="#d088b8"/>
</linearGradient>
<linearGradient id="g3" x1="0" y1="0" x2="0" y2="1">  <!-- Green: optimization -->
  <stop offset="0" stop-color="#3ddc84"/><stop offset="1" stop-color="#4dc9b8"/>
</linearGradient>
<linearGradient id="p1" x1="0" y1="0" x2="1" y2="0">  <!-- Horizontal blue -->
  <stop offset="0" stop-color="#4a8cf4"/><stop offset="1" stop-color="#7c5cf5"/>
</linearGradient>
```

For gold/highlight nodes: use `fill="#f0d060"` directly (no gradient needed).

## Node Template (Single)

```html
<g class="node" style="opacity:0;animation:fadeNode .5s {DELAY}s forwards">
  <rect x="{X}" y="{Y}" width="{W}" height="{H}" rx="8"
        fill="url(#g1)" fill-opacity=".1" stroke="#4a8cf4" stroke-opacity=".25"/>
  <rect x="{X}" y="{Y}" width="{H}" height="{H}" rx="8" fill="url(#g1)"/>
  <text x="{X+H/2}" y="{Y+H/2+2}" text-anchor="middle" fill="white"
        font-size="13" font-weight="700">{STEP_NUM}</text>
  <text class="label" x="{X+H+15}" y="{Y+H/2-2}" font-size="12">{TITLE}</text>
  <text class="sublabel" x="{X+H+15}" y="{Y+H/2+10}" font-size="7.5">{SUBTITLE}</text>
</g>
```

For icon steps (shield, star, etc.), replace `{STEP_NUM}` with a grapheme and set `font-size="10"`.

## Completion Badge

A green pill at the end of the flow, typically the last node to fade in:

```html
<g style="opacity:0;animation:fadeNode .4s 1.9s forwards">
  <rect x="585" y="74" width="260" height="44" rx="22"
        fill="url(#g3)" fill-opacity=".12" stroke="#3ddc84" stroke-opacity=".3"/>
  <text class="label" x="715" y="100" text-anchor="middle"
        fill="#3ddc84" font-size="13" font-weight="700">✅ Pipeline Complete</text>
</g>
```

## CSS (required for all diagrams)

```css
.svg-diagram{width:100%;max-width:860px;margin:1.5rem auto;display:block;overflow:visible}
.svg-diagram .node rect,.svg-diagram .node .bg{transition:all .3s}
.svg-diagram .node:hover rect,.svg-diagram .node:hover .bg{filter:brightness(1.3)}
.svg-diagram .node .label{font-family:var(--font);font-size:11px;font-weight:600;fill:var(--text);pointer-events:none}
.svg-diagram .node .sublabel{font-family:var(--font);font-size:8px;fill:var(--text3);pointer-events:none}
.svg-diagram .conn{fill:none;stroke-width:1.5;stroke-linecap:round}
.svg-arrow{fill:var(--border-light);opacity:.5}
@keyframes fadeNode{to{opacity:1}}
```
