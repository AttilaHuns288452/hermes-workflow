#!/usr/bin/env python3
"""
cc_orchestrate.py — CommandCode CLI orchestration layer with intelligent routing,
health checks, and automatic fallback for coding tasks.

Usage:
    python3 cc_orchestrate.py "Your task here"
    python3 cc_orchestrate.py --task "Fix the parser bug" --profile large-engineering
    python3 cc_orchestrate.py --health-check deepseek-v4-flash

Routing priority:
    1. deepseek/deepseek-v4-flash
    2. meituan/longcat-2.0:free
    3. poolside/laguna-s-2.1-free
    4. Best available free model
    5. Local Ollama (qwen2.5-coder:3b)
"""

import argparse
import datetime
import json
import logging
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# Configuration
LOG_DIR = Path.home() / ".hermes" / "logs" / "cc-orchestrate"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "orchestrate.log"),
    ],
)
log = logging.getLogger("cc-orchestrate")

# Model identifiers (CommandCode format)
MODELS = {
    "deepseek-v4-flash": "deepseek/deepseek-v4-flash",
    "longcat-2.0": "meituan/longcat-2.0:free",
    "laguna-s21": "poolside/laguna-s-2.1-free",
    "free-fallback": "meituan/longcat-2.0:free",
    "ollama-local": "qwen2.5-coder:3b",
}

# Routing priority order
ROUTING_LADDER = [
    "deepseek-v4-flash",
    "longcat-2.0",
    "laguna-s21",
    "free-fallback",
    "ollama-local",
]

# Task profiles
TASK_PROFILES = {
    "large-engineering": {
        "description": "Large software-engineering tasks",
        "models": ["deepseek-v4-flash", "longcat-2.0", "laguna-s21"],
        "retry_on_failure": True,
    },
    "architecture": {
        "description": "Architecture/reasoning tasks",
        "models": ["deepseek-v4-flash", "longcat-2.0", "laguna-s21"],
        "retry_on_failure": True,
    },
    "simple-edit": {
        "description": "Simple edits, formatting, small scripts",
        "models": ["deepseek-v4-flash", "laguna-s21", "free-fallback"],
        "retry_on_failure": False,
    },
    "long-context": {
        "description": "Extremely long-context tasks",
        "models": ["deepseek-v4-flash", "longcat-2.0"],
        "retry_on_failure": True,
    },
    "local-only": {
        "description": "Local-only/private tasks",
        "models": ["ollama-local"],
        "retry_on_failure": False,
    },
}

# Health check cache (avoid redundant checks)
_health_cache: dict[str, tuple[bool, float]] = {}
HEALTH_CACHE_TTL = 60  # seconds


def is_model_healthy(model_name: str) -> bool:
    """Quick health check for a model by attempting a minimal completion."""
    now = time.time()
    if model_name in _health_cache:
        healthy, ts = _health_cache[model_name]
        if now - ts < HEALTH_CACHE_TTL:
            return healthy

    model_id = MODELS.get(model_name, model_name)
    try:
        cmd = [
            "commandcode",
            "-p",
            "Say 'ok' if you can respond.",
            "--model",
            model_id,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            healthy = "ok" in (result.stdout + result.stderr).lower()
        elif result.returncode == 10:
            healthy = False
        else:
            healthy = False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        healthy = False

    _health_cache[model_name] = (healthy, now)
    return healthy


def classify_task(task: str) -> str:
    """Classify task into a profile based on content heuristics."""
    task_lower = task.lower()

    if any(kw in task_lower for kw in ["private", "local only", "offline", "no cloud", "sensitive"]):
        return "local-only"

    if any(kw in task_lower for kw in ["fix typo", "format", "rename", "small change", "quick fix", "one line", "simple edit"]):
        return "simple-edit"

    if any(kw in task_lower for kw in ["long context", "entire codebase", "large repository", "thousands of lines", "whole project"]):
        return "long-context"

    if any(kw in task_lower for kw in ["architecture", "design", "system design", "refactor", "migrate", "strategy", "plan"]):
        return "architecture"

    return "large-engineering"


def select_model(task: str, profile: str | None = None) -> list[str]:
    """Select ordered list of models for a task."""
    if profile and profile in TASK_PROFILES:
        return TASK_PROFILES[profile]["models"]
    profile = classify_task(task)
    return TASK_PROFILES[profile]["models"]


def invoke_cc(task: str, model_name: str, session_name: str | None = None) -> tuple[bool, str, str]:
    """
    Invoke commandcode with a specific model.
    Returns (success, stdout, stderr).
    """
    model_id = MODELS.get(model_name, model_name)
    cmd = ["commandcode", "-p", task, "--model", model_id]

    if session_name:
        cmd.extend(["--name", session_name])

    log.info(f"Invoking: {' '.join(cmd[:6])}... model={model_name}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        success = result.returncode == 0
        if not success:
            combined = (result.stdout + result.stderr).lower()
            if "insufficient credits" in combined or "purchase more" in combined:
                log.warning(f"Credit exhausted for {model_name}")
                return False, result.stdout, f"CREDIT_EXHAUSTED: {result.stderr}"
        return success, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "TIMEOUT: Command timed out after 300s"
    except FileNotFoundError:
        return False, "", "commandcode not found in PATH"


def run_task(
    task: str,
    profile: str | None = None,
    session_name: str | None = None,
    max_retries: int = 1,
) -> dict:
    """
    Run a task with automatic model selection and fallback.
    Returns a result dict with full execution log.
    """
    execution_id = f"cc-{datetime.datetime.now():%Y%m%d_%H%M%S}"
    models_to_try = select_model(task, profile)

    result = {
        "execution_id": execution_id,
        "task": task,
        "profile": profile or classify_task(task),
        "selected_models": [],
        "successful_model": None,
        "fallback_reason": None,
        "attempts": [],
        "success": False,
        "stdout": "",
        "stderr": "",
        "duration_seconds": 0,
        "timestamp": datetime.datetime.now().isoformat(),
    }

    start_time = time.time()

    for model_name in models_to_try:
        if model_name not in ROUTING_LADDER:
            continue

        model_id = MODELS.get(model_name, model_name)
        attempt = {
            "model": model_name,
            "model_id": model_id,
            "start_time": datetime.datetime.now().isoformat(),
        }

        if not is_model_healthy(model_name):
            attempt["status"] = "unhealthy"
            attempt["reason"] = "Health check failed"
            result["attempts"].append(attempt)
            log.warning(f"Model {model_name} unhealthy, skipping")
            continue

        success, stdout, stderr = invoke_cc(task, model_name, session_name)

        attempt["status"] = "success" if success else "failed"
        attempt["duration"] = time.time() - start_time
        attempt["stdout_preview"] = stdout[:200] if stdout else ""
        attempt["stderr_preview"] = stderr[:200] if stderr else ""

        if success:
            result["successful_model"] = model_name
            result["success"] = True
            result["stdout"] = stdout
            result["stderr"] = stderr
            log.info(f"Success with {model_name}")
            break
        else:
            result["fallback_reason"] = stderr[:100] if stderr else "Unknown error"
            log.warning(f"Failed with {model_name}: {stderr[:100]}")

            retryable = any(
                kw in (stderr + stdout).lower()
                for kw in ["timeout", "rate limit", "503", "502", "504", "connection", "econnreset"]
            )
            if retryable and max_retries > 0:
                log.info(f"Retrying {model_name} (transient failure)")
                attempt["retried"] = True
                success, stdout, stderr = invoke_cc(task, model_name, session_name)
                if success:
                    result["successful_model"] = model_name
                    result["success"] = True
                    result["stdout"] = stdout
                    result["stderr"] = stderr
                    break

        result["attempts"].append(attempt)

    result["duration_seconds"] = round(time.time() - start_time, 2)
    result["selected_models"] = [a["model"] for a in result["attempts"]]

    log_path = LOG_DIR / f"{execution_id}.json"
    with open(log_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    log.info(f"Saved execution log: {log_path}")

    return result


def main():
    parser = argparse.ArgumentParser(description="CommandCode orchestration layer")
    parser.add_argument("task", nargs="?", help="Task description")
    parser.add_argument("--profile", choices=list(TASK_PROFILES.keys()), help="Task profile")
    parser.add_argument("--session", help="Session name for continuity")
    parser.add_argument("--health-check", help="Health check a specific model")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--dry-run", action="store_true", help="Show routing without executing")
    args = parser.parse_args()

    if args.health_check:
        healthy = is_model_healthy(args.health_check)
        print(f"{args.health_check}: {'healthy' if healthy else 'unhealthy'}")
        sys.exit(0 if healthy else 1)

    if args.list_models:
        print("Available models:")
        for name, model_id in MODELS.items():
            print(f"  {name}: {model_id}")
        print(f"\nRouting ladder: {' -> '.join(ROUTING_LADDER)}")
        sys.exit(0)

    if not args.task:
        parser.error("task is required")

    if args.dry_run:
        profile = args.profile or classify_task(args.task)
        models = select_model(args.task, args.profile)
        print(f"Task: {args.task}")
        print(f"Profile: {profile}")
        print(f"Models to try: {models}")
        sys.exit(0)

    result = run_task(args.task, args.profile, args.session)

    if result["success"]:
        print(result["stdout"])
    else:
        print(f"FAILED: All models exhausted", file=sys.stderr)
        for attempt in result["attempts"]:
            print(f"  - {attempt['model']}: {attempt['status']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
