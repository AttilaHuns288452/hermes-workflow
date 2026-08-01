#!/usr/bin/env python3
"""
run_pipeline.py — Run MoneyPrinterTurbo pipeline to materials stage.
Downloads fresh Pexels clips per search term (in script order) + generates Edge TTS audio.
Stops at "materials" to avoid broken final concat. Outputs to storage/tasks/<uuid>/

Usage:
    cd ~/Documents/Projects/MoneyPrinterTurbo
    source .venv/Scripts/activate
    python scripts/run_pipeline.py
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.schema import VideoParams
from app.services import task as tm
from app.utils import utils

# === SOPHISTICATED SCRIPT (Behavioral Finance Psychology) ===
SCRIPT = """What if the wealthiest person you know... isn't the one with the highest salary?

There's a quiet pattern among people who build generational wealth. 

They don't talk about money. They talk about ownership.

A lawyer making five hundred thousand a year leases a BMW. 
A plumber making eighty thousand owns the building his shop sits in.

Twenty years later... the plumber's grandchildren inherit the building. 
The lawyer's grandchildren inherit the lease payments.

This isn't about income. It's about what you DO with income.

Robert Kiyosaki said it thirty years ago. 
Rich people acquire assets. The middle class acquires liabilities they THINK are assets.

Your house? Liability. 
Your 401k match? Asset. 
That rental property? Asset. 
The car you finance? Liability.

Here's what nobody tells you: 
Every dollar you spend... votes for the person you're becoming.

The question isn't "can I afford this?"
The question is... "does this make me an owner... or a renter?"

Most people choose renter. Every single day. Without realizing it.

What did you choose today?"""

# === 17 SEARCH TERMS — ONE PER SCRIPT BEAT (IN ORDER) ===
# These are downloaded in order from Pexels, creating 1:1 visual-audio mapping
TERMS = [
    "wealthy person walking confident",           # Hook
    "generational wealth family legacy",          # Pattern
    "business owner holding keys",                # Ownership
    "lawyer luxury car lease",                    # Lawyer $500k
    "plumber proud building owner",               # Plumber $80k
    "grandfather giving keys to grandchild",      # Grandkids inherit building
    "stressed family paying bills",               # Lawyer grandkids lease
    "decision making crossroads",                 # Income vs action
    "Robert Kiyosaki rich dad poor dad book",     # Kiyosaki authority
    "assets vs liabilities diagram",              # Assets vs liabilities
    "house mortgage liability",                   # House liability
    "401k investment growth",                     # 401k asset
    "rental property passive income",             # Rental asset
    "car financing payment",                      # Car liability
    "voting ballot money metaphor",               # Every dollar votes
    "credit card hesitation",                     # Can I afford
    "fork in road owner vs renter",               # Owner or renter
    # Note: 17 terms (final question "What did you choose today?" uses same clip as #17)
]

def main():
    task_id = utils.get_uuid()
    print(f"🎬 Task: {task_id}")
    print(f"📖 Script: {len(SCRIPT)} chars")
    print(f"🎯 Terms: {len(TERMS)} search terms")
    
    params = VideoParams(
        video_subject="Wealth Building: Owner vs Renter Mindset",
        video_script=SCRIPT,
        video_terms=TERMS,
        video_source="pexels",
        video_count=1,
        video_aspect="9:16",
        voice_name="en-US-ChristopherNeural",  # Edge TTS (will be replaced by ElevenLabs in assembly)
        subtitle_enabled=False,                 # Critical: avoids 3GB Whisper download
    )
    
    # Run pipeline UP TO materials (stop before broken final video concat)
    print("📥 Running pipeline: script → terms → audio → materials...")
    result = tm.start(task_id=task_id, params=params, stop_at="materials")
    
    if result:
        print(f"\n✅ Pipeline stopped at materials stage")
        print(f"   Audio: {result.get('audio_file', 'N/A')}")
        print(f"   Materials downloaded: {len(result.get('materials', []))} clips")
        
        # Save task_id for next step
        with open("last_task_id.txt", "w") as f:
            f.write(task_id)
        
        print(f"\n📝 Task ID saved: {task_id}")
        print("Next: run build_from_pipeline.py (uses Edge TTS audio)")
        print("       OR build_elevenlabs.py (uses ElevenLabs audio from gen_elevenlabs.py)")
    else:
        print("❌ Pipeline failed")
        sys.exit(1)

if __name__ == "__main__":
    main()