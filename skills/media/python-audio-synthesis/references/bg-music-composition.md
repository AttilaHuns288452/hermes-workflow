# Background Music Composition Reference

Full working script for generating a 97-second motivational/inspirational background
music track. Generate longer by adjusting `TOTAL_BEATS` and `TOTAL_SAMPLES`.

## Complete Script

```python
"""Generate background music track programmatically.
Chord progression: C - G - Am - F (I-V-vi-IV)
Tempo: 120 BPM
"""

import numpy as np
import wave
from pathlib import Path

SAMPLE_RATE = 44100
BPM = 120
BEAT_DURATION = 60.0 / BPM  # 0.5 seconds
TARGET_DURATION = 97  # seconds (pad slightly longer than video)
TOTAL_SAMPLES = int(SAMPLE_RATE * TARGET_DURATION)
beat_samples = int(SAMPLE_RATE * BEAT_DURATION)
TOTAL_BEATS = int(TARGET_DURATION / BEAT_DURATION) + 8

# ── Pitch Helpers ──────────────────────────────────────────────

def note_freq(note_name):
    notes = {'C': -9, 'D': -7, 'E': -5, 'F': -4, 'G': -2, 'A': 0, 'B': 2}
    base = notes.get(note_name[0].upper(), 0)
    octave = int(note_name[-1]) if len(note_name) > 1 else 4
    semitones = base + (octave - 4) * 12
    return 440.0 * (2 ** (semitones / 12.0))

# ── Chord Voicings ────────────────────────────────────────────

CHORDS = [
    [note_freq('C4'), note_freq('E4'), note_freq('G4')],   # C major
    [note_freq('G3'), note_freq('B3'), note_freq('D4')],   # G major
    [note_freq('A3'), note_freq('C4'), note_freq('E4')],   # A minor
    [note_freq('F3'), note_freq('A3'), note_freq('C4')],   # F major
]

# ── Sound Generators ──────────────────────────────────────────

def soft_pad(freq, duration, amplitude=0.15):
    """Soft synth pad — fundamental + two harmonics, ADSR envelope."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = (np.sin(2 * np.pi * freq * t)
            + 0.4 * np.sin(2 * np.pi * freq * 2 * t)
            + 0.2 * np.sin(2 * np.pi * freq * 3 * t))
    attack = int(0.05 * SAMPLE_RATE)
    release = int(0.1 * SAMPLE_RATE)
    env = np.ones_like(wave)
    env[:attack] = np.linspace(0, 1, attack)
    env[-release:] = np.linspace(1, 0, release)
    return amplitude * wave * env

def kick(duration=0.25, amplitude=0.35):
    """808-style kick — exponential frequency sweep."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freq = 150 * np.exp(-t * 25) + 40
    return amplitude * np.sin(2 * np.pi * freq * t) * np.exp(-t * 8)

def hihat(duration=0.04, amplitude=0.06):
    """White-noise burst with fast decay."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return amplitude * np.random.uniform(-1, 1, len(t)) * np.exp(-t * 80)

def clap(duration=0.1, amplitude=0.1):
    """Noise burst with medium decay."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return amplitude * np.random.uniform(-1, 1, len(t)) * np.exp(-t * 20)

def bell(freq, duration, amplitude=0.1):
    """Bell-like melody note — harmonics with exponential decay."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = (np.sin(2 * np.pi * freq * t)
            + 0.5 * np.sin(2 * np.pi * freq * 2 * t)
            + 0.3 * np.sin(2 * np.pi * freq * 3 * t))
    return amplitude * wave * np.exp(-t * 3)

# ── Melody Phrase (C major pentatonic) ────────────────────────

MELODY = [
    note_freq('C4'), note_freq('E4'), note_freq('G4'), note_freq('A4'),
    note_freq('G4'), note_freq('E4'), note_freq('D4'), note_freq('C4'),
    note_freq('E4'), note_freq('G4'), note_freq('B4'), note_freq('C5'),
    note_freq('B4'), note_freq('G4'), note_freq('E4'), note_freq('D4'),
]

# ── Build the Track ───────────────────────────────────────────

left = np.zeros(TOTAL_SAMPLES)
right = np.zeros(TOTAL_SAMPLES)

for beat in range(TOTAL_BEATS):
    start = beat * beat_samples
    if start >= TOTAL_SAMPLES - beat_samples:
        break

    chord_idx = (beat // 4) % len(CHORDS)
    chord = CHORDS[chord_idx]

    # Pad (sustains for 4 beats)
    for freq in chord:
        n = soft_pad(freq, BEAT_DURATION * 4, 0.08)
        end = min(start + len(n), TOTAL_SAMPLES)
        sl = end - start
        left[start:end] += n[:sl]
        right[start:end] += n[:sl]

    # Bass (root, one octave down)
    bass = soft_pad(chord[0] / 2, BEAT_DURATION * 2, 0.12)
    end = min(start + len(bass), TOTAL_SAMPLES)
    sl = end - start
    left[start:end] += bass[:sl]
    right[start:end] += bass[:sl]

    # Kick on every beat
    k = kick()
    end = min(start + len(k), TOTAL_SAMPLES)
    sl = end - start
    left[start:end] += k[:sl]
    right[start:end] += k[:sl]

    # Hi-hat on off-beats
    if beat % 2 == 1:
        h = hihat()
        end = min(start + len(h), TOTAL_SAMPLES)
        sl = end - start
        left[start:end] += h[:sl]
        right[start:end] += h[:sl]

    # Clap on beats 2 and 4
    if beat % 4 in (1, 3):
        c = clap()
        end = min(start + len(c), TOTAL_SAMPLES)
        sl = end - start
        left[start:end] += c[:sl]
        right[start:end] += c[:sl]

    # Melody on every other beat
    if beat % 2 == 0:
        m = bell(MELODY[beat % len(MELODY)], BEAT_DURATION * 2, 0.1)
        end = min(start + len(m), TOTAL_SAMPLES)
        sl = end - start
        left[start:end] += m[:sl]
        right[start:end] += m[:sl]

# ── Master Bus ────────────────────────────────────────────────

max_val = max(np.max(np.abs(left)), np.max(np.abs(right)))
if max_val > 0:
    left = left / max_val * 0.7
    right = right / max_val * 0.7

# Fade in/out
fade_in = int(0.5 * SAMPLE_RATE)
fade_out = int(2.0 * SAMPLE_RATE)
left[:fade_in] *= np.linspace(0, 1, fade_in)
right[:fade_in] *= np.linspace(0, 1, fade_in)
left[-fade_out:] *= np.linspace(1, 0, fade_out)
right[-fade_out:] *= np.linspace(1, 0, fade_out)

# ── Write WAV ─────────────────────────────────────────────────

output_path = "bg_music.wav"
with wave.open(output_path, 'w') as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    li = np.int16(left * 32767)
    ri = np.int16(right * 32767)
    interleaved = np.empty(len(li) * 2, dtype=np.int16)
    interleaved[0::2] = li
    interleaved[1::2] = ri
    wf.writeframes(interleaved.tobytes())

actual = len(left) / SAMPLE_RATE
file_size = Path(output_path).stat().st_size / 1e6
print(f"Generated: {output_path}")
print(f"Duration: {actual:.1f}s  |  Size: {file_size:.1f} MB")
print(f"Format: 16-bit Stereo 44100Hz WAV")
```

## Quick-Start (Short Version)

For a test/placeholder track, strip down to just pads and a kick:

```python
import numpy as np, wave
SR, DUR = 44100, 10  # 10 seconds
t = np.linspace(0, DUR, SR * DUR, False)
wave = 0.3 * (np.sin(2*np.pi*261.63*t) + 0.5*np.sin(2*np.pi*523.25*t))
fade = int(0.1 * SR)
wave[:fade] *= np.linspace(0, 1, fade)
wave[-fade:] *= np.linspace(1, 0, fade)
with wave.open('test.wav', 'w') as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes(np.int16(wave * 32767).tobytes())
print("test.wav written")
```

## Customization Ideas

| Change | How |
|--------|-----|
| Change key | Shift all note_freq calls up/down by N semitones |
| Change BPM | Adjust BPM constant (default 120) |
| Add breakdown | Pause drums for 8 beats in the middle |
| Build tension | Increase hi-hat frequency or add snare rolls before the climax |
| Different genre | Replace chord progression (e.g., ii-V-I for jazz, I-V-vi for pop) |
| Lo-fi feel | Add low-pass filter, slow tape wow, vinyl crackle noise |
