---
name: figma-integration
description: Figma API, auth, prototype workflows, and HTML bridging.
triggers:
  - figma
  - prototype in figma
  - figma api
  - figma token
  - figma oauth
  - wire frames
  - connect frames
  - figma prototype
tags: [figma, design, prototype, api, ui-ux]
---

# Figma Integration

## REST API — What It Can and Cannot Do

**CAN do (read):**
- Read file content, nodes, styles, components
- Read comments, versions, dev resources
- Read team library content, variables (Enterprise)
- Download images/SVGs from files

**CANNOT do (write):**
- Create frames, rectangles, text nodes
- Wire prototype connections (On Click → Navigate To)
- Set interactions, transitions, or animations
- Modify file layout or structure

**Write scopes are limited to:**
- `file_comments:write` — post/delete comments
- `file_dev_resources:write` — dev resources only
- `file_variables:write` — variables/collections (Enterprise only)
- `webhooks:write` — webhook management

There is NO `file_content:write` scope. Figma's REST API is fundamentally read-only for file structure.

## Authentication

### Personal Access Token (PAT) — simplest
1. Figma → Settings → Security → Personal access tokens
2. Generate token, set as `FIGMA_ACCESS_TOKEN` env var
3. Use: `curl -H "X-Figma-Token: $TOKEN" https://api.figma.com/v1/me`

### OAuth 2.0 — for apps
1. Create app at figma.com/developers/apps
2. **Correct scopes** (granular, not deprecated):
   - `file_content:read`
   - `file_metadata:read`
   - `file_comments:write`
   - `file_dev_resources:write`
3. Authorization URL: `https://www.figma.com/oauth?client_id=...&redirect_uri=...&scope=file_content:read+file_metadata:read&response_type=code`
4. User authorizes → gets code → exchange for token via POST

**Deprecated scopes (do not use):**
- `file_read` — deprecated, use granular scopes
- `files:read` — deprecated, use `file_content:read`

## GUI Automation via cua-driver

For tasks the REST API cannot do (creating frames, wiring prototypes), use `computer_use` with cua-driver:

```bash
# Install
hermes computer-use install
powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/trycua/cua/main/libs/cua-driver/scripts/install.ps1 | iex"

# MCP config for Hermes — add to ~/.hermes/config.yaml:
# mcp_servers:
#   cua-driver:
#     command: "C:\\Users\\Attila\\AppData\\Local\\Programs\\Cua\\cua-driver\\bin\\cua-driver.exe"
#     args: ["mcp"]
```

**Workflow for wiring Figma prototypes:**
1. `computer_use(action="capture", app="Figma")` — see current state
2. Create frames via GUI (rectangles + text)
3. Click "Prototype" tab in right sidebar
4. Drag connection noodles between frame edges
5. Set interactions (On Click → Navigate To, Dissolve/Fade)
6. Click Play to test

**Limitations of GUI automation:**
- Figma is Electron — complex UI tree
- Prototype wiring requires precise drag between frame edges
- Slow (~10-15 clicks per frame to build from scratch)
- Requires Figma desktop app open

## HTML Prototype as Figma Simulation

When Figma integration is blocked or overkill, build an HTML file that simulates Figma's prototype mode:

**Visual elements:**
- Dark canvas with dot grid background
- White frames positioned absolutely on canvas
- Blue bezier connection arrows between frames (SVG)
- Frame labels (like Figma's frame names)
- Top bar with frame tabs

**Interactive features:**
- Click frame → opens viewport mode (black bg, centered, back button)
- ESC to exit viewport
- Hotspot hover states with connection labels
- Smooth transitions between screens

**Reference:** `C:\Users\Attila\ui-ux-showcase\figma-prototype.html`

## HTML Import to Figma

Figma does NOT natively import HTML files. Options:
1. **html.to.design plugin** — Figma plugin that converts live web pages to Figma frames (requires plugin install inside Figma)
2. **Screenshot → paste** — loses editability
3. **Manual recreation** — build frames from scratch in Figma

None of these are automatable from outside Figma without GUI automation.

## Common Pitfalls

- **Wrong OAuth scopes**: `file_read` is deprecated. Always use granular scopes.
- **Expecting REST API to create nodes**: It cannot. Use GUI automation or build HTML prototypes.
- **HTML import**: Not supported natively. html.to.design is a plugin, not an API.
- **cua-driver not appearing as tool**: MCP server must be in config.yaml AND session must be reloaded after adding it.
- **PAT vs OAuth confusion**: PAT is simpler for personal use. OAuth is for apps that other users will authorize.
