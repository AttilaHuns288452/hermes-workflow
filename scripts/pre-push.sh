#!/usr/bin/env bash
# Pre-push gate: the same checks .github/workflows/public-quality.yml runs,
# minus the slow frontend build. Install with:
#   ln -sf ../../scripts/pre-push.sh .git/hooks/pre-push
# Bypass once with:  git push --no-verify
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 1

# Pick an interpreter that actually has pytest. `python3` on PATH can be a
# Hermes-managed venv without it, which fails the gate for the wrong reason.
PY="${PYTHON:-}"
if [ -z "$PY" ]; then
  for cand in python3 python; do
    if command -v "$cand" >/dev/null 2>&1 && "$cand" -c 'import pytest' >/dev/null 2>&1; then
      PY="$cand"; break
    fi
  done
fi
if [ -z "$PY" ]; then
  for cand in "$HOME"/.hermes/installs/*/environments/*/venv/bin/python3; do
    if [ -x "$cand" ] && "$cand" -c 'import pytest' >/dev/null 2>&1; then
      PY="$cand"; break
    fi
  done
fi
[ -z "$PY" ] && PY=python3

fail=0
run() {
  local name="$1"; shift
  if "$@" >/dev/null 2>&1; then
    printf '  ok   %s\n' "$name"
  else
    printf '  FAIL %s\n' "$name"
    "$@" 2>&1 | tail -15 | sed 's/^/       /'
    fail=1
  fi
}

echo "pre-push gate  ($PY)"
run "validate_repo"         "$PY" scripts/validate_repo.py
run "audit_skills"          "$PY" scripts/audit_skills.py
run "audit_public_secrets"  "$PY" scripts/audit_public_secrets.py
run "pytest"                "$PY" -m pytest tests/test_public_validation.py -q
run "repo_drift"            "$PY" scripts/repo_drift.py
run "py_compile"            "$PY" -m py_compile scripts/repo_drift.py

if [ "$fail" -ne 0 ]; then
  echo
  echo "pre-push gate FAILED - push blocked."
  echo "Fix the failure above, or 'git push --no-verify' to bypass."
  exit 1
fi
echo "pre-push gate passed"
