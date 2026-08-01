# ElevenLabs TTS + Caption Generation Workflow

## API Call

Generate narration audio **with** word-level timestamps in a single call:

```
POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps
Headers: xi-api-key, Content-Type: application/json
Body:
{
  "text": "...",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
}
```

Returns JSON with:
- `audio_base64` — base64-encoded MP3 audio
- `alignment.characters` — array of individual characters including spaces
- `alignment.character_start_times_seconds` — float timestamps per character
- `alignment.character_end_times_seconds` — float timestamps per character

## Caption Conversion: Characters → Words

Group successive non-space characters, taking the first char's start and the last char's end:

```python
import json

resp = requests.post(url, headers=headers, json=payload, timeout=60)
data = resp.json()
ali = data["alignment"]
chars = ali["characters"]
starts = ali["character_start_times_seconds"]
ends = ali["character_end_times_seconds"]

words = []
current = ""
start = 0.0
for i, c in enumerate(chars):
    if c == " " or c == "\n":
        if current:
            words.append({
                "word": current,
                "start": start,
                "end": ends[i - 1] if i > 0 else starts[i],
            })
            current = ""
    else:
        if not current:
            start = starts[i]
        current += c
if current:
    words.append({"word": current, "start": start, "end": ends[-1]})

captions = [
    {"word": w["word"], "startMs": round(w["start"] * 1000), "endMs": round(w["end"] * 1000)}
    for w in words
]
```

## Remotion Captions

The `CaptionOverlay` component expects **milliseconds** in `startMs`/`endMs`. ElevenLabs returns seconds — failing to convert causes `NaN` in Sequence `from` prop and a `"from prop must be finite"` error.

## Save Narration MP3 (from base64)

```python
import base64
audio_bytes = base64.b64decode(data["audio_base64"])
with open("assets/audio/narration.mp3", "wb") as f:
    f.write(audio_bytes)
```

## Voice References

| Voice | ID | Best for |
|-------|-----|----------|
| Rachel | `21m00Tcm4TlvDq8ikWAM` | Narration, authoritative |
| Default key path | `~/Documents/Projects/MoneyPrinterTurbo/.elevenlabs_key` | |
