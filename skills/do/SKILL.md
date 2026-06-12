---
name: do
description: Executes a task using the skills selected by the `decide` skill. Acts as the dispatcher that loads and applies the chosen skills to fulfill the user's request.
triggers:
  - after `decide` has identified relevant skills
---

# Do Skill

## Role
Receives the selected skills from `decide`, loads them, and applies them to execute the user's request.

## Workflow
1. Receive the skill selections from `decide`
2. Load each selected skill using `skill_view(name=...)`
3. Follow the instructions from each loaded skill
4. Execute the task using the appropriate tools and guidance
5. Report results back to the user

## Execution Pattern
- For single-skill tasks: load that skill, follow its workflow
- For multi-skill tasks: load all relevant skills, combine their guidance as needed
- For complex workflows: break into phases if the skills prescribe phased execution

## Output Format
State which skills were loaded and how they were applied:
- "Loaded skills: ..."
- "Execution approach: ..."
- "Results: ..."
