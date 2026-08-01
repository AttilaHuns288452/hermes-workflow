---
name: hermes-local-patching
description: Patch the local Hermes Agent install at C:\Users\Attila\AppData\Local\hermes\hermes-agent (a git checkout) when upstream patches drift or no official fix exists. Covers drift porting, real-import verification, and the update-reverts-patches pitfall.
---

# Patching the local Hermes install

The install is a full git checkout at `C:\Users\Attila\AppData\Local\hermes\hermes-agent\`.
You can patch it, verify with real imports, and revert via git.

## Apply an upstream patch

1. Download the .diff, then `git apply --check` from the repo root.
2. **If it fails (drift):** hand-port. Upstream patches anchor on *structural
   patterns*, not line numbers — find the same pattern at its current site
   (`grep -n` the anchor, e.g. `api.kimi.com` header branches), then use the
   `patch` tool with surrounding context for uniqueness. Apply the change at
   EVERY sibling site of the pattern, not just the first match — sibling
   call paths are where half-applied fixes silently miss.
3. Verify with **real imports**, not the patch's own tests (those target the
   upstream commit and won't exist/match locally):
   `PYTHONPATH="$(pwd)" <repo>/venv/Scripts/python verify_script.py`
   — exercise the real function paths + one control case (ensure the patch is
   gated and doesn't fire for unrelated providers/base URLs).
4. Delete the verify script after it passes (keep the tree clean).
5. **Restart Hermes** — running processes have old modules loaded; patches
   take effect on next start.

## Pitfalls

- **`hermes update` reverts local patches.** Re-apply after every update.
  (The durable fix is upstream — file a PR with the patch.)
- Venv python lives at `hermes-agent/venv/Scripts/python` (no `python.exe` on
  PATH; `AppData/Local/hermes/venv` doesn't exist).
- The tree may already be dirty from prior work — `git diff --stat` and only
  touch your own files.
- Patch is gated, so a fix for one provider must never fire for others —
  always verify a control (non-target base_url/provider) in the test script.

Provider quirks that required local patches: `references/zai-glm-429-fix.md`.
Connecting to z.ai/ZCode (Bearer-not-x-api-key contract, where credentials
live + how they refresh, the `zai`-name special case, captcha-gate
diagnostics): `references/zai-connection-auth.md`.
