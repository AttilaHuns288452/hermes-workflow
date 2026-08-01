---
name: local-ai-routing
description: Use local AI models first whenever they are capable, escalating to cloud models only when the task exceeds local capabilities
tags:
  - local-ai
  - model-routing
  - qwen
  - gemma
  - efficiency
triggers:
  - local mode
  - use local model
  - local only
  - offline mode
  - run locally
  - no cloud
---

# Local AI Routing Skill

## Purpose

Use local models first whenever they are capable of completing the task with good quality. Escalate to cloud models only when the task exceeds local capabilities (very large codebases, frontier-level reasoning, extensive research, or long autonomous agent execution).

Prioritize:
1. Accuracy
2. Model specialization
3. Speed
4. Resource efficiency

---

## Model Router

### 🧠 Gemma4

**Primary Role:** General reasoning and multimodal assistant.

**Strengths:**
- Deep reasoning
- Long-form writing
- Documentation
- Summarization
- Explanation
- Brainstorming
- Instruction following
- Long-context conversations
- Image understanding (where supported by the local build)

**Preferred Tasks:**
- Explain concepts
- Write documentation
- Design documents
- Reports
- Technical writing
- Research summaries
- Architecture discussions
- General conversations

**Avoid:**
- Large-scale code generation
- Repository-wide refactoring
- Heavy programming tasks better suited to Qwen

---

### 💻 Qwen3:4B

**Primary Role:** Default local assistant.

**Strengths:**
- Coding
- Planning
- General reasoning
- Tool use
- Agent workflows
- Problem solving
- Project planning
- Software design
- Debugging

**Preferred Tasks:**
- Default model for most requests
- Programming
- Software engineering
- Algorithms
- Data structures
- Terminal commands
- Git
- Development workflows
- Architecture planning
- Automation

**Avoid:**
- OCR
- Image analysis

---

### 👨‍💻 Qwen2.5-Coder:3B

**Primary Role:** Coding specialist.

**Strengths:**
- Code generation
- Refactoring
- Bug fixing
- Unit tests
- Code review
- Boilerplate
- API implementation
- Small-to-medium programming tasks

**Preferred Tasks:**
- Implement functions
- Fix bugs
- Refactor code
- Explain code
- Generate tests
- Convert between languages
- Optimize code

**Avoid:**
- General knowledge
- Creative writing
- Long-form planning

---

### 👁️ Qwen2.5-VL:3B

**Primary Role:** Vision model.

**Strengths:**
- OCR
- Screenshots
- UI analysis
- Image understanding
- Charts
- Tables
- PDFs
- Diagrams
- Error screenshots

**Preferred Tasks:**
- Analyze screenshots
- Read documents
- Explain UI
- Extract text
- Review web/app designs
- Detect visual issues

**Avoid:**
- Large coding tasks unless image understanding is required

---

## Routing Rules

If the request contains:

| Trigger | Route To |
|---------|----------|
| Images, screenshots, PDFs, diagrams, charts | Qwen2.5-VL first |
| Programming, debugging, algorithms, software engineering | Qwen3 by default; Qwen2.5-Coder for implementation/refactoring/code review |
| Writing, documentation, explanations, reports, summaries | Gemma4 |
| General chat or mixed tasks | Qwen3 |

---

## Escalation Rules

Escalate to cloud models **only** when local quality is likely to be insufficient.

**Examples:**
- Very large repositories
- Complex multi-file refactoring
- Frontier-level reasoning
- Advanced research requiring current web knowledge
- Long-running autonomous agent workflows
- Tasks that exceed local context limits

Always attempt local execution first when practical.

---

## Model Priority

1. **Qwen3:4B** — default
2. **Qwen2.5-Coder:3B** — coding specialist
3. **Gemma4** — reasoning and writing
4. **Qwen2.5-VL:3B** — vision

Only escalate when a cloud model is expected to provide a meaningful improvement in quality or capability.

---

## Ponytail Mode

Ponytail level: **full**. Lazy senior developer mode is active.

- No unrequested abstractions
- Shortest working diff wins
- Deletion over addition
- Boring over clever
- Fewest files possible

Mark deliberate simplifications with `// ponytail:` comments.
