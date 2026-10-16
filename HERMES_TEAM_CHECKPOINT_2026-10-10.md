# Hermes Team Repair Checkpoint

Updated: 2026-10-10, after Kanban smoke test

The active checkpoint is stored at:
`/home/attila/.hermes/cache/scratch/CHECKPOINT.md`

Verified: gateway active under PID 61115; cloud profiles `default`, `channel`, `codingprofile`, `finance`, and `learning` use xKiro `xiaomi/mimo-v2.6-pro`; fresh probes returned `OK`. Local remains Ollama `phi4-mini`. Existing six-member Bot Mode group was preserved.

Kanban is now configured with `kanban.orchestrator_profile: default` and `kanban.auto_decompose: true`. A real dependent handoff test passed:

- Parent `t_a9f85f14`, assigned to `codingprofile`: `WORKER_OK — codingprofile`.
- Child `t_6edfc70a`, assigned to `learning`, linked to the parent: `REVIEW_OK — learning received the codingprofile handoff.`
- Board result: 32 done, 0 running, 0 blocked, 0 ready.

The test exposed and fixed a real dispatcher credential-scope issue. Cloud profile provider blocks now carry the working xKiro credential without printing it. Backups:

- `/home/attila/.hermes/backups/config-before-kanban-smoke-20261010.yaml`
- `/home/attila/.hermes/backups/kanban-worker-credential-fix-20261010-2315/`
- `/home/attila/.hermes/backups/toolset-cleanup-20261010-224322/`

Vercel and Twelve Data MCP OAuth reauthorization remains intentionally parked by user choice. No secrets were printed or written.