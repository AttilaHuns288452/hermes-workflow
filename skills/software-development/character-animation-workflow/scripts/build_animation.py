#!/usr/bin/env python3
"""
Build a standalone character-animation HTML scene from a scene plan + SVG rig data.
This produces a self-contained HTML file with inline SVG + inline GSAP that can be
opened in a browser or captured via Playwright (see references/playwright-frame-capture.md).

Usage:
    uv run python scripts/build_animation.py \
        --rig projects/gta-finance-comparison/artifacts/rig_plan_alex.json \
        --poses projects/gta-finance-comparison/artifacts/pose_library_alex.json \
        --timeline projects/gta-finance-comparison/artifacts/action_timeline_sample.json \
        --output renders/animation_preview.html

Workflow:
    1. Load scene plan + rig + pose library + action timeline
    2. Generate standalone HTML with inline SVG character + GSAP animation
    3. Write to output path

The generated HTML includes:
    - Inline SVG character (from rig plan part definitions)
    - GSAP timeline playing all scene actions in sequence
    - Game-style HUD overlay (health bar, stat display, alert popups)
    - Optional background image support
"""

import json, sys, argparse, textwrap
from pathlib import Path

FPS = 12
W, H = 1280, 720


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_svg_parts(rig_plan: dict) -> str:
    """Generate inline SVG markup from a rig plan's character parts."""
    char = rig_plan.get("rig_plan", {}).get("characters", [{}])[0]
    parts = char.get("parts", [])
    svg_elems = []
    svg_elems.append(f'<ellipse class="shadow" cx="{W//2}" cy="560" rx="120" ry="22" fill="rgba(0,0,0,.18)"/>')

    for p in parts:
        pid = p["id"]
        kind = p.get("kind", "")
        parent = p.get("parent")
        layer = p.get("layer", 0)

        if kind == "torso":
            cx, cy = W // 2, 400
            svg_elems.append(
                f'<ellipse id="{pid}" class="part outline" cx="{cx}" cy="{cy}" rx="80" ry="120" fill="#ff8f68"/>'
            )
        elif kind == "head":
            cx, cy = W // 2, 230
            svg_elems.append(
                f'<circle id="{pid}" class="part outline" cx="{cx}" cy="{cy}" r="90" fill="#ffd39f"/>'
            )
        elif kind == "eye":
            side = "left" if "left" in pid else "right"
            cx = W // 2 + (-35 if side == "left" else 35)
            svg_elems.append(
                f'<ellipse id="{pid}" class="part outline eye" cx="{cx}" cy="215" rx="18" ry="26" fill="white"/>'
            )
        elif kind == "pupil":
            side = "left" if "left" in pid else "right"
            cx = W // 2 + (-31 if side == "left" else 39)
            svg_elems.append(
                f'<circle id="{pid}" class="part pupil" cx="{cx}" cy="218" r="8" fill="#202632"/>'
            )
        elif kind == "mouth":
            svg_elems.append(
                f'<path id="{pid}" class="part outline" d="M285 275 Q{W//2} 305 355 275" fill="none"/>'
            )
        elif kind == "limb":
            side = "left" if "left" in pid else "right"
            if side == "left":
                svg_elems.append(
                    f'<path id="{pid}" class="part outline" d="M255 360 C210 380 190 420 180 455" fill="none" stroke="#ff8f68" stroke-width="24" stroke-linecap="round"/>'
                )
            else:
                svg_elems.append(
                    f'<path id="{pid}" class="part outline" d="M385 360 C440 330 465 290 475 240" fill="none" stroke="#ff8f68" stroke-width="24" stroke-linecap="round"/>'
                )
    return "\n      ".join(svg_elems)


def build_gsap_timeline(actions: list, fps: int, char_count: int) -> str:
    """Build GSAP timeline calls from action timeline data."""
    # Generate basic timeline actions
    lines = []
    lines.append(f"const tl = gsap.timeline({{paused: false}});")

    for i, scene in enumerate(actions):
        sid = scene.get("scene_id", f"scene_{i}")
        for action in scene.get("actions", []):
            at = action.get("at_seconds", 0)
            dur = action.get("duration_seconds", 0.5)
            action_type = action.get("action", "perform")
            pose = action.get("pose", "idle")
            easing = action.get("easing", "power2.out")

            # Map action types to GSAP calls
            if action_type == "anticipate":
                lines.append(
                    f"tl.from('#character_alex', {{y:26, scale:0.94, opacity:0, "
                    f"duration:{dur}, ease:'{easing}'}}, {at});"
                )
            elif action_type == "perform" and pose == "look_right":
                lines.append(
                    f"tl.to('.pupil', {{x:6, duration:{dur/2}, ease:'{easing}'}}, {at});"
                )
                lines.append(
                    f"tl.to('#head', {{rotation:8, duration:{dur/2}, ease:'back.out(1.4)'}}, {at + dur/4});"
                )
            elif action_type == "settle":
                lines.append(
                    f"tl.to('.pupil', {{x:0, duration:{dur/2}, ease:'{easing}'}}, {at});"
                )
                lines.append(
                    f"tl.to('#head', {{rotation:0, duration:{dur/2}, ease:'{easing}'}}, {at});"
                )
            else:
                # Generic motion
                lines.append(
                    f"tl.to('#character_alex', {{y:-{8 + i*4}, duration:{dur}, "
                    f"ease:'back.out(1.4)'}}, {at});"
                )

        # Add blink in every scene
        blink_at = scene.get("start_seconds", 0) + 1.5
        lines.append(
            f"tl.to('.eye', {{scaleY:0.08, transformOrigin:'center', duration:0.08, "
            f"repeat:1, yoyo:true, ease:'none'}}, {blink_at});"
        )

    return "\n      ".join(lines)


def build_html(
    svg_markup: str,
    gsap_timeline: str,
    duration_s: float,
    fps: int,
    bg_color: str = "linear-gradient(#9bd7ff 0% 65%, #75c878 65%)",
) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ width: {W}px; height: {H}px; overflow: hidden;
         background: {bg_color};
         font-family: 'Courier New', monospace; }}
  .gta-hud {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }}
  .health-bar {{ position: absolute; top: 16px; left: 16px; background: rgba(0,0,0,0.6);
                border: 2px solid #fff; border-radius: 4px; padding: 4px; width: 200px; }}
  .health-bar-label {{ color: #fff; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 2px; }}
  .health-bar-fill {{ height: 8px; background: #22c55e; border-radius: 2px; transition: width 0.3s; width: 65%; }}
  .stat-display {{ position: absolute; top: 16px; right: 16px; background: rgba(0,0,0,0.6);
                  border: 2px solid #fff; border-radius: 4px; padding: 6px 12px;
                  color: #fbbf24; font-size: 14px; font-weight: bold; text-align: right; }}
  .stat-display span {{ color: #22c55e; display: block; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; }}
  .alert-popup {{ position: absolute; bottom: 80px; left: 50%; transform: translateX(-50%);
                  background: rgba(0,0,0,0.8); border: 2px solid #fbbf24; border-radius: 6px;
                  padding: 8px 16px; color: #fbbf24; font-size: 16px; font-weight: bold; text-align: center; opacity: 0; }}
  .title-card {{ position: absolute; bottom: 120px; left: 50%; transform: translateX(-50%);
                 color: #fff; font-size: 24px; font-weight: bold;
                 text-shadow: 3px 3px 0 rgba(0,0,0,0.5); text-align: center; opacity: 0; }}
  svg {{ width: 920px; position: absolute; left: 180px; top: 42px; overflow: visible; }}
  .outline {{ stroke: #202632; stroke-width: 7; stroke-linecap: round; stroke-linejoin: round; }}
</style>
</head>
<body>
  <svg viewBox="0 0 {W} {H}" role="img" aria-label="Character animation">
    {svg_markup}
  </svg>
  <div class="gta-hud">
    <div class="health-bar"><div class="health-bar-label">FINANCIAL HEALTH</div>
      <div class="health-bar-fill" id="health_fill"></div></div>
    <div class="stat-display" id="stat_display">
      <span>ASSETS</span>$12,450</div>
    <div class="alert-popup" id="alert_popup">💡 assets work for you</div>
    <div class="title-card" id="title_card">MEET ALEX</div>
  </div>
  <script>
    // INLINE GSAP (load from CDN or embed a minified copy here)
    // For production, embed gsap.min.js directly into this script block.
    // CDN fallback:
    var gsapScript = document.createElement('script');
    gsapScript.src = 'https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js';
    gsapScript.onload = function() {{
      {gsap_timeline}
    }};
    document.head.appendChild(gsapScript);
  </script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Build character animation HTML scene")
    parser.add_argument("--rig", required=True, help="Path to rig_plan JSON")
    parser.add_argument("--poses", required=True, help="Path to pose_library JSON")
    parser.add_argument("--timeline", required=True, help="Path to action_timeline JSON")
    parser.add_argument("--output", default="renders/animation_preview.html", help="Output HTML path")
    args = parser.parse_args()

    rig = load_json(args.rig)
    poses = load_json(args.poses)
    timeline = load_json(args.timeline)

    svg = build_svg_parts(rig)
    scenes = timeline.get("action_timeline", {}).get("scenes", [])
    fps = timeline.get("action_timeline", {}).get("fps", FPS)
    duration = max((s.get("end_seconds", 0) for s in scenes), default=12)

    gsap_code = build_gsap_timeline(scenes, fps, len(scenes))
    html = build_html(svg, gsap_code, duration, fps)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"Written: {out} ({out.stat().st_size // 1024} KB)")
    print(f"Duration: {duration}s at {fps}fps — open in browser or capture via Playwright")


if __name__ == "__main__":
    main()
