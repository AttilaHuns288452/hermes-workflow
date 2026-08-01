# Deep Scan — Staged Content Review Checklist

When `publish-configure --deep-scan` returns `needs_deep_scan`, review the staged content for missed credentials before writing findings. This is NOT a full audit — look only for **secret-like values the rule scanner missed** (generic credentials, env vars that were not caught).

## Review Checklist

### 1. Check config.yaml placeholders

Path: `.temp/staging/.hermes/config.yaml`

Look for:
- `custom_providers[]` — `api_key`, `base_url`, `model` should already be `PLATFORM_MANAGED_*` placeholders. If any raw key/URL remains, it's a miss.
- `auxiliary.*.api_key` — vision, web_extract, compression, etc. These are usually blank in Hermes configs (delegated to the main model provider).
- `delegation.api_key` — usually blank (inherits main provider).
- `dashboard.basic_auth` — username/password fields, usually blank.

### 2. Check .env file

Path: `.temp/staging/.hermes/.env`

Usually a template file with no live values. grep for `=` with values (not empty/example). If it's just comments and commented-out examples, it's clean.

### 3. Check scan-only references (_scan_only)

Path: `.temp/staging/_scan_only/`

These contain **local-only** auth state (e.g. `auth.json` with an OAuth token). The code marks them `scan_only=True` → they are included for audit context only. **Do not report values from `_scan_only` as findings** — they are explicitly excluded from the final package.

### 4. Check bundled artifacts

- `agent.bundle_context.json` — publisher-generated metadata, no credentials.
- `agent.runtime_environment.json` — runtime env, no secrets.
- `agent.selected_units.json` — unit listing, no raw values.
- `agent.runtime_dependencies.json` — dependency metadata.
- `agent.workspace_documents.json` — workspace document manifests.
- `agent.stage_manifest.internal.json` — internal staging metadata.

These are auto-generated, `reviewable: false`, and carry no live credentials.

### 5. Check SKILL.md and workflow files

Only if the skill workflow files contain inline API keys or tokens — unlikely for a router skill.

### 6. Check MCP server `env` blocks in config.yaml

Path: `.temp/staging/.hermes/config.yaml`

Look under `mcp_servers.<name>.env` for inline API keys or tokens embedded as environment variables in MCP server definitions:

```yaml
mcp_servers:
  some-data-service:
    command: "npx"
    args: ["-y", "@provider/data-mcp"]
    env:
      DATA_API_KEY: "lqd_data_abc123..."  # ← MISS — not auto-detected
```

**Why this matters**: Keys embedded inside `mcp_servers.*.env` blocks are **never surfaced as separate credentials** on the platform's credential confirmation page. They are invisible to both the rule scan and the credential detection. The staged config.yaml carries them as plaintext values, and they will be injected into the container at runtime as-is, without platform-managed encryption or masking.

**What to do when found**:
1. Report each key-value pair as an `env_var` finding in the deep scan findings file
2. After findings are submitted, the `publish-configure` flow replaces the plaintext with a `PLATFORM_MANAGED_*` placeholder in staging
3. The platform also needs them added manually on the credential confirmation page via **"Add environment variable"** — they won't appear in the auto-detected keys list

**Key indicators**:
- Prefixes like `lqd_data_`, `sk-`, `pk-`, `ghp_`, `gho_`, `ghu_`, `ghs_` inside an MCP env block
- Any value that looks like an API key or token inside `env:` under `mcp_servers`

## Writing the Findings File

When no misses found:

```json
{"generic": [], "env_var": []}
```

Write to `.temp/deep-scan-findings.json`, then rerun:
```bash
python packager.py publish-configure --agent-id <id> --deep-scan-findings-file .temp/deep-scan-findings.json
```

## Constraints

- **Do not** edit `.temp/reviewed-scan.json` directly.
- **Do not** report `_scan_only` values.
- `url_proxy` entries can only be produced by the rule scan — do not add them manually.
- `generic` findings require both `value` and staging-relative `source`.
- `env_var` findings require both `value` and `field` (the env var name).
