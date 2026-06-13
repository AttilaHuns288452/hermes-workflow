# Secret Scan Patterns & Key Rotation Workflow

## Provider-Specific API Key Patterns

When scanning mirrored skills for leaked credentials, check for these patterns:

| Provider | Pattern | Example Match |
|----------|---------|---------------|
| **FreeLLMAPI** | `freellmapi-[a-f0-9]\{32,\}` | `freellmapi-478fb71189798799bd9dc7c65b80c8a` |
| **OpenAI** | `sk-[A-Za-z0-9]\{20,\}` | `sk-proj-...` |
| **Anthropic** | `sk-ant-[A-Za-z0-9]\{20,\}` | `sk-ant-...` |
| **GitHub PAT** | `ghp_[A-Za-z0-9]\{36,\}` | `ghp_xxxx...` |
| **GitHub OAuth** | `gho_[A-Za-z0-9]\{36,\}` | `gho_xxxx...` |
| **GitHub App** | `ghs_[A-Za-z0-9]\{36,\}` | `ghs_xxxx...` |
| **Slack** | `xox[bpras]-[A-Za-z0-9-]\{10,\}` | `xoxb-...` |
| **Google API** | `AIza[0-9A-Za-z_-]\{35\}` | `AIzaSy...` |
| **AWS Access Key** | `AKIA[0-9A-Z]\{16\}` | `AKIAIOSFODNN7EXAMPLE` |
| **OpenRouter** | `sk-or-v1-[a-f0-9]\{64,\}|` | `sk-or-v1-...` |
| **HuggingFace** | `hf_[A-Za-z0-9]\{32,\}` | `hf_xxxx...` |
| **Gemini** | `AIza[0-9A-Za-z_-]\{35,\}` | `AIzaSy...` |
| **Groq** | `gsk_[A-Za-z0-9]\{40,\}` | `gsk_xxxx...` |
| **DeepSeek** | `sk-[a-f0-9]\{32,\}` | `sk-xxxx...` |
| **Cerebras** | `csk-[a-f0-9]\{40,\}` | `csk-xxxx...` |
| **Together AI** | `tgp-v1-[A-Za-z0-9]\{40,\}` | `tgp-v1-...` |
| **Generic Bearer** | `Bearer [A-Za-z0-9_-]\{32,\}` | `Bearer eyJ...` |

## Common Leak Locations in Mirrored Skills

API keys tend to end up in these file types during skill mirroring:

1. **`references/` files** — setup transcripts, debugging logs, CLI output (most common source — **3 of 4 leaks in this session came from a references file**)
2. **`scripts/verify-*.py`** — verification scripts with hardcoded test keys
3. **`README.md` / runbook-style docs** — inline curl/pip commands with `$TOKEN` expanded
4. **Code examples** in SKILL.md or reference docs — `requests.post(..., headers={'Authorization': f'Bearer ...'})`
5. **`templates/*.yaml/**/*.json` — config files with default values that are actually real

## Key Rotation Workflow (Full Script)

When a real key is found in the public repo, follow this exact sequence:

### Step 1: Rotate on the Service
```bash
# FreeLLMAPI example — adapt for other providers
# Login
TOKEN=$(curl -s http://localhost:3001/api/auth/login -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@localhost","password":"<admin-password>"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Regenerate
NEW_KEY=$(curl -s http://localhost:3001/api/settings/api-key/regenerate -X POST \
  -H "Authorization: Bearer $TOKEN" \
  | python -c "import sys,json; print(json.load(sys.stdin).get('apiKey',''))")

echo "NEW_KEY=$NEW_KEY"
```

### Step 2: Update Local Credentials
```bash
# .env
sed -i "s|^FREELMAPI_API_KEY=.*|FREELMAPI_API_KEY=$NEW_KEY|" ~/.hermes/.env

# Hermes auth (remove old, add new)
hermes auth remove custom:freellmapi 1
hermes auth add freellmapi --type api-key --api-key "$NEW_KEY" --label "FreeLLMAPI Key"
```

### Step 3: Scrub Repo Files
Replace ALL occurrences of the leaked key in the repo with `[REDACTED]`:
```bash
cd ~/Documents/Projects/hermes-workflow
grep -rl "$LEAKED_KEY" skills/ | xargs sed -i "s|$LEAKED_KEY|[REDACTED]|g"
```

### Step 4: Amend Git History
If the leaked file was in the most recent commit:
```bash
git add -A
git commit --amend --no-edit
git push --force-with-lease origin master
```

If the leak is in an older commit, use filter-branch or, preferably,
`git filter-repo` to purge the file from all history.

## Prevention Checklist

Before every ecosystem documentation export (Phase 0.5):

- [ ] Scan all mirrored files for provider-specific API key patterns
- [ ] Verify `.env.example` has NO real values (use `YOUR_*` placeholders)
- [ ] Verify `config.yaml.template` has NO real keys/paths/passwords
- [ ] Check git history for previously committed secrets (esp. before first push)
- [ ] If any scan fails → rotate the exposed key, scrub, amend, force push
- [ ] Only proceed to Phase 1 after passing all scans
