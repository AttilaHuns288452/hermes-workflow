# Security

This repository is public. Automated scanners are useful safeguards, not proof that every file or history revision is free of secrets.

## Automated checks

The `public-quality` CI workflow runs:

- `scripts/audit_skills.py` to validate skill frontmatter and scan `SKILL.md` files for credential-shaped values.
- `scripts/audit_public_secrets.py` to scan Git-tracked and non-ignored working-tree text files, including docs and generated site assets. It does not follow symlinks, skips binary files, and fails if a text file exceeds its scan-size limit or cannot be read.
- Repository tests, configuration validation, frontend lint, `npm run lint:skills`, and the frontend production build.

Secret-scan output contains file locations and pattern names only, not matched values. Detection is heuristic: unknown formats, encoded values, binary payloads, ignored files, or credentials present only in remote history may not be detected. Review findings before publishing, and do not treat a clean scan as a guarantee.

## Historical remediation

- **2026-09-16:** A prior public-history incident involving provider access tokens was recorded. The repository history was rewritten at that time; clones or caches created before that rewrite may still contain old blobs. Revoke any credential that may remain valid, and do not copy credentials from historical commits.
- **2026-08-14:** Local build artifacts containing machine-specific paths were removed from tracking, and ignore rules were added to reduce recurrence.
- **2026-08-14:** Earlier skill-sync material was reviewed for personal paths and credential-bearing configuration; a tracked bytecode cache was removed.

These are historical notes, not a statement that a comprehensive independent security audit has passed for the current revision.

## If you find a secret

1. Revoke or rotate it with the issuing provider immediately.
2. Remove it from the working tree and, if committed, follow the repository's history-remediation process.
3. Report the file location without pasting the value into a public issue, commit, or chat.

For setup, keep credentials in the active Hermes profile's environment file or auth store. Do not commit `.env` files, tokens, passwords, certificates, or private keys.
