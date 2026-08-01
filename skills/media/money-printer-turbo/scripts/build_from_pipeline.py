#!/usr/bin/env python3
"""
build_from_pipeline.py — Frame-perfect assembly using pipeline's Edge TTS audio + fresh downloads.
Uses ffmpeg filter_complex with word-count proportional timing per segment.
Outputs: storage/tasks/<uuid>/pipeline-final.mp4

Prerequisite: python scripts/run_pipeline.py (downloads fresh clips + generates audio)

Usage:
    cd ~/Documents/Projects/MoneyPrinterTurbo
    source .venv/Scripts/activate
    python scripts/build_from_pipeline.py
"""

import os, sys, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

AUDIO_PATH = ""  # Will use task_dir/audio.mp3
CACHE_DIR = "storage/cache_videos"

SEGMENTS_TEXT = [
    "What if the wealthiest person you know... isnt the one with the highest salary?",
    "There is a quiet pattern among people who build generational wealth.",
    "They do not talk about money. They talk about ownership.",
    "A lawyer making five hundred thousand a year leases a BMW.",
    "A plumber making eighty thousand owns the building his shop sits in.",
    "Twenty years later... the plumbers grandchildren inherit the building.",
    "The lawyers grandchildren inherit the lease payments.",
    "This is not about income. It is about what you DO with income.",
    "Robert Kiyosaki said it thirty years ago.",
    "Rich people acquire assets. The middle class acquires liabilities they THINK are assets.",
    "Your house? Liability. Your 401k match? Asset.",
    "That rental property? Asset. The car you finance? Liability.",
    "Here is what nobody tells you:",
    "Every dollar you spend... votes for the person you are becoming.",
    "The question is not can I afford this?",
    "The question is... does this make me an owner... or a renter?",
    "Most people choose renter. Every single day. Without realizing it.",
    "What did you choose today?",
]

def get_duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
        capture_output=True, text=True, timeout=10
    )
    return float(json.loads(result.stdout)["format"]["duration"])

def main():
    if not os.path.exists("last_task_id.txt"):
        print("❌ last_task_id.txt not found. Run run_pipeline.py first.")
        sys.exit(1)
    
    task_id = open("last_task_id.txt").read().strip()
    TASK_DIR = os.path.join("storage/tasks", task_id)
    AUDIO_PATH = os.path.join(TASK_DIR, "audio.mp3")
    FINAL = os.path.join(TASK_DIR, "pipeline-final.mp4")
    
    if not os.path.exists(AUDIO_PATH):
        print(f"❌ Pipeline audio not found: {AUDIO_PATH}")
        sys.exit(1)
    
    print(f"🎬 Task: {task_id}")
    print(f"🎵 Audio: {AUDIO_PATH}")
    
    audio_dur = get_duration(AUDIO_PATH)
    print(f"   Edge TTS audio duration: {audio_dur:.2f}s")
    
    all_videos = []
    for fname in os.listdir(CACHE_DIR):
        if fname.endswith(".mp4"):
            fpath = os.path.join(CACHE_DIR, fname)
            mtime = os.path.getmtime(fpath)
            all_videos.append((fname, mtime, fpath))
    
    all_videos.sort(key=lambda x: x[1], reverse=True)
    fresh_17 = all_videos[:17]
    fresh_17.reverse()
    
    if len(fresh_17) < 17:
        print(f"❌ Only {len(fresh_17)} fresh videos found. Need 17.")
        sys.exit(1)
    
    total_words = sum(len(s.split()) for s in SEGMENTS_TEXT)
    
    selected = []
    print("\n📹 Segment mapping:")
    for i, (text, (fname, _, fpath)) in enumerate(zip(SEGMENTS_TEXT, fresh_17)):
        word_count = len(text.split())
        target_dur = (word_count / total_words) * audio_dur
        src_dur = get_duration(fpath)
        selected.append((fname, fpath, src_dur, target_dur, text[:50]))
        print(f"  {i+1:2d}. {fname} ({src_dur:.1f}s → {target_dur:.1f}s) | {text[:50]}...")
    
    filter_parts = []
    input_parts = []
    for idx, (fname, fpath, src_dur, target_dur, _) in enumerate(selected):
        abs_path = fpath.replace("\\", "/")
        input_parts.extend(["-i", abs_path])
        filter_parts.append(
            f"[{idx}:v]trim=0:{target_dur},setpts=PTS-STARTPTS,"
            f"scale=1080:1920:force_original_aspect_ratio=decrease,"
            f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,"
            f"fps=30[v{idx}]"
        )
    
    concat_inputs = "".join(f"[v{i}]" for i in range(len(selected)))
    filter_parts.append(f"{concat_inputs}concat=n={len(selected)}:v=1:a=0[outv]")
    filter_complex = ";".join(filter_parts)
    
    cmd = [
        "ffmpeg", "-y",
        *input_parts,
        "-i", AUDIO_PATH,
        "-filter_complex", filter_complex,
        "-map", "[outv]", "-map", f"{len(selected)}:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(audio_dur),
        "-movflags", "+faststart",
        FINAL
    ]
    
    print(f"\n⚡ Building with {len(selected)} precisely-timed clips...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"❌ FFmpeg failed: {result.stderr[-1500:]}")
        sys.exit(1)
    
    vdur = get_duration(FINAL)
    size = os.path.getsize(FINAL) / 1024 / 1024
    print(f"\n✅ DONE: {vdur:.1f}s | {size:.1f} MB")
    print(f"   Output: {FINAL}")
    
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=width,height,r_frame_rate",
         "-of", "default=noprint_wrappers=1:nokey=1", FINAL],
        capture_output=True, text=True, timeout=10
    )
    res = result.stdout.strip().replace("\n", "x")
    print(f"   Resolution: {res}")

if __name__ == "__main__":
    main()