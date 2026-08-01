# Agent Card Content Strategy

Crafting a compelling agent card is critical for marketplace success. Use a **GitHub README-style** markdown format — it's familiar, scannable, and visually appealing.

## Template Structure

```markdown
# 🎨 Agent Name

Your one-line value proposition — what does this Agent DO in 15 words?

---

## ✨ Capabilities

List each major capability with a bullet, emoji, and short description.
Group related features under sub-headings when there are 5+.

- **Feature A** — What it does in one sentence
- **Feature B** — What it does in one sentence

---

## 🚀 Quick Start

Show 2-3 example prompts the buyer would actually type:

> *"Generate an architecture diagram of a microservices system with Kubernetes"*
>
> *"Create a modern landing page like Stripe's design"*

---

## 🛠️ How It Works

Brief explanation of how the Agent selects the right tool/approach per request.

**Output formats:** list of supported formats

---

## 📋 Requirements

- Prerequisite 1 (e.g. modern web browser)
- Prerequisite 2 (e.g. Python 3.8+)
```

## Image Guidelines

- Supported formats: PNG, JPG, WebP
- Max 4096 px per side, ≤2 MB each, ≤10 images
- Use screenshots of actual outputs (diagrams, web pages, art)
- First image is the card thumbnail — make it count

## Category Selection

| Agent Type | Best Category |
|---|---|
| Developer tools, CLI agents | `Developer Tools` |
| Design, art, creative | `Design & Creative` |
| Writing, content | `Writing & Content` |
| Data analysis | `Data & Analytics` |
| Business automation | `Business & Productivity` |

## Tags Strategy

- 5-10 tags, comma-separated
- Lead with the most specific tags first
- Include format keywords (svg, json, html, markdown)
- Include category keywords (creative, design, diagram, generative-art)
- Example: `creative, design, diagram, ascii-art, infographic, p5js, generative-art, web-design`

## Pricing Strategy (Mass Adoption)

For creators who prioritize user volume over per-user profit:

| Tier | Recommended | Rationale |
|---|---|---|
| **Free trial** | Always enable | 3-5 free uses or 24-48h trial removes purchase friction |
| **Subscription** | Lowest available monthly rate | Predictable, accessible. Raise later when value is proven. |
| **Per-hour** | Cheap if available | Good for occasional users |
| **One-time/buyout** | N/A for Run Online | Not applicable for cloud-hosted agents |

Key: price for adoption first, profit second. A cheap agent with 1000 users > a premium agent with 10 users.
