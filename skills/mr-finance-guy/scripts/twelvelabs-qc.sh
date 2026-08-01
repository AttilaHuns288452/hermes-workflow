#!/usr/bin/env bash
# ============================================================
# twelve-labs-qc.sh — Upload a generated video to Twelve Labs,
# analyze it, and produce a structured QC report.
#
# Usage:
#   ./twelvelabs-qc.sh VIDEO_FILE [INDEX_ID]
#
# The INDEX_ID defaults to the Mr. Finance Guy Channel index.
# Requires TWELVE_LABS_API_KEY env var or hardcoded below.
# ============================================================

set -euo pipefail

KEY="${TWELVE_LABS_API_KEY:-tlk_3GPGSWK0PX0GY82Y8NS8H0564ZBD}"
INDEX_ID="${2:-6a41d0afe88aeaea42b7b916}"
VIDEO="$1"
API="https://api.twelvelabs.io/v1.3"

if [ -z "${VIDEO:-}" ] || [ ! -f "$VIDEO" ]; then
  echo "Usage: $0 VIDEO_FILE [INDEX_ID]"
  echo "Error: VIDEO_FILE not found or not specified"
  exit 1
fi

echo "=== Twelve Labs QC ==="
echo "Video: $VIDEO"
echo "Index: $INDEX_ID"
echo ""

# 1. Upload
echo "[1/4] Uploading video..."
TASK_JSON=$(curl -s -X POST -H "x-api-key: $KEY" \
  -F "index_id=$INDEX_ID" \
  -F "video_file=@$VIDEO" \
  "$API/tasks")
TASK_ID=$(echo "$TASK_JSON" | python -c "import json,sys; print(json.load(sys.stdin)['_id'])")
VIDEO_ID=$(echo "$TASK_JSON" | python -c "import json,sys; print(json.load(sys.stdin)['video_id'])")
echo "  Task ID: $TASK_ID"
echo "  Video ID: $VIDEO_ID"

# 2. Wait for indexing
echo "[2/4] Waiting for indexing..."
while true; do
  STATUS=$(curl -s -H "x-api-key: $KEY" "$API/tasks/$TASK_ID" | \
    python -c "import json,sys; print(json.load(sys.stdin)['status'])")
  echo "  Status: $STATUS"
  if [ "$STATUS" = "ready" ]; then break; fi
  sleep 30
done

# 3. Frame layout analysis
echo "[3/4] Running frame layout analysis..."
ANALYSIS=$(curl -s -X POST -H "x-api-key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"video_id\": \"$VIDEO_ID\",
    \"prompt\": \"Analyze this video's visual layout per scene. For each scene: 1) Background color 2) Cards at top — what text, what color, are they visible? 3) Character position and size 4) Narration text position 5) Are the two cards clearly visible and distinct?\"
  }" \
  "$API/analyze")
echo "$ANALYSIS" | python -c "
import json, sys
for line in sys.stdin:
    line = line.strip()
    if line and '\"text\"' in line:
        try:
            d = json.loads(line)
            print(d.get('text',''), end='')
        except: pass
print()
"

# 4. Check for common issues
echo "[4/4] Checking for known issues..."
# Download the thumbnail for pixel check
THUMB_URL=$(curl -s -H "x-api-key: $KEY" "$API/indexes/$INDEX_ID/videos/$VIDEO_ID" | \
  python -c "import json,sys; d=json.load(sys.stdin); urls=d.get('hls',{}).get('thumbnail_urls',[]); print(urls[0] if urls else '')")

if [ -n "$THUMB_URL" ]; then
  curl -sL -o /tmp/qc_thumb.jpeg "$THUMB_URL"
  python -c "
from PIL import Image
from collections import Counter

img = Image.open('/tmp/qc_thumb.jpeg').convert('RGB')
w, h = img.size

# Check left card area for white-on-white problem
left_card_colors = []
for y in range(int(h*0.10), int(h*0.22)):
    for x in range(0, w//2):
        px = img.getpixel((x, y))
        left_card_colors.append(tuple(v//25*25 for v in px))
left_common = Counter(left_card_colors).most_common(10)

print(f'Left card area distinct colors: {len(Counter(left_card_colors))}')

# Check if card is pure white (invisible)
whites = [c for c in left_common if c[0][0] >= 250 and c[0][1] >= 250 and c[0][2] >= 250]
non_whites = [c for c in left_common if not (c[0][0] >= 250 and c[0][1] >= 250 and c[0][2] >= 250)]
white_pct = sum(c[1] for c in whites) / sum(c[1] for c in left_common) * 100 if sum(c[1] for c in left_common) > 0 else 0

if white_pct > 98:
    print('⚠️  WARNING: Left card area is >98% white — card is INVISIBLE on white background!')
    print('   Fix: Add light gray fill (#EEEEEE) or blue accent to the left card.')
else:
    print(f'✅ Left card area has {100-white_pct:.0f}% non-white content — visible.')

# Check right card area for green
right_card_colors = []
for y in range(int(h*0.10), int(h*0.22)):
    for x in range(w//2, w):
        px = img.getpixel((x, y))
        right_card_colors.append(tuple(v//25*25 for v in px))
right_common = Counter(right_card_colors).most_common(10)
greens = [c for c in right_common if c[0][1] > c[0][0] and c[0][1] > c[0][2]]
if greens:
    print(f'✅ Right card has green content: {greens[:3]}')
else:
    print('⚠️  WARNING: No green detected in right card area.')

# Check character area
char_colors = []
for y in range(int(h*0.30), int(h*0.70)):
    for x in range(0, int(w*0.35)):
        px = img.getpixel((x, y))
        char_colors.append(tuple(v//30*30 for v in px))
char_common = Counter(char_colors).most_common(6)
skin_tones = [c for c in char_common if 150 < c[0][0] < 240 and c[0][0] > c[0][2] and c[0][0] > max(c[0][1]-20, 0)]
if skin_tones:
    print(f'✅ Character has skin tones: {skin_tones[:2]}')
else:
    print('⚠️  WARNING: No skin tones detected in character area. Character may be a pure black blob.')
    print('   Fix: Ensure character sprites have visible face/hand skin tones.')

print()
print('=== QC Complete ===')
" 2>/dev/null || echo "(Note: Requires Pillow for pixel analysis)"
else
  echo "  No thumbnail available for pixel check."
fi
