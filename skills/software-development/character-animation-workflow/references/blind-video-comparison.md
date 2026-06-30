# Blind-Model Frame Comparison

## When to Use

Your model cannot analyze video or images (e.g. DeepSeek). You need to compare a generated video against a reference to identify layout, positioning, or quality issues.

## Workflow

### 1. Extract Frames at Matching Timestamps

```bash
mkdir -p comparison

for t in 1 5 10 15 20 25 30 35 40 45 50 55 60 65; do
  ffmpeg -y -ss $t -i reference.mp4 -vframes 1 -q:v 3 "comparison/ref_$(printf '%02d' $t)s.jpg"
  ffmpeg -y -ss $t -i generated.mp4 -vframes 1 -q:v 3 "comparison/my_$(printf '%02d' $t)s.jpg"
done
```

### 2. Build a Side-by-Side HTML Page

Create a static HTML page with a 2-column grid (reference left, generated right). Use relative image paths and serve via HTTP:

```python
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
os.chdir("comparison")
HTTPServer(("0.0.0.0", 8899), SimpleHTTPRequestHandler).serve_forever()
```

Then open `http://localhost:8899` in the browser. The user looks at the comparison and describes differences.

### 3. What to Ask the User to Look For

- **Character position** — Is the character too low? Too far left/right?
- **Image relevance** — Do the props match what the narration says?
- **Pose direction** — Is the character pointing toward the content or away?
- **Text readability** — Is the narration overlay readable?
- **Visual balance** — Does the composition feel natural or awkward?
- **Color contrast** — Do labels/headers pop against the background?

### 4. Iterating

After the user describes the issues:
1. Update the compositing script
2. Regenerate scenes: `python replicate_video.py`
3. Re-render segments + audio: `python compose_final.py`
4. Re-extract frames and refresh the comparison page
5. Ask again: "Does this fix the issue?"

## Pitfalls

- **file:// URLs don't work** in the Hermes browser. Always use an HTTP server.
- **Background the server** — use `terminal(background=true)` for the HTTP server, then navigate to it.
- **Model can't see images either** — vision_analyze may also fail. The user is the only one who can validate visual output.
- **Different durations** — Reference and generated videos may have different lengths. Extract frames at the same timestamps where both exist.
