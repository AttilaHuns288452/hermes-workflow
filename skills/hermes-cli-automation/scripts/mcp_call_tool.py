#!/usr/bin/env python3
"""Invoke one tool on a stdio MCP server over raw JSON-RPC, no client session needed.

Usage: mcp_call_tool.py <tool_name> '<json-args-or-empty>' -- <command> [args...]
Prints the tool's text content. Exit 0 = ok, 2 = tool error, 1 = launch/timeout.
"""
import json
import subprocess
import sys
import time


def main() -> int:
    argv = sys.argv[1:]
    if "--" not in argv:
        print(__doc__)
        return 1
    i = argv.index("--")
    head, command = argv[:i], argv[i + 1 :]
    if len(head) != 2 or not command:
        print(__doc__)
        return 1
    tool, args_raw = head
    try:
        args = json.loads(args_raw or "{}")
    except json.JSONDecodeError as e:
        print(f"bad json args: {e}")
        return 1

    p = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    def send(obj: dict) -> None:
        p.stdin.write(json.dumps(obj) + "\n")
        p.stdin.flush()

    send({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "mcp-call-tool", "version": "1"},
        },
    })
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    send({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": tool, "arguments": args},
    })

    deadline = time.time() + 300
    while time.time() < deadline:
        line = p.stdout.readline()
        if not line:
            break
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("id") == 2:
            p.terminate()
            if "error" in msg:
                print("TOOL ERROR:", json.dumps(msg["error"])[:2000])
                return 2
            res = msg.get("result", {})
            for c in res.get("content", []):
                if c.get("type") == "text":
                    print(c["text"])
            return 2 if res.get("isError") else 0
    p.terminate()
    print("TIMEOUT or launch failure: no tools/call response")
    return 1


if __name__ == "__main__":
    sys.exit(main())
