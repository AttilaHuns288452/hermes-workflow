---
name: python-audio-synthesis
description: >
  Generate audio (background music, sound effects, placeholders) programmatically
  using Python's numpy + wave (stdlib) when external music APIs or download
  sources are blocked. Creates 16-bit stereo WAV files from scratch with chord
  progressions, drum patterns, melodies, ADSR envelopes, and fades.
trigger:
  - "generate background music"
  - "create audio track programmatically"
  - "music source blocked by Cloudflare"
  - "need placeholder audio for video"
  - "royalty-free music download failed"
  - "no API key for music generation"
category: media
stability: production
---

# Python Audio Synthesis

Generate audio files programmatically when web-based music sources (Pixabay,
Mixkit, Joystock, etc.) are behind Cloudflare/CloudFront and cannot be scraped.

## When to Use

- Royalty-free music sites are Cloudflare-blocked and return 403/HTML pages
- No paid music API key is configured (ElevenLabs Music, Suno)
- You need a custom-length track that matches your video duration exactly
- You need a simple placeholder while waiting for API access

## Core Techniques

### 1. Basic Waveform Generation

```python
import numpy as np
import wave

SAMPLE_RATE = 44100

def sine_wave(freq, duration, amplitude=0.3):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return amplitude * np.sin(2 * np.pi * freq * t)
```

### 2. Chord Progressions (I-V-vi-IV Pop Progression)

```python
def note_freq(note_name):
    notes = {'C': -9, 'D': -7, 'E': -5, 'F': -4, 'G': -2, 'A': 0, 'B': 2}
    base = notes.get(note_name[0].upper(), 0)
    octave = int(note_name[-1]) if len(note_name) > 1 else 4
    semitones = base + (octave - 4) * 12
    return 440.0 * (2 ** (semitones / 12.0))

CHORDS = [
    [note_freq('C4'), note_freq('E4'), note_freq('G4')],  # C major
    [note_freq('G3'), note_freq('B3'), note_freq('D4')],  # G major
    [note_freq('A3'), note_freq('C3'), note_freq('E4')],  # A minor
    [note_freq('F3'), note_freq('A3'), note_freq('C4')],  # F major
]
```

### 3. ADSR Envelope (Attack / Decay / Sustain / Release)

Apply to any waveform to avoid clicks and make sounds organic:

```python
def apply_envelope(wave, attack_s=0.05, release_s=0.1):
    env = np.ones_like(wave)
    attack = int(attack_s * SAMPLE_RATE)
    release = int(release_s * SAMPLE_RATE)
    env[:attack] = np.linspace(0, 1, attack)
    env[-release:] = np.linspace(1, 0, release)
    return wave * env
```

### 4. 808-Style Kick Drum

```python
def kick_drum(duration=0.3, amplitude=0.5):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freq = 150 * np.exp(-t * 25) + 40
    wave = np.sin(2 * np.pi * freq * t)
    return amplitude * wave * np.exp(-t * 8)
```

### 5. Hi-Hat (White Noise Burst)

```python
def hihat(duration=0.05, amplitude=0.08):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    noise = np.random.uniform(-1, 1, len(t))
    return amplitude * noise * np.exp(-t * 80)
```

### 6. Melody (Pentatonic or Scale-Based)

```python
MELODY_NOTES = [
    note_freq('C4'), note_freq('E4'), note_freq('G4'), note_freq('A4'),
    note_freq('G4'), note_freq('E4'), note_freq('D4'), note_freq('C4'),
]

def melody_note(freq, duration, amplitude=0.12):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = np.sin(2 * np.pi * freq * t)
    wave += 0.5 * np.sin(2 * np.pi * freq * 2 * t)  # 2nd harmonic
    wave += 0.3 * np.sin(2 * np.pi * freq * 3 * t)  # 3rd harmonic
    return amplitude * wave * np.exp(-t * 3)  # Exponential decay
```

### 7. Stereo WAV Output

```python
def write_stereo_wav(left, right, output_path, sample_rate=SAMPLE_RATE):
    max_val = max(np.max(np.abs(left)), np.max(np.abs(right)))
    if max_val > 0:
        left = left / max_val * 0.7
        right = right / max_val * 0.7

    with wave.open(output_path, 'w') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        left_int = np.int16(left * 32767)
        right_int = np.int16(right * 32767)
        interleaved = np.empty(len(left_int) * 2, dtype=np.int16)
        interleaved[0::2] = left_int
        interleaved[1::2] = right_int
        wf.writeframes(interleaved.tobytes())
```

## Full Composition Template

See `references/bg-music-composition.md` for the complete working script template.

The recommended BPM is 120 (0.5s per beat). The track structure:

| Element | Beats | Description |
|---------|-------|-------------|
| Chord pad | Every 4 beats | Soft synth pad with harmonics, sustains across chord changes |
| Kick | Every beat | 808-style, 0.25s |
| Hi-hat | Off-beats (2,4,6,8) | 0.04s noise burst |
| Clap | Beats 2 and 4 | 0.1s noise burst |
| Bass | Every 2 beats | Root note one octave down from chord |
| Melody | Every 2 beats | Bell-like pentatonic notes |

## Pitfalls

- **Prevent clipping:** Always normalize before writing WAV. Use `max_val` normalization to `0.7` amplitude.
- **Fade in/out:** Apply 0.5s fade-in and 2s fade-out to avoid pops. The fade-out should match your video duration.
- **Stereo interleaving:** numpy's `ravel()` with alternating left/right produces slightly wrong output. Use explicit `empty` + `[0::2]` / `[1::2]` slicing which is frame-accurate.
- **Length calculation:** Compute `TOTAL_SAMPLES = int(SAMPLE_RATE * duration_seconds)` upfront. Slice all arrays to this length.
- **Phase cancellation:** Left and right channels should carry the same content for background music. Only separate for directional effects.
- **Memory:** A 97-second stereo WAV at 44100Hz generates ~17MB. For longer tracks, write in chunks.
- **Directories:** Create the output directory with `Path(parent).mkdir(parents=True, exist_ok=True)` before writing.
- **FileNotFoundError on write:** Python's `wave.open` with `'w'` won't create parent directories. Always create them first.

## Verification

```bash
# Check file type and basic info
file output.wav

# Check duration and format
python -c "
import wave
with wave.open('output.wav') as wf:
    frames = wf.getnframes()
    rate = wf.getframerate()
    channels = wf.getnchannels()
    print(f'{frames/rate:.1f}s, {rate}Hz, {channels}-channel')
"

# Verify playable
ffprobe -v error -show_entries format=duration,format_name output.wav
```

## Alternatives When This Won't Suffice

- **ElevenLabs Music API** (paid) — generates professional tracks from text prompts
- **Suno AI** (paid) — full song generation with vocals
- **Pixabay** (free, Cloudflare) — large library of royalty-free tracks
- **Uppbeat / Mixkit** (free) — curated royalty-free music
- **YouTube Audio Library** (free) — extensive catalog, no attribution needed

## Related Skills

- `songwriting-and-ai-music` — lyric writing and AI music prompts (Suno, etc.)
- `short-video-production` — full video production with tools
