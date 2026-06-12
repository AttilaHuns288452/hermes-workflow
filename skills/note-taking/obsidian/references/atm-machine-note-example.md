# ATM Machine — Note Quality Reference Standard

This file documents the ATM Machine project's Obsidian vault structure as a concrete quality benchmark. Future project notes should match or exceed this level of detail.

## Vault Structure

```
Projects/ATM Machine/
├── ATM Machine.md              ← Main project note (primary reference)
├── ATM Design.md               ← Design specification note
├── FILE TREE & GRAPH.md        ← Structure + diagrams
├── Core/
│   ├── Bank.md                 ← Central registry class
│   ├── Account.md              ← Account class
│   └── Transaction.md          ← Transaction dataclass
├── UI/
│   └── ATM UI.md               ← Console interface
├── Utils/
│   └── Validators.md           ← Input validation
├── Tests/
│   └── ATM Tests.md            ← Unit test suite
└── Tags/
    └── README.md               ← Tag index
```

## Quality Characteristics

| Aspect | ATM Machine | What to Always Include |
|--------|------------|----------------------|
| **Overview paragraph** | ✅ "A console-based ATM simulation built with Python." | One-paragraph elevator pitch |
| **Key Features** | ✅ Table with 5 features, each with brief explanation | Bullet list with \<feature\> — \<explanation\> |
| **Project Structure** | ✅ Text tree with file paths and one-line purpose per file | Text tree, every file annotated |
| **Architecture section** | ✅ Per-class breakdown: purpose, methods, validation, flow | Tables or bullets per class/module |
| **Code Patterns** | ✅ Python example showing account creation, deposit, withdraw | Concrete code snippet showing core API usage |
| **Related Files** | ✅ 8 wikilinks, each with purpose | [[Note]] — relationship description |
| **Mermaid Graph** | ✅ Full vault graph showing note/folder relationships | graph TD with \<br/\> labels |
| **Tags** | ✅ 6 tags at bottom | #project #language #framework #category |
| **Supporting notes** | ✅ Each class has its own note with methods table | Methods table, class definition, position graph |
| **Design note** | ✅ Separate design note with architecture + tech stack | Architecture diagram, design tokens if applicable |

## Minimum Bar

If you're short on time, the **irreducible minimum** for any project note is:
1. Title + one-paragraph summary
2. Project structure tree
3. Architecture with class/component descriptions
4. Related Files with wikilinks (at least parent note)
5. Mermaid knowledge graph map
6. Tags

## Example: A subpar note vs. ATM-quality note

| Aspect | Subpar | ATM-quality |
|--------|--------|-------------|
| Summary | "A countdown timer." | "A polished dark-theme countdown timer web app with keyboard shortcuts, presets, sound alerts, and a visual progress bar." |
| Architecture | None | State machine diagram (4 states), 5 component descriptions, method tables |
| Code | None | 3 code blocks showing timer tick, audio beep, keyboard bindings |
| Links | None | 2 wikilinks to related notes |
| Graph | None | Mermaid graph showing 6 node relationships |
| Tags | None | 5 tags at bottom |
