---
name: system-load-triage
description: Use when the user reports high CPU or load spikes on Linux.
---

# System Load Triage (Linux)

Class: "why is my CPU overloaded / what's eating it" on the host that runs scheduled trading-bot backtests, the Hermes gateway, and a desktop. On this host, load spikes are usually self-inflicted scheduled jobs colliding, not malware or runaways — attribute before alarming. One workflow: quantify → attribute → prove → judge → prevent.

## Procedure (in order)

1. **Quantify.** `uptime`, `nproc`, `ps aux --sort=-%cpu | head -15`. Load ≫ nproc means oversubscription — with numpy/BLAS processes this is arithmetic, not automatically a fault: each BLAS-using process spawns ~one thread per core (check `grep Threads /proc/<pid>/status`), so N concurrent numpy jobs = N × cores threads competing. Don't trust a single `ps` snapshot — a transient process (even `ps` itself) can top it; re-sample before concluding.
2. **Attribute every heavy PID before touching it.**
   - Parent chain: `ps -o ppid= -p <pid>` then `ps -o args= -p <ppid>` — the parent names the launcher. A Hermes script wrapper (`~/.hermes/scripts/*.py`) as parent = Hermes cron fired it; a bash `-lic` wrapper = an agent terminal.
   - Start time: `ps -o lstart= -p <pid>`. Start ≈ boot time ⇒ boot-time launch, not a human.
   - Launch-source sweep: `crontab -l`, `ls ~/.config/autostart/`, `systemctl --user list-units --type=service,timer --state=running`, and Hermes `~/.hermes/cron/jobs.json` (job names + schedule expressions).
3. **Prove computing vs hung before recommending a kill.** Sample CPU ticks and disk reads twice:
   ```bash
   u1=$(awk '{print $14+$15}' /proc/PID/stat); i1=$(awk '/read_bytes/{print $2}' /proc/PID/io)
   sleep 10
   u2=$(awk '{print $14+$15}' /proc/PID/stat); i2=$(awk '/read_bytes/{print $2}' /proc/PID/io)
   # ~1000 ticks over 10s ≈ 1 core busy
   ```
   Rising utime with zero read_bytes = genuine compute (ML backtest, model training) — it is slow from contention, not stuck, and it will finish. Flat utime = spinning/waiting — investigate or kill.
4. **Judge let-finish vs kill.** Default for scheduled jobs that missed their slot and are mid-run: LET THEM FINISH (user-confirmed). Before killing a bot job, check its output artifact freshness — e.g. no row for today in the trade ledger ⇒ the run writes only at the end, so killing loses the run and the job must be re-run anyway. Kill only true runaways (accidental loops, fork explosions).
5. **Prevent recurrence — after the storm, not during it:**
   - Stagger heavy schedules. Never let two multi-core jobs share a slot; contention turns two ~30-min jobs into hours.
   - One owner per job. If system crontab AND Hermes cron fire the same script at different times, dedupe — double-runs append duplicate rows to ledgers.
   - Expect a catch-up burst: schedulers re-fire jobs that missed their slot while the machine was off, all at once at boot. Weekly jobs + a late boot = every weekly job collides in one burst.

## Pitfalls

- %CPU alone doesn't distinguish a backtest from a hang — always run the step-3 sampler; a job pegging 4 cores with zero I/O is working, not wedged.
- Cron catch-up bursts look like a runaway storm (three processes at 200%+, load 2× cores) but are self-limiting; the fix is schedule hygiene, not kills.
- Heavy-job schedules inherited from different projects drift into overlap — when touching any bot cron, re-read ALL schedules (system + Hermes) as one set before adding a new one.
