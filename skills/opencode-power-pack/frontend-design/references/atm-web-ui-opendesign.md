# ATM Web UI — OpenDesign Retro-Futuristic Terminal Template

## Project Context

Built as the web frontend for the ATM Machine project. Demonstrates the OpenDesign methodology from the `frontend-design` skill: bold aesthetic direction, not generic "AI slop".

## Aesthetic Direction

| Dimension | Choice | Rationale |
|-----------|--------|-----------|
| **Tone** | Industrial terminal / cyberpunk banking | Distinctive, memorable, fits "ATM" domain |
| **Display Font** | Space Mono | Monospace, technical, geometric |
| **UI Font** | JetBrains Mono | Readable monospace, coding heritage |
| **Primary Color** | Phosphor green `#00ff88` | Terminal heritage, high contrast |
| **Warning Color** | Amber `#ffb800` | Attention without alarm |
| **Error Color** | Crimson `#ff3355` | Clear failure signal |
| **Background** | Deep charcoal `#05080a` | Not pure black — softer on eyes |

## Design Tokens (CSS Custom Properties)

```css
:root {
  --bg-deep:       #05080a;
  --bg-panel:      #0a0f14;
  --bg-elevated:   #0f161e;
  --fg-primary:    #c8e8c8;
  --fg-muted:      #6a8a6a;
  --accent-phosphor: #00ff88;
  --accent-amber:    #ffb800;
  --accent-crimson:  #ff3355;

  --font-ui:       'JetBrains Mono', monospace;
  --font-display:  'Space Mono', monospace;

  --space-1: 0.25rem;  --space-2: 0.5rem;  --space-3: 0.75rem;
  --space-4: 1rem;     --space-5: 1.5rem;  --space-6: 2rem;
}
```

## Layout Architecture

```
┌─────────────────────────────────────────────────────────┐
│  HEADER (56px)  ──  Prompt + Title + Status + Clock    │
├──────────────┬──────────────────────────────────────────┤
│  SIDEBAR     │  MAIN PANEL                              │
│  (280px)     │  ┌────────────────────────────────────┐  │
│  • Account   │  │ OUTPUT LOG (flex:1)                │  │
│  • Quick     │  │  • Timestamped lines               │  │
│    Actions   │  │  • Color-coded types               │  │
│              │  │  • Auto-scroll                     │  │
│              │  ├────────────────────────────────────┤  │
│              │  │ INPUT FORM                         │  │
│              │  │  • Styled prompt + input           │  │
│              │  └────────────────────────────────────┘  │
├──────────────┴──────────────────────────────────────────┤
│  FOOTER (48px)  ──  Version | Mode | Keyboard hints     │
└─────────────────────────────────────────────────────────┘
```

**Responsive**: <900px stacks sidebar above main panel.

## Component Patterns

### Terminal Output Lines
```html
<div class="line system">
  <span class="timestamp">[14:32:01]</span>
  <span class="prefix">SYS</span>
  <span class="msg">MESSAGE</span>
</div>
```
Types: `system`, `user`, `prompt-line`, `menu`, `divider`

### Modal Dialogs
- Backdrop blur + scale animation
- Focus trap, keyboard accessible
- Form validation inline

### Sidebar Sync
Reactively updates from `state.currentAccount`:
- Status badge (connected/disconnected)
- Account number, holder, balance
- Quick action buttons (enabled/disabled by auth state)

## Input Handling

- **Command input**: Free-text + number shortcuts
- **Modal forms**: Structured for sensitive input (PIN, amounts)
- **Keyboard shortcuts**: `H`=help, `Q`=quit/logout
- **Validators**: Reused from Python core (portable logic)

## Files

| File | Purpose |
|------|---------|
| `atm.html` | Structure, semantics, accessibility |
| `atm.css` | Complete design system (tokens → components) |
| `atm-core.js` | Domain: Transaction, Account, Bank, Validators |
| `atm-ui.js` | Controller: render, routing, modals, state |
| `atm.js` | Entry point / module loader |

## Accessibility (WCAG 2.2 AA)

- Semantic HTML: `<main>`, `<header>`, `<footer>`, `<aside>`, `<nav>`, `<form>`
- Focus visible: custom outline on all interactives
- Contrast: 4.5:1 body, 3:1 UI controls
- `prefers-reduced-motion`: disables animations
- ARIA: `role="log" aria-live="polite"` on output, `aria-modal` on dialogs

## Reuse Checklist

- [ ] Copy `atm-core.js` → adapt domain classes
- [ ] Copy `atm-ui.js` → replace command handlers
- [ ] Copy `atm.css` → swap tokens for new palette/fonts
- [ ] Copy `atm.html` → restructure sections
- [ ] Keep `atm.js` as thin loader

## Tags

#opendesign #template #terminal-ui #retro-futuristic #frontend-design #atm-machine