# Vision transcription of slide images

When a deck is image-only, each slide image is transcribed to text with the profile's native vision model, then the transcripts feed the question bank.

## Request shape

- Endpoint: the xKiro OpenAI-compatible endpoint (`https://api.xkiro.com/v1/chat/completions`), model `z-ai/glm-5.3-flash` (the main chat/vision model).
- Image as a base64 data URL: `{type:'image_url', image_url:{url:'data:image/png;base64,...'}}` plus a text turn: "Transcribe this slide completely."
- System prompt: transcribe ONLY slide text — every title, heading, definition, bullet, label, table cell, in reading order, plain lines, no summarizing.
- `temperature: 0`, `max_tokens: 2000`.
- Headers: `Authorization: Bearer <key>` AND a browser-like `User-Agent` — without the UA, Cloudflare rejects with 403 code 1010.

## Key loading

`XKIRO_API_KEY` is declared in `~/.hermes/config.yaml` as a `key_env` reference but is NOT exported into the execute_code kernel. Load it from `~/.hermes/.env` (`XKIRO_API_KEY=...`) inside the script. Never print the key.

## Batch loop (background process)

```python
def call(img, tries=3): ... # backoff 6s*(attempt+1), return 'TRANSCRIBE_FAILED' after 3
for deck in decks:
    path = f'transcripts/{deck}.json'
    done = json.load(open(path)) if exists(path) else {}
    for slide_img in sorted(images):
        n = slide_number(slide_img)
        if str(n) in done and done[str(n)] != 'TRANSCRIBE_FAILED': continue
        done[str(n)] = call(slide_img)
        json.dump(done, open(path,'w'), indent=1)   # checkpoint after EVERY slide
```

- Run it as a background terminal process (`terminal(background=True, notify=True)`), not inside execute_code — the kernel timeout kills in-flight loops; disk checkpoints survive and a rerun fills only missing/FAILED entries.
- Throughput: ~5-10s per slide; a 15-slide deck ≈ 2 min.

## Validation

- After the run, load each deck JSON: slide count must equal image count; flag entries equal to `TRANSCRIBE_FAILED` or shorter than ~40 chars, and re-transcribe just those.
- Two writers on the same checkpoint file corrupt it (concatenated JSON objects) — kill stale processes before reruns; salvage by repeated `json.JSONDecoder.raw_decode` over the file and merging dicts.
- Deck/lecture slide 1 is often decorative cover art — expect garbled or minimal text there and don't force it into the reviewer.
