#!/usr/bin/env python3
"""MCP SDK round-trip probe: initialize + tools/list (+ optional tool call) over stdio.

Middle layer between probe_mcp_stdio.py (raw JSON-RPC) and `hermes mcp test`: this runs
the same MCP client stack Hermes uses. SDK success + Hermes failure means the fault is in
the launch (argv/env/timeout), not the server or protocol version.

Usage: mcp_sdk_roundtrip.py <command> [args...] [--call TOOL '{"json":"args"}']
Requires a python with the `mcp` package installed (the Hermes generation venv ships it).
"""
import asyncio
import json
import sys

def main() -> int:
    argv = sys.argv[1:]
    call = None
    if "--call" in argv:
        i = argv.index("--call")
        name = argv[i + 1]
        args = json.loads(argv[i + 2]) if len(argv) > i + 2 else {}
        call = (name, args)
        argv = argv[:i]
    if not argv:
        print(__doc__)
        return 1
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError:
        print("ERROR: no python env with the 'mcp' package; run with the Hermes generation venv python")
        return 2

    async def run() -> int:
        params = StdioServerParameters(command=argv[0], args=argv[1:])
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                tools = await session.list_tools()
                names = sorted(t.name for t in tools.tools)
                print(f"initialize OK, {len(names)} tools: {names[:8]}{' ...' if len(names) > 8 else ''}")
                if call:
                    name, args = call
                    res = await session.call_tool(name, args)
                    txt = res.content[0].text if res.content else str(res)
                    print(f"call {name}: {txt[:600]}")
                return 0

    return asyncio.run(run())

if __name__ == "__main__":
    sys.exit(main())
