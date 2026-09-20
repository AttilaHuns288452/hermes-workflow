#!/usr/bin/env python3
"""Query the chat model's native vision with local images.
Usage: python3 vlm_query.py IMG1 [IMG2 ...] "prompt" [max_tokens]
Key from XKIRO_API_KEY env or ~/.hermes/.env. One image per request;
retries the next image (and downscale) when a response comes back empty."""
import base64, json, os, sys, urllib.request
from pathlib import Path

MODEL = "z-ai/glm-5.3-flash"
ENDPOINT = "https://api.xkiro.com/v1/chat/completions"

def load_key():
    k = os.environ.get("XKIRO_API_KEY")
    if k: return k
    for p in [Path.home()/".hermes"/".env", Path.home()/".env"]:
        if p.exists():
            for line in p.read_text().splitlines():
                if line.startswith("XKIRO_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("no XKIRO_API_KEY in env or ~/.hermes/.env")

def prep(path):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im.thumbnail((1100, 1100))
    out = Path("/tmp") / f"vlm_{Path(path).stem}.jpg"
    im.save(out, quality=88)
    return out

def ask(image, prompt, max_tokens):
    b64 = base64.b64encode(Path(image).read_bytes()).decode()
    body = json.dumps({"model": MODEL, "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}]}).encode()
    req = urllib.request.Request(ENDPOINT, data=body, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + load_key(),
        # WAF rejects header-less clients with 403 code 1010
        "User-Agent": "hermes-agent/1.0 (python-urllib; vlm-query)",
        "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())["choices"][0]["message"].get("content") or ""

def main():
    args = sys.argv[1:]
    max_tokens = 1600
    if args and args[-1].isdigit():
        max_tokens = int(args.pop())
    paths = [a for a in args if Path(a).exists()]
    prompt = " ".join(a for a in args if a not in paths)
    if not paths or not prompt:
        sys.exit('usage: vlm_query.py IMG... "prompt" [max_tokens]')
    for i, p in enumerate(paths):
        try:
            out = ask(prep(p), prompt, max_tokens)
        except urllib.error.HTTPError as e:
            out = ""
            if e.code == 402:
                sys.exit("402 wallet empty — fall back to pixel-scan QA")
            print(f"HTTP {e.code} on image {i+1}", file=sys.stderr)
        if out:
            print(out)
            return
        print(f"[empty response on image {i+1}; retrying next]", file=sys.stderr)
    sys.exit("all vision calls returned empty — try fewer/smaller images")

if __name__ == "__main__":
    main()
