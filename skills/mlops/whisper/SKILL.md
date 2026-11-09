---
name: whisper
description: Transcribe and translate speech in 99 languages.
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [openai-whisper, transformers, torch]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Whisper, Speech Recognition, ASR, Multimodal, Multilingual, OpenAI, Speech-To-Text, Transcription, Translation, Audio Processing]

---

# Whisper - Robust Speech Recognition

OpenAI's multilingual speech recognition model.

## When to use Whisper

**Use when:**
- Speech-to-text transcription (99 languages)
- Podcast/video transcription
- Meeting notes automation
- Translation to English
- Noisy audio transcription
- Multilingual audio processing
- Distilling a recorded defense/review/meeting into reusable notes with verbatim speaker quotes

**Metrics**:
- **72,900+ GitHub stars**
- 99 languages supported
- Trained on 680,000 hours of audio
- MIT License

**Use alternatives instead**:
- **AssemblyAI**: Managed API, speaker diarization
- **Deepgram**: Real-time streaming ASR
- **Google Speech-to-Text**: Cloud-based

## Quick start

### Installation

```bash
# Requires Python 3.8-3.11
pip install -U openai-whisper

# Requires ffmpeg
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
# Windows: choco install ffmpeg
```

### Basic transcription

```python
import whisper

# Load model
model = whisper.load_model("base")

# Transcribe
result = model.transcribe("audio.mp3")

# Print text
print(result["text"])

# Access segments
for segment in result["segments"]:
    print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}")
```

## Model sizes

```python
# Available models
models = ["tiny", "base", "small", "medium", "large", "turbo"]

# Load specific model
model = whisper.load_model("turbo")  # Fastest, good quality
```

| Model | Parameters | English-only | Multilingual | Speed | VRAM |
|-------|------------|--------------|--------------|-------|------|
| tiny | 39M | ✓ | ✓ | ~32x | ~1 GB |
| base | 74M | ✓ | ✓ | ~16x | ~1 GB |
| small | 244M | ✓ | ✓ | ~6x | ~2 GB |
| medium | 769M | ✓ | ✓ | ~2x | ~5 GB |
| large | 1550M | ✗ | ✓ | 1x | ~10 GB |
| turbo | 809M | ✗ | ✓ | ~8x | ~6 GB |

**Recommendation**: Use `turbo` for best speed/quality, `base` for prototyping

## Transcription options

### Language specification

```python
# Auto-detect language
result = model.transcribe("audio.mp3")

# Specify language (faster)
result = model.transcribe("audio.mp3", language="en")

# Supported: en, es, fr, de, it, pt, ru, ja, ko, zh, and 89 more
```

### Task selection

```python
# Transcription (default)
result = model.transcribe("audio.mp3", task="transcribe")

# Translation to English
result = model.transcribe("spanish.mp3", task="translate")
# Input: Spanish audio → Output: English text
```

### Initial prompt

```python
# Improve accuracy with context
result = model.transcribe(
    "audio.mp3",
    initial_prompt="This is a technical podcast about machine learning and AI."
)

# Helps with:
# - Technical terms
# - Proper nouns
# - Domain-specific vocabulary
```

### Timestamps

```python
# Word-level timestamps
result = model.transcribe("audio.mp3", word_timestamps=True)

for segment in result["segments"]:
    for word in segment["words"]:
        print(f"{word['word']} ({word['start']:.2f}s - {word['end']:.2f}s)")
```

### Temperature fallback

```python
# Retry with different temperatures if confidence low
result = model.transcribe(
    "audio.mp3",
    temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
)
```

## Command line usage

```bash
# Basic transcription
whisper audio.mp3

# Specify model
whisper audio.mp3 --model turbo

# Output formats
whisper audio.mp3 --output_format txt     # Plain text
whisper audio.mp3 --output_format srt     # Subtitles
whisper audio.mp3 --output_format vtt     # WebVTT
whisper audio.mp3 --output_format json    # JSON with timestamps

# Language
whisper audio.mp3 --language Spanish

# Translation
whisper spanish.mp3 --task translate
```

## Batch processing

```python
import os

audio_files = ["file1.mp3", "file2.mp3", "file3.mp3"]

for audio_file in audio_files:
    print(f"Transcribing {audio_file}...")
    result = model.transcribe(audio_file)

    # Save to file
    output_file = audio_file.replace(".mp3", ".txt")
    with open(output_file, "w") as f:
        f.write(result["text"])
```

## Local GPU transcription (faster-whisper) — preferred for local files

faster-whisper (CTranslate2) is ~4x faster than openai-whisper and runs large-v3-turbo on a 4 GB GPU with int8. Prefer it over openai-whisper for any local file on this machine.

```bash
# Isolated venv (system python may lack wheels)
python3 -m venv fwvenv && fwvenv/bin/pip install -q faster-whisper numpy
```

```python
from faster_whisper import WhisperModel

# int8 keeps large-v3-turbo inside 4 GB VRAM; falls back to cpu/int8 gracefully
try:
    model = WhisperModel("large-v3-turbo", device="cuda", compute_type="int8")
except Exception:
    model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")

segments, info = model.transcribe(audio, vad_filter=True, beam_size=5)
# segments is a lazy generator; iterate once, write each line as it arrives
for s in segments:
    print(f"[{fmt(s.start)} - {fmt(s.end)}] {s.text}")
```

Measured: ~61 min of audio in ~4.5 min on RTX 3050 4 GB (large-v3-turbo, cuda int8).

### Pitfall: file-path decode breaks on newer PyAV

faster-whisper decodes file paths through PyAV; when PyAV's `av.open()` signature drifts (e.g. a removed `metadata_errors` kwarg), `model.transcribe("file.m4a")` dies with `TypeError` before any audio is read. Don't chase av version pins (older wheels may not exist for the current Python) — bypass the broken decode: pre-decode with ffmpeg and pass raw samples instead. `transcribe()` accepts a float32 numpy array directly.

```bash
ffmpeg -y -i input.m4a -ar 16000 -ac 1 -c:a pcm_s16le audio16k.wav
```

```python
import wave, numpy as np

def load_wav16k(path):
    with wave.open(path, "rb") as w:
        assert w.getframerate() == 16000 and w.getnchannels() == 1
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return data.astype(np.float32) / 32768.0

segments, info = model.transcribe(load_wav16k("audio16k.wav"), vad_filter=True, beam_size=5)
```

### Pitfall: full-length encode blows RAM on long audio (chunk it, run in foreground)

A single `transcribe()` pass materializes encoder states for the WHOLE spectrogram (~3 GB for 2h of audio) and gets OOM-killed in Hermes background terminal workers (they live in a ~4 GB memory cgroup, oom_score_adj 200, SIGKILL; `dmesg` shows `oom_memcg=hermes-worker-*.scope`). Don't run long transcriptions as one background job. Recipe (measured: 2h audio in 321s wall on RTX 3050 4GB, large-v3-turbo cuda int8, ~18x realtime):

1. Free VRAM first if Ollama holds it: `ollama stop --all` (llama-server unloads on idle, auto-reloads on next request).
2. Pre-decode to 16k wav once (also dodges the PyAV pitfall above), then slice ~15 min chunks with `wave` module reads (offset + nframes), transcribe 2-4 chunks per FOREGROUND terminal call (well under the per-call time ceiling; RAM per chunk stays ~1-2 GB).
3. Global timestamp = chunk_offset + s.start; append header + lines to the output file per call so progress survives.

Note: `background=true` + `process_manage(action='wait')` is unreliable on this harness (wait clamps to 180s and the process gets SIGKILLed at the clamp; `setsid/nohup` wrappers are rejected by the terminal tool) - foreground chunked calls are the reliable path.

### Transcript deliverable format

Write `[HH:MM:SS - HH:MM:SS] text` per segment with a short header (source, detected language + probability), saved next to the source in `~/Downloads`. `info.language` / `info.language_probability` are reported from the run — record them, don't re-derive. Code-switched audio (e.g. Taglish) detects as the dominant language with high confidence; keep the segments in the original language and offer translation/diarization/prose cleanup as follow-ups instead of doing them unasked.

### Distilling transcripts into reusable notes

When the ask is "notes that apply generally / what did the panelists actually say" rather than a raw transcript: strip project-specific facts, generalize to roles, organize by theme, and attach verbatim timestamped quotes under each lesson. Full recipe and pitfalls in `references/distill-and-quote.md`.

## GPU acceleration

```python
import whisper

# Automatically uses GPU if available
model = whisper.load_model("turbo")

# Force CPU
model = whisper.load_model("turbo", device="cpu")

# Force GPU
model = whisper.load_model("turbo", device="cuda")

# 10-20× faster on GPU
```

## Integration with other tools

### Subtitle generation

```bash
# Generate SRT subtitles
whisper video.mp4 --output_format srt --language English

# Output: video.srt
```

### With LangChain

```python
from langchain.document_loaders import WhisperTranscriptionLoader

loader = WhisperTranscriptionLoader(file_path="audio.mp3")
docs = loader.load()

# Use transcription in RAG
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

vectorstore = Chroma.from_documents(docs, OpenAIEmbeddings())
```

### Extract audio from video

```bash
# Use ffmpeg to extract audio
ffmpeg -i video.mp4 -vn -acodec pcm_s16le audio.wav

# Then transcribe
whisper audio.wav
```

## Best practices

1. **Use turbo model** - Best speed/quality for English
2. **Specify language** - Faster than auto-detect
3. **Add initial prompt** - Improves technical terms
4. **Use GPU** - 10-20× faster
5. **Batch process** - More efficient
6. **Convert to WAV** - Better compatibility
7. **Split long audio** - <30 min chunks
8. **Check language support** - Quality varies by language
9. **Use faster-whisper** - 4× faster than openai-whisper
10. **Monitor VRAM** - Scale model size to hardware

## Performance

| Model | Real-time factor (CPU) | Real-time factor (GPU) |
|-------|------------------------|------------------------|
| tiny | ~0.32 | ~0.01 |
| base | ~0.16 | ~0.01 |
| turbo | ~0.08 | ~0.01 |
| large | ~1.0 | ~0.05 |

*Real-time factor: 0.1 = 10× faster than real-time*

## Language support

Top-supported languages:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Korean (ko)
- Chinese (zh)

Full list: 99 languages total

## Limitations

1. **Hallucinations** - May repeat or invent text
2. **Long-form accuracy** - Degrades on >30 min audio
3. **Speaker identification** - No diarization
4. **Accents** - Quality varies
5. **Background noise** - Can affect accuracy
6. **Real-time latency** - Not suitable for live captioning

## Resources

- **GitHub**: https://github.com/openai/whisper ⭐ 72,900+
- **Paper**: https://arxiv.org/abs/2212.04356
- **Model Card**: https://github.com/openai/whisper/blob/main/model-card.md
- **Colab**: Available in repo
- **License**: MIT


