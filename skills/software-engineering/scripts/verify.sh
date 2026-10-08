#!/usr/bin/env bash
# Runnable self-check for the Universal Software Engineering capability.
# Fails if: the skill stops resolving, retrieval stops surfacing it for core
# engineering queries, or secrets leak into skill content.
set -u
SKILL_DIR="$HOME/.hermes/skills/software-engineering"
FAIL=0

for f in SKILL.md references/production-domains.md; do
  [ -s "$SKILL_DIR/$f" ] || { echo "MISSING $f"; FAIL=1; }
done

# Retrieval: every query must surface software-engineering in top 5,
# unless a dedicated specialist legitimately outranks it (specific wins).
for q in "prevent double booking" "idempotent payment retry" "database migration rollback" \
         "cache invalidation after mutation" "make checkout production safe" \
         "prevent overselling inventory" "streaming reliability retries" \
         "transaction history audit" "incident response production"; do
  hits=$(python3 "$HOME/.hermes/scripts/lightrag_find.py" "$q" 5)
  if ! echo "$hits" | grep -q "software-engineering"; then
    # acceptable if a domain-specific skill owns the query instead
    if echo "$hits" | grep -qE "database-migrations|deployment-patterns|security|production-audit"; then
      echo "OK (specialist owns): $q"
    else
      echo "RETRIEVAL MISS: $q"; FAIL=1
    fi
  fi
done

# Secrets scan: no key/token patterns in skill content
grep -rEn "(sk-[A-Za-z0-9]{16,}|sb_secret_[A-Za-z0-9_-]{10,}|am_sk_[A-Za-z0-9]{10,}|BEGIN [A-Z ]*PRIVATE KEY)" \
  "$SKILL_DIR" && { echo "SECRET LEAK"; FAIL=1; }

[ "$FAIL" -eq 0 ] && echo "PASS: skill present, retrieval OK, no secrets"
exit $FAIL
