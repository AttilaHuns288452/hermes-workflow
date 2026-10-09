#!/usr/bin/env python3
"""
Hermes Ecosystem Audit — lightweight + deep

One script, two modes:
  --light  (fast, <10s): change detection only. Runs frequently via cron.
  --deep   (thorough):  full capability-map refresh + registry + changelog.

Idempotent: running twice with no environment changes produces NO writes
(except a timestamp touch in registry.last_checked).

Usage:
  python ecosystem-audit.py --light
  python ecosystem-audit.py --deep
  python ecosystem-audit.py --deep --force   # force deep even if nothing changed

Cron:
  lightweight  -> 0 3 * * *  (daily 03:00)
  deep         -> 0 4 * * 0  (weekly Sunday 04:00)

Registry:  ~/.hermes/ecosystem-registry.json
Changelog: ~/.hermes/ecosystem-changelog.md
Capability: CAPABILITY_GRAPH.md (updated on deep when topology changes)
"""
import argparse, json, hashlib, subprocess, sys, os, re, datetime, pathlib

HERMES = pathlib.Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
REGISTRY = HERMES / "ecosystem-registry.json"
CHANGELOG = HERMES / "ecosystem-changelog.md"
INTEGRATION_MANIFEST = HERMES / "four-repo-integration-manifest.json"
UPSTREAM_MIRRORS = HERMES / "upstream-sources" / "four-repo-integration"


def sh(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return f"ERR:{e}"

def file_hash(p: pathlib.Path):
    if not p.exists(): return "MISSING"
    try:
        h = hashlib.sha256()
        h.update(p.read_bytes())
        return h.hexdigest()[:12]
    except: return "ERR"

def list_skills():
    out = sh('hermes skills list 2>&1 | head -n 5', 10)
    cnt = sh('hermes skills list 2>&1', 10).count('\n')
    # fallback: count skill dirs
    dirs = 0
    for base in [HERMES / "skills", pathlib.Path.home() / ".agents" / "skills"]:
        if base.exists():
            dirs += len([d for d in base.iterdir() if d.is_dir()])
    # external dirs from config
    return {"hermes_skills_list_lines": cnt, "dir_count_approx": dirs}

def snapshot():
    """Collect lightweight environment fingerprint."""
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    snap = {"timestamp": now}
    # counts
    snap["skills"] = list_skills()
    snap["mcp"] = sh("hermes mcp list 2>&1 | cat", 10)[:4000]
    snap["mcp_hash"] = hashlib.sha256(snap["mcp"].encode()).hexdigest()[:12]
    snap["config_hash"] = file_hash(HERMES / "config.yaml")
    snap["soul_hash"] = file_hash(HERMES / "SOUL.md")
    # decide skill is canonical
    snap["decide_skill_hash"] = file_hash(HERMES / "skills/decide/SKILL.md")
    snap["decide_home_hash"] = file_hash(HERMES / "DECIDE.md")
    snap["capability_graph_hash"] = file_hash(HERMES / "CAPABILITY_GRAPH.md")
    snap["scripts"] = sorted([p.name for p in (HERMES / "scripts").glob("*.py")]) if (HERMES / "scripts").exists() else []
    snap["scripts_hash"] = hashlib.sha256(" ".join(snap["scripts"]).encode()).hexdigest()[:12]
    # LightRAG
    snap["lightrag_index"] = file_hash(HERMES / "lightrag_index/skill_index.json")
    # Upstream integration: detect mirror disappearance or pinned-head drift without
    # injecting the mirrors into the per-turn skill roots.
    snap["four_repo_manifest_hash"] = file_hash(INTEGRATION_MANIFEST)
    mirrors = {}
    if UPSTREAM_MIRRORS.is_dir():
        for mirror in sorted(p for p in UPSTREAM_MIRRORS.iterdir() if p.is_dir()):
            head = sh(f'git -C "{mirror}" rev-parse HEAD 2>/dev/null', 10).strip()
            mirrors[mirror.name] = {"exists": True, "head": head or "not-a-git-repo"}
    snap["four_repo_mirrors"] = mirrors
    # tools
    snap["providers"] = sh("hermes config get providers 2>&1 | head -n 30", 10)[:2000]
    snap["model_default"] = sh("hermes config get model.default 2>&1 | head -n 5", 10).strip()
    # plugins / cron
    snap["plugins"] = sh(f'ls "{HERMES}/plugins/" 2>&1 | tr "\\n" " " | head -c 500', 10).strip()
    snap["cron"] = sh("hermes cron list 2>&1 | cat", 10)[:3000]
    snap["cron_hash"] = hashlib.sha256(snap["cron"].encode()).hexdigest()[:12]
    # codegraph/graphify quick
    snap["graphify_projects"] = sh(f'ls "{pathlib.Path.home()}/Documents/Projects/"*/graphify-out/graph.json 2>&1', 10).count('\n')
    return snap

def load_registry():
    if REGISTRY.exists():
        try: return json.loads(REGISTRY.read_text(encoding="utf-8"))
        except: return {}
    return {}

def save_registry(snap):
    REGISTRY.write_text(json.dumps(snap, indent=2, ensure_ascii=False), encoding="utf-8")

def append_changelog(entry: str):
    header = "# Ecosystem Changelog\n\n> Auto-maintained by `scripts/ecosystem-audit.py`. Only meaningful changes logged.\n\n"
    if not CHANGELOG.exists():
        CHANGELOG.write_text(header, encoding="utf-8")
    ts = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d %H:%M %z")
    line = f"## {ts}\n{entry}\n\n"
    # prepend after header (keep recent first) — simple append for now (ponytail: append, not reflow)
    with open(CHANGELOG, "a", encoding="utf-8") as f:
        f.write(line)

def diff_snap(old, new):
    diffs = []
    for k in ["config_hash","soul_hash","decide_skill_hash","decide_home_hash","capability_graph_hash","mcp_hash","scripts_hash","cron_hash","lightrag_index","four_repo_manifest_hash"]:
        if old.get(k) != new.get(k):
            diffs.append(f"{k}: {old.get(k,'∅')} → {new.get(k,'∅')}")
    if old.get("skills") != new.get("skills"):
        diffs.append(f"skills: {old.get('skills')} → {new.get('skills')}")
    if old.get("four_repo_mirrors") != new.get("four_repo_mirrors"):
        diffs.append(f"four_repo_mirrors: {old.get('four_repo_mirrors', {})} → {new.get('four_repo_mirrors', {})}")
    # also check skill/scripts list content diff
    if old.get("scripts") != new.get("scripts"):
        diffs.append(f"scripts: {old.get('scripts')} → {new.get('scripts')}")
    return diffs

def lightweight():
    snap = snapshot()
    old = load_registry()
    if not old:
        save_registry(snap)
        msg = f"Initial registry created. skills={snap['skills']} mcp_hash={snap['mcp_hash']} model={snap['model_default']}"
        print(msg)
        append_changelog(f"- **INIT** {msg}")
        return 0

    diffs = diff_snap(old, snap)
    snap["last_checked"] = snap["timestamp"]
    snap["last_lightweight"] = snap["timestamp"]
    # preserve last_deep if exists
    if "last_deep" in old: snap["last_deep"] = old["last_deep"]
    if "history" in old: snap["history"] = old["history"]

    if not diffs:
        # idempotent: only update timestamp, no changelog noise
        save_registry(snap)
        print(f"[light] no changes — mcp:{snap['mcp_hash']} decide:{snap['decide_skill_hash']} model:{snap['model_default']}")
        return 0

    # changes detected
    save_registry(snap)
    entry = "- **LIGHT** changes:\n" + "\n".join(f"  - {d}" for d in diffs)
    entry += f"\n  - model_default: {snap['model_default']}"
    print(entry)
    append_changelog(entry)

    # Heuristic: if skill/mcp/config changed, nudge toward deep audit
    significant = any(k in " ".join(diffs) for k in ["decide","mcp_hash","skills","config_hash"])
    if significant:
        print("[light] significant change — next deep audit will reconcile DECIDE/CAPABILITY_GRAPH")
    return 0

def deep(force=False):
    snap = snapshot()
    old = load_registry()
    diffs = diff_snap(old, snap) if old else ["initial deep audit"]

    if not force and not diffs and old.get("last_deep"):
        # Check if deep is due anyway (weekly). If last_deep < 7 days ago and no changes, skip heavy work.
        try:
            last = datetime.datetime.fromisoformat(old["last_deep"])
            now = datetime.datetime.now(datetime.timezone.utc)
            if last.tzinfo is None: last = last.replace(tzinfo=datetime.timezone.utc)
            if (now - last).days < 7:
                print(f"[deep] no changes and last deep {old['last_deep']} <7d ago — skipping (use --force to override)")
                snap["last_checked"] = snap["timestamp"]
                snap["last_deep_skipped"] = snap["timestamp"]
                if "last_deep" in old: snap["last_deep"] = old["last_deep"]
                save_registry(snap)
                return 0
        except: pass

    print("[deep] running full audit...")
    # 1) Refresh counts in CAPABILITY_GRAPH.md and DECIDE.md headers if drifted
    cap = HERMES / "CAPABILITY_GRAPH.md"
    if cap.exists():
        txt = cap.read_text(encoding="utf-8")
        # Update the "Last audit:" line with fresh counts
        skills_lines = snap["skills"].get("hermes_skills_list_lines","?")
        mcp_enabled = snap["mcp"].count("✓ enabled") if "✓ enabled" in snap["mcp"] else snap["mcp"].count("enabled")
        new_header_re = re.compile(r"\*Last audit:.*?\*")
        fresh = f"*Last audit: {snap['timestamp'][:10]} · {skills_lines} skills (hermes list) · mcp hash {snap['mcp_hash']} · model {snap['model_default']}*"
        if new_header_re.search(txt):
            txt2 = new_header_re.sub(fresh, txt, count=1)
            if txt2 != txt:
                cap.write_text(txt2, encoding="utf-8")
                print(f"[deep] CAPABILITY_GRAPH.md header refreshed")

    # 2) Ensure DECIDE home stays synced to skill (skill is canonical)
    decide_skill = HERMES / "skills/decide/SKILL.md"
    decide_home = HERMES / "DECIDE.md"
    if decide_skill.exists() and decide_home.exists():
        skill_hash = file_hash(decide_skill)
        # If skill changed since last registry decide_skill_hash, ensure home pointer is fresh
        if old.get("decide_skill_hash") != skill_hash:
            # Re-sync home pointer's "Last sync:" line
            try:
                home_txt = decide_home.read_text(encoding="utf-8")
                home_txt = re.sub(r"Last sync:.*", f"Last sync: {snap['timestamp'][:10]} skill hash {skill_hash}.", home_txt)
                decide_home.write_text(home_txt, encoding="utf-8")
                print(f"[deep] DECIDE.md home pointer re-synced to skill {skill_hash}")
            except Exception as e:
                print(f"[deep] DECIDE sync warn: {e}")

    # 3) Underutilization / conflict quick heuristics (lightweight checks, not LLM)
    checks = []
    mcp_text = snap["mcp"]
    if "clawlink" in mcp_text and "clawlink" not in (HERMES / "skills/decide/SKILL.md").read_text(encoding="utf-8"):
        checks.append("clawlink MCP present but not routed in decide skill")
    if "0ab9f667b0f3" in snap["cron"] and "storageQuotaExceeded" in snap["cron"]:
        checks.append("hermes backup cron still failing (Drive quota) — needs manual cleanup")
    if checks:
        print("[deep] heuristics:")
        for c in checks: print(f"  ! {c}")

    # 4) Save registry + changelog
    snap["last_checked"] = snap["timestamp"]
    snap["last_deep"] = snap["timestamp"]
    save_registry(snap)
    entry = "- **DEEP** audit\n"
    if diffs: entry += "  changes: " + "; ".join(diffs[:6]) + "\n"
    else: entry += "  no env changes — header refresh + heuristic check only\n"
    if checks: entry += "  heuristics: " + "; ".join(checks) + "\n"
    append_changelog(entry)
    print(f"[deep] done — registry + changelog updated. model={snap['model_default']} mcp_hash={snap['mcp_hash']}")
    return 0

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--light", action="store_true", help="lightweight change detection")
    ap.add_argument("--deep", action="store_true", help="deep audit")
    ap.add_argument("--force", action="store_true", help="force deep even if no changes / not due")
    args = ap.parse_args()
    if args.deep:
        sys.exit(deep(force=args.force))
    elif args.light:
        sys.exit(lightweight())
    else:
        # default: lightweight
        sys.exit(lightweight())
