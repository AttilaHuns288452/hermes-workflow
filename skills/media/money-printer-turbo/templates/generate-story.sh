#!/usr/bin/env bash
# generate-story.sh - One-shot TikTok video generator for MoneyPrinterTurbo
# 
# Place this in ~/Documents/Projects/MoneyPrinterTurbo/ and run:
#   bash generate-story.sh "Your story here" "keyword1, keyword2, keyword3"
#
# Handles:
#   - Venv activation
#   -- Full pipe: script → TTS → Pexels footage → video
#   - Automatic FFmpeg fallback when MoviePy crashes (Windows BrokenPipeError)
#   - Outputs to storage/tasks/<uuid>/tiktok-final.mp4

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STORY="${1:-}"
TERMS="${2:-dark alley night, creepy house, door knocking horror, suspense thriller, mysterious stranger}"
VOICE="${3:-en-US-AriaNeural}"
VOICE_RATE="${4:-1.0}"

if [ -z "$STORY" ]; then
  echo "❌ Usage: $0 \"Your story here\" [\"keywords\"] [\"voice-name\"] [voice-rate]"
  echo ""
  echo "Examples:"
  echo "  $0 \"Story text\"                                          (default voice, normal speed)"
  echo "  $0 \"Story text\" \"term1, term2\" \"en-US-ChristopherNeural\" 0.80"
  echo ""
  echo "Recommended dramatic voices:"
  echo "  en-US-ChristopherNeural  (deep, calm, authoritative — best for skeleton AI style)"
  echo "  en-US-RogerNeural        (warm, deep, inspiring)"
  echo "  en-US-GuyNeural          (general storytelling)"
  echo "  en-US-AriaNeural         (female, balanced — default)"
  echo ""
  echo "Voice rate: 0.75 (very slow/dramatic)  0.80 (slow)  0.90 (slightly calm)  1.0 (normal)"
  exit 1
fi

cd "$SCRIPT_DIR"
source .venv/Scripts/activate

echo "🎬 Generating TikTok video..."
echo "📖 Story: $STORY"
echo "🎯 Terms: $TERMS"
echo ""

# Generate with subtitles disabled (avoids ~3GB Whisper model download)
python cli.py \
  --video-subject "TikTok Story" \
  --video-script "$STORY" \
  --video-terms "$TERMS" \
  --voice-name "en-US-AriaNeural" \
  --video-aspect "9:16" \
  --no-subtitle-enabled 2>&1

CLI_EXIT=$?

# Find the most recent task directory
TASK_DIR=$(ls -td storage/tasks/*/ 2>/dev/null | head -1)

if [ $CLI_EXIT -ne 0 ] && [ -n "$TASK_DIR" ]; then
  if [ -f "${TASK_DIR}combined-1.mp4" ] || ls "${TASK_DIR}"temp-clip-*.mp4 1>/dev/null 2>&1; then
    echo ""
    echo "⚠️  CLI had an error, but media files exist. Running manual FFmpeg pipeline..."
    
    if [ -f "${TASK_DIR}ffmpeg-concat-list.txt" ]; then
      echo "   Concat from temp clips..."
      ffmpeg -y -f concat -safe 0 -i "${TASK_DIR}ffmpeg-concat-list.txt" \
        -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p -movflags +faststart \
        "${TASK_DIR}combined-manual.mp4" 2>/dev/null
      COMBINED="${TASK_DIR}combined-manual.mp4"
    elif [ -f "${TASK_DIR}combined-1.mp4" ]; then
      COMBINED="${TASK_DIR}combined-1.mp4"
    else
      echo "❌ No video clips found to combine."
      exit 1
    fi
    
    if [ -f "$COMBINED" ] && [ -f "${TASK_DIR}audio.mp3" ]; then
      ffmpeg -y -i "$COMBINED" -i "${TASK_DIR}audio.mp3" \
        -c:v copy -c:a aac -b:a 128k -shortest -movflags +faststart \
        "${TASK_DIR}tiktok-final.mp4" 2>/dev/null
      
      echo ""
      echo "✅ Video saved to: ${TASK_DIR}tiktok-final.mp4"
      ls -lh "${TASK_DIR}tiktok-final.mp4"
    else
      echo "❌ Missing combined video or audio file."
      ls -la "${TASK_DIR}"
      exit 1
    fi
  else
    echo "❌ Failed to generate video. No media files found."
    exit 1
  fi
elif [ $CLI_EXIT -eq 0 ] && [ -n "$TASK_DIR" ] && [ -f "${TASK_DIR}final-1.mp4" ]; then
  # CLI succeeded — just rename for consistency
  cp "${TASK_DIR}final-1.mp4" "${TASK_DIR}tiktok-final.mp4"
  echo ""
  echo "✅ Video saved to: ${TASK_DIR}tiktok-final.mp4"
  ls -lh "${TASK_DIR}tiktok-final.mp4"
else
  echo ""
  echo "⚠️  CLI finished but no final video found. Check task directory:"
  [ -n "$TASK_DIR" ] && ls -la "$TASK_DIR" || echo "   No task directory found."
  exit 1
fi
