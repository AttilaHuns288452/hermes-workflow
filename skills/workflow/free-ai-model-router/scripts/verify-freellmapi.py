#!/usr/bin/env python3
"""Verify FreeLLMAPI setup and model availability."""

import requests
import sys

def verify_freellmapi(base_url="http://localhost:3001", api_key=None):
    """Verify FreeLLMAPI is running and check model availability."""
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    print(f"🔍 Checking FreeLLMAPI at {base_url}/v1")
    
    # 1. Health check
    try:
        resp = requests.get(f"{base_url}/v1/models", headers=headers, timeout=5)
        if resp.status_code == 401:
            print("❌ Invalid API key")
            return False
        elif resp.status_code != 200:
            print(f"❌ Server error: {resp.status_code} - {resp.text}")
            return False
        data = resp.json()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect - is FreeLLMAPI running on port 3001?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    models = data.get("data", [])
    print(f"✅ Connected - {len(models)} models in catalog")
    
    # 2. Count available models
    available = [m for m in models if m.get("available")]
    unavailable = [m for m in models if not m.get("available")]
    
    print(f"   Available: {len(available)}")
    print(f"   Need keys: {len(unavailable)}")
    
    if available:
        print("\n✅ Available models:")
        for m in available[:10]:
            print(f"   - {m['id']} ({m.get('owned_by', 'unknown')})")
        if len(available) > 10:
            print(f"   ... and {len(available) - 10} more")
    else:
        print("\n⚠️  NO MODELS AVAILABLE - add upstream provider keys via dashboard")
        print("   Open http://localhost:5173 → API Keys → add OpenRouter, Groq, NVIDIA, etc.")
    
    # 3. Show unavailable reasons
    reasons = {}
    for m in unavailable:
        reason = m.get("unavailable_reason", "unknown")
        reasons[reason] = reasons.get(reason, 0) + 1
    
    if reasons:
        print("\n📋 Unavailable reasons:")
        for reason, count in sorted(reasons.items(), key=lambda x: -x[1]):
            print(f"   {reason}: {count} models")
    
    return len(available) > 0

def test_chat(base_url="http://localhost:3001", api_key=None, model="auto"):
    """Test a chat completion."""
    if not api_key:
        print("❌ No API key provided")
        return False
    
    print(f"\n🤖 Testing chat with model: {model}")
    try:
        resp = requests.post(
            f"{base_url}/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [{"role": "user", "content": "Say OK"}], "max_tokens": 10},
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            print(f"✅ Response: {content[:50]}...")
            return True
        else:
            print(f"❌ Error: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Verify FreeLLMAPI setup")
    parser.add_argument("--url", default="http://localhost:3001", help="FreeLLMAPI base URL")
    parser.add_argument("--key", help="Unified API key (freellmapi-...)")
    parser.add_argument("--test-chat", action="store_true", help="Test chat completion")
    parser.add_argument("--model", default="auto", help="Model to test")
    args = parser.parse_args()
    
    ok = verify_freellmapi(args.url, args.key)
    
    if args.test_chat and args.key:
        test_chat(args.url, args.key, args.model)
    
    sys.exit(0 if ok else 1)