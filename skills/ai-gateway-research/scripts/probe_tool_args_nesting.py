#!/usr/bin/env python3
"""Probe a gateway for tool-argument mangling across nesting shapes.

Sends one FORCED tool call per shape with a sentinel value and diffs the
returned function arguments against it. A nested object arriving as {} is
destroyed in the provider's function-call serialization — unrepairable
downstream; mitigate at the schema layer (advertise the nested object as a
JSON-encoded string, parse it back at dispatch).

Usage:
  probe_tool_args_nesting.py --models openai/gpt-6.1-terra,z-ai/glm-5.3-flash \
      [--base-url https://api.xkiro.com/v1] [--key-env XKIRO_API_KEY]

Verdicts: OK = sentinel intact · DROP = nested value lost · NOCALL / BADJSON /
ERROR = model or transport failure (not a mangling verdict).
"""
import argparse
import json
import os
import sys
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
SENT = "sent7l"

# name: (parameters schema, user instruction, checker(args) -> bool)
SHAPES = {
    "flat array-of-objects": (
        {"type": "object", "properties": {"ops": {"type": "array", "items": {
            "type": "object", "properties": {"k": {"type": "string"}}, "required": ["k"]}}},
         "required": ["ops"]},
        'Call t with ops=[{"k": "sent7l"}].',
        lambda a: isinstance(a.get("ops"), list) and bool(a["ops"]) and a["ops"][0].get("k") == SENT,
    ),
    "object-in-array-item": (
        {"type": "object", "properties": {"calls": {"type": "array", "items": {
            "type": "object", "properties": {"name": {"type": "string"}, "arguments": {"type": "object"}},
            "required": ["name", "arguments"]}}},
         "required": ["calls"]},
        'Call t with calls=[{"name": "n", "arguments": {"q": "sent7l"}}].',
        lambda a: bool(a.get("calls")) and a["calls"][0].get("arguments", {}).get("q") == SENT,
    ),
    "object-in-object": (
        {"type": "object", "properties": {"spec": {"type": "object", "properties": {
            "inner": {"type": "object", "properties": {"q": {"type": "string"}}, "required": ["q"]}},
            "required": ["inner"]}},
         "required": ["spec"]},
        'Call t with spec={"inner": {"q": "sent7l"}}.',
        lambda a: a.get("spec", {}).get("inner", {}).get("q") == SENT,
    ),
    "string-in-array": (
        {"type": "object", "properties": {"tags": {"type": "array", "items": {"type": "string"}}},
         "required": ["tags"]},
        'Call t with tags=["sent7l"].',
        lambda a: isinstance(a.get("tags"), list) and SENT in a["tags"],
    ),
}


def probe(base, key, model, shape_name):
    parameters, instruction, check = SHAPES[shape_name]
    tools = [{"type": "function", "function": {"name": "t", "description": "probe", "parameters": parameters}}]
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": instruction}],
        "tools": tools,
        "tool_choice": {"type": "function", "function": {"name": "t"}},
        "max_tokens": 200,
    }).encode()
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions", data=body,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json", **UA})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            d = json.load(r)
    except Exception as e:  # transport/HTTP — report, never fake a verdict
        return "ERROR", str(e)[:80]
    tcs = d["choices"][0]["message"].get("tool_calls") or []
    if not tcs:
        return "NOCALL", ""
    try:
        args = json.loads(tcs[0]["function"].get("arguments") or "{}")
    except ValueError:
        return "BADJSON", (tcs[0]["function"].get("arguments") or "")[:80]
    return ("OK" if check(args) else "DROP"), json.dumps(args)[:100]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--models", required=True, help="comma-separated model IDs")
    p.add_argument("--base-url", default="https://api.xkiro.com/v1")
    p.add_argument("--key-env", default="XKIRO_API_KEY")
    ns = p.parse_args()
    key = os.environ.get(ns.key_env, "")
    if not key:
        sys.exit(f"set {ns.key_env}")
    models = [m.strip() for m in ns.models.split(",") if m.strip()]
    width = max(len(s) for s in SHAPES) + 2
    print("model".ljust(28), *(s.ljust(width) for s in SHAPES))
    for model in models:
        row = []
        for shape in SHAPES:
            verdict, detail = probe(ns.base_url, key, model, shape)
            row.append(verdict.ljust(width))
            if verdict != "OK":
                print(f"  {model} :: {shape} -> {verdict} {detail}", file=sys.stderr)
        print(model.ljust(28), *row)


if __name__ == "__main__":
    main()
