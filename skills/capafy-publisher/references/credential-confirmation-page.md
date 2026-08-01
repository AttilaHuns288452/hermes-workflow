# Credential Confirmation Page

When `publish-configure` succeeds, it returns a `review_url` like `https://api.capafy.ai/C<token>` (for Run Online mode). Paste this URL verbatim to the creator — in a browser it redirects to:

```
https://capafy.ai/developer/createAgent?source=temp-link&token=...&page=credential
```

## Page Structure

The page has a **timer bar** (links expire after ~59 minutes). "Unsaved content will be lost after expiration."

### Heading: "Credential Confirmation / Detected Keys (N keys)"

Two distinct credential sections:

### 1. Proxy-Hosted — LLM Config & Hosted Key

These keys are stored on Capafy's proxy servers with AES-256 encryption, decrypted only when forwarding requests. They **never** enter the agent's container.

Each entry shows:
- **Key name** (e.g. `custom_providers[0].api_key`)
- **Base URL** (e.g. `http://localhost:3001/v1`) — the LLM endpoint
- **Model** (e.g. `auto`)
- **API Key** — masked display (e.g. `FREEL****I_KEY`)
- **API Source** / **URL Source** — file paths (e.g. `.hermes/config.yaml`)

Available actions per entry:
- **Edit** — change the endpoint URL or API key
- **Unselect this key from hosting** — remove it from the hosted set
- **Add Hosted Key** — add a new url_proxy entry

### 2. Container-Injected — Environment Variables & Generic Config

These are injected into the container's environment at runtime as plaintext. Each entry shows:
- **Key name** (e.g. `OPENROUTER_API_KEY`)
- **Category** — "Generic Config"
- **Value** — masked display (e.g. `sk-or****d9e39`)
- **Source** — file path (e.g. `.hermes/.env`)

Available actions per entry:
- **Edit** — change the value before hosting
- **Unselect this key from hosting** — remove from the hosted set
- **Add environment variable** — add a new env_var entry

### Footer

- **How Your Keys Are Protected** — expandable explanation section
- **Confirm & Save Keys** — saves all edits/removals and advances the workflow

## Bulk Operations

### Unselecting multiple keys

The page shows each key with an "Unselect this key from hosting" button (a trash-can SVG icon, `title="Unselect this key from hosting"`). To unselect all unwanted keys at once, run this in the browser DevTools console:

```js
document.querySelectorAll('button[title="Unselect this key from hosting"]').forEach(b => b.click());
```

This is useful when the deep scan uploaded several env vars (GitHub token, OpenRouter key, etc.) that the creator does not want hosted alongside the LLM endpoint.

### Adding keys

- **Add Hosted Key** — adds a new url_proxy entry (another LLM endpoint)
- **Add environment variable** — adds a new generic env var

## Post-Unselection State

After a key is unselected, the page moves it into an **"Unselected Keys"** section below the main key lists. Each unselected entry shows a **"Restore"** button to move it back. The heading updates to reflect the new count (e.g. "Detected Keys (1 key)").

## Important Notes

- **The bare `/C...` URL works in a browser.** When accessed via a normal browser, `https://api.capafy.ai/C<token>` redirects to the frontend automatically. The 401 prefix-error (e.g. `"This path requires the /agent/, /app/, /public/, or /container/ prefix"`) only occurs when the URL is accessed from an API client without following redirects, or inside an API-only context. If the creator reports this error, advise them to open the URL in a regular browser tab.

- **Configuration confirmation belongs on the web page, not in chat.** Do not ask the creator to paste API keys, endpoints, or token values in chat. Direct them to the review URL to Edit / Add / Unselect entries there.

- **`localhost` endpoints are fine to submit.** Even if the endpoint URL is `http://localhost:3001/v1` or another LAN/private-network address, submit it to the credential confirmation page — the creator edits or removes it there. Do not reject, judge, or suggest an alternate provider in chat.

- **URL expires in ~1 hour.** If the creator cannot visit in time, refresh with `publish-refresh-url --agent-id <id> --step configure` and paste the fresh URL.

- **Temp link is single-session — page reload loses all changes.** The credential confirmation page uses a temporary link with a ~32–59 minute expiry (the countdown resets on each full page load, not from link creation). If the browser is closed, the tab is refreshed, or the page state is otherwise lost (e.g. browser automation session resets — browser_navigate reloads the page and resets the timer), **all unselections, edits, and added keys are lost**. The page re-loads fresh with the original detected keys. You must redo all edits after re-navigating to the fresh URL. This is not a save-able form — the Confirm & Save Keys button is the only persistence point.

- **LLM Config (url_proxy) has NO Unselect button for cloud-hosted agents.** The platform requires at least one url_proxy entry. The Proxy-Hosted section for the LLM endpoint shows only "Edit" and "Add Hosted Key" — there is no way to remove the last remaining LLM provider. If the creator wants to replace the endpoint (e.g. change localhost to a real provider), use the "Edit" button. Container-Injected entries (generic config and env vars) DO have "Unselect this key from hosting" buttons and can be freely removed.

- **Browser automation: setting input values requires native JS setters.** The page uses a reactive framework that intercepts input events, so `input.value = '...'` alone does not register the change. To set values programmatically:
  1. Use the native value setter: `Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set.call(inputElement, newValue)`
  2. Then dispatch `input` and `change` events: `inputElement.dispatchEvent(new Event('input', {bubbles:true})); inputElement.dispatchEvent(new Event('change', {bubbles:true}))`
  3. Verify the value took by reading `inputElement.value`
  4. Click "Save" — if it didn't register, the "Save" button may be disabled

- **API alternative when browser UI is unstable.** If the temp link keeps expiring or the reactive framework won't accept programmatic value changes, submit credentials directly via the API: `capafy_platform.api.save_config_keys_raw(agent_id, payload)` where payload = `{"agentVersionId": "<version_id>", "requiredCredentials": json.dumps({...})}`. This bypasses the browser UI entirely. The endpoint is `POST /agent/agents/{agent_id}/credentials`. See `config_keys_request.py:build_config_keys_request()` for the exact schema.

- **The "Add environment variable" and "Add Hosted Key" buttons share the same CSS class (keyHostingAddBtn).** Differentiated only by inner text. To click the right one programmatically: `document.querySelectorAll('button')[N].click()` — button order is: Detected Keys accordion, Add Hosted Key, empty, Save, Cancel (when form open), Add environment variable, Restore buttons, How Your Keys Are Protected, Confirm & Save Keys.

- **MCP server env vars are NOT auto-detected.** Keys embedded inside `mcp_servers.<name>.env` blocks in config.yaml (e.g. `LLMQUANT_API_KEY` under `mcp_servers.llmquant-data.env`) are never surfaced as credentials on this page. They are invisible to both the rule scan and credential detection. To include them:
  1. Run the deep scan first — it will find them and replace the plaintext with `PLATFORM_MANAGED_*` placeholders in staging
  2. On this page, click **"Add environment variable"** and enter the key name (not "Add Hosted Key" — these are generic config values, not LLM endpoints)
  3. The creator types the value directly on the platform page (never in chat)

## API 500 on Re-Submission (save_config_keys)

Calling `save_config_keys()` / `save_config_keys_raw()` a **second time** after the initial deep-scan submission returns `HTTP 200` with `{code: 500, msg: "Internal server error"}` even with a structurally valid payload. The platform rejects subsequent credential submissions — it only accepts the first one. After that, all credential changes must go through the web page UI's "Confirm & Save Keys" button. If the API returns 500, do not retry or modify the payload; direct the creator to the web page.

## Programmatic Click Fails on "Confirm & Save Keys"

The "Confirm & Save Keys" React button does NOT fire the submission API call when activated programmatically. The following all fail to trigger the actual fetch/XHR:
- `browser_click(ref)` — page re-renders (keys reorder visually) but no request fires
- `element.dispatchEvent(new MouseEvent('click', ...))` — same, UI responds, API silent
- `element.click()` — same result

The button React event handler likely checks `event.isTrusted` or uses a framework-internal callback that only fires on genuine user interaction. **The only reliable way to confirm credentials is a real user mouse click.** After clicking, verify with `get_latest_version_raw(agent_id)` → `isConfirmedConfigKeys` should become `1`.

**Workaround when the browser is unstable:** If the temp link keeps expiring and programmatic clicks fail, the creator must visit the fresh URL and click the button themselves — there is no API-only path to toggle `isConfirmedConfigKeys` from `0` to `1`.

## After Confirmation
1. Call `get_latest_version_raw(agent_id)`
2. Check `isConfirmedConfigKeys` — should be `1` after confirmation
3. If also `isConfirmedSkills: 1` and status is still `draft (0)`, proceed to `publish-ship`

## Two-Layer Architecture: staged config vs credential page

The url_proxy entries on this page and the agent's `model.provider` in the staged config.yaml are **independent layers**:

| Layer | Purpose | Configured by |
|-------|---------|--------------|
| **url_proxy** (this page) | Capafy's proxy forwarding for LLM requests | Deep scan of staged `config.yaml` + `custom_providers[]` |
| **model.provider** (staged config) | Which provider the agent runtime uses internally | `publish-init` staged config from skill source |

The agent runtime reads `model.provider` from its own config.yaml and looks for the corresponding env var (e.g. `OPENROUTER_API_KEY`). The url_proxy entry is for Capafy's proxy layer — it's how the platform routes and authenticates LLM requests through its servers.

**This means:**

- The url_proxy can show an old/different provider (e.g. `freellmapi` at `localhost:3001`) while the staged config says `model.provider: openrouter` — and the agent will use OpenRouter, NOT the url_proxy provider. The url_proxy entry exists because the platform requires at least one for Run Online mode (`require_cloud_hosted_url_proxy_entries` gate).

- If you edit the staged config's `model.provider` AFTER the initial `publish-configure`, the url_proxy entry on this page will NOT auto-update — it reflects whatever was detected during the last deep scan. The url_proxy can be edited on this page, or left as-is if it's not referenced by the agent's runtime config.

- The agent needs the **env var** for its chosen provider (e.g. `OPENROUTER_API_KEY`) to be injected as a Container-Injected credential. The url_proxy LLM Config entry does NOT supply this — it only routes through Capafy's proxy.
