# ElevenLabs Free Tier Integration for MoneyPrinterTurbo

> How to use ElevenLabs' **free tier** (10k chars/mo) with MoneyPrinterTurbo for premium "Skeleton Socrates" voice quality without paying.

---

## Critical: Model Selection

**Free tier model restrictions (as of 2025):**
| Model | Free Tier | Notes |
|-------|-----------|-------|
| `eleven_monolingual_v1` | ❌ Deprecated, removed | Do not use |
| `eleven_multilingual_v1` | ❌ Deprecated, removed | Do not use |
| **`eleven_flash_v2_5`** | ✅ **Available** | Fast, lower latency, free tier compatible |
| `eleven_multilingual_v2` | ✅ Available | Higher quality, more chars per request |

**Use `eleven_flash_v2_5` for all free-tier generation.**

---

## Voice ID Reference

| Voice | Voice ID | Style | Best For |
|-------|----------|-------|----------|
| **Adam** | `pNInz6obpgDQGcFmaJgB` | Deep, authoritative, ominous | **Skeleton Socrates / financial storytelling** |
| Daniel | `onwK4e9ZLuTAKqWW03F9` | British, authoritative | Prestige / documentary |
| Roger | `CwhRBWXzGAHq8TQ4Fs17` | Warm, deep | Inspiring / motivational |
| Liam | `TX3LPaxmHKxFdv7VOQHJ` | Irish, storyteller | Emotional / narrative |
| Brian | `nPczCjzI2devNBz1zQrb` | Balanced, versatile | General purpose |

**Default for this niche: Adam (`pNInz6obpgDQGcFmaJgB`)**

---

## Optimal Voice Settings for Narration

```json
{
  "stability": 0.5,
  "similarity_boost": 0.75,
  "style": 0.3,
  "use_speaker_boost": true
}
```

- **Stability 0.5**: Natural variation (not robotic)
- **Similarity 0.75**: Faithful to voice character
- **Style 0.3**: Slight expressiveness (not flat)
- **Speaker boost**: Enhanced quality

---

## API Key Storage Pattern (Windows Git-Bash Compatible)

**Problem:** API keys with special characters cause shell escaping issues.

**Solution:** Store key in a file, read at runtime.

```bash
# One-time setup
echo "sk_7a78545e7feb46db4156b587178831edb1cbe27768737545" > elevenlabs.key

# In Python scripts:
with open('elevenlabs.key') as f:
    API_KEY = f.read().strip()
```

Avoids: quoting issues, history exposure, clipboard truncation.

---

## Python Audio Generation Script

See `scripts/gen_elevenlabs.py` — generates full script audio with optimal settings.

```python
import requests, json, os

with open('elevenlabs.key') as f:
    API_KEY = f.read().strip()

BASE_URL = "https://api.elevenlabs.io/v1"
headers = {"xi-api-key": API_KEY, "Content-Type": "application/json"}

script = """Your sophisticated script here..."""

voice_id = "pNInz6obpgDQGcFmaJgB"  # Adam
data = {
    "text": script.strip(),
    "model_id": "eleven_flash_v2_5",  # CRITICAL for free tier
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.3,
        "use_speaker_boost": True
    }
}

resp = requests.post(f"{BASE_URL}/text-to-speech/{voice_id}", json=data, headers=headers, timeout=90)
if resp.status_code == 200:
    with open("voice-samples/elevenlabs_sophisticated.mp3", "wb") as f:
        f.write(resp.content)
```

---

## Integration with MoneyPrinterTurbo

### Option A: config.toml (if CLI supported)
```toml
tts_provider = "elevenlabs"
elevenlabs_api_key = "sk_..."
elevenlabs_voice_id = "pNInz6obpgDQGcFmaJgB"
elevenlabs_model_id = "eleven_flash_v2_5"
```
*Note: Verify your MoneyPrinterTurbo version supports `eleven_flash_v2_5` in config.*

### Option B: Direct Generation + Pipeline Assembly (RECOMMENDED)

**Why:** Bypasses any CLI config issues, gives full control over voice settings, guarantees free-tier model.

```bash
# 1. Generate ElevenLabs audio
python scripts/gen_elevenlabs.py

# 2. Run MoneyPrinterTurbo pipeline to get fresh footage
python scripts/run_pipeline.py

# 3. Assemble with ElevenLabs audio
python scripts/build_elevenlabs.py
```

---

## Character Budget (Free Tier: 10,000 chars/mo)

| Video Length | Script Chars | Videos/Month |
|--------------|--------------|--------------|
| 60s | ~900 chars | ~11 |
| 90s | ~1,350 chars | ~7 |
| 120s | ~1,800 chars | ~5 |

**Optimization:** Keep scripts ~900-1,100 chars for 60-90s videos to maximize monthly output.

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `401 invalid_api_key` | Key not read correctly | Use file-read pattern, verify `cat elevenlabs.key` |
| `401 subscription_required` | Wrong model | Use `eleven_flash_v2_5` (not `eleven_monolingual_v1`) |
| `401 missing_permissions` | API key scope | Free tier keys may not have `voices_read` — skip voice listing, use known voice IDs |
| `429 rate_limit` | Too many requests | Add delay between requests, batch generation |

---

## Test Script

```bash
# Quick voice test (Adam, 23 chars = ~0.02% of monthly budget)
python -c "
import requests, json, os
with open('elevenlabs.key') as f: k=f.read().strip()
r=requests.post('https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB',
    headers={'xi-api-key':k,'Content-Type':'application/json'},
    json={'text':'Testing ElevenLabs Adam voice.','model_id':'eleven_flash_v2_5'})
print('Status:', r.status_code)
if r.status_code==200:
    open('test.mp3','wb').write(r.content)
    print('OK: test.mp3')
"
```