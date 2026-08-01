#!/usr/bin/env python3
"""
mpv2_custom_video.py — Standalone pipeline using MoneyPrinterV2's KittenTTS + Pexels clips + ffmpeg VHS effects.

Usage:
    cd ~/Documents/Projects/MoneyPrinterV2
    source venv/Scripts/activate
    python scripts/mpv2_custom_video.py

Dependencies (installed in MoneyPrinterV2 venv):
    - kittentts (from requirements.txt)
    - soundfile
    - requests

Output:
    ~/Documents/Projects/MoneyPrinterV2/mpv2_custom_final.mp4

Customize:
    Edit STORY and SEARCH_TERMS below for your content.
"""

import os, sys, json, subprocess, glob, re, requests, base64
from uuid import uuid4

ROOT = os.path.expanduser("~/Documents/Projects/MoneyPrinterV2")
TURBO = os.path.expanduser("~/Documents/Projects/MoneyPrinterTurbo")
CACHE = os.path.join(TURBO, "storage", "cache_videos")
AUDIO_DIR = os.path.join(ROOT, ".mp")
OUTPUT = os.path.join(ROOT, "mpv2_custom_final.mp4")
os.makedirs(AUDIO_DIR, exist_ok=True)
os.chdir(ROOT)

# ======================================================================
# CUSTOMIZE: Replace with your story and search terms
# ======================================================================
STORY = """Two kids grow up in the same neighborhood. Same school. Same opportunities.
One saves his allowance. The other buys toys.

By their teens, the saver starts learning. Investing. Trading. Side hustles.
Most fail. But each failure teaches him something.
The other one parties.

Now they're adults. Both have jobs. But one has skills that make money while he sleeps.
The other trades time for dollars.

Decades pass. One builds generational wealth.
The other? Same job. Same stress. Same life he's always had.

Same starting point. Different choices.
That's the only difference between you and the person you want to become."""

# One search term per story beat/sentence (Pexels searches in order)
SEARCH_TERMS = [
    "two children different paths childhood",
    "teenager studying books investing",
    "teenager partying wasting time",
    "adult office worker stressed clock",
    "businessman success money laptop",
    "successful businessman family house",
    "father giving keys to son legacy",
    "elderly man tired at work desk",
    "two diverging roads decision",
    "wealthy family mansion generational",
    "poor elderly worker retirement sad",
    "clock ticking time money metaphor",
    "hands counting money savings jar",
    "mirror reflection two different lives",
    "real estate keys ownership home",
    "young investor stock market graph",
    "legacy grandfather grandchildren park",
]
# ======================================================================

# --- Pexels API key (shared from MoneyPrinterTurbo config) ---
PEXELS_KEY = os.environ.get("PEXELS_API_KEY")
if not PEXELS_KEY:
    try:
        import tomllib
        with open(os.path.join(TURBO, "config.toml"), "rb") as f:
            cfg = tomllib.load(f)
        keys = cfg.get("pexels_api_keys", [])
        if keys:
            PEXELS_KEY = keys[0]
    except Exception:
        pass


def get_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
        capture_output=True, text=True, timeout=10,
    )
    return float(json.loads(r.stdout)["format"]["duration"])


def search_pexels(term, per_page=1):
    if not PEXELS_KEY:
        return []
    try:
        r = requests.get(
            "https://api.pexels.com/videos/search",
            params={"query": term, "per_page": per_page, "orientation": "portrait"},
            headers={"Authorization": PEXELS_KEY},
            timeout=15,
        )
        if r.status_code == 200:
            return r.json().get("videos", [])
    except Exception:
        pass
    return []


def download_clips():
    print("=== Step 1: Downloading Pexels clips ===")
    os.makedirs(CACHE, exist_ok=True)
    downloaded = []
    for i, term in enumerate(SEARCH_TERMS):
        print(f"  Searching: '{term}'...", end=" ")
        videos = search_pexels(term)
        if not videos:
            print("no results")
            continue
        video = videos[0]
        # Pick best quality vertical clip
        url = None
        for vf in video.get("video_files", []):
            if vf.get("width", 0) >= 540 and vf.get("height", 0) >= 960:
                url = vf["link"]
                break
        if not url:
            url = video["video_files"][0]["link"]
        ext = url.split("?")[0].rsplit(".", 1)[-1] if "." in url.split("?")[0] else "mp4"
        fname = f"pexels_{uuid4().hex[:8]}.{ext}"
        fpath = os.path.join(CACHE, fname)
        try:
            r = requests.get(url, timeout=60)
            with open(fpath, "wb") as f:
                f.write(r.content)
            dur = get_duration(fpath)
            downloaded.append(fpath)
            print(f"{dur:.1f}s")
        except Exception as e:
            print(f"failed: {e}")
    if not downloaded:
        print("WARNING: No clips downloaded. Using cached clips.")
        downloaded = sorted(glob.glob(os.path.join(CACHE, "*.mp4")), key=os.path.getmtime, reverse=True)[:17]
        downloaded.reverse()
    print(f"  Total: {len(downloaded)} clips\n")
    return downloaded


def generate_audio():
    print("=== Step 2: Generating KittenTTS audio ===")
    sys.path.insert(0, ROOT)
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from kittentts import KittenTTS as KittenModel
    import soundfile as sf

    model = KittenModel("KittenML/kitten-tts-mini-0.8")
    audio_path = os.path.join(AUDIO_DIR, f"story_{uuid4().hex[:8]}.wav")
    print("  Rendering neural TTS...")
    audio = model.generate(STORY, voice="Jasper")
    sf.write(audio_path, audio, 24000)
    dur = len(audio) / 24000
    size = os.path.getsize(audio_path) / 1024
    print(f"  Audio: {dur:.1f}s | {size:.0f} KB\n")

    # Also convert to MP3 for ffmpeg
    mp3_path = audio_path.replace(".wav", ".mp3")
    subprocess.run(
        ["ffmpeg", "-y", "-i", audio_path, "-codec:a", "libmp3lame", "-b:a", "192k", mp3_path],
        capture_output=True, text=True, timeout=60,
    )
    return mp3_path, dur


def build_video(clips, audio_path, audio_dur):
    print("=== Step 3: Building video ===")

    # Split STORY into sentences for proportional timing
    sentences = [s.strip() for s in STORY.replace("?", ".\n").replace("!", ".\n").split(".") if s.strip()]
    total_words = sum(len(s.split()) for s in sentences)

    # Trim clips to match (handle clip count mismatch)
    pair_count = min(len(clips), len(sentences))
    clips = clips[:pair_count]
    times = [(len(sentences[i].split()) / total_words) * audio_dur for i in range(pair_count)]

    # Build per-clip filter chain
    filter_parts = []
    input_parts = []
    for i, (fpath, dur) in enumerate(zip(clips, times)):
        src_dur = get_duration(fpath)
        clip_dur = max(min(dur, src_dur), 1.5)
        input_parts.extend(["-i", fpath.replace("\\", "/")])
        filter_parts.append(
            f"[{i}:v]trim=0:{clip_dur},setpts=PTS-STARTPTS,"
            f"scale=1080:1920:force_original_aspect_ratio=decrease,"
            f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,"
            f"setsar=1,fps=30[v{i}]"
        )
        print(f"  Clip {i+1:2d}/{pair_count}: {os.path.basename(fpath)} -> {clip_dur:.1f}s")

    concat_in = "".join(f"[v{i}]" for i in range(pair_count))
    filter_parts.append(f"{concat_in}concat=n={pair_count}:v=1:a=0[outv]")

    # VHS radio aesthetic overlay
    vhs_overlay = (
        f"color=c=gray:s=1080x1920:d={audio_dur}:r=30[base];"
        f"[base]drawbox=x=0:y=1:w=iw:h=1:color=white@0.05:t=fill,"
        f"drawbox=x=0:y=ih-2:w=iw:h=1:color=white@0.05:t=fill[scanlines];"
        f"[outv]colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,"
        f"vignette[vid];"
        f"[vid][scanlines]overlay[outv2]"
    )
    fc = ";".join(filter_parts) + ";" + vhs_overlay

    print("\n  Rendering (quality: CRF 20, AAC 256k)...")
    cmd = (
        ["ffmpeg", "-y"]
        + input_parts
        + [
            "-i", audio_path.replace("\\", "/"),
            "-filter_complex", fc,
            "-map", "[outv2]", "-map", f"{pair_count}:a",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-r", "30",
            "-c:a", "aac", "-b:a", "256k",
            "-t", str(audio_dur), "-movflags", "+faststart",
            OUTPUT.replace("\\", "/"),
        ]
    )

    subprocess.run(cmd, check=True, timeout=600)
    final_dur = get_duration(OUTPUT)
    size_mb = os.path.getsize(OUTPUT) / 1024 / 1024
    print(f"\n{'='*50}")
    print(f"✅ DONE: {size_mb:.1f} MB | {final_dur:.1f}s")
    print(f"   {OUTPUT}")
    print(f"{'='*50}")


if __name__ == "__main__":
    clips = download_clips()
    audio_path, audio_dur = generate_audio()
    build_video(clips, audio_path, audio_dur)
