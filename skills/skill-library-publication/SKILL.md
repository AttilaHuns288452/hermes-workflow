---
name: skill-library-publication
description: Use when the public skill repo drifts from the live tree.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [skills, git, publishing, sync]
    related_skills: [external-skill-import, git-repo-hygiene, ecosystem-audit]
---

# Publishing a Skill Library

Syncing the public repo of skills (the workflow shared with classmates, friends, peers) against the live `~/.hermes/skills` tree. The repo is a **subset by design**: no credentials, no machine state, no private project facts. Direction matters: the live tree is the source, the repo is the publication.

## When to Use

- The user says their public repo is stale, missing skills, or differs from their setup.
- After importing packs locally and the repo should carry them.
- Before telling a user "your repo has X and your setup has Y" — measure it first.

## Procedure

1. **Inventory both sides by frontmatter `name:`**, falling back to the directory name when YAML fails to parse. Include every root from `skills.external_dirs` in the live set or externally-installed skills get mislabelled as missing.
2. **Classify every name**:
   - shared with different bytes: `git log -1 --format=%ct -- <repo path>` against the local file's mtime. Repo older than the local edit = stale publication.
   - local-only = work never published.
   - repo-only = library breadth the live profile does not install (keep it; it is what readers get).
3. **Settle licensing with an attribution file, not by withholding the pack.** The repo's own LICENSE covers only the skills you authored; imported packs keep their own terms, and the default answer is a root `ATTRIBUTION.md` table (pack → upstream URL → license → what was excluded) rather than leaving the pack out. Verify licences from the upstream API instead of inferring them from the tree or from memory:
   ```bash
   gh api repos/<owner>/<repo> --jq '.license.spdx_id'
   ```
   A vendored pack usually carries no LICENSE file locally even when upstream is MIT/Apache-2.0, so "no LICENSE in its tree" is NOT evidence of unlicensed. Record what the API returns verbatim: `NOASSERTION` or a named non-OSI license is written as its own entry (with the reason), never rounded to MIT because the project looks open. State the excluded subsets too — paid-service-only material (a vendor's cloud/build/live-update skills) is a deliberate omission a reader should see, not a silent gap. Only genuinely unlicensed material stays unpublished, and the commit message names it.
4. **Scan every staged file** before committing: key shapes (`sk-`, `osb_`, `sbp_`, `ghp_`, `AKIA`, PRIVATE KEY blocks), private paths (`~/.hermes/mcp-tokens`, `~/.ssh`), and absolute home paths (report those; rewrite only if asked).
5. **Publish on a branch, then be explicit about WHERE it landed**: `git checkout -b sync/<topic>-<date>`, commit with the counts and what was held, `git push -u origin <branch>`. A branch push is NOT "the repo is updated", and reporting it as done is the failure this step exists to prevent. Merging to the default branch is still the owner's call, but state the branch, the default branch's commit, and whether the deploy source carries it in the same breath. **When the user asks "is it updated?", verify against the default branch and the deploy source, never against your working branch**: find which branch deploys (`gh api repos/<owner>/<repo>/pages --jq .source.branch`, or the platform config in `.github/workflows/`), check that ref with `git ls-tree -r --name-only origin/<default> | grep <path>` or `git cat-file -e origin/<default>:<path>`, and only then answer yes. Work sitting on a feature branch while the deploy source lags reads to the user as "nothing happened". If there is no branch protection blocking it and the change was meant to be live, open the PR, report its CI state honestly (an account billing lock is not a code failure), and merge. **After merging a PR, a later `git push origin HEAD:master` from the same local branch is rejected as non-fast-forward** — the remote merge commit is not in your history: `git fetch` then `git merge origin/master` locally (the merge is trivial unless files changed on both sides) and push again. Do not force-push over a merge commit to avoid the merge.
6. **Run the repo's own gate** (e.g. `scripts/audit_skills.py`): frontmatter, duplicate names, secret hits. Fix hard failures before pushing.
   **When CI fails, read the annotation before reading the code.** A run that fails in ~2s with no steps executed is not a code failure: `gh run view <id>` shows `The job was not started because your account is locked due to a billing issue`. Prove whether it is account-wide or repo-specific with one empty throwaway public repo carrying a one-line workflow — if that fails identically, no amount of workflow editing will help, and the fix is on the account (payment method / spending limit), not in the repo. "Billing issue" does NOT imply money owed: it also fires when a metered account has no payment method on file even at zero balance, so read the metered-vs-included figures before telling the user they have an unpaid bill. Reserved-vs-actual check: public-repo standard runners are free, so `0` artifacts, `0` LFS files, no Codespaces and no Marketplace purchases means the minutes are not the cause. Do not stall the sync waiting for a runner — run the workflow's steps locally and report both states separately ("gates pass locally, hosted runner blocked by an account lock").
7. **When hosted CI is unavailable, gate the push locally instead of dropping the gate.** A pre-push hook is the smallest thing that keeps the checks real: `scripts/pre-push.sh` runs the same scripts the workflow runs, symlinked into `.git/hooks/pre-push` (`ln -sf ../../scripts/pre-push.sh .git/hooks/pre-push`), bypassable per-push with `--no-verify`. Do NOT attach a payment method to unblock runners just to run free-tier checks; the hook is free and runs the failure at the moment you can still fix it. Expect the hook to catch real drift on its first run — that is the gate working, and the fix belongs in the skill it flags, not in the hook. **The script must be committed EXECUTABLE.** `chmod +x scripts/pre-push.sh && git update-index --chmod=+x scripts/pre-push.sh` — a hook tracked as mode `100644` makes every `git push` print `hint: The '.git/hooks/pre-push' hook was ignored because it's not set as executable` and run with NO gate at all, which looks exactly like a passing gate unless you read the hint. Confirm with `git ls-files -s scripts/pre-push.sh` showing `100755`.
   **Never let the gate depend on whatever `python3` is first on PATH.** A Hermes-managed venv can sit ahead of the system interpreter and carry no `pytest`, so the hook fails on `No module named pytest` — a red gate that says nothing about the repo, and the easiest wrong conclusion is "the tests are broken". Probe for an interpreter that can actually run the suite, print which one was chosen, and allow an override:
   ```bash
   PY="${PYTHON:-}"
   [ -z "$PY" ] && for c in python3 python; do
     command -v "$c" >/dev/null 2>&1 && "$c" -c 'import pytest' >/dev/null 2>&1 && { PY="$c"; break; }
   done
   [ -z "$PY" ] && for c in "$HOME"/.hermes/installs/*/environments/*/venv/bin/python3; do
     [ -x "$c" ] && "$c" -c 'import pytest' >/dev/null 2>&1 && { PY="$c"; break; }
   done
   [ -z "$PY" ] && PY=python3
   echo "pre-push gate  ($PY)"
   ```
   Then invoke every step as `"$PY" scripts/...`. The same rule applies to any gate script that must run outside the agent's session: resolve the interpreter by capability, never by assuming the shell's PATH matches the one the agent had.

## Support Files

- `references/drift-checker-implementation.md` — how to implement or extend the repo-vs-live comparison: the all-files walk, CRLF-normalized byte compare, the live-root convention that silently empties the shared set, and the two-direction test fixture.

## Pitfalls

- **A drift checker that compares only `SKILL.md` certifies a repo it never checked.** A skill is a directory, not a file: one whose body matched byte-for-byte was still missing 11 of 13 `references/` files locally published. Compare every file under each shared skill dir and report missing vs differs separately — the first run of a corrected checker found 556 out of sync on a repo the old one called clean. Normalize line endings first: git's `autocrlf` rewrites CRLF↔LF on checkout, so a Windows-authored script is byte-different and content-identical, and without normalization the gate cries wolf on every .ps1. See `references/drift-checker-implementation.md` for the comparison helper and the test-fixture trap.
- **A drift checker reports ITERATIVELY — loop it until it says clean, do not trust one pass.** Syncing the reported stale list and re-running reveals MORE stale files, because the comparison is sensitive to whatever the previous pass settled (a copied tree changes names/aliases for the next comparison). One repo went 18 → 13 → 5 → 3 → 0 over four passes. Script the loop (sync-reported-stale, re-run, break on zero) and stop only on a clean report; a single pass that "synced everything it listed" leaves the repo still drifted while the output looked finished.
- **A name appearing "unpublished" can be a file the repo has under a DIFFERENT directory name.** Check for the declared frontmatter `name` on both sides, not just the path: a router skill living at `<pack>/SKILL.md` was reported unpublished because its `name:` differs from its directory, and the fix was copying that one file into the pack root — not creating a new skill dir. Same for a sub-skill directory that exists in the repo while its parent's own `SKILL.md` is missing.
- **Run the repo's secret scan BEFORE pushing and decide per hit whether it is the scanner or the content.** Security/payload skills legitimately contain credential-SHAPED teaching examples, so a raw `Bearer <token>` rule fires on public documentation. Decode the hit before touching it: base64/JWT payloads that say `alg:none` and name `John Doe` are the canonical jwt.io sample, not a leak. Fix the PATTERN with an explicit, documented exclusion (and prove both directions — a real token still matches, the sample does not) rather than editing the skill content or lowering the rule to something that misses real keys. Verify the fix by re-running the gate, not by reasoning about the regex.
- **A hardcoded count assertion in the repo's tests is a trap, not a gate.** `assert "1,484 repository skills" in CATALOG` fails on every legitimate addition. Change it to compute the real count (`len(list((ROOT/"skills").rglob("SKILL.md")))`) and assert the catalog advertises THAT, so it guards drift instead of freezing a number.
- **A "missing" verdict from a path you guessed is not evidence of absence — list the tree first.** Repo layout inserts category dirs unpredictably (`skills/capacitor-mobile/` vs `skills/development/capacitor-mobile/`), so `git cat-file -e origin/master:<guessed path>` and `gh api .../contents/<guessed path>` return 404 for a file that is present and correctly published. Resolve the real path once with `git ls-tree -r --name-only origin/<default> | grep -i '<name>'` and verify against what the tree reports. Reporting a false missing file to the user is worse than the extra round trip.
- **A hand-curated site does not follow the skills.** Catalog JSON and `SKILLS_CATALOG.md` counts are often written by hand with no generator. Check `package.json` scripts and `scripts/` before promising the site reflects the sync, and say plainly when it does not.
- **"Every skill is installed" claims rot.** If the catalog says that while the repo holds skills the live profile never installs, fix the sentence, not the data.
- **Do not prune the repo to match the live catalog.** Repo-only skills are shareable breadth; deleting them to make the sets equal shrinks what peers get for no local gain. Explaining the two sets as disk-vs-injected is usually the answer the user needs.
- **Sync is one-directional by default.** Refreshing repo copies from the live tree is safe. Importing repo-only skills back costs prompt budget (each row is name + 60 description chars, every turn), so treat it as a separate measured decision with a named gap list, not a mirror operation.
- **A "different skills" report is usually drift, not divergence.** Quantify it (how many shared names, how many repo-older, how many local-only) before proposing any action.
