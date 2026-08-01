#!/usr/bin/env bash
# build_sophisticated.sh — One-shot sophisticated video builder
# Usage: bash templates/build_sophisticated.sh
# Requires: MoneyPrinterTurbo venv activated, cached videos in storage/cache_videos/

# CONFIGURATION
TASK_DIR="storage/tasks/$(date +%s)-sophisticated"
CACHE_DIR="storage/cache_videos"
AUDIO_FILE="voice-samples/sophisticated_money.mp3"
FINAL_VIDEO="${TASK_DIR}/sophisticated-final.mp4"

mkdir -p "$TASK_DIR"

echo "🎬 Building sophisticated financial storytelling video..."
echo "   Task dir: $TASK_DIR"
echo "   Audio: $AUDIO_FILE"

# Check audio exists
if [ ! -f "$AUDIO_FILE" ]; then
    echo "❌ Audio file not found: $AUDIO_FILE"
    echo "   Generate it first with: python gen_sophisticated.py"
    exit 1
fi

# Get audio duration
AUDIO_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$AUDIO_FILE")
echo "   Audio duration: ${AUDIO_DUR}s"

# 18 segments: (script_segment, target_duration, visual_keywords)
cat > "$TASK_DIR/segments.json" << 'EOF'
[
  ["What if the wealthiest person you know... isn't the one with the highest salary?", 4.5, "wealthy couple walking"],
  ["There's a quiet pattern among people who build generational wealth.", 4.0, "family legacy portrait"],
  ["They don't talk about money. They talk about ownership.", 3.5, "business owner keys"],
  ["A lawyer making five hundred thousand a year leases a BMW.", 4.0, "luxury car lease"],
  ["A plumber making eighty thousand owns the building his shop sits in.", 4.5, "commercial building deed"],
  ["Twenty years later... the plumber's grandchildren inherit the building.", 4.5, "grandfather teaching grandchildren"],
  ["The lawyer's grandchildren inherit the lease payments.", 3.5, "financial stress bills"],
  ["This isn't about income. It's about what you DO with income.", 3.5, "decision crossroads"],
  ["Robert Kiyosaki said it thirty years ago.", 3.0, "financial authority book"],
  ["Rich people acquire assets. The middle class acquires liabilities they THINK are assets.", 5.5, "assets vs liabilities diagram"],
  ["Your house? Liability. Your 401k match? Asset.", 4.0, "house investment account"],
  ["That rental property? Asset. The car you finance? Liability.", 4.0, "rental property keys"],
  ["Here is what nobody tells you:", 2.5, "shadow document mystery"],
  ["Every dollar you spend... votes for the person you are becoming.", 4.5, "voting ballot metaphor"],
  ["The question is not can I afford this?", 3.0, "credit card pause"],
  ["The question is... does this make me an owner... or a renter?", 4.5, "fork in road choice"],
  ["Most people choose renter. Every single day. Without realizing it.", 4.0, "sleepwalking automatic"],
  ["What did you choose today?", 3.0, "mirror reflection direct camera"]
]
EOF

# Python script to pick best videos and build filter_complex
python3 << 'PYEOF'
import os, json, subprocess

TASK_DIR = os.environ.get('TASK_DIR')
CACHE_DIR = os.environ.get('CACHE_DIR')
AUDIO_FILE = os.environ.get('AUDIO_FILE')
FINAL_VIDEO = os.environ.get('FINAL_VIDEO')

with open(os.path.join(TASK_DIR, 'segments.json')) as f:
    segments = json.load(f)

# Get all cached videos with durations
all_videos = []
for fname in os.listdir(CACHE_DIR):
    if fname.endswith('.mp4'):
        fpath = os.path.join(CACHE_DIR, fname)
        result = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','json',fpath],capture_output=True,text=True,timeout=10)
        dur = float(json.loads(result.stdout)['format']['duration'])
        if 2 <= dur <= 25:
            all_videos.append((fname, dur))

all_videos.sort(key=lambda x: x[1])
print(f"📹 {len(all_videos)} usable cached videos")

# Pick best video per segment (duration match)
used = set()
selected = []
for text, target, keywords in segments:
    best = None
    best_score = 999
    for fname, vdur in all_videos:
        if fname in used: continue
        score = abs(vdur - target)
        if score < best_score:
            best_score = score
            best = (fname, vdur)
    if best:
        fname, vdur = best
        used.add(fname)
        selected.append((fname, vdur, target, text[:50]))
        print(f"  {fname} ({vdur:.1f}s -> {target:.1f}s) | {text[:50]}...")
    else:
        print(f"  ⚠️ NO VIDEO for: {text[:50]}...")

total_target = sum(t for _,_,t,_ in selected)
print(f"\n📊 Target: {total_target:.1f}s | Audio: {float(AUDIO_DUR):.1f}s")

# Build filter complex
filter_parts = []
input_parts = []
for idx, (fname, vdur, target, _) in enumerate(selected):
    fpath = os.path.join(CACHE_DIR, fname).replace('\\\\', '/')
    input_parts.extend(['-i', fpath])
    filter_parts.append(f'[{idx}:v]trim=0:{target},setpts=PTS-STARTPTS,'
                        f'scale=1080:1920:force_original_aspect_ratio=decrease,'
                        f'pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,'
                        f'fps=30[v{idx}]')

concat_inputs = ''.join(f'[v{i}]' for i in range(len(selected)))
filter_parts.append(f'{concat_inputs}concat=n={len(selected)}:v=1:a=0[outv]')

filter_complex = ';'.join(filter_parts)

# Save for bash execution
with open(os.path.join(TASK_DIR, 'ffmpeg_inputs.txt'), 'w') as f:
    for part in input_parts:
        f.write(f"{part}\n")

with open(os.path.join(TASK_DIR, 'filter_complex.txt'), 'w') as f:
    f.write(filter_complex)

with open(os.path.join(TASK_DIR, 'selected_videos.json'), 'w') as f:
    json.dump(selected, f, indent=2)

PYEOF

# Build the final video
echo ""
echo "⚡ Building with ffmpeg filter_complex..."

# Read inputs and filter
INPUTS=$(cat "$TASK_DIR/ffmpeg_inputs.txt" | tr '\n' ' ')
FILTER=$(cat "$TASK_DIR/filter_complex.txt")

ffmpeg -y $INPUTS -i "$AUDIO_FILE" \
  -filter_complex "$FILTER" \
  -map "[outv]" -map "$((${#selected[@]})):a" \
  -c:v libx264 -preset fast -crf 22 \
  -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k \
  -t "$AUDIO_DUR" \
  -movflags +faststart \
  "$FINAL_VIDEO" 2>&1 | tail -10

# Verify
if [ -f "$FINAL_VIDEO" ]; then
    VDUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$FINAL_VIDEO")
    SIZE=$(du -h "$FINAL_VIDEO" | cut -f1)
    RES=$(ffprobe -v error -show_entries stream=width,height -of csv=p=0 "$FINAL_VIDEO" | tr '\n' 'x')
    echo ""
    echo "✅ SOPHISTICATED VIDEO COMPLETE"
    echo "   File: $FINAL_VIDEO"
    echo "   Duration: ${VDUR}s"
    echo "   Size: $SIZE"
    echo "   Resolution: ${RES}"
else
    echo "❌ Build failed"
    exit 1
fi