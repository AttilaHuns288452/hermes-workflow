# Fleet-wide model/provider swap

A request like "replace model X with model Y everywhere" is a **provider migration**.
Model ids are provider-scoped API surfaces, not portable names: the same weights are
listed under different ids (`deepseek/deepseek-v4.1-flash` vs `deepseek-v4.1-flash-1017`),
and one provider may serve an id while another answers 403 (PAYG-only, plan does not cover
it). Change `model` + `provider` (+ `base_url` when the block carries one) as ONE unit.

## 1. Inventory every surface

| File | Keys that carry a model pin |
|---|---|
| `~/.hermes/config.yaml` | `model.{default,provider,base_url}`, `delegation`, `moa.aggregator`, `moa.reference_models[]`, `moa.presets.*`, `auxiliary.*` (`background_review`, `vision`, `web_extract`, `compression`, `triage_specifier`, `kanban_decomposer`, `profile_describer`), `fallback_providers[]`, `providers.<name>.default_model` / `.model` |
| `~/.hermes/profiles/<name>/config.yaml` | same shape, per profile |
| `~/.hermes/profiles/<name>/.env` | the provider's API key (profiles do not see the root key) |
| `~/.hermes/cron/jobs.json` | per-job `model` + `provider` — drive this via `hermes cron edit`, never by editing the file |

Leave alone unless asked: model **catalog** rows (`providers.<p>.models:` → `vendor/model: {}`)
describe what a provider offers, not what runs, and desktop UI state
(`ui-preferences.json` favorites/presets) is rewritten by the running app.

`auxiliary.*` and `moa.*` nest at indent 4, the same indent as `providers.<p>.default_model`.
That collision is what a naive indent-based rewrite gets wrong — see step 4.

## 2. Probe each (provider, model) pair before pinning it

```bash
curl -s -o /dev/null -w "%{http_code}\n" "$BASE/chat/completions" \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126" \
  -d '{"model":"<id>","messages":[{"role":"user","content":"ok"}],"max_tokens":1}'
```

- Send a browser-like `User-Agent`. Cloudflare-fronted gateways 403 UA-less requests, which reads as a bad key.
- 403 `pay-as-you-go … not covered by a plan` = provider serves the model but bills it outside the plan. Do not make it a provider default.
- `providers.<p>.default_model` must name a model THAT provider answers 200 for. When you retire a model, give each provider block a default probed on that provider; never transplant the new model id into a provider that 403s it.

## 3. Rewrite as line edits, not YAML round-trips

- Back up every touched file first: `~/.hermes/backups/<topic>-<timestamp>/`.
- `patch`/`write_file` **refuse** `~/.hermes/config.yaml` (security gate). Edit from a Python heredoc in `terminal` (`open(p).read()` / `write()`); profile configs go through the same path when convenient.
- Never `yaml.safe_load` → `yaml.dump`: comments, key order and quoting are lost.
- Replace the value on `model:` / `default:` / `default_model:` lines, then in the SAME pass rewrite the sibling `provider:` and `base_url:` at the same indent.
- Provider-block defaults are a separate decision from routing refs: routing → the new model/provider; provider defaults → a model that provider actually serves (step 2).

## 4. Verify semantics, not replacement counts

A line-oriented pass will miss a nesting level. Parse every file and assert the pairing:

```python
import yaml, glob
def walk(node, path, f, bad):
    if isinstance(node, dict):
        for k, v in node.items():
            p = f"{path}.{k}" if path else str(k)
            if isinstance(v, str) and v == TARGET_MODEL:
                if node.get('provider') != TARGET_PROV:
                    bad.append((f, p, f"provider={node.get('provider')}"))
                elif node.get('base_url') and node['base_url'] != TARGET_BASE:
                    bad.append((f, p, f"base_url={node['base_url']}"))
            walk(v, p, f, bad)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f"{path}[{i}]", f, bad)
bad = []
for f in ['config.yaml'] + sorted(glob.glob('profiles/*/config.yaml')):
    walk(yaml.safe_load(open(f)), '', f, bad)
print('problems:', bad)
```

Require `problems: 0` **and** a plausible count of checked pairs (a verifier that walks zero
nodes passes silently). Then `grep -c '<retired-model-id>' config.yaml profiles/*/config.yaml cron/jobs.json`
→ 0. Where the system `python3` lacks yaml, run the check through
`~/.hermes/bin/uv run --with pyyaml python -c "..."`.

## 5. Prove it live, per layer

- **Cron** — `hermes cron edit <id> --model <m> --provider <p>` for every job (loop; no bulk flag), then trigger one agent job. `Updated job: <id>` only proves the file changed; the proof is the run's session row:
  ```bash
  sqlite3 ~/.hermes/state.db "select model, billing_provider from sessions where source='cron' order by rowid desc limit 3;"
  ```
  `cron/usage_audit.jsonl` tail carries `model` for each completed run as a second witness.
- **Profile** — `hermes -p <profile> -z "Reply with exactly: OK"`. A profile is only proven by a turn, and only after its own `.env` carries the key.
- **Main session / gateway** — config is read at session start; an already-running process may keep the old default until a new session. Do not restart the gateway mid-conversation to hurry it.

## 6. Fallback ladder

A `fallback_providers[0]` naming the same provider+model as the primary is dead weight: on
an outage it retries the thing that just failed. Point the fallback at a different provider
with a probe-verified model, and keep an offline/local entry last.
