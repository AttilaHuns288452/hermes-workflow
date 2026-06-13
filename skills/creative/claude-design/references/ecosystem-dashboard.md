# Ecosystem Documentation Dashboard

Build an educational HTML dashboard that documents an AI agent's own workflow, skills, tools, model routing, and integrated knowledge graph — a self-documenting ecosystem site.

## When To Use This Pattern

Build an ecosystem dashboard when the user asks for **a website about their Hermes/agent workflow** — documenting skills, tools, models, agents, integrations, pipeline, and knowledge graph in one place.

This is **not** a product landing page (use `claude-design` core + `popular-web-designs`) or a sketch/mockup (use `sketch`). It is an **information architecture + documentation** artifact that happens to be an HTML site.

The pattern also applies when the user says "document my setup", "create a dashboard for my tools", or "make a site about my workflow".

## Workflow

### 1. Audit the Ecosystem

Before writing any HTML, inventory what exists. Load `session_memory` to pull prior context. Then check:

- **Skills** — list all skills with categories (`skills_list` + `skill_view` for details)
- **ECC agents** — count, model distribution, categories (check `Projects/ECC/agents/`)
- **Model routing** — layers, providers, models per layer
- **Knowledge graph** — current state of `kg_output.json` (nodes, edges)
- **CodeGraph / Graphify** — versions, file counts, tools
- **LLMQuant** — domains available
- **Other integrations** — MoneyPrinterTurbo, OpenCode, Freebuff, FreeLLMAPI, etc.

Run `scan_vault.py` + `render_galaxy_kg.py` to get latest KG data before building the site.

### 2. Design the Information Architecture

An ecosystem dashboard typically needs these sections:

| Section | Why |
|---|---|
| **Hero** | What is this ecosystem? Single sentence + key stats |
| **What is [Agent Name]** | Explain the agent framework and how it works |
| **/decide (Routing Brain)** | Visual flowchart of the decision process |
| **Pipeline** | The execution sequence step-by-step |
| **Skills** | All available skills with category filtering |
| **CodeGraph / Graphify** | Code knowledge tools and how they complement each other |
| **ECC Agents** | Agent library with search + filter + model distribution |
| **Model Routing** | Fallback chain visualization + detailed tier cards |
| **LLMQuant** | Domain skills grid (when applicable) |
| **Ecosystem Integration** | ASCII flow diagram showing how everything connects |
| **Knowledge Graph** | Direct link + stats + open button + file path + inline preview |
| **Obsidian** | Documentation template and vault status |
| **Use Cases** | Real projects executed through the pipeline |

### 3. Build the HTML

- **Self-contained single HTML file** — embed CSS in `<style>`, JS in `<script>` (unless the site will be served).
- **Dark theme** — the default ecosystem-dashboard aesthetic uses deep-space backgrounds, gradient accents, and subtle surface layers. Keep the CSS in `:root` variables for maintainability.
- **Responsive** — works on mobile, tablet, desktop. Test at least one breakpoint.
- **Fade-in animations** on scroll via `IntersectionObserver` — adds polish without external dependencies.

#### Knowledge Graph Integration (Critical UX Pattern)

The KG is the most impactful section for user comprehension. Include:

1. **Stats cards** — nodes, edges, file size, project clusters
2. **Open button** — `<a class="kg-open-btn" onclick="window.open(...)">✦ Open Interactive Galaxy KG ↗</a>` styled link
3. **File paths** — two copy-to-clipboard paths: Windows absolute path + `file:///` URL
4. **Inline iframe preview** — `<iframe src="file:///path/to/knowledge_graph.html">` at ~300px height so users can see the graph without leaving the page
5. **Complementary cards** — brief pointers to Obsidian Graph View, Graphify, CodeGraph MCP

The file paths should have **copy buttons** that use `navigator.clipboard.writeText()` and show a "✓ Copied!" confirmation.

### 4. Verify

- Check `wc -l` and file size
- Verify `grep -c` `<div` and `</div>` counts match
- If browser tools are available, navigate to `file:///path/to/site.html` and inspect
- Check console for JavaScript errors (especially the `llmquantGrid` and `skillGrid` dynamic content)

### 5. Report

Deliver:
- Exact file path
- File size and line count
- What sections were added/improved
- Direct path(s) to open

## Default CSS Theme

Use these variables for the deep-space dark aesthetic:

```css
:root {
  --bg:#07070d; --surface:#0f0f1a; --surface2:#18182a; --surface3:#22223a;
  --border:#2a2a44; --text:#e8e8f0; --text2:#8080b0;
  --accent:#6c5ce7; --accent2:#a29bfe;
  --green:#00e676; --orange:#ff9100; --red:#ff1744; --blue:#448aff;
  --cyan:#00e5ff; --pink:#f50057; --yellow:#ffea00;
  --grad:linear-gradient(135deg,#6c5ce7,#a29bfe,#00e5ff);
  --grad2:linear-gradient(135deg,#f50057,#ff9100,#ffea00);
  --radius:14px;
  --font:'Inter',-apple-system,sans-serif;
  --mono:'JetBrains Mono','Fira Code',monospace;
}
```

## /decide Visual Flow Pattern

The routing brain section needs to be **visual**, not just text. Use a multi-row layout with numbered steps:

```
Row 1: session_memory → Decompose → Score & Route
Row 2: Graphify → Domain Skills → Model Routing
Row 3: Obsidian Docs → KG Refresh
```

Each step gets a card with: number badge, emoji icon, label, and 1-line description. Arrows between them. Use `.df-row` flex containers with `.df-step` cards and `.df-arrow` connectors.

Follow with three metadata cards: **Mandatory Rules**, **Conflict Resolution**, **Output Format**.

## Model Routing Visual Chain

Use a horizontal chain with emoji badges — each step is a mini-card with border-color matching reliability:

```html
🏅 OpenCode → 🥈 Freebuff → 🥉 FreeLLMAPI → ⚠️ OpenRouter → 💎 Paid
```

Then below it, detailed `.mtier` cards with border-left colors (green → yellow → orange → red → accent), tag lists, and descriptions.

## Anti-Patterns

- **Don't** make the KG section hidden or hard to find — it's the most visually impressive part of the site. Give it prominent nav placement (both a "Knowledge Graph" link and a highlighted "Galaxy KG" link).
- **Don't** use placeholder data for stats — run the actual scan to get real node/edge counts.
- **Don't** forget the LLMQuant section if quant domains are part of the ecosystem.
- **Don't** include the entire agent data inline in HTML if there are 64+ agents — JS injection from a JSON array is cleaner and keeps the file maintainable.
- **Don't** ship without checking that JS-rendered sections (`llmquantGrid`, `skillGrid`, `agentsGrid`, `modelDist`) have matching HTML `id` elements in the DOM.

## Related Skills

- `popular-web-designs` — supply a visual vocabulary from real design systems if the user wants a branded look
- `sketch` — for throwaway mockups *before* settling on the dashboard layout
- `note-taking/obsidian-knowledge-graph` — for the KG scanning and rendering scripts
- `software-development/graphify-integrate` — for the Graphify code-graph export side
