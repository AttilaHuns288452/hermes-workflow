#!/usr/bin/env bash
# Pre-push gate: the same checks .github/workflows/public-quality.yml runs,
# minus the slow frontend build. Add it with:
#   ln -sf ../../scripts/pre-push.sh .git/hooks/pre-push
# Bypass once with:  git push --no-verify
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 1

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

echo "pre-push gate"
run "validate_repo"         python3 scripts/validate_repo.py
run "audit_skills"          python3 scripts/audit_skills.py
run "audit_public_secrets"  python3 scripts/audit_public_secrets.py
run "pytest"                python3 -m pytest tests/test_public_validation.py -q
run "repo_drift"            python3 scripts/repo_drift.py
run "py_compile"            python3 -m py_compile scripts/repo_drift.py

if [ "$fail" -ne 0 ]; then
  echo
  echo "pre-push gate FAILED - push blocked."
  echo "Fix the failure above, or 'git push --no-verify' to bypass."
  exit 1
fi
echo "pre-push gate passed"
