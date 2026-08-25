# Figma MCP Data Parsing Reference

## Tool: `mcp__figma_dev__get_figma_data`

### Parameters
- `fileKey` (required): From URL `figma.com/design/<fileKey>/...`
- `nodeId` (optional): From `node-id=X-Y` → convert to `X:Y`
- `depth` (optional): Limit tree depth (2 = overview, omit = full)

### Output Format
Custom YAML-like structure (NOT Figma REST JSON):
```
NAME: "File Name"
GLOBAL_VARS:
  style_<hash>: fontFamily, fontSize, etc.
  fill_<hash>: ['#HEXCOLOR']
  layout_<hash>: dimensions: { width, height }
ELEMENTS:
  EL-<hash>: type=FRAME|TEXT, layout, fills
NODES:
  [CANVAS] "Page Name" #nodeId
    [TEXT] #nodeId text="Visible text content"
    [FRAME] "frameName" #nodeId template=EL-<hash>
```

### Parsing Patterns

```python
import json, re

# Load from disk (auto-saved when > context limit)
with open(spillover_path, "r", encoding="utf-8") as f:
    data = json.loads(f.read())
result_text = data.get("result", "")

# 1. Extract ALL visible text nodes
text_nodes = re.findall(
    r'\[TEXT\]\s+#([\d:]+)\s+.*?text="([^"]*)"', result_text
)
for node_id, text in text_nodes:
    print(f"  #{node_id}: {text}")

# 2. Find numbered screen labels
screen_labels = re.findall(
    r'text="(\d+ · [^"]+)"', result_text
)

# 3. Find phone-sized frames (390x844)
# Search for "width: 390" near "height: 844" in layout blocks

# 4. Count total named nodes
names = re.findall(r'^NAME:\s*"([^"]+)"', result_text, re.MULTILINE)
```

### Key Quirks
- Output is a SINGLE massive string (2+ MB for large files)
- `\\n` in text = literal backslash-n, NOT newlines
- Node IDs use `#` prefix in NODES section
- `template=EL-<hash>` = frame uses shared element definition
- Two numbering systems may coexist: individual frames + flow board
- Full output auto-saved to `cache/spillover/` when too large for context
- Use `execute_code` with regex for parsing, NOT direct `read_file` on the full output

### Connected Tools
- `mcp__figma_dev__download_figma_images` — SVG/PNG from node IDs
- `mcp__flowbite__convert_figma_to_code` — Figma → code (needs FIGMA_ACCESS_TOKEN)

### Workflow: Figma → HyperFrames → MP4
1. Pull Figma data: `mcp__figma_dev__get_figma_data(fileKey="...", nodeId="0:1")`
2. Parse text nodes to understand screen content
3. Build HyperFrames HTML composition (use `patch` for large files — `write_file` may timeout >8KB)
4. `npm run check` → `npm run render` → deliver MP4
