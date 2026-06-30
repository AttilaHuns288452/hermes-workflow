#!/usr/bin/env python3
"""Generate a simple motivational/inspirational background music WAV file.
Uses a I-V-vi-IV (C-G-Am-F) chord progression at 120 BPM.
Outputs stereo 44100Hz 16-bit WAV.

Usage:
    python python-bg-music-generator.py [duration_seconds] [output_path]

    duration_seconds: total length in seconds (default: 97)
    output_path: where to save the WAV (default: bg_music.wav)

Requires: numpy (pip install numpy)
"""

import numpy as np
import wave
import sys

SAMPLE_RATE = 44100
AMPLITUDE = 0.25

def sine_wave(freq, duration, amp=AMPLITUDE):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)

def square_wave(freq, duration, amp=0.08):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return (amp * np.sign(np.sin(2 * np.pi * freq * t))).astype(np.float32)

def main():
    DURATION = int(sys.argv[1]) if len(sys.argv) > 1 else 97
    OUTPUT = sys.argv[2] if len(sys.argv) > 2 else "bg_music.wav"
    CHORD_DURATION = 8  # 2 bars per chord
    TOTAL_BARS = int(np.ceil(DURATION / CHORD_DURATION))
    DURATION = TOTAL_BARS * CHORD_DURATION  # round up

    print(f"Generating {DURATION}s of music → {OUTPUT}")

    # I-V-vi-IV chord progression
    chords = [
        (261.63, 329.63, 392.00),  # C major (I)
        (392.00, 493.88, 587.33),  # G major (V)
        (220.00, 261.63, 329.63),  # A minor (vi)
        (349.23, 440.00, 523.25),  # F major (IV)
    ]

    audio = np.zeros(int(SAMPLE_RATE * DURATION), dtype=np.float32)

    for i in range(TOTAL_BARS):
        chord = chords[i % len(chords)]
        t_start = i * CHORD_DURATION
        t_end = t_start + CHORD_DURATION

        # Sustained pad
        pad = (sine_wave(chord[0], CHORD_DURATION) +
               sine_wave(chord[1], CHORD_DURATION) +
               sine_wave(chord[2], CHORD_DURATION)) * 0.3

        s = int(t_start * SAMPLE_RATE)
        e = int(t_end * SAMPLE_RATE)
        audio[s:e] += pad[:e-s]

        # Kick drum on every beat
        for beat in range(CHORD_DURATION):
            b = int((t_start + beat) * SAMPLE_RATE)
            if b < len(audio):
                end = min(b + 2000, len(audio))
                kick = square_wave(60, 0.045, 0.12)
                audio[b:end] += kick[:end-b]

    # Normalize
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.5

    # Write stereo WAV
    with wave.open(OUTPUT, "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        audio_int16 = (audio * 32767).astype(np.int16)
        stereo = np.zeros((len(audio_int16), 2), dtype=np.int16)
        stereo[:, 0] = audio_int16
        stereo[:, 1] = audio_int16
        wf.writeframes(stereo.tobytes())

    print("Done!")

if __name__ == "__main__":
    main()
