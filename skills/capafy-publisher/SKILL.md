---
name: capafy-publisher
description: "Publish, update, or re-ship an Agent/Skill on the Capafy platform. Triggers include publish, list, upload, ship, package, Capafy, agent_id, review_url, log in, switch account, earnings / payout, statistics, refund, certification / KYC, relist, delist, delete-draft. Covers the full publish-init / publish-configure / publish-ship chain plus login, earnings queries, refund handling, and KYC certification. Supports Claude Code, Codex, OpenClaw, and Hermes hosts."
---
# capafy-publisher

This file keeps only the run entries and the rules the host LLM must follow. Publishing is driven by the CLI's JSON output; internal details such as target, mode, scan, stage, package, and validate are handled by the code.

## Run Prerequisites

- Run scripts in this directory with `python3` (on systems where `python3` is missing, use `python` — notably Windows where the two aliases can differ).
- Python >= 3.8; Python 3.11+ uses the stdlib `tomllib`, 3.8-3.10 uses the built-in TOML fallback shipped with this skill.
- The host must allow `python3` (or `python`) execution inside this skill's directory. Claude Code needs `Bash(python3:*)` allowed in its permission settings. On Windows, test with `python packager.py <command>` if `python3` is not found.

## Self-Update

Run this before each use:

```bash
python3 self_update.py --check
```

Handle the response:

- `up_to_date`: continue.
- `update_available`: tell the creator and ask; on agreement run `python3 self_update.py`, then restart from the beginning after the update finishes.
- `check_failed`: continue using the current version; if a later platform response header carries `X-Skill-Version-Status: outdated|deprecated`, remind the creator at the next human-confirmation point.

`self_update.py` downloads a zip per the install manifest; if the manifest carries `sha256` / `sha256Hex` / `sha256_hex` it verifies the digest. When the update bundle does not carry `requirements.txt`, dependency installation is skipped. The Windows install mode first copies the updater into the system temp directory and lets an external runner replace the live skill directory, so the running script does not lock its own directory.

## Read Order

Runtime reads only:

- `SKILL.md`
- `publish-workflow.md`
- `api-docs/index.json`
- `api-docs/00_overview.md`
- `references/agent-card-content-strategy.md` — guide for writing compelling agent card descriptions, tags, and pricing (see that file before asking the creator to fill in card details on the web page)
- `references/provider-refs-none-guard.md` — traceback and fix for the `custom_providers` `NoneType` crash in `publish-configure` (read when the error surfaces)
- `references/deep-scan-review-checklist.md` — staged-file review procedure for deep scan findings (read when `--deep-scan` returns `needs_deep_scan`)
- `references/credential-confirmation-page.md` — describes the credential review page UI structure (Proxy-Hosted vs Container-Injected sections), URL redirect behavior, and post-confirmation reconciliation (read before directing the creator to the configure review_url)
- `references/publishability-assessment.md` — tiers (green/yellow/red) for evaluating which skills are cloud-publishable, pricing strategy by agent type, and MCP env block key pitfalls (read when the creator asks "what should I publish?" or "is this skill publishable?")

**Do not** read Markdown under `.temp/`, `.pytest_cache/`, `dist/`, or `docs/`.

## Public Commands

```text
login-init
login-verify
login-token
publish-init
publish-configure
publish-ship
publish-status
publish-remote-status
publish-refresh-url
publish-list
```

`publish-status` only reads the local `.temp/` working state and does **not** reflect platform review / listing status; its JSON includes `status_scope: local_only` and `does_not_include_remote_review_status: true`. For platform review / listing status, use `publish-remote-status --agent-id <agent_id>`. To find the creator's Agent IDs, use `publish-list`.

Login:

- Not logged in: `login-init` → `login-verify`
- Before email-OTP login the host must complete the compliance-consent gate: take the current platform `base_url`, strip the trailing `/api` to get `web_base`, show the creator `web_base/terms-of-service` and `web_base/privacy-policy`, and require explicit consent to both the terms of service and the privacy policy. Vague replies (e.g. "ok", "go", "continue", "next") do not count as explicit consent; do not run `login-init` until explicit consent is given. This rule applies only to email-OTP login; `CAPAFY_ACCESS_TOKEN`, the local `config.json`, and `login-token` use the post-issuance auth path and do not re-prompt for consent.
- When the creator pastes a token directly, or asks to switch the platform account / user: `login-token --access-token <token>` is the only entry. It must first call `GET /agent/account` with that token to validate against the platform; only when the HTTP call succeeds and the account response is valid is the token written to the local `config.json` (the file under the capafy-publisher root) as the new local fallback account. This does not touch the user skill's account file — the user skill has its own swap logic.
- When `login-token` validation fails, halt and report; do not write or overwrite the local `config.json` (under the capafy-publisher root), and do not echo back the token the creator pasted.
- Token priority: `CAPAFY_ACCESS_TOKEN` → local `config.json` (under the capafy-publisher root). If `CAPAFY_ACCESS_TOKEN` is set in the current process, it still overrides whatever `login-token` wrote locally; to let the new local account take effect, remove or replace that environment variable.
- `base_url` only reads the explicit argument, `CAPAFY_PLATFORM_BASE_URL`, and the code default; it is not read from the local `config.json`.
- `publish-init` first validates the platform login state; when not logged in or the token is invalid it returns a structured login error and does not enter candidate discovery.

## Publish Main Chain

```text
publish-init → web confirmation → publish-configure → handle per JSON output → publish-ship → web confirmation
```

The three web confirmation pages are: after `publish-init`, **confirm the file contents to upload**; after `publish-configure`, **confirm the keys / environment variables etc. to be hosted**; after `publish-ship`, **final confirmation and submit for review**.

What comes next after `publish-configure` / `publish-ship` is decided entirely by the structured payload: `status`, `review_url`, `developer_next_steps`, `blocking_category`, `failed_step`, and similar fields take precedence over this document.

CLI exit codes only separate true command failures from normal workflow pauses. States that require the host LLM or creator to act, such as candidate selection or deep scan, exit `0` and return `ok: true`, `requires_action: true`, and an `action_type`. True errors exit `1` and return `ok: false`, `status: error`; parse the JSON payload before deciding how to report the result.

## Core Iron Rules

**Always talk to the creator in plain language**: CLI parameters, JSON fields, and internal state names exist only between you (the host LLM) and the code; **do not** speak them directly to the creator. Translate quoted phrases for the creator using this table:

| Program field / parameter | What to say to the creator |
|---|---|
| `--skill-dir` | "skill directory" / "skill source directory" |
| `--runtime-dir` | "project root" / "workspace path" |
| `--env` | "target runtime environment" |
| `--selections-file` | "selections file" |
| `--reset-local-state` | "discard the local draft and start over" |
| `--deep-scan` | "deep scan" |
| `--dispositions-file` | "dispositions file" |
| `agent_id` | "Agent ID" |
| `agent_version_id` | "Version ID" |
| `agentType` / `agent_type` | "publishing mode" |
| `agentType: run_online` / `agent_type: run_online` | "Run Online mode" |
| `agentType: download` / `agent_type: download` | "Download mode" |
| `selections` / `selection_groups` / `workflowInfo.selection_groups` | "the skill selection for this release" |
| `Phase A` / `discover_units` | "local scan" |
| `manifest` / `.temp/` working state | "local draft" |
| `review_url` | Paste the link verbatim plus a one-line note about what the page is for; differentiate by source: `publish-init` = "confirm the file contents to upload", `publish-configure` = "confirm the keys / environment variables etc. to be hosted", `publish-ship` = "final confirmation and submit for review" |
| `publish-init` / `publish-configure` / `publish-ship` | "publish step one / configure / submit for review", or just speak the command name |

Translate fields not in this table by the same principle; when uncertain, prefer plain language describing what it does instead of inventing new terminology.

When reporting credentials after `publish-configure`, keep the credential buckets separate:

- `url_proxy` means cloud-hosted LLM provider configuration: model API key plus endpoint / base URL.
- `generic` means other standalone secrets or sensitive configuration values.
- `env_var` means runtime environment variables required by the Agent.

Never say "no API key is needed" only because `generic: 0` and `env_var: 0`. If `url_proxy > 0`, say the Agent has no extra third-party service keys, but still needs cloud LLM provider configuration to be confirmed. If the CLI response includes `credential_summary.creator_message`, use that message as the source of truth for user-facing wording.

Configuration confirmation belongs on the platform web page, not in chat, and only in the `run_online` configure flow. Do not introduce cloud endpoint reachability checks in `download` / buyout, `publish-init`, or `publish-ship`. Do not inspect, judge, or ask the creator to manually edit LLM provider entries in chat because an endpoint is localhost / LAN / private-network / otherwise likely unavailable from the cloud. Do not generate or recommend an alternate provider such as OpenRouter as a chat-side fallback for a local endpoint. Submit the discovered provider key and endpoint candidates to the Run Online configuration confirmation page; the creator confirms, removes, or edits them there.

When explaining a discovered credential, only state a source that is present in the CLI payload or reviewed scan metadata. Do not infer that a key came from `.hermes/config.yaml` just because it was paired with a Hermes provider. Hermes keys may come from config, `.env`, auth profiles, credentials/oauth caches, or process/OS environment fallback; if the exact source is not visible, say it is a discovered configuration candidate and direct the creator to the web confirmation page.

No matter which step of the main chain you are on, or which error has interrupted you, the rules below do not change:

1. **Anything that needs creator action: send a visible message first, then pause.** When the CLI JSON returns a `review_url`, paste it to the creator verbatim (all of them if multiple) along with a note about what the page is for; questions to the creator (deep-scan consent / `agent_id` confirmation / skill reselection / whether to abandon the agent, etc.) follow the same rule — send a top-level chat message, do not silently wait inside a thinking / processing block. **`review_url` is valid for one hour and then expires**: if some time later the creator says "continue publishing / try again" or anything that requires opening a web page, do not re-paste an old `review_url` from earlier in the session — run `publish-refresh-url --agent-id <agent_id> --step <init|configure|ship>` first, then paste the fresh URL. Do not rerun `publish-init` / `publish-configure` / `publish-ship` solely to refresh an expired link.
   - `review_url` returned by `publish-init`: the creator should **confirm the file contents to upload**.
   - `review_url` returned by `publish-configure`: the creator should **confirm the keys / environment variables etc. to be hosted** (filled in on the web page; do not let the creator send secrets in chat).
   - `review_url` returned by `publish-ship`: the creator should **make the final confirmation and submit for review**. `status: shipped` only means the package has been uploaded to the platform and the final-page URL has been issued; **the actual "submit for review" action must be performed by the creator on the final page**. Until the creator explicitly tells you the final page has been clicked through, never say "submitted / under review / approved" or anything else carrying "submitted for review / review process started" semantics.
2. **After a web page, you must reconcile with the platform.** When the creator returns from a web page with a signal like "confirm / done / fixed / price set", first call `capafy_platform.api.get_latest_version_raw(agent_id)` and read the returned `agentType` / status / `agentVersionId` before answering — do not infer from the local manifest. When you need to check whether the confirmation page already has selected skills, do not look at the raw response's top-level `selectionGroups`; that field may be empty. Look only at `workflowInfo.selection_groups`, or the `selection_groups` exposed by `packaging._shared.platform.get_latest_version()` in code. After the web confirmation page, **the platform is the source of truth**.
3. **Review status comes from the platform only.** Questions like "how far has the review gone / did it pass / is it listed?" must call `publish-remote-status --agent-id <agent_id>` or `get_latest_version_raw(agent_id)`. `publish-status` only reads the local `.temp/`; `publish-ship`'s `status: shipped` only means the package has been uploaded — **it does not mean submitted for review, under review, or approved**. The full chain is: `shipped` → the creator clicks submit on the final page → platform latest-version readback actually shows "under review" → only then does the platform progress to "approved / rejected". Until every link has been satisfied, do not say "submitted / under review / approved" in chat. **`status` and `auditStatus` are both states of the latest version, not aggregates across the whole agent history; do not mix them up**: `status` is the **agent lifecycle state** of the latest version overall (draft → review → listed → delisted, the main axis); `auditStatus` is only the **review sub-state** during the "under review" segment of `status` (automated / manual / passed / failed). **Real meaning of the two `0` values**: `status: 0` = **draft (not submitted)**, `auditStatus: 0` = **review not started**; when you see these two `0`s you must report "draft / review not started" and **never** misread them as "submitted / under review / approved". Full enums (`status` 0=draft / 1=under review / 2=review failed / 3=review passed pending listing / 4=listed / 5=expired / 6=delisted; `auditStatus` 0=not started / 1=auto review in progress / 2=manual review in progress / 3=review failed / 4=review passed) are in `api-docs/00_overview.md`.
4. **`agentType` mismatch = local state invalidated.** When the platform `agentType` differs from the local manifest's `agent_type` (typical: the creator toggled `run_online` ↔ `download` on the web page), the platform has already rolled the version back to draft and cleared the confirmed skill selection. Return to `publish-configure --agent-id <agent_id>` so the code re-stages / re-scans / re-packages under the new `agentType`; do not report "submitted for review" based on the stale manifest.
5. **Source of `agent_id`.** It must come from explicit creator confirmation or from `capafy_platform.api.list_agents_raw()`. Do not invent it from `.temp/` manifest, the previous session, or anywhere else.
6. **Blocks do not justify a new agent.** Once an `agent_id` has been obtained, any block defaults to resume (`publish-status` → `publish-configure` / `publish-ship` / wait for the creator to finish the `review_url`); do not return to `publish-init` and rebuild. `--reset-local-state` only clears local staging — it does **not** tell the platform to abandon the agent; use it only when the creator explicitly says "scrap this and ship a new one", and recap that decision in chat before running. **Resubmitting a rejected version is also a block, not an agent swap**: when the creator wants to "fix the rejected version / resubmit for review", rerun the main chain `publish-init` → `publish-configure` (re-scan + re-package) → `publish-ship` (re-upload) — **the selections payload of `publish-init` must carry the original `agent_id` at the top level**, so the code goes through `create_version_from_draft` to create a new version on the same Agent; **omitting `agent_id` makes the code go through `create_agent_from_draft` and create a brand-new Agent**, which is wrong and leaves an orphan listing on the platform. In chat with the creator, frame it as "running the scan / package / submit-for-review flow again on the same Agent"; **never** say things like "running the whole pipeline again / the previous flow has ended / generated a new draft version" that imply an agent swap.
7. **No making things up — and also no filtering out candidates.** Before constructing `--selections`, you must have already run `publish-init` (without `--selections`) in this session with the same `--env` / `--runtime-dir` / `--skill-dir` and obtained candidates, or you must have passed `--skill-dir` to lock down a single skill. `skills[].path / .name` etc. must correspond one-to-one to Phase A candidates; the moment you catch yourself thinking "I remember / should be / usually there is...", stop and rescan. **The converse is equally forbidden**: do not filter Phase A candidates yourself by exact match against the Agent Card's `Name` / `Description` — the code-level `discover_units` does not filter by agent name, and "no candidate exactly matches the Agent Card name" does **not** equal "no files / no skill in the workspace". In that case, you must read all candidates verbatim to the creator and ask in plain language per the translation table, e.g.: "I scanned N skills locally, but none of them exactly matches your Agent Card name `<name>` — do you want to publish one of them? Or switch the skill directory? Or update the Agent Card name?" Never reply with "not found / no files / no skill".
8. **For continued publishing, reconcile history first.** Before updating an existing Agent (selections carries `agent_id`), you must call `get_latest_version_raw(agent_id)`, read the previous version's skill `name` / `description` / `purpose` from `workflowInfo.selection_groups`, and match them against local Phase A candidates by `name` (first priority) then `description` (second priority); ask the creator about anything that does not match — do not copy from last time or guess. **Do not treat historical paths as local paths**: `workflowInfo.selection_groups.skills[].path` is the **logical path** the platform saved for the previous version (relative to that run's `--runtime-dir`), **not the current file location on this machine**. Whether the creator picks "reuse" or "switch", you must first confirm the **current package directory on this machine** (project root + skill directory) with the creator in plain language per the field table, and run Phase A with those confirmed real paths — do not pass the historical `path` directly as `--skill-dir` / `--runtime-dir`.
9. **Only one publish main chain at a time; no parallel / auto-batch.** At any moment only one publish main chain (`publish-init → publish-configure → publish-ship`) can be in progress; while the current chain has not finished, you may not start another main chain in parallel or nested to publish a different Agent, and you may not auto-loop through a directory running init→ship on every skill in turn.
   - **Allowed**: bundling multiple skills inside a single Agent's `skills[]` and shipping them together — this is the normal one-Agent-many-skills usage, not batch.
   - **Allowed**: after a `publish-ship` has finished, if the creator wants to publish another Agent in the same session, you may start a new publish main chain in sequence, starting normally from `publish-init`; confirm each step of each chain — do not auto-chain multiple together.
   - **Not allowed**: treating multiple skills as separate Agents and having the publisher "batch publish" them at once — you may not run through N publish main chains for the creator in a single prompt.
   - **Does not affect version updates**: a version update on the same `agent_id` is itself one publish main chain — proceed normally.
   - **Triggers and handling**:
     a. If the creator opens with "ship these skills for me / publish all skills in this directory / do them one by one", pause first and confirm intent in plain language per the table — is this one Agent containing multiple skills (a bundle), or multiple independent Agents? If bundle, proceed normally to `publish-init`; if independent Agents, tell the creator explicitly that they will be processed **one chain at a time, sequentially** (no auto-loop), and have the creator pick which one to publish **this time** — the others will be handled as separate chains afterward.
     b. After a `publish-ship` has finished and the creator wants to publish another Agent, start a new publish main chain to handle it — there is no need to open a new session; but still run only this one chain — do not roll later ones into it "for convenience".

## publish-init

Before running, confirm with the creator whether this is a **brand-new publish** or a **continue / version update**:

- Brand-new publish: when the creator has not said what to publish, ask about scope first; when they have given only the runtime / project root and no skill, run Phase A directly and read the candidates to the creator for selection.
- Continue / version update: obtain `agent_id` per Core Iron Rule #5, and reconcile historical selections per Core Iron Rule #8.

Once an `agent_id` has been obtained in this session, any block defaults to resume — do not rebuild the agent:

- Any error from `publish-configure` / `publish-ship`: first read the payload's `developer_next_steps` / `failed_step` / `blocking_category`, then decide whether to retry the same step, run the supplementary sensitive-info scan, or wait for the creator to finish the `review_url` web confirmation. **Do not** rerun `publish-init` to recreate just because something failed.
- If `publish-configure` reads the platform back and finds the first page (the file-contents confirmation) had `skills[]` empty after confirmation, the creator removed all skills on the web page. Halt; have the creator return to the first page and pick at least one skill, or rerun the publish first step with the correct project root / skill directory. Do not continue to configure / ship.
- Web confirmation page will not open / is stuck / the creator is offline: pause and wait for the creator. Do not rerun `publish-init`.
- Seeing the `existing_local_publish_state` blocking error: this is a guard, not an error. The first choice is `publish-status` to inspect local state, then `publish-configure` / `publish-ship` to continue — **not** straight to `--reset-local-state`. **Exception**: if `publish-status` shows the local `agent_id` differs from the agent you are now publishing, the old staging cannot be resumed — it belongs to a different agent. Explain the mismatch to the creator, then use `--reset-local-state` to clear it.
- `publish-init --reset-local-state` only clears local `.temp/` staging; it does **not** tell the platform "abandon the previous agent". Unless the creator explicitly says "I want to ship a new agent, not the old one", do not use `--reset-local-state`, and certainly do not use it to "fix" upload errors.
- When the creator explicitly wants to switch runtime / switch skill set and `publish-init` needs to be rerun, the selections **must carry the original `agent_id`**, going through the "continue / version update" branch; only when the creator explicitly wants a brand-new agent may `agent_id` be omitted, and the decision to abandon the old agent must be recapped to the creator in chat before running.

`publish-init` must be given an explicit target runtime environment and the project root of the creator's current host session:

```bash
python3 packager.py publish-init --env <env_id> --runtime-dir <absolute_path>
```

- `--env <env_id>`: target runtime; values are `claude_code` / `codex` / `openclaw` / `hermes`. If the object being published is a `metadata.openclaw` skill, you must use `openclaw`.
- `--runtime-dir <absolute_path>`: the project root / workspace root the host session has open; do not derive this value from the source path of the skill being published, a parent `skills` directory, or the publisher skill root.
- `--skill-dir <single_skill_dir>`: optional; pass it only when the creator explicitly specifies a single local skill source directory. It must point at a single skill root containing `SKILL.md`; it cannot be a parent `skills` directory, and it does not replace `--runtime-dir`.
- Claude Code / Codex: pass the project root opened when starting `claude` / `codex`, i.e. the current session working directory.
- OpenClaw: pass the current OpenClaw workspace directory, e.g. `/home/admin_wsl/.openclaw/workspace_xxx`; do not pass a regular project root, user home, `~/.openclaw`, `~/.openclaw/skills`, or a single skill directory.
- Hermes: pass the project root opened when starting the host session, and set `--env hermes`. The publisher stages the active Hermes home selected by `HERMES_HOME`, then `~/.hermes/active_profile`, then default `~/.hermes`; there is no `publish-init --profile` option.
- On Windows native, `C:\Users\me\project` is fine; on WSL / Linux, pass a path the current system can actually access, e.g. `/mnt/c/Users/me/project` — do not expect the publisher to auto-translate Windows paths.
- dot-agent targets do not auto-detect the host environment and do not check whether `runtime_dir` is reasonable; OpenClaw targets validate that it must be a real workspace.

Example: when Codex is currently running at `/home/admin_wsl/sunnet/project/agent_store` and the skill being published lives at `/home/admin_wsl/.agents/skills/skill-vetter`, pass:

```bash
python3 packager.py publish-init --env codex --runtime-dir /home/admin_wsl/sunnet/project/agent_store --skill-dir /home/admin_wsl/.agents/skills/skill-vetter
```

### publish-init copy-pastable examples

Prefer `--selections-file`; do not stuff multi-line JSON into a shell string. The first run must be Phase A without `--selections`, to obtain real candidates:

```bash
python3 packager.py publish-init --env codex --runtime-dir /home/admin_wsl/sunnet/project/agent_store --skill-dir /home/admin_wsl/.agents/skills/skill-vetter
```

Then write `.temp/confirmed-selections.json` based on the Phase A candidates. `skills[].path` / `name` must be verbatim from the candidates; `purpose` is the use-description the creator has confirmed:

```json
{
  "title": "Skill Security Review",
  "description": "Automatically reviews third-party skill source for security issues; flags red-flag patterns and permission boundaries",
  "skills": [
    {
      "path": ".agents/skills/skill-vetter",
      "name": "skill-vetter",
      "purpose": "Reviews skill source for credential leaks, network exfiltration, permission overreach, and other security risks"
    }
  ],
  "plugins": [],
  "crons": []
}
```

When submitting the first-page draft, you must reuse the same `--env` / `--runtime-dir` / `--skill-dir`:

```bash
python3 packager.py publish-init --env codex --runtime-dir /home/admin_wsl/sunnet/project/agent_store --skill-dir /home/admin_wsl/.agents/skills/skill-vetter --selections-file .temp/confirmed-selections.json
```

When updating an existing Agent, the request body simply adds `agent_id` at the top level; `agent_id` must come from explicit creator confirmation or `list_agents_raw()`:

```json
{
  "agent_id": "agt_xxx",
  "title": "Skill Security Review",
  "description": "Automatically reviews third-party skill source for security issues; flags red-flag patterns and permission boundaries",
  "skills": [
    {
      "path": ".agents/skills/skill-vetter",
      "name": "skill-vetter",
      "purpose": "Reviews skill source for credential leaks, network exfiltration, permission overreach, and other security risks"
    }
  ],
  "plugins": [],
  "crons": []
}
```

When `publish-init` is run without `--selections`, it returns the top-level `skills` / `plugins` / `crons` candidate arrays directly; when `--skill-dir` is given, the candidates only include that explicit skill. Candidate entries do not carry a `selection` field — they only count as "selected" once they appear in the `--selections` of the second submission. The host LLM combines candidates with user context to produce `title`, `description`, and a per-unit `purpose`, confirms with the creator, then submits.

This Phase A response is a soft action: the command exits `0`, `status` is `needs_selection`, and `requires_action` is `true`. Do not report it as an error just because the workflow paused for candidate selection.

For large workspaces, pass `--brief --title "<Agent Card name>" --description "<Agent Card description>"` on Phase A. Brief mode keeps candidate output compact (`path` / `name` / one-line `description` plus minimal flags), filters out the publisher skill itself, suppresses nested child skill copies when the parent skill is already a candidate, and may mark the best text match with `suggested: true`. This is only a publisher-side suggestion and sort order; it does not authorize the host LLM to hide other candidates from the creator.

### Hermes Runtime Notes

Hermes support targets Hermes Agent v0.14+ and stages `.hermes/config.yaml`, `.hermes/.env`, `.hermes/SOUL.md`, and `.hermes/skills`. It supports the main `model`, `auxiliary.*`, `delegation`, `fallback_providers[]`, and `custom_providers[]` provider blocks.

Hermes OAuth/cache state is scan-only: `.hermes/credentials`, `.hermes/oauth`, Hermes-managed Claude login state at `.hermes/.anthropic_oauth.json`, and Google Gemini CLI login state at `.hermes/auth/google_oauth.json` may be read to materialize platform-managed provider keys, but they must not be included in the final package. Runtime state such as sessions, memories, logs, credentials, oauth, auth, and worktrees is excluded from packaged Hermes trees.

Supported hosted provider keys include Anthropic, OpenAI, Google/Gemini, Nous, DeepSeek, xAI, Z.AI, Moonshot/Kimi, MiniMax, and OpenRouter. During configure, Hermes provider blocks are normalized to the most general Hermes form: `custom_providers[]` owns the hosted `api_key`, `base_url`, `api_mode`, credential pool, and provider model value, while `model`, `auxiliary.*`, `delegation`, and `fallback_providers[]` reference it with `provider: custom:<name>`. Bare official provider blocks such as `provider: openai`, `provider: anthropic`, `provider: gemini`, and `provider: openrouter` are converted to stable `publisher_<provider>_official` custom provider definitions with the official base URL filled in when missing. Custom providers are preserved as user-managed endpoints; if they carry `api_key`, `base_url`, or model fields, those values are replaced with platform-managed placeholders during configure.

Hermes `api_mode` uses Hermes-local values. For example, OpenAI Responses-compatible local config uses `api_mode: codex_responses`, while the platform-facing `url_proxy.api_format` remains `openai-responses`; confirmation rewrite maps the platform value back to the Hermes-local `api_mode`.

Hermes custom provider references are supported. If `model`, `auxiliary.*`, `delegation`, or `fallback_providers[]` uses `provider: custom:<name>` or a bare custom provider name and `custom_providers[].name` defines that provider, the referencing block is treated as a pure reference and does not create a duplicate `url_proxy`; the `custom_providers[]` definition owns the hosted key and endpoint. If a referencing block also defines inline `api_key`, `base_url`, or `credential_pool`, the configuration is ambiguous and configure will block; ask the creator to choose either a pure custom provider reference or a standalone inline provider block. Bare official provider names such as `openai`, `anthropic`, `gemini`, and `openrouter` remain official providers even if a custom provider is unfortunately named the same.

Before shipping Hermes in Run Online mode, tell the creator to select the intended profile (`HERMES_HOME` or `~/.hermes/active_profile`) and stop any local gateway if it writes runtime state into `.hermes`. Do not ask for API keys or OAuth tokens in chat; the configure web page is where hosted keys are confirmed.

When updating an existing Agent, do not just ask "do you want to pick a new skill?". First ask the creator whether to switch the skill directory, then split the choice into two options:

1. Use the historical selection and flow. Continue with the historical selection returned by the platform; `workflowInfo.selection_groups` only represents the skill selection already confirmed by the previous version — it is not a fresh discovery result.
2. Use new skills and a new flow. Return to Phase A, rescan for candidates, reconfirm `skills[]` against the new skill directory, then submit.

Explain both options clearly first, then let the creator choose. If the creator says "just changing the old skill's contents", the default is to continue with the current skill — do not reselect. Settle this judgment inside `publish-init`; do not defer it to `publish-configure`.

**Whether option 1 or option 2, you must first confirm the current package directory on this machine** (project root + skill directory) with the creator in plain language per the field table, and pass those confirmed real paths as `--runtime-dir` / `--skill-dir` to Phase A — see Core Iron Rule #8 "Do not treat historical paths as local paths". `workflowInfo.selection_groups.skills[].path` is the **platform logical path** of the previous version (relative to that run's `--runtime-dir`); it does not represent the actual current file location on this machine, and the creator may have moved or renamed files since. Passing the historical `path` directly as `--skill-dir` / `--runtime-dir` will cause staging / bundle to write to the wrong path, and the validator will report cycles downstream.

- Continue with the current skill: this run is just updating the contents of the same skill — reuse the existing `skills[]` and continue directly to the downstream draft / scan / submit.
- Switch to a different skill: this run is changing the publish target — return to Phase A, rescan, then reconfirm `skills[]`.

If Phase A returns an empty `skills[]`, or none of the candidates match the creator's intent, **do not enter the next step** and do not submit an empty `skills`. Read the candidates to the creator and have them confirm the actual project root / skill directory in plain language per the table, or confirm whether to publish one of the other discovered skills this time. `publish-init --selections` requires at least one selected skill; without a skill there is no way to request creating a platform draft.

Two hard rules — break either and stop right away to rerun Phase A or ask the creator:

- **Phase A is mandatory**: before constructing `--selections`, you must have already executed `publish-init` (without `--selections`) in this session with the same `--env` / `--runtime-dir` / `--skill-dir` and obtained a candidate JSON; or you must have passed `--skill-dir` to lock down a single skill. If neither is satisfied, you may not construct selections from memory, previous sessions, or guesses.
- **No making things up**: every `skills[].path`, `skills[].name`, `plugins[].path`, and `crons[].id` in `--selections` must correspond item-by-item to a Phase A candidate (or to the explicit skill from `--skill-dir`). Any path / name / description / purpose of unknown origin must go back to Phase A for a rescan, or be asked to the creator first. The moment you find yourself thinking "I remember there is...", "there should be...", "there is usually one...", stop.

`--selections` must not be wrapped in `selection_groups`, and must not carry `workflow_intent` / step index structures; when updating an existing Agent, add `agent_id` at the top level (source per Core Iron Rule #5).

## Sensitive Information Deep Scan

**⚠️ Critical pre-scan warning**: ALL credentials discovered in `.hermes/.env` and `.hermes/config.yaml` will be uploaded to the platform's credential review page as configuration candidates — including personal tokens for GitHub, OpenRouter, Codex, or any other third-party service. The creator must review the credential confirmation page and unselect any keys that should not be hosted. If the creator reacts with surprise (e.g. "why is my GitHub token there?"), the pre-scan warning was insufficient. Do not skip or abbreviate this.

**Consent step before the first entry to `publish-configure` (Run Online mode only)**: after the creator completes the first page (confirm the file contents to upload), reconcile per Core Iron Rule #2 with `get_latest_version_raw(agent_id)`; if the platform `agentType` is `run_online`, before running `publish-configure` you must first ask the creator in plain language whether to run a deep scan, e.g.: "This release uses Run Online mode; do you want to run a deep scan? I'll re-read the packaged content to look for generic-secret / sensitive-value risks the rules did not catch — it costs more time and tokens. Skipping means only the regular rule scan runs."

Send this question as a visible chat message and then pause, per Core Iron Rule #1.

- Creator agrees: run `publish-configure --agent-id <agent_id> --deep-scan`; once `needs_deep_scan` comes back, produce a findings JSON object per the "Sensitive Deep Scan" section of `publish-workflow.md` (top level has only `generic` / `env_var` arrays), then submit via `publish-configure --agent-id <agent_id> --deep-scan-findings-file <path>`. See `references/deep-scan-review-checklist.md` for the staged-file review procedure (which paths to check, what to look for, what to skip).
- Creator declines or chooses the fast path: run `publish-configure --agent-id <agent_id>` without `--deep-scan` — the code runs only the regular rule scan.
- Download mode (`agentType: download`) does not need this consent step; the platform does not host runtime keys, so go straight to the regular `publish-configure`.

Hard rules (details about sources, fields, and submission live in `publish-workflow.md`'s "Sensitive Deep Scan" section):

- Misses cannot be resolved by hand-patching buckets, nor by having the host LLM proactively collect new variables from the host environment.
- Generic secrets go into `generic` (each item has `value` + staging-relative `source`); environment variables go into `env_var` (each item has `value` + `field`); `url_proxy` can still only be produced by the rule scan, runtime contract, or source config.
- Do not edit `.temp/reviewed-scan.json` directly, and do not use already-generated buckets as review input.
- When `--deep-scan-findings-file` validation fails, fix the findings' `value` / `source` / `field` and rerun — do not change the scan rules at this step.
- Once you have confirmed there are no misses, rerun `publish-configure` without `--deep-scan` to continue with the platform configuration.
- **Host-required config files must not be excluded wholesale**: files already recognized as host-required runtime config such as `.claude/settings.json` / `.claude/settings.local.json` only go through `strip` (their keys have already been replaced by the code with `PLATFORM_MANAGED_*` placeholders). When the deep scan flags secrets in such files, do not suggest excluding the file outright — the file shell is required for running Claude Code in the cloud; top-level local `permissions` allowlists in Claude settings files are removed by the main flow. See the rule about not excluding host-required config files wholesale in `publish-workflow.md`.

## Other Requests

- `relist` / `delist` / `delete-draft`: the current shipped runtime does not have these APIs. Tell the creator explicitly that they are not supported, and do not work around them.
- Earnings, payout, statistics, refunds, KYC: read `api-docs/00_overview.md`.
- Local-only packaging self-check: there is no standalone local pre-flight entry; go through the formal main chain and handle failures per the JSON payload.

## Pitfalls

- **`isConfirmedSkills: 0` blocks `publish-configure`.** The CLI returns `"skill confirmation not completed — run publish-init first and confirm skills"`. This means the creator must visit the `review_url` from `publish-init` and confirm the skills/file selection on the web page. There is no API shortcut to set `isConfirmedSkills = 1` — it is exclusively set by the web confirmation page. Do not retry `publish-configure` as a workaround; paste the (refreshed) `review_url` and wait for web confirmation.

- **`custom_providers` can be `None` and crash `publish-configure` with `'NoneType' object is not iterable`.** The crash surfaces in `find_custom_provider()` at `provider_refs.py:14` when iterating over the providers list. Fix: guard `find_custom_provider` with `if not isinstance(custom_providers, list): return None`. See `references/provider-refs-none-guard.md` for the full traceback and fix. Symptom: `TypeError: 'NoneType' object is not iterable` with traceback ending at `provider_refs.py:14, for provider in custom_providers`.

- **Skill list is single-select on the web page.** The Capafy "Skill List" section on the `publish-init` review page only allows ONE skill to show as "Confirmed" at a time (radio-button behavior). Clicking a Pending skill sets it to "Confirmed" and toggles the previously confirmed one back to "Pending" or "Auto Recommended". Despite this UI limitation, the `workflowInfo` submitted by `publish-init` carries ALL selected skills, and the platform registers them all. After confirming any single skill on the web page, `isConfirmedSkills` becomes 1 — confirming even one skill unlocks the full set that was sent by `publish-init`. The "Selected N / M" counter on the page still shows 1, but the platform records all skills as selected.

- **Changing billing on the web page can flip `agentType`.** If the creator edits pricing from `subscription` to `download` (or vice versa) on the web page, the platform changes `agentType` from `run_online` to `download` (or the reverse). After the creator returns from a web page, always reconcile with `get_latest_version_raw(agentId)` and check `agentType` against expectations. If it changed, the platform has rolled the version back to draft and cleared `isConfirmedSkills`. Rerun `publish-configure --agent-id <id>` so the code re-stages under the new type.

- **Card details are web-page-only.** The following fields cannot be set via the CLI API — they must be filled on the `review_url` web page:
  - `detailedDescription` — the long README-style agent card body
  - `tags` — comma-separated keyword list
  - `screenshots` / `images` — up to 10 PNG/JPG/WebP, ≤2 MB each
  - `billings` / pricing — the card pricing tier (toggled on the web page)
  The CLI's `publish-init` only sends `title`, `shortDescription`, and `workflowInfo` (skill selections). For a polished agent card, prepare a README-style description beforehand using `references/agent-card-content-strategy.md`.

- **`publish-refresh-url` before re-pasting a URL.** Review URLs expire after 1 hour. If the creator returns after more than an hour and needs to visit the page, run `publish-refresh-url --agent-id <id> --step <init|configure|ship>` first — never re-paste an old `review_url` from earlier in the session.

- **Pricing defaults to $10/month subscription.** If the creator wants a different pricing strategy (e.g. cheap/mass-adoption), they must change it on the web page. The default plan includes 3 free trials with 24h expiration.

- **MCP server `env` block keys are invisible to credential detection.** Keys embedded inside `mcp_servers.<name>.env` in config.yaml (e.g. `LLMQUANT_API_KEY` under `mcp_servers.llmquant-data.env`) are never auto-detected as credentials — they bypass both the rule scan and the deep scan's generic/env_var detection. They remain as plaintext in the staged config.yaml. To properly host them: (a) the deep scan must manually flag them as `env_var` findings, and (b) the creator must manually add them on the credential confirmation page using **"Add environment variable"** (NOT "Add Hosted Key" — hosted keys are for LLM endpoints with URL+API key pairs; env vars are standalone values). See `references/credential-confirmation-page.md` and `references/deep-scan-review-checklist.md`.

Use the JS native setter trick: Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set.call(inp, val); inp.dispatchEvent(new Event('input', {bubbles:true})); inp.dispatchEvent(new Event('change', {bubbles:true}));

- **"Confirm & Save Keys" button requires a real user click.** Programmatic clicks (`browser_click`, `element.click()`, `dispatchEvent(new MouseEvent(...))`) cause page re-renders but NEVER trigger the actual API call to set `isConfirmedConfigKeys = 1`. The React event handler checks `event.isTrusted` or uses framework-internal callbacks that only fire on genuine user interaction. After clicking, verify with `get_latest_version_raw(agent_id)` -> `isConfirmedConfigKeys` should become `1`.

- **API alternative when browser credential page is unstable.** When the browser temp link keeps expiring (reloads reset all edits) or the React framework won't register programmatic value changes, you can POST credentials directly via save_config_keys_raw(agent_id, request_body). The payload format is: `{"agentVersionId": "<version_id>", "requiredCredentials": json.dumps({"url_proxy": [...], "generic": [...], "env_var": [...], "excludes": [...]})}`. See capafy_platform/api.py:save_config_keys_raw and packaging/configure/platform/config_keys_request.py:build_config_keys_request for the exact schema. **CRITICAL LIMITATION**: This only works ONCE (the first submission after deep scan). The second call returns `{code: 500, msg: "Internal server error"}` even with a valid payload — the platform rejects subsequent credential submissions. After that, all further credential changes must go through the web page's "Confirm & Save Keys" button (real user click required).

- **Two-layer provider model is easy to confuse.** The staged config's `model.provider` and the credential page's url_proxy LLM Config are DIFFERENT layers:
  - `model.provider` in staged `config.yaml` → determines which provider the AGENT RUNTIME uses (it reads its own config at startup)
  - url_proxy LLM Config on credential page → determines what Capafy's PROXY forwards to
  - They can be completely different (e.g. config says `openrouter` but url_proxy shows `freellmapi` at `localhost:3001`)
  - The url_proxy must exist for cloud-hosted agents (platform requires >=1), but doesn't have to match the model.provider
  - The agent's LLM access comes from the **env var** (e.g. `OPENROUTER_API_KEY` as Container-Injected), NOT from the url_proxy entry. The url_proxy is for Capafy's proxy routing only.
  - If the creator seems confused or asks "will this really work?" when the url_proxy shows something different from the configured model, explain the two-layer model briefly rather than trying to make them match.
  - If you change the staged config's `model.provider` AFTER configure has run (e.g. patching staged config directly), the credential page url_proxy will NOT auto-update — it shows whatever was detected during the last deep scan. That's fine as long as the new provider's API key is injected as an env var.

- **Credential page resume after session interruption.** When a publish was interrupted during the credential step — temp link expired, `isConfirmedConfigKeys=0`, `current_stage=config_submitted` — the next session must **reconcile first** before touching the browser:
  1. Run `publish-status` (local state) and `publish-remote-status --agent-id <id>` (platform state).
  2. Get a fresh URL with `publish-refresh-url --agent-id <id> --step configure`.
  3. **Before navigating to the page, present the current detected key landscape to the creator in chat.** Walk through each detected key individually. The creator may not remember what was on the page from the previous session, and some keys (especially personal tokens from `.hermes/.env` like `GITHUB_TOKEN`, `OPENROUTER_API_KEY`, personal API keys) may have been a surprise or upset them.
  4. Confirm the credential strategy per key: keep, unselect, or add a new env var. Only after the creator explicitly approves the strategy should you interact with the credential page.
  5. After confirming, verify `isConfirmedConfigKeys` becomes `1` by calling `publish-remote-status --agent-id <id>` (not `publish-status`, which is local-only). If still `0`, the "Confirm & Save Keys" real-user-click rule applies (see pitfall above).

- **Rule scan runs on STAGED files, not originals.** Each `publish-configure` re-scans the staged `.temp/staging/` files fresh. To remove unwanted credentials (e.g., personal `GITHUB_TOKEN`, `OPENROUTER_API_KEY` from `.hermes/.env`, or a local `custom_providers` entry pointing to `localhost`), you MUST edit the staged files **before** running `publish-configure`:
  - Staged `.env`: `/c/Users/.../capafy-publisher/.temp/staging/.hermes/.env` — comment out or delete lines.
  - Staged `config.yaml`: same path — remove or comment out `custom_providers` entries for local endpoints.
  The `deep-scan-findings` file with `excludes` does NOT remove rule-scan detections; it only adds deep-scan findings. To suppress rule-scan results, the staged files themselves must not contain the secrets.

- **API credential submission (`save_config_keys_raw`) is SINGLE-USE.** It only works ONCE — the first call after deep scan succeeds. All subsequent calls return `{code: 500, msg: "Internal server error"}` even with valid payloads. After that, all credential changes MUST go through the web page's "Confirm & Save Keys" button (real user click required due to React's `event.isTrusted` check). Browser automation (`browser_click`, `element.click()`, `dispatchEvent`) NEVER triggers the actual API call.

- **Web "Confirm & Save Keys" requires a REAL user click.** Programmatic clicks cause page re-renders but NEVER set `isConfirmedConfigKeys = 1`. The React handler checks `event.isTrusted` or uses internal callbacks that only fire on genuine user interaction. After any credential changes via browser, verify with `publish-remote-status --agent-id <id>` → `isConfirmedConfigKeys` should be `1`. If still `0`, the creator must click the button themselves.

- **`package failed: packaged bundle still contains creator-local paths`** — The package validator rejects skill files that reference local/relative file paths. **This validator is extremely aggressive** — it catches many more patterns than just `~/` and `./`. Known pattern classes the validator flags:

  | Pattern class | Example from real failures | Fix |
  |---|---|---|
  | `~/` home paths | `~/architecture-diagram.html`, `~/.hermes/.env` | Replace with generic description |
  | `./` relative paths | `./architecture-diagram.html`, `./my-file.html` | Replace with generic description |
  | `.../` ellipsis paths | `.../issues/N/comments` | Expand to full URL `https://api.github.com/repos/OWNER/REPO/issues/N/comments` |
  | `/word` absolute-looking paths | `/users endpoint`, `/dashboard` | Rewrite as plain English (e.g. "users endpoint", "the dashboard") |
  | `$VAR` shell variable in path-like context | `$PR_NODE_ID` inside GraphQL query string | Replace with `gh` CLI approach or restructure to avoid embedded variable in string |
  | Complex shell escaping with `$var` inside quoted JSON | GraphQL mutations with `\\\"$VAR\\\"` in curl `-d` strings | Prefer `gh` CLI approach over raw curl with escaped JSON |

  **Better approach — comprehensive sweep before any configure-ship attempt:**

  1. **(Pre-check in one command)** Before `publish-configure`, run a combined search for ALL known patterns:
     ```
     search_files(pattern='~/', path='<skill_dir>')
     search_files(pattern='\\./', path='<skill_dir>')
     search_files(pattern='\\.\\.\\./', path='<skill_dir>')
     search_files(pattern=' [/$][a-z]', path='<skill_dir>')  -- catches `/users`, `/dashboard` after space
     ```
     Pay special attention to code blocks (```bash```) and inline file-path examples.

  2. **Patch the source** SKILL.md (and any reference files):

     | What to find | Replace with |
     |---|---|
     | `~/path`, `~/.file` | Generic description of the concept (not a file path) |
     | `./my-file.html`, `./some-file.ext` | "a .html file" / generic description |
     | `open ./file` / `xdg-open ./file` | "suggest the user open it in their browser" |
     | `Save with write_file to a .html file (e.g. ./name.html)` | "Save the generated content with write_file to produce a .html file" |
     | `.../issues/N/...` / `.../pulls/N/...` | Expand to full URL: `https://api.github.com/repos/OWNER/REPO/...` |
     | `/word` in prose (e.g. `/users endpoint`, `/dashboard`) | Rewrite as plain English (no leading slash) |
     | Shell variables inside escaped JSON strings in `curl -d` | Replace with `gh` CLI approach or restructure |
     | Complex GraphQL queries with embedded vars | Prefer `gh api graphql -f query='...'` pattern |

  3. Re-run `publish-configure --agent-id <id>` — this creates fresh staging from the fixed source.
  4. Then run `publish-ship`.

  **CRITICAL never-do's:**
  - Do NOT edit staged files after `publish-configure` — it breaks the staging digest check (`reviewed-scan.json no longer matches the prepared download review staging`) and the ship will fail. Always fix the source, not the staging.
  - Do NOT fix one pattern at a time and re-ship — the validator will surface the NEXT pattern on each attempt, making the process take N+1 rounds. Fix ALL known patterns in one pass.
  - If `publish-ship` still fails after comprehensive source fix + re-configure: read the error message carefully for the specific remaining pattern, search the source for that exact string, patch it, re-configure, re-ship.

## Safety Boundaries

- `cwd` may be the publisher skill's own directory; do not default to treating it as the workspace to publish.
- When the creator says "workflow / project / workspace" and the input source is unclear, confirm with the creator first; when only a skill directory is given, treat it as `--skill-dir` and separately confirm the real `--runtime-dir`.
- Do not modify the working-state files under `.temp/` yourself. When you need to switch `runtime_dir` / switch selections, handle it per Core Iron Rule #6: by default rerun `publish-init` carrying the original `agent_id` (the continue / version-update branch), and **do not** proactively suggest `--reset-local-state`; only use reset when the creator explicitly says "scrap this agent and ship a new one", and recap that decision in chat first.
- **Exception: local agent_id differs from the target agent.** When `publish-status` shows a local `agent_id` (e.g. `7888913993`) that doesn't match the agent the creator is now working on (e.g. `8465413265`), the local staging belongs to a different agent and cannot be resumed. `--reset-local-state` is the correct path here — the creator did not change their mind about the same agent; they are publishing a different one. Check with `publish-status` first, explain the mismatch to the creator, then reset.
