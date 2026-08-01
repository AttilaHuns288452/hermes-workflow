# MCP SDK 0.x → 1.x (FastMCP) Migration

When a custom Python MCP server fails with `AttributeError` or `ExceptionGroup` errors mentioning `create_initialization_options`, `tools_changed`, or `ServerCapabilities`, it was written for MCP SDK 0.x and needs to be migrated to the 1.x API.

## Quick migration: old Server → FastMCP

**Old pattern (MCP SDK 0.x, broken on 1.x):**

```python
from mcp.server import Server
from mcp.types import Tool, TextContent, ...

app = Server("my-server")

@app.list_tools()
async def list_tools():
    return ListToolsResult(tools=[...])

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    ...

def main():
    from mcp.server.stdio import stdio_server
    async def _run():
        async with stdio_server() as (r, w):
            await app.run(r, w, app.create_initialization_options({
                "serverInfo": {...},
                "capabilities": ServerCapabilities(tools={}),
            }))
    import asyncio
    asyncio.run(_run())
```

**New pattern (FastMCP, MCP SDK 1.x compatible):**

```python
from mcp.server.fastmcp import FastMCP

app = FastMCP("my-server")

@app.tool()
def my_tool(param1: str = "default", param2: bool = True) -> str:
    """Docstring becomes the tool description. Args docstring becomes param descriptions."""
    # ... logic ...
    return json.dumps(result)

def main():
    app.run(transport="stdio")
```

## Key differences

| Old API | FastMCP replacement |
|---------|-------------------|
| `from mcp.server import Server` | `from mcp.server.fastmcp import FastMCP` |
| `@app.list_tools()` returning `ListToolsResult(...)` | `@app.tool()` with a regular async/sync function |
| `@app.call_tool()` with name + arguments | Tool function signature with typed params (name derived from function name) |
| Manual `stdio_server()` + `asyncio.run()` | `app.run(transport="stdio")` |
| `ServerCapabilities`, `InitializeOptions` | Handled automatically |
| `CallToolResult(content=[TextContent(type="text", text=...)])` | Just return `str` — FastMCP wraps it |
| Tools defined in `inputSchema` dict | Typed function parameters auto-generate JSON Schema |

## Type mapping

| Python type | JSON Schema |
|-------------|-------------|
| `str` | `{"type": "string"}` |
| `int` | `{"type": "integer"}` |
| `float` | `{"type": "number"}` |
| `bool` | `{"type": "boolean"}` |
| `list[str]` | `{"type": "array", "items": {"type": "string"}}` |
| `Optional[str]` | `{"type": "string"}` (nullable: not always added) |
| `str = "default"` | Adds `{"default": "default"}` |

## Docstring → description

FastMCP reads the function docstring and maps it as follows:

```
def my_tool(vault_path: str = ..., include_x: bool = ...) -> str:
    """Scan a vault and produce a graph.
    
    Args:
        vault_path: Absolute path to the vault.
        include_x: Whether to include X nodes.
    """
```

- First paragraph → tool `description`
- `Args:` section → per-parameter `description` in inputSchema

## Caveats

- FastMCP's `run(transport="stdio")` uses `asyncio` internally. No need to wrap it yourself.
- The `list_tools` / `call_tool` decorators from old `Server` will throw `TypeError` or `AttributeError` if mixed with FastMCP — remove them entirely.
- `ExceptionGroup` wrapping an `AttributeError: 'dict' object has no attribute 'tools_changed'` is the specific signal that `create_initialization_options` was called with a dict instead of the new options object in MCP 1.x. The FastMCP rewrite eliminates the need for this call.
