## Description:

Blender 3D Modeling gives agents access to AgentPMT-hosted headless Blender workflows for rendering model views and turntables, converting 3D formats, checking and repairing printability, slicing for printing, and running scoped Blender Python scripts.

This skill is ready for commercial/non-commercial use.

## Publisher:

[agentpmt](https://clawhub.ai/user/agentpmt)

### License/Terms of Use:

MIT-0

## Use Case:

Developers, technical artists, product teams, game asset teams, and 3D printing users can use this skill to process existing 3D model files through remote Blender actions. It supports preview renders, turntable videos, file conversion, printability analysis and repair, G-code generation, and custom Blender Python workflows.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: 3D model files or public model URLs are sent to AgentPMT for remote Blender processing.

Mitigation: Use the skill only for files the user is comfortable sharing with AgentPMT, and avoid including secrets or confidential material in prompts, filenames, URLs, or metadata.

Risk: The run_script action executes custom Blender Python in the provider's environment.

Mitigation: Review scripts before execution, keep scripts scoped to the requested output, and do not run code copied from untrusted prompts or files.

Risk: The security evidence flags unpinned setup install commands.

Mitigation: Prefer the ClawHub or OpenClaw setup path over unpinned npx fallback commands.

Risk: Automated mesh repair, slicing, and generated G-code may be unsuitable as source-of-truth production or printer input without review.

Mitigation: Review repaired models, printability results, slice previews, and generated G-code before using them for manufacturing or printing.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/agentpmt/skills/blender-3d-modeling)
- [AgentPMT marketplace product](https://www.agentpmt.com/marketplace/blender-3d-modeling)
- [AgentPMT publisher profile](https://clawhub.ai/user/agentpmt)
- [AgentPMT account MCP/REST setup](https://clawhub.ai/agentpmt/agentpmt-account-mcp-rest-api-setup)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown instructions with JSON action parameters and optional shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Guides agents to call remote AgentPMT actions that can return task IDs, JSON status, signed file URLs, rendered images, videos, model files, G-code, and Blender-generated artifacts.]

## Skill Version(s):

1.0.1 (source: server release evidence and skill frontmatter)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
