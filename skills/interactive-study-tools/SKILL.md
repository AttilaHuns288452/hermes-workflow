---
name: interactive-study-tools
description: "Build single-file HTML study sites with reviewer and quiz."
category: creative
version: 1.0.0
---

# Interactive Study Tools

Build single-file HTML study websites combining structured reviewer content with interactive quiz engines. One file, no build step, no frameworks.

## When to Use

- User asks for a "study website", "reviewer", "quiz", "exam prep tool", or "learning application"
- Converting documents (PDF, docx) into interactive web-based study material
- Building multiple-choice quiz systems with scoring, results, and topic analysis

## Architecture

Single self-contained HTML file with inline CSS + JS:

```
const REVIEWER = [{id, title, content}, ...];
const QUIZ = [{id, q, opts, ans, topic, src, diff}, ...];
let state = { view, currentQ, answers, marked, submitted, results };
```

Separate data from presentation. Quiz questions are a structured JS array.

## Quiz Data Schema

```javascript
{
  id: Number,
  q: String,
  opts: [String x 4],
  ans: Number,  // index 0-3
  topic: String,
  src: String,
  diff: "easy"|"medium"|"hard"
}
```

## Answer Distribution Balancing

Naive question creation skews toward one letter. Use a placement helper:

```python
from collections import Counter
pos_count = Counter()
def add_question(qid, q, correct, wrongs, topic, src, diff):
    target = min(range(4), key=lambda p: pos_count[p])
    opts = [""] * 4
    opts[target] = correct
    wi = 0
    for i in range(4):
        if i != target:
            opts[i] = wrongs[wi]; wi += 1
    pos_count[target] += 1
```

For 75 questions yields ~19/19/19/18 distribution.

## Delegation Timeout Pitfall

Subagents time out (480s) on single-file generation exceeding ~40KB. For study sites with 75+ questions (70-90KB output), build directly. Don't delegate.

## Content Extraction Pipeline

1. Extract text: python-docx for .docx, PyPDF2 for PDF
2. Parse into topic sections: definitions, examples, formulas, distinctions
3. Build reviewer as HTML strings with semantic tags
4. Build quiz questions with plausible distractors
5. Wire: reviewer practice button -> quiz; quiz results -> reviewer review link

## Required Quiz UX

- One question at a time, A/B/C/D buttons
- Progress bar + question counter
- Question navigation grid with answered/marked state
- Mark for review
- Submit with confirmation
- Results: score, percentage, topic breakdown, weakest/strongest
- Incorrect review: your answer, correct answer, explanation
- Randomize question + option order
- Keyboard shortcuts (arrows, 1-4)
- localStorage for mistake persistence

## Required Reviewer UX

- Sidebar navigation, search/filter
- Each section: title, definition, intuition, formal definition, examples, tables, exam tips, traps, memory cues
- Practice button per section filters quiz

## Design

- Dark theme, single accent color, CSS custom properties
- Responsive sidebar (hamburger on mobile)
- Color-coded indicators: blue=definition, green=formula, yellow=tip, red=trap
- Monospace for formulas, Unicode math symbols
