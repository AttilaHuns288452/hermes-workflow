#!/usr/bin/env python3
"""
ECC Agent Runner — Reads an ECC agent .md spec, strips frontmatter + defense baseline,
extracts the actionable prompt body, and provides it as a structured prompt for
the free model chain (OpenCode/Freebuff/FreeLLMAPI/OpenRouter).

Usage:
    python ecc-runner.py <agent_name> [task_arg...]

    agent_name:  e.g. code-simplifier, comment-analyzer, silent-failure-hunter
    task_arg:    Optional extra context (file paths, code snippet, shell command)

Output: Writes to stdout:
    # ECC Agent: <agent_name> (free-model-compatible)
    ## Prompt
    <stripped agent body>
    
    ## Task Context
    <any task args>

Exit codes:
    0 — Success, agent found and extracted
    1 — Agent file not found
    2 — Agent file parse error
"""

import json
import os
import re
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────
ECC_DIR = Path.home() / "Documents" / "Projects" / "ECC" / "agents"

# Agents that are safer on free models (analysis-heavy, no dangerous writes)
# Known-good set:
SAFE_AGENTS = {
    "comment-analyzer": {"skill_name": "ecc-comment-analyzer", "best_model": "opencode/deepseek-v4-flash-free"},
    "silent-failure-hunter": {"skill_name": "ecc-silent-failure-hunter", "best_model": "opencode/deepseek-v4-flash-free"},
    "pr-test-analyzer": {"skill_name": "ecc-pr-test-analyzer", "best_model": "opencode/deepseek-v4-flash-free"},
    "type-design-analyzer": {"skill_name": "ecc-type-design-analyzer", "best_model": "opencode/deepseek-v4-flash-free"},
    "code-simplifier": {"skill_name": "ecc-code-simplifier", "best_model": "opencode/deepseek-v4-flash-free"},
    "doc-updater": {"skill_name": "ecc-doc-updater", "best_model": "opencode/deepseek-v4-flash-free"},
    "database-reviewer": {"skill_name": "ecc-database-reviewer", "best_model": "opencode/deepseek-v4-flash-free"},
    "refactor-cleaner": {"skill_name": "ecc-refactor-cleaner", "best_model": "opencode/deepseek-v4-flash-free"},
    "performance-optimizer": {"skill_name": "ecc-performance-optimizer", "best_model": "opencode/deepseek-v4-flash-free"},
    # Vision agents — need multimodal
    "image-prompt-engineer": {"skill_name": "ecc-image-prompt-engineer", "best_model": "opencode/mimo-v2.5-free"},
    "visual-storyteller": {"skill_name": "ecc-visual-storyteller", "best_model": "opencode/mimo-v2.5-free"},
    "ui-designer": {"skill_name": "ecc-ui-designer", "best_model": "opencode/mimo-v2.5-free"},
}

# All 64 ECC agents mapped to free-model compatibility tiers
ALL_AGENTS = {}

def index_all_agents():
    """Index all ECC agent .md files with their tier info."""
    if not ECC_DIR.exists():
        return {}
    agents = {}
    for f in sorted(ECC_DIR.glob("*.md")):
        name = f.stem
        content = f.read_text(encoding="utf-8", errors="replace")
        
        # Extract model from frontmatter
        model_match = re.search(r'^model:\s*(.*)', content, re.MULTILINE)
        if model_match:
            model = model_match.group(1).strip().strip('"\'')
        else:
            model = "unknown"
        
        # Tier classification for free model compatibility
        if model == "haiku":
            tier = "strong"     # lowest requirement, runs great on free
        elif model == "sonnet":
            tier = "good"       # mid-tier, most agents run fine on free
        elif model == "opus":
            tier = "limited"    # complex agents, may degrade on free
        else:
            tier = "unknown"    # unclassified model — assume limited as conservative fallback
        
        agents[name] = {"model": model, "tier": tier, "file": str(f)}
    
    return agents


def strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter (--- delimited)."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return content


def strip_defense_baseline(content: str) -> str:
    """Remove the common Prompt Defense Baseline section (identical across all agents)."""
    # Remove from "## Prompt Defense Baseline" to the next top-level heading
    lines = content.split("\n")
    result = []
    in_defense = False
    for line in lines:
        if line.strip().startswith("## Prompt Defense Baseline"):
            in_defense = True
            continue
        if in_defense:
            # End at next top-level heading or end of section
            if line.strip().startswith("#") and not line.strip().startswith("##"):
                in_defense = False
                result.append(line)
                continue
            if line.strip().startswith("##") and "Prompt Defense" not in line:
                in_defense = False
                result.append(line)
                continue
            # Skip defense lines
            continue
        result.append(line)
    
    # Clean up excessive blank lines
    text = "\n".join(result)
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    return text.strip()


def extract_agent_body(agent_name: str) -> tuple[str | None, str | None]:
    """
    Extract the actionable body from an ECC agent .md file.
    
    Returns: (body_text, error_msg)
    """
    agent_file = ECC_DIR / f"{agent_name}.md"
    if not agent_file.exists():
        # Try without .md extension lookup
        alt_path = ECC_DIR / agent_name
        if alt_path.exists() and alt_path.is_file():
            agent_file = alt_path
        else:
            return None, f"Agent '{agent_name}' not found at {agent_file}"
    
    content = agent_file.read_text(encoding="utf-8", errors="replace")
    
    # Remove frontmatter
    body = strip_frontmatter(content)
    
    # Remove defense baseline
    body = strip_defense_baseline(body)
    
    # Add a header clarifying this has been adapted for free model usage
    preamble = (
        "[ECC Agent Adapted for Free Model]\n"
        "[Original model requirement: stripped — running on opencode/free model chain]\n"
        "[Prompt Defense Baseline removed — standard Hermes safety applies]\n\n"
    )
    
    body = preamble + body
    return body, None


def extract_agent_frontmatter(agent_name: str) -> dict | None:
    """Extract frontmatter metadata from an agent .md file."""
    agent_file = ECC_DIR / f"{agent_name}.md"
    if not agent_file.exists():
        return None
    
    content = agent_file.read_text(encoding="utf-8", errors="replace")
    
    # Extract frontmatter between --- delimiters
    m = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return {"name": agent_name}
    
    frontmatter = m.group(1)
    meta = {"name": agent_name}
    
    for line in frontmatter.strip().split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip().strip('"\'')
    
    return meta


def list_available_agents(tier: str = "all") -> list[dict]:
    """List available ECC agents, optionally filtered by free-model compatibility tier."""
    agents = index_all_agents()
    results = []
    for name, info in sorted(agents.items()):
        meta = extract_agent_frontmatter(name) or {}
        if tier == "all" or info["tier"] == tier:
            results.append({
                "name": name,
                "model": info["model"],
                "tier": info["tier"],
                "description": meta.get("description", "No description"),
                "tools": meta.get("tools", "unknown"),
            })
    return results


# ── CLI Entry Point ────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ECC Agent Runner — Hermes Bridge", file=sys.stderr)
        print("", file=sys.stderr)
        print("Usage:", file=sys.stderr)
        print(f"  python {sys.argv[0]} <agent_name> [task_context...]", file=sys.stderr)
        print("", file=sys.stderr)
        print("  agent_name   one of the 64 ECC agents (e.g. code-simplifier)", file=sys.stderr)
        print("  task_context  optional file paths, code, or instructions", file=sys.stderr)
        print("", file=sys.stderr)
        print("Commands:", file=sys.stderr)
        print(f"  python {sys.argv[0]} list                      List all 64 agents", file=sys.stderr)
        print(f"  python {sys.argv[0]} list-safe                 List free-model-safe agents", file=sys.stderr)
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        agents = list_available_agents()
        print(f"# ECC Agents Available: {len(agents)}")
        print("")
        print("| Agent | Native Model | Free Tier | Description |")
        print("|-------|-------------|-----------|-------------|")
        for a in agents:
            print(f"| {a['name']} | {a['model']} | {a['tier']} | {a['description'][:80]} |")
        sys.exit(0)
    
    if cmd == "list-safe":
        agents = list_available_agents("good") + list_available_agents("strong")
        print(f"# ECC Agents Good for Free Models: {len(agents)}")
        print("")
        print("| Agent | Native Model | Free Tier | Description |")
        print("|-------|-------------|-----------|-------------|")
        for a in agents:
            print(f"| {a['name']} | {a['model']} | {a['tier']} | {a['description'][:80]} |")
        sys.exit(0)
    
    # Extract and print the agent prompt
    body, error = extract_agent_body(cmd)
    if error:
        print(error, file=sys.stderr)
        
        # Suggest similar names
        agents = index_all_agents()
        similar = [n for n in agents if cmd in n or n in cmd]
        if similar:
            print(f"Did you mean: {', '.join(similar[:5])}?", file=sys.stderr)
        sys.exit(1)
    
    meta = extract_agent_frontmatter(cmd) or {}
    safe_info = SAFE_AGENTS.get(cmd, {})
    tier = safe_info.get("best_model", "opencode/deepseek-v4-flash-free")
    
    print(f"# ECC Agent: {meta.get('name', cmd)}")
    print(f"# Description: {meta.get('description', 'N/A')}")
    print(f"# Original model: {meta.get('model', 'unknown')}")
    print(f"# Running on: {tier} (free model chain)")
    print(f"# Tools: {meta.get('tools', 'unknown')}")
    print()
    print(body)
    print()
    
    # Task context if provided
    if len(sys.argv) > 2:
        task_context = " ".join(sys.argv[2:])
        print("## Task Context")
        print(task_context)
