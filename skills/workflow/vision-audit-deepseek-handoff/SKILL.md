---
name: vision-audit-deepseek-handoff
description: Audit UI with a vision model, hand fixes to a coder.
---

# Vision Audit → DeepSeek Handoff loop

The user's standing workflow for design/UI work: **MiMo 2.5 audits screenshots → DeepSeek V4 Flash implements → parent verifies → re-audit**. Proven 2026-08 on a 3-screen core app; both audit passes caught real regressions (hooks-order crash, single-letter day labels) that static review missed.

## Why MiMo via opencode run (not delegate_task)

`delegation.model` in config.yaml pins ALL delegate_task children to deepseek-v4-flash. A MiMo child is impossible through delegation — run it explicitly:

```bash
opencode run --model opencode-go/mimo-v2.5 "<brief>"
```

The brief MUST be self-contained: absolute screenshot paths, the frozen design language, per-screen audit dimensions, and an exact output format (numbered findings `[SCREEN] [SEVERITY] description -> one-line fix` + a TOP-N priority list that "a developer can execute without seeing the screenshots"). Background it (`terminal background=true, notify_on_complete`) — audits take 2-5 min.

## When the vision route is down: OpenRouter direct (proven 2026-08)

`vision_analyze` failed all session ("unknown variant `image_url`, expected `text`" from Console Go upstream = provider rejects image payloads; also transient "Connection error"). Working fallback — direct OpenRouter call, key read in-process from the Hermes `.env` (NEVER print it):

- Key: `OPENROUTER_API_KEY` in `~/AppData/Local/hermes/.env` (the credential pool in `auth.json` stores only fingerprints — useless; `opencode/auth.json` key may be stale → 401).
- POST `https://openrouter.ai/api/v1/chat/completions`, model `qwen/qwen-2.5-vl-72b-instruct` (free), message content = `[{type:text}, {type:image_url, image_url:{url: "data:image/png;base64,<b64>"}}]`, max_tokens ~500-800.
- Prompt for terse findings: "Report ONLY concrete problems, one line each with severity (HIGH/MED/LOW) and exact location. If none, reply exactly: CLEAN". Batch all screenshots in one loop; ~10-20s per image.
- Ask a targeted re-audit after fixes (e.g. "check specifically: X section alignment") — faster and confirms the fix.

## Verify suspicious vision flags with geometry, don't re-trust the model

A vision model flagged a contact-row overlap that its own CLEAN verdicts on 3 other identical-markup screens missed. When a flag is plausible but uncertain (or it found something real): measure with Playwright `getBoundingClientRect()` — element boxes, gaps, overlap widths — and decide on numbers. One real bug caught this way: a stray `</span>` closing a `<div>` nested the row text inside a 32px avatar (text box measured 18px wide). Fix + verify = re-measure + a whole-file tag-balance check (`python -c` regex count `<div` vs `</div>`, `<span>` vs `</span>`, etc.).

## Screenshot capture rules (playwright, headless chrome)

- 1440×900 viewport; log in with real test creds; **settle 4.5s after the login page loads before filling** — clicking before React hydration attaches triggers a native GET form submit (URL becomes `/login?email=...`).
- Wait 5-8s per target page; first hit of a route triggers Next dev on-demand compile — screenshots taken mid-compile show "Compiling…"/"Rendering…" badges and skeleton-only content. If the audit returns INCONCLUSIVE/loading-state verdicts, re-capture in steady state and re-audit — timing artifacts, not code bugs (but check for a real hang: page stuck on skeleton after 8s = missing fetch timeout, see below).
- After fixes, re-capture and run a **PASS/FAIL checklist** — the loop closes only when the vision model confirms.

## Handoff to DeepSeek

- The numbered findings ARE the spec: pass them verbatim, each with its one-line fix, plus file ownership (touch ONLY these files), quality bar (`tsc --noEmit && npm run build`), and "no commits/push".
- **Timed-out agents usually wrote the files anyway**: check the transcript tail + `git diff --stat`; finish the last error yourself. Two failure modes seen in one session:
  1. Nonsense math in completed code — verify agent-written formulas (a "weighted average" came back as `x / (x - (x - (x - x)))` = divide-by-zero).
  2. New code paths added fetch() calls WITHOUT timeouts → hanging API = page stuck on skeleton forever. Rule: every external fetch in agent code gets `signal: AbortSignal.timeout(8000)`.
- Verify agent claims yourself: tsc + build + a browser DOM probe (h1 present, no error-boundary Reset button, 0 pageerrors) + real-data E2E (add a row through the UI, read back the value, then delete the row via direct REST with the session JWT — the UI trash button is not always locatable).

## Cleanup discipline

Test data created during E2E must be removed: extract the session JWT from the `sb-*-auth-token` cookies (base64- JSON, chunked), then `DELETE /rest/v1/<table>?id=eq.<id>` with `apikey` + `Authorization: Bearer <jwt>`. Confirm `remaining: []` before declaring done.

## Related

- `ecc-bridge` — the ECC review gate for the same app (code-focused; this loop is the visual counterpart).
