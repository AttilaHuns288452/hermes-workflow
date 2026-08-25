---
name: figma-api-reference
description: Figma REST API scopes, OAuth setup, and limitations.
triggers:
  - figma
  - figma api
  - figma oauth
  - figma token
  - figma prototype
---

# Figma API Reference

## Hard limitation: REST API is read-only for file content

The Figma REST API **cannot create nodes, frames, or prototype connections.** Write scopes only cover comments, dev resources, variables, and webhooks.

**To create frames and wire prototype interactions:**
- Figma Plugin API (runs inside Figma's context, not callable from CLI/scripts)
- Figma desktop app (manual)
- HTML prototype fallback — clickable screens with transitions (see `figma-html-import` for import-safe HTML patterns, or build a standalone interactive prototype)

## Correct OAuth scopes (2026)

Old scopes `file_read`, `file_write`, `files:read` are deprecated or invalid.

| Scope | Permission |
|-------|-----------|
| `file_content:read` | Read file contents (nodes, editor type) |
| `file_metadata:read` | Read file metadata |
| `file_comments:read` | Read comments |
| `file_comments:write` | Post/delete comments |
| `file_dev_resources:read` | Read dev resources |
| `file_dev_resources:write` | Write dev resources |
| `file_versions:read` | Read version history |
| `file_variables:read` | Read variables (Enterprise only) |
| `file_variables:write` | Write variables (Enterprise only) |
| `current_user:read` | Read name, email, profile image |
| `folders:read` | List folders and files |
| `selections:read` | Read most recent selection |
| `webhooks:read/write` | Manage webhooks |

**Format:** Colon-separated `scope:permission` (e.g. `file_content:read`). NOT `scope:action` (e.g. `file_read:true`).

## OAuth flow

1. Auth URL: `https://www.figma.com/oauth?client_id=...&redirect_uri=...&scope=file_content:read+file_metadata:read&response_type=code&state=...`
2. User authorizes in browser → redirect to `localhost:PORT/callback?code=...`
3. Exchange code: POST `https://www.figma.com/api/oauth/token` with `client_id`, `client_secret`, `redirect_uri`, `code`, `grant_type=authorization_code`

**Redirect URI must be pre-configured** in Figma app settings.

## Personal Access Token (simpler for read-only)

- Figma account settings → Personal access tokens → Generate
- Use as `X-Figma-Token: figd_...` header
- No OAuth flow, no redirect URI needed
- Read-only (cannot create/modify files)

## Pitfalls

- **Wrong scope format:** `file_read:true` → `Invalid scopes for app`. Use `file_content:read`.
- **Assuming REST API can create frames:** It cannot. Don't promise prototype creation via API.
- **OAuth app vs Personal Access Token:** OAuth app needs redirect URI + code exchange. PAT is just a header. For read-only, prefer PAT.
