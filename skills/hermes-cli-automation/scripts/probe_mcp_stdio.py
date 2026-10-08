#!/usr/bin/env python3
"""Probe a stdio MCP server without a client: initialize + tools/list + resources/list.

Usage: probe_mcp_stdio.py -- <command> [args...]
Example: probe_mcp_stdio.py -- ~/.local/share/mcp-servers/packet-tracer/.venv/bin/python -m packet_tracer_mcp --stdio

Exit 0 = server answered tools/list (prints counts + sample names).
Exit 1 = no tools/list response (server failed to launch or speaks no MCP).
"""
import json
import subprocess
import sys


def main() -> int:
    argv = sys.argv[1:]
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2

    msgs = "\n".join(
        [
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "probe", "version": "0"},
                    },
                }
            ),
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}),
            json.dumps({"jsonrpc": "2.0", "id": 3, "method": "resources/list", "params": {}}),
        ]
    )

    try:
        proc = subprocess.run(
            argv, input=msgs, capture_output=True, text=True, timeout=60
        )
    except subprocess.TimeoutExpired:
        print("FAIL: server did not answer within 60s", file=sys.stderr)
        return 1

    tools = resources = None
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue  # servers may interleave non-JSON noise on stdout
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("id") == 2:
            tools = d.get("result", {}).get("tools")
        if d.get("id") == 3:
            resources = d.get("result", {}).get("resources")

    if tools is None:
        print("FAIL: no tools/list response — launch command itself is wrong", file=sys.stderr)
        tail = proc.stderr[-500:].strip()
        if tail:
            print("stderr tail:\n" + tail, file=sys.stderr)
        return 1

    print(f"OK tools={len(tools)} resources={len(resources or [])}")
    print("sample:", ", ".join(t["name"] for t in tools[:10]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
