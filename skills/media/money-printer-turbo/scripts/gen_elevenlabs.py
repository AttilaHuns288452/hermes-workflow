#!/usr/bin/env python3
"""
gen_elevenlabs.py — Generate premium ElevenLabs audio for MoneyPrinterTurbo.
Uses Adam voice (pNInz6obpgDQGcFmaJgB) with eleven_flash_v2_5 model (free tier compatible).
Outputs: voice-samples/elevenlabs_sophisticated.mp3
"""

import requests, json, os, sys, subprocess

# --- CONFIG ---
SCRIPT = """What if the wealthiest person you know... isn't the one with the highest salary?

There is a quiet pattern among people who build generational wealth. 

They do not talk about money. They talk about ownership.

A lawyer making five hundred thousand a year leases a BMW. 
A plumber making eighty thousand owns the building his shop sits in.

Twenty years later... the plumber's grandchildren inherit the building. 
The lawyer's grandchildren inherit the lease payments.

This is not about income. It is about what you DO with income.

Robert Kiyosaki said it thirty years ago. 
Rich people acquire assets. The middle class acquires liabilities they THINK are assets.

Your house? Liability. 
Your 401k match? Asset. 
That rental property? Asset. 
The car you finance? Liability.

Here is what nobody tells you: 
Every dollar you spend... votes for the person you are becoming.

The question is not can I afford this?
The question is... does this make me an owner... or a renter?

Most people choose renter. Every single day. Without realizing it.

What did you choose today?"""

VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Adam
MODEL_ID = "eleven_flash_v2_5"     # Free tier compatible
VOICE_SETTINGS = {
    "stability": 0.5,
    "similarity_boost": 0.75,
    "style": 0.3,
    "use_speaker_boost": True
}
OUT_PATH = "voice-samples/elevenlabs_sophisticated.mp3"
# --- END CONFIG ---

def main():
    # Read API key from file (avoids shell quoting issues)
    key_path = "elevenlabs.key"
    if not os.path.exists(key_path):
        print(f"❌ API key file not found: {key_path}")
        print("   Create it: echo 'sk_xxx' > elevenlabs.key")
        sys.exit(1)
    
    with open(key_path) as f:
        API_KEY = f.read().strip()
    
    if not API_KEY or len(API_KEY) < 20:
        print("❌ Invalid API key in elevenlabs.key")
        sys.exit(1)

    BASE_URL = "https://api.elevenlabs.io/v1"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    
    data = {
        "text": SCRIPT.strip(),
        "model_id": MODEL_ID,
        "voice_settings": VOICE_SETTINGS
    }
    
    url = f"{BASE_URL}/text-to-speech/{VOICE_ID}"
    
    print(f"🎙️  Generating ElevenLabs audio...")
    print(f"   Voice: Adam ({VOICE_ID})")
    print(f"   Model: {MODEL_ID}")
    print(f"   Script: {len(SCRIPT)} chars")
    
    resp = requests.post(url, json=data, headers=headers, timeout=120)
    
    if resp.status_code != 200:
        print(f"❌ ElevenLabs API Error: {resp.status_code}")
        try:
            err = resp.json()
            print(f"   {json.dumps(err, indent=2)}")
        except:
            print(f"   {resp.text[:300]}")
        sys.exit(1)
    
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "wb") as f:
        f.write(resp.content)
    
    size = os.path.getsize(OUT_PATH)
    print(f"✅ Generated: {OUT_PATH} ({size/1024:.0f} KB)")
    
    # Verify duration
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", OUT_PATH],
        capture_output=True, text=True, timeout=10
    )
    dur = float(json.loads(result.stdout)["format"]["duration"])
    print(f"   Duration: {dur:.1f}s")
    print(f"   Chars used: ~{len(SCRIPT)} / 10,000 free tier monthly budget")

if __name__ == "__main__":
    main()