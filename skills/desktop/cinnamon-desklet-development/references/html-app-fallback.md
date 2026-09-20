# Standalone HTML Application Fallback

Complete pattern for building a feature-rich Linux Mint utility as a
single-file HTML app when a Cinnamon desklet is not appropriate.

## When to use

- Feature set too large for a desklet (>10 entries, multiple panels)
- GTK3/Qt not available on the system
- User needs search, filtering, copy/paste, favorites
- Offline-first requirement

## Complete template

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>App Title</title>
<style>
:root {
  --bg-primary: #1e1e1e;
  --bg-secondary: #252526;
  --bg-card: #2d2d2d;
  --bg-card-hover: #333333;
  --bg-input: #1a1a1a;
  --border: #3c3c3c;
  --border-focus: #00bcd4;
  --text-primary: #e0e0e0;
  --text-secondary: #a0a0a0;
  --text-muted: #757575;
  --accent: #00bcd4;
  --accent-hover: #00acc1;
  --accent-glow: rgba(0, 188, 212, 0.15);
  --font-mono: 'Consolas', 'Monaco', 'Courier New', monospace;
  --font-sans: 'Segoe UI', 'Ubuntu', 'Cantarell', sans-serif;
  --radius: 6px;
  --radius-lg: 10px;
  --shadow: 0 2px 8px rgba(0,0,0,0.3);
}

[data-theme="light"] {
  --bg-primary: #f5f5f5;
  --bg-secondary: #ffffff;
  --bg-card: #ffffff;
  --bg-card-hover: #f0f0f0;
  --bg-input: #ffffff;
  --border: #d0d0d0;
  --border-focus: #00838f;
  --text-primary: #212121;
  --text-secondary: #616161;
  --text-muted: #9e9e9e;
  --accent: #00838f;
  --accent-hover: #006064;
  --accent-glow: rgba(0, 131, 143, 0.1);
  --shadow: 0 2px 8px rgba(0,0,0,0.1);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: var(--font-sans);
  background: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
  line-height: 1.5;
}

/* Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: var(--bg-secondary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

/* Header */
.header {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  padding: 16px 24px;
  position: sticky;
  top: 0;
  z-index: 100;
}

/* Search */
.search-input {
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  font-size: 0.95rem;
  outline: none;
  transition: all 0.2s;
}
.search-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

/* Cards */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 18px;
  transition: all 0.2s;
}
.card:hover {
  border-color: var(--accent);
  box-shadow: var(--shadow);
}

/* Buttons */
.btn {
  padding: 8px 16px;
  background: var(--accent);
  color: var(--bg-primary);
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  transition: all 0.2s;
}
.btn:hover { background: var(--accent-hover); }

/* Toast */
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: var(--bg-card);
  border: 1px solid var(--accent);
  color: var(--text-primary);
  padding: 12px 20px;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  transform: translateY(100px);
  opacity: 0;
  transition: all 0.3s;
  z-index: 1000;
}
.toast.visible { transform: translateY(0); opacity: 1; }

/* Responsive */
@media (max-width: 768px) {
  .header { padding: 12px 16px; }
}
</style>
</head>
<body>

<div class="header">
  <h1>App Title</h1>
  <input type="text" class="search-input" id="searchInput" placeholder="Search...">
</div>

<div id="content"></div>
<div class="toast" id="toast"></div>

<script>
// === DATABASE ===
const DATA = [
  { id: 'entry1', title: 'Entry 1', description: '...' },
  // ... more entries
];

// === STATE ===
let state = {
  search: '',
  theme: localStorage.getItem('theme') || 'dark',
  favorites: JSON.parse(localStorage.getItem('favorites') || '[]'),
};

// === UTILITIES ===
function showToast(message) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('visible');
  setTimeout(() => toast.classList.remove('visible'), 2000);
}

async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast('✓ Copied to clipboard');
  } catch (e) {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showToast('✓ Copied to clipboard');
  }
}

function toggleFavorite(id) {
  const idx = state.favorites.indexOf(id);
  if (idx > -1) state.favorites.splice(idx, 1);
  else state.favorites.push(id);
  localStorage.setItem('favorites', JSON.stringify(state.favorites));
  render();
}

// === RENDER ===
function render() {
  const filtered = DATA.filter(d =>
    d.title.toLowerCase().includes(state.search.toLowerCase()) ||
    d.description.toLowerCase().includes(state.search.toLowerCase())
  );
  // ... render cards
}

// === THEME ===
document.documentElement.setAttribute('data-theme', state.theme);

// === INIT ===
render();
</script>
</body>
</html>
```

## Key features to include

1. **Search** — filter by title, description, keywords
2. **Copy to clipboard** — with fallback for older browsers
3. **Favorites** — persisted in localStorage
4. **Theme toggle** — dark/light, persisted, matches desktop
5. **Toast notifications** — for copy confirmation
6. **Responsive** — works on laptop screens
7. **Offline** — no external dependencies

## Desktop shortcut

```ini
# ~/.local/share/applications/<name>.desktop
[Desktop Entry]
Name=App Name
Comment=Description
Exec=xdg-open /home/user/Applications/app.html
Icon=appropriate-icon
Type=Application
Categories=Category;Subcategory;
Keywords=keyword1;keyword2;
StartupNotify=true
Terminal=false
```

## Verification checklist

- [ ] File opens in browser with `file:///` protocol
- [ ] Search filters correctly
- [ ] Copy button works (check clipboard)
- [ ] Favorites persist after refresh
- [ ] Theme toggle works and persists
- [ ] Desktop shortcut launches the app
- [ ] No console errors
- [ ] Responsive at 1280px width
