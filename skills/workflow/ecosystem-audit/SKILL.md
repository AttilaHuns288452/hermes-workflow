---
name: ecosystem-audit
description: "Weekly Hermes ecosystem audit: MCP, skills, cron."
---

# Ecosystem Audit

Self-contained weekly audit (cron `workflow-ecosystem-audit`, Mon 07:00). No user present — no questions. **Only writes allowed: patches to `decide/SKILL.md` + the sync scripts' own output.** Everything else is read-only; report findings.

## Steps

1. **MCP health** — `cd ~/AppData/Local/hermes && hermes mcp list`. Then test each enabled server: `timeout 60 hermes mcp test <name>`. ⚠️ In a loop, `| tail -5` scrolls early results out of the process log buffer — run servers individually, or grep `✓|✗|Connected|failed|Unauthorized`.
   - **Expected failures, not regressions:** `opendesign` → connection failed when the Open Design app isn't running (daemon-gated; `od-*` skills are the fallback, documented in /decide). `figma` → `401 Unauthorized` = Composio auth expired, needs re-auth. Both are signatures, report as "expected/down", don't treat as breakage.
   - 12 servers enabled (baseline 2026-08): 21st, agentmemory, codegraph, graphify, llmquant-data, obsidian-kg, opendesign, vscode, firecrawl, figma, flowbite, figma-dev. `obsidian-kg` reports "1 tool" in `hermes mcp test` but exposes 5 (rest are resources/prompts) — a live `list_resources` call proves it works.
2. **Skills inventory** — run `python scripts/audit-skills.py` (counts SKILL.md, flags broken frontmatter, lists empty category dirs). Cross-check `external_dirs` in `config.yaml` exist. Baseline 2026-08-14: 412 skills / 33 categories / 19 external_dirs.
   - Broken frontmatter: typically unquoted `: ` in a description (YAML "mapping values are not allowed here") — report file + fix, don't edit (outside allowed writes).
3. **Routing coverage** — read `skills/decide/SKILL.md`; verify the domain table covers: supabase, vercel/nextjs deploys, browser automation, elevenlabs-tts, ocr, comfyui/gpt-image-2, mlops (hf/llama-cpp/wandb), openhue, wix, music/audio, impeccable, stop-slop, od-* category, and all enabled MCP servers. **Empty category dirs that /decide routes to = dead routes** — patch the row to a real skill (2026-08-10 fixed: email→`email--himalaya`/`gmail`, research→`research--arxiv`/`research--blogwatcher`/`research--grounded-citations`, smart-home→`smart-home--openhue`). Keep the existing `| Trigger | Route To |` style.
4. **OpenDesign sync** — `python scripts/export-design-skills-to-opendesign.py` then `python scripts/import-opendesign-skills-to-hermes.py` (both idempotent). Steady-state output: export "plugins generated ~201, DB rows inserted 0"; import "imported 66, skipped (collision) 77" — 0 new is normal, not a failure.
5. **Cron health** — `hermes cron list` truncates the view at ~7 jobs: take `head -50` AND `tail -60` of the same command, or read `cron/jobs.json` directly. Flag `last_status: error`; read `cron/output/<job_id>/` for detail. Trivial-safe fix only: missing script path → copy the script into `scripts/` (see `hermes-cron-jobs` skill; `cron edit --script` rejects absolute paths). Note "Gateway is not running" warning — scheduler won't fire until started.
   - **Backup cron error signature:** `storageQuotaExceeded` (403) = Drive quota (15 GiB), NOT a script bug. 2026-08-14 root cause: `state-snapshots/` (~1.1 GB/day rolling hermes-backup outputs) was inside BACKUP_ITEMS → every zip 2–3 GB → quota blown. Fixed: excluded state-snapshots (zip 2.06 GB → 657 MB), KEEP 5→3, cleaned `tmp/` staging junk that failed runs leave behind (~25 GB: `tmp/backup-account` + stale zips — script only cleans on success). Full detail in `workflow/hermes-backup-workflow` skill. If the error recurs, check `rclone about YOUR_RCLONE_REMOTE:` first.

## Report format

```
## Ecosystem Audit — <date>
- MCP: [up/down list, tool counts]
- Skills: [count, broken frontmatter count]
- /decide routing: [gaps + patches applied, or "complete"]
- OpenDesign sync: [exported/imported counts]
- Cron: [errored jobs + suggested fixes]
- Pipelines updated: [changes made]
```

## Pitfalls

- `session_search` may not exist in cron environments — skip it, the job is self-contained.
- `find skills -name SKILL.md` in git-bash undercounts (path-length limits); trust the python glob (406 vs 288 observed).
- Skills named identically in `external_dirs` (e.g. `~/.agents/skills`) make bare `skill_view` ambiguous — use the local `skills/...` path.
- `search_files`/rg can throw "IO error: cannot find the file" on files that exist (hit on SOUL.md and scripts in this dir) — fall back to `read_file` or `grep` in terminal, both work.
- 10 minutes max for the MCP test loop; run it in background and poll.
