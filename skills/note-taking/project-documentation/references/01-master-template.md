---
# Rich Documentation Master Template

Rich style with literal code blocks, file trees, wikilinks, and relationship graphs.
This is the user's enforced preference for all project documentation.

---

## 01_overview/README.md

```markdown
---
type: project-doc
section: overview
project: <Project Name>
tags: [project-name, overview, tech-stack]
---

# <Project Name> — Overview

**Purpose:** One-paragraph description of what this system does and who it's for.

## 📁 File Tree

```
project-root/
├── src/core/
│   ├── main.py              # 🟢 Entry point
│   └── module.py            # ⚙️ Core logic
├── web/
│   ├── index.html           # 🌐 Web entry
│   └── style.css            # 🎨 Styles
├── tests/
│   └── test_main.py         # 🧪 Unit tests
├── package.json             # 📦 Config
└── docs/
    └── api.md               # 📝 Documentation
```

**→ [[02_architecture]]** · **→ [[03_modules]]** · **→ [[06_gaps_and_todos]]**

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Runtime** | Python 3.11+ |
| **UI** | Vanilla HTML/CSS/JS |
| **Hosting** | Vercel |

## 🚀 Quick Start

```bash
cd /path/to/project
python main.py
```
```

## 02_architecture/README.md

```markdown
---
type: project-doc
section: architecture
project: <Project Name>
tags: [architecture, class-diagram]
---

# 🏗️ <Project Name> — Architecture

## 🔗 Class Relationship Graph

```
┌──────────────────────────────┐
│           ClassA              │
│  method1() → Type1           │
│  method2() → Type2           │
└──────────┬───────────────────┘
           │ owns *
           ▼
┌──────────────────────────────┐
│           ClassB              │
│  attr: str                    │
│  method() → None              │
└──────────────────────────────┘
```

## 🖥️ Component Tree

```
app/
├── component1               ← standalone
└── component2
    └── subcomponent          ← dependent
```

**→ [[01_overview]]** · **→ [[03_modules]]** · **→ [[04_data_flow]]**
```

## 03_modules/README.md

```markdown
---
type: project-doc
section: modules
project: <Project Name>
tags: [modules, source-code]
---

# 📦 <Project Name> — Modules

## 1️⃣ `path/to/file.py` — Module Name

```python
class KeyClass:
    """Purpose statement."""

    def __init__(self, param: str) -> None:
        self.param = param

    def method(self, arg: float) -> bool:
        """What this method does."""
        return arg > 0
```

**Key behaviors:**
- `method()` returns True when arg is positive
- Raises `ValueError` on invalid input

## 2️⃣ `path/to/next.js` — Next Module

```javascript
class Component {
  constructor(name) {
    this.name = name;
  }
  render() {
    return `<div>${this.name}</div>`;
  }
}
```

**→ [[01_overview]]** · **→ [[02_architecture]]** · **→ [[05_dependencies]]**
```

## 04_data_flow/README.md

```markdown
---
type: project-doc
section: data-flow
project: <Project Name>
tags: [data-flow, sequences]
---

# 🔀 <Project Name> — Data Flow

## Flow 1: Main Action

```
User enters value
    │
    ▼
Validator.validate(value)
    │  rejected → "Invalid input"
    │  accepted
    ▼
Core.process(value)
    │  state before: X
    │  state after: Y
    ▼
print(f"Result: {result}")
```

**Code path:**
```python
value = input("Enter: ")
validated = validate_amount(value)
result = core.process(validated)
print(f"Result: {result}")
```

**→ [[01_overview]]** · **→ [[02_architecture]]** · **→ [[03_modules]]**
```

## 05_dependencies/README.md

```markdown
---
type: project-doc
section: dependencies
project: <Project Name>
tags: [dependencies, imports]
---

# 🔗 <Project Name> — Dependencies

## 📊 Import Graph

```
main.py
  │
  └── module.py
        │
        └── submodule.py
```

## 📦 Library Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `next` | 16.x | React framework |
| `react` | 19.x | UI library |

## 🌐 External Services

| Service | Integration | Purpose |
|---------|-------------|---------|
| **Vercel** | Git push → deploy | Hosting |
| **Analytics** | `<Analytics />` in layout | Tracking |

**→ [[01_overview]]** · **→ [[06_gaps_and_todos]]**
```

## 06_gaps_and_todos/README.md

```markdown
---
type: project-doc
section: gaps
project: <Project Name>
tags: [gaps, todos, limitations]
---

# ⚠️ <Project Name> — Gaps & TODOs

## 🔴 Major Gaps

### 1. No Data Persistence 🗑️

```python
class Bank:
    def __init__(self):
        self.accounts = {}  # ← resets every run, no file save
```

All data is in-memory. No file I/O or database.

**Fix:** Add `save_to_file()` / `load_from_file()` using json or sqlite3.

## 📋 Priority Todo

- [ ] Add persistence layer
- [ ] Add input validation
- [ ] Write tests

**→ [[01_overview]]** · **→ [[05_dependencies]]**
```
