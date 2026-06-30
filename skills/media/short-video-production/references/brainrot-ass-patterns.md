# Brainrot ASS Subtitle Patterns

Full ASS template for the "Socrates skeleton" brainrot finance video format.
Copy this and modify text/timings for your own video.

## ASS Styles

```
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: h_white,Impact,64,&H00FFFFFF,&H00000000,&H00000000,&H80999999,0,0,3,2,1,5,10,10,60,1
Style: h_gold,Impact,64,&H0000FFD7,&H00000000,&H00000000,&H80999999,0,0,3,2,1,5,10,10,60,1
Style: h_red,Impact,64,&H004444FF,&H00000000,&H00000000,&H80999999,0,0,3,2,1,5,10,10,60,1
Style: h_green,Impact,64,&H0044FF44,&H00000000,&H00000000,&H80999999,0,0,3,2,1,5,10,10,60,1
Style: sub_white,Arial,32,&H00FFFFFF,&H00000000,&H00000000,&H80999999,0,0,3,1,1,5,10,10,40,1
Style: caption,Arial,24,&H00FFFFFF,&H00000000,&H00000000,&H80CC0000,0,0,3,1,1,2,10,10,60,1
Style: label,Arial,20,&H0000FFD7,&H00000000,&H00000000,&H80999999,0,0,3,1,1,9,10,10,10,1
Style: bar_fill,Arial,14,&H00FFFFFF,&H00000000,&H00000000,&H80999999,0,0,3,1,1,9,10,10,26,1
```

## HUD Elements (Permanent Overlays)

These are timed from `0` to `total_duration` seconds. Replace `{total_dur}` with your video length.

```
Dialogue: 0,0:00:00.00,{end_ts},label,,0,0,0,,{\an9}{\c&H0000FF&}●{\c} LIVE
Dialogue: 0,0:00:00.00,{end_ts},label,,0,0,0,,{\an9}{\fs20}FINANCIAL IQ
Dialogue: 0,0:00:00.00,{end_ts},bar_fill,,0,0,0,,{\an9}{\fs14}{\c&H444444&}█{\c&H00FFD7&}███████{\c&H444444&}███{\c} 72%
Dialogue: 0,0:00:00.00,{end_ts},bar_fill,,0,0,0,,{\an9}{\fs12}{\c&H888888&}1.2M VIEWS{\c}
```

## Brainrot Impact Headers

Timed to appear/disappear with the narration. Each header gets its own Dialogue line with `{\an5}` (center-center) and `{\pos(540, Y)}` for vertical placement.

```
Dialogue: 1,0:00:00.00,0:00:02.50,h_gold,,0,0,0,,{\an5}{\pos(540,600)}SOCRATES
Dialogue: 1,0:00:02.00,0:00:05.00,h_white,,0,0,0,,{\an5}{\pos(540,720)}THE UNEXAMINED\NLIFE
Dialogue: 1,0:00:04.00,0:00:07.50,h_red,,0,0,0,,{\an5}{\pos(540,720)}YOUR BANK ACCOUNT?
```

**Y-position guide for layered headers (3 lines stacking):**
- Line 1 (top): y=680
- Line 2 (middle): y=760  
- Line 3 (bottom): y=840
- Single center: y=700-720

**Color conventions:**
- Gold: key concepts, positive reveals
- Red: warnings, problems, pain points
- Green: solutions, success, assets
- White: neutral exposition, facts

## Bottom Captions (Narration Text)

```
Dialogue: 2,0:00:00.00,0:00:07.50,caption,,0,0,0,,{\an2}The unexamined life is not worth living.\NBut in 2026, your bank account? Even worse.
Dialogue: 2,0:00:07.50,0:00:12.00,caption,,0,0,0,,{\an2}Here is the truth they don't teach in school.
```

## Two-Pass FFmpeg Pipeline

### Pass 1: Base Video

```python
import subprocess
base_cmd = [
    "ffmpeg", "-y",
    "-loop", "1", "-i", "character.jpg",
    "-t", "60",  # match your narration duration
    "-filter_complex",
    "[0:v]scale=1242:2208:force_original_aspect_ratio=increase,"  # 115% oversize
    "crop=1080:1920,format=yuv420p[vid]",
    "-map", "[vid]",
    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
    "-r", "30", "-pix_fmt", "yuv420p", "-an",
    "base_video.mp4"
]
subprocess.run(base_cmd, timeout=120)
```

### Pass 2: Burn ASS + Mux Audio

```python
import shutil
shutil.copy2("overlays.ass", "sub.ass")  # short path avoids Windows colon issues

second_cmd = [
    "ffmpeg", "-y",
    "-i", "base_video.mp4",
    "-i", "narration.mp3",
    "-filter_complex", "[0:v]subtitles=sub.ass[vid]",
    "-map", "[vid]", "-map", "1:a",
    "-c:v", "libx264", "-preset", "superfast", "-crf", "20",
    "-c:a", "aac", "-b:a", "192k",
    "-pix_fmt", "yuv420p", "-r", "30", "-shortest",
    "-movflags", "+faststart",
    "final_video.mp4"
]
subprocess.run(second_cmd, timeout=120)
```

## ASS Alignment Guide

| Code | Position | Used For |
|:----:|:--------:|----------|
| {\an1} | Bottom-left | Watermark |
| {\an2} | Bottom-center | Narration captions |
| {\an5} | Center-center | Impact headers (with explicit pos) |
| {\an7} | Top-left | Labels |
| {\an9} | Top-right | HUD elements (LIVE, stat bar) |

## Time-to-Frame Conversion

```python
def ts(t):
    """Convert seconds to ASS timestamp."""
    hh = int(t // 3600)
    mm = int((t % 3600) // 60)
    ss = int(t % 60)
    cs = int((t % 1) * 100)
    return f"{hh}:{mm:02d}:{ss:02d}.{cs:02d}"
```

## Word-Count Timing Estimation

For a script with N words and total narration duration D seconds:
- Each segment's duration = (word_count_in_segment / total_words) * D
- Average US English speaking rate: 150 wpm (slow/dramatic) to 160 wpm (normal)
