#!/usr/bin/env python
"""Headless OpenDesign client over its MCP daemon (see opendesign-mcp skill).
Usage: od-gen.py agents | plugins | projects | create <name> | run "<prompt>" [project-name] [model]
Works only while the OpenDesign app is running (it hosts the sidecar daemon).
"""
import subprocess, json, threading, os, sys, time

BASE = r"C:\Users\YOUR_USERNAME\AppData\Local\Programs\Open Design release-stable-win"
CLI = os.path.join(BASE, r"resources\app\prebundled\daemon\daemon-cli.mjs")
DATA = r"C:\Users\YOUR_USERNAME\AppData\Roaming\Open Design\namespaces\release-stable-win\data"

def daemon_url():
    log = os.path.join(os.environ["APPDATA"], "Open Design", "namespaces", "release-stable-win", "logs", "daemon", "latest.log")
    if os.path.isfile(log):
        for line in open(log, encoding="utf-8", errors="replace"):
            if '"url"' in line and "127.0.0.1" in line:
                return line.split('"url": "')[1].split('"')[0]
    return "http://127.0.0.1:7456"

def call(method, params, timeout=90):
    env = os.environ.copy()
    env.update({"OD_DATA_DIR": DATA, "OD_SIDECAR_NAMESPACE": "release-stable-win",
                "ELECTRON_RUN_AS_NODE": "1", "OD_DAEMON_URL": daemon_url()})
    proc = subprocess.Popen([os.path.join(BASE, "Open Design.exe"), CLI, "mcp"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, bufsize=1, env=env)
    out = []
    def reader():
        for line in iter(proc.stdout.readline, ""):
            out.append(line)
    threading.Thread(target=reader, daemon=True).start()
    def send(msg):
        proc.stdin.write(json.dumps(msg) + "\n"); proc.stdin.flush()
    # ids MUST differ from the initialize id (1) or the matcher grabs the init response
    send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
          "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                     "clientInfo": {"name": "od-gen", "version": "1.0"},
                     "initializationOptions": {"bloom": False}}})
    time.sleep(1.2)
    mid = 2
    send({"jsonrpc": "2.0", "id": mid, "method": "tools/call",
          "params": {"name": method, "arguments": params}})
    deadline = time.time() + timeout
    while time.time() < deadline:
        for l in out:
            try:
                msg = json.loads(l)
                if msg.get("id") == mid:
                    return msg.get("result", msg)
            except Exception:
                continue
        time.sleep(0.3)
    proc.terminate()
    return {"timeout": True, "raw": "\n".join(out[-10:])}

def text_of(result):
    if isinstance(result, dict) and "content" in result:
        return "\n".join(c.get("text", "") for c in result["content"])
    return str(result)

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "agents"
    if mode == "agents":
        print(text_of(call("list_agents", {}))[:4000])
    elif mode == "plugins":
        print(text_of(call("list_plugins", {}))[:3000])
    elif mode == "projects":
        print(text_of(call("list_projects", {}))[:3000])
    elif mode == "create":
        print(text_of(call("create_project", {"name": sys.argv[2]}))[:2000])
    elif mode == "run":
        prompt = sys.argv[2]
        project = sys.argv[3] if len(sys.argv) > 3 else None
        model = sys.argv[4] if len(sys.argv) > 4 else "deepseek-v4-flash"
        params = {"prompt": prompt, "agent": "opencode", "model": model}
        if project: params["project"] = project
        r = call("start_run", params)
        txt = text_of(r)
        print("START:", txt[:1500])
        try:
            run_id = json.loads(txt).get("runId") or json.loads(txt).get("id")
        except Exception:
            run_id = None
        if not run_id:
            sys.exit(2)
        print("POLLING", run_id, flush=True)
        while True:
            time.sleep(30)
            s = text_of(call("get_run", {"runId": run_id}))
            print("TICK:", s[:300], flush=True)
            if any(k in s for k in ("succeeded", "failed", "canceled")):
                print("FINAL:", s[:2000])
                break
    else:
        print("unknown mode", mode); sys.exit(1)

if __name__ == "__main__":
    main()
