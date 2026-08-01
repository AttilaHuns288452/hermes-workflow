# Pixel Comparison QC — Reference vs Generated Video

## Why

Twelve Labs Pegasus analysis is powerful but has blind spots: it says "text is readable"
even when a white card on a white background is invisible at thumbnail scale. Pixel-level
comparison of the video thumbnails catches these layout failures that Pegasus misses.

## The Technique

Twelve Labs auto-generates thumbnails (320×568 JPEG) for every indexed video. By
extracting these and running PIL analysis on specific zones, we can detect:

1. **Invisible elements** — card area too uniform = card not visible
2. **Missing accent colors** — no green in right card zone, no blue in left card zone
3. **Character blob detection** — all black pixels with no skin tones
4. **Color scheme drift** — card colors don't match reference

## Step-by-Step

### 1. Get thumbnails

```bash
# Reference thumbnail
curl -sL -o ref.jpeg "https://deuqpmn4rs7j5.cloudfront.net/.../thumbnails/5.jpeg"
# Generated thumbnail
curl -sL -o gen.jpeg "https://deuqpmn4rs7j5.cloudfront.net/.../thumbnails/5.jpeg"
```

The thumbnail URL pattern: `https://deuqpmn4rs7j5.cloudfront.net/{ASSET_BUCKET}/assets/{VIDEO_ID}/thumbnails/5.jpeg`
Extract the video ID from the Twelve Labs video metadata response (`video.hls.thumbnail_urls[0]`).

### 2. Analyze zones with Python PIL

```python
from PIL import Image
from collections import Counter

img = Image.open('thumbnail.jpeg').convert('RGB')
w, h = img.size  # Typically 320×568

# LEFT CARD ZONE (top-left quadrant, 10-22% from top)
left_colors = []
for y in range(int(h*0.10), int(h*0.22)):
    for x in range(0, w//2):
        px = img.getpixel((x, y))
        left_colors.append(tuple(v//25*25 for v in px))
left_common = Counter(left_colors).most_common(10)

# RIGHT CARD ZONE (top-right quadrant)
right_colors = []
for y in range(int(h*0.10), int(h*0.22)):
    for x in range(w//2, w):
        px = img.getpixel((x, y))
        right_colors.append(tuple(v//25*25 for v in px))
right_common = Counter(right_colors).most_common(10)

# CHARACTER ZONE (left side, 30-70% from top)
char_colors = []
for y in range(int(h*0.30), int(h*0.70)):
    for x in range(0, int(w*0.35)):
        px = img.getpixel((x, y))
        char_colors.append(tuple(v//30*30 for v in px))
char_common = Counter(char_colors).most_common(6)
```

### 3. Interpret results

| Metric | Good | Bad |
|--------|------|-----|
| Left card white % | <95% (has accent) | >98% (invisible) |
| Right card green | Present (60,180,90) | Absent or too dark |
| Character skin tone | Present (~210,120,30) | Only (0,0,0) |
| Card row pixel variation | Some variation | All identical |

### 4. Automated detection (heuristic rules)

```python
# Invisible card check
white_pct = sum(c[1] for c in left_common if all(v >= 250 for v in c[0])) / total
if white_pct > 0.98:
    print("WARNING: Left card invisible on white bg")

# Character blob check
skin = any(150 < c[0][0] < 240 and c[0][0] > c[0][2] for c in char_common)
if not skin:
    print("WARNING: No skin tones — character may be a black blob")
```

## When to Run

After generating a new video and before showing the user:
1. Upload to Twelve Labs
2. Wait for indexing
3. Extract thumbnail URL
4. Run pixel analysis
5. Fix any warnings
6. Show the user only when clean

## Reference: Known Good Values (from "Active Income vs Passive Income")

| Zone | Reference colors (quantized) |
|------|------------------------------|
| Left card | (240,240,240) gray, (30,180,210) blue |
| Right card | (240,240,240) gray, (60,180,90) green |
| Character | (240,240,240) bg, (210,120,30) skin, (0,0,0) suit |
| Lower third | (240,240,240) bg, (0,0,0) text |
