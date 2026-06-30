# Synthesized Sound Effects (Web Audio API Fallback)

When external MP3 URLs are blocked (CORS, ad-blockers, slow network), fall back to synthesized sounds using the Web Audio API.

## "Baka!" Sound — Two-Syllable Voice Simulation

Synthesizes a harsh "BA-KA!" using oscillators + noise burst:

```typescript
function playBakaSynth() {
  try {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    const now = audioContext.currentTime;

    const playTone = (
      startTime: number, freq: number, endFreq: number,
      duration: number, type: OscillatorType = 'sawtooth', volume: number = 0.3
    ) => {
      const osc = audioContext.createOscillator();
      const gain = audioContext.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, startTime);
      osc.frequency.exponentialRampToValueAtTime(endFreq, startTime + duration);
      gain.gain.setValueAtTime(volume, startTime);
      gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
      osc.connect(gain);
      gain.connect(audioContext.destination);
      osc.start(startTime);
      osc.stop(startTime + duration);
    };

    // "BA" — lower, more percussive
    playTone(now, 180, 220, 0.12, 'sawtooth', 0.35);
    playTone(now + 0.08, 140, 160, 0.1, 'triangle', 0.25);

    // "KA!" — higher, sharper, faster
    playTone(now + 0.22, 350, 380, 0.08, 'square', 0.3);
    playTone(now + 0.26, 330, 400, 0.12, 'sawtooth', 0.35);

    // Noise burst for the "K" consonant
    const bufferSize = audioContext.sampleRate * 0.08;
    const buffer = audioContext.createBuffer(1, bufferSize, audioContext.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufferSize * 0.3));
    }
    const noise = audioContext.createBufferSource();
    const noiseGain = audioContext.createGain();
    noise.buffer = buffer;
    noiseGain.gain.setValueAtTime(0.15, now + 0.22);
    noiseGain.gain.exponentialRampToValueAtTime(0.001, now + 0.28);
    noise.connect(noiseGain);
    noiseGain.connect(audioContext.destination);
    noise.start(now + 0.22);
    noise.stop(now + 0.3);
  } catch (e) {
    // Audio not supported — silently fail
  }
}
```

## Integration with MP3-first Pattern

```typescript
export function playBakaSound() {
  try {
    const audio = new Audio("https://www.myinstants.com/media/sounds/baka-m.mp3");
    audio.volume = 0.6;
    audio.play().catch(() => playBakaSynth());  // fallback if MP3 blocked
  } catch {
    playBakaSynth();
  }
}
```

## Constraints

| Constraint | Notes |
|-----------|-------|
| **User gesture required** | Must be triggered by click/tap. `setTimeout` from non-gesture events fails silently. |
| **Secure context** | Web Audio API requires HTTPS or localhost. |
| **Mobile autoplay** | iOS Safari blocks autoplay of both media elements and AudioContext. Always wrap in try-catch. |
| **Volume** | Keep under 0.5 to avoid startling users. |
