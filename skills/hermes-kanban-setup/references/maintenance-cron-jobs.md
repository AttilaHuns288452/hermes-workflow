# Maintenance Cron Jobs

Four cron jobs keep the system healthy. All are `deliver: local` — silence means healthy. View results with `hermes cronjob list`.

## 1. LightRAG Daily Rebuild (`e3529912964e`)
- **Schedule**: daily at 4am
- **Command**: `python C:/Users/YOUR_USERNAME/AppData/Local/hermes/lightrag_index/build_index.py`
- **What**: rebuilds TF-IDF index from all 19 external skill dirs
- **Why**: skills added/updated need re-indexing. Sub-second, zero API cost.

## 2. Kanban Gateway Health (`b9af45968dde`)
- **Schedule**: every 30 minutes
- **Command**: `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8642/`
- **What**: pings the gateway. 404 = normal. No response or non-404 = alert.
- **Why**: dispatcher runs inside gateway — dead gateway = stalled kanban tasks.

## 3. Profile Config Drift Check (`9b15784784a2`)
- **Schedule**: daily at 6am
- **Command**: Python script comparing profiles' `skills.external_dirs` + `mcp_servers` against global config
- **What**: reports any profile missing skill dirs or MCP servers
- **Why**: new profiles created without `--clone-from learning` miss config.

## 4. Daily State Backup (`1e593d58df6d`)
- **Schedule**: daily at 3am
- **Commands**:
  - `hermes backup -q -l "daily-$(date +%Y%m%d)"`
  - `cp ~/AppData/Local/hermes/kanban.db ~/hermes-kanban-backup-$(date +%Y%m%d).db`
- **Why**: disaster recovery. Restore with `/snapshot restore <label>`.

## Recreate Any Cron Job

```bash
hermes cronjob create --schedule "<cron>" --name "<name>" --prompt "<command>" --enabled-toolsets terminal
```
