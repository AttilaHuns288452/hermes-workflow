# Documentation Layer Template

For this user, every project needs three identity docs. The moldguard project is the reference implementation.

## README.md

```markdown
# <Project Name> — <tagline>

**Prototype** for <context>. <one-line what it does>.

Live: <url>

## What it does

<2-3 sentences: the job, the audience, the key differentiator.>

## Pages

| File | Route | Purpose |
|---|---|---|
| ... | ... | ... |

## Architecture

<file tree + one-line per directory/module>

## Design system

See `DESIGN.md`. <world name> — <palette summary>.

## Data status

<what's mock vs real, honesty rules>

## Run locally

```bash
cd <dir>
python3 -m http.server 8765
```

## Verification

```bash
for f in js/*.js; do node -c "$f" || echo "FAIL: $f"; done
for p in index.html ...; do curl -s -o /dev/null -w "%{http_code} $p\n" http://localhost:8765/$p; done
```

## Status

<current state, known gaps>
```

## PRODUCT.md

```markdown
# Product

## Platform
web

## Stack
<static/framework, build/no-build, deps>

## Users
- **Primary:** <who>
- **Secondary:** <who>

## Product Purpose
<what problem it solves, for whom, what success looks like>

## Positioning
<the differentiator — what it is and isn't>

## Information architecture
<the flow/spine>

## Design
`DESIGN.md` is the visual contract.

## Honesty rules
- <no fake data, no inflated metrics, no black box, no store>

## Constraints
- <no backend, no real auth, no live data>

## Status
<current>
```

## messaging.md

```markdown
# <Project> — Messaging Fact-Check Register

**Purpose:** every claim the prototype makes is tracked here.

- **Source:** <where data comes from>
- **Pages:** <all html files>

---

## Claim register

| # | Claim | Where used | Source | Status |
|---|---|---|---|---|
| C1 | ... | ... | ... | ✅ |

## Honest omissions (do NOT add without flagging)
- <no real X, no inflated Y, no fabricated Z>

## Visual-only claims (design system)
| # | Claim | Where | Source | Status |
|---|---|---|---|---|

## Fact-check method
1. Every piece of visible copy traced to a register row
2. Mock data ranges verified realistic
3. No inflated metrics
4. All claims about "real" data labeled prototype/mock

## Open questions for next iteration
| # | Question | Owner | Blocks |
|---|---|---|---|
```

## When to create

- User says "improve" / "redesign" a site → check for docs FIRST
- Docs missing → create all three before visual work
- Docs exist → read them FIRST, they outrank assumptions
- User says "same documentation as moldguard" → use this template
