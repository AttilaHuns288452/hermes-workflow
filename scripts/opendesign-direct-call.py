import subprocess, json, sys, time, threading, os

# Open Design path — override with $OD_INSTALL_DIR env var if set
od_install = os.environ.get("OD_INSTALL_DIR", r"C:\Program Files\Open Design")
base = od_install
cmd = [
    os.path.join(base, "Open Design.exe"),
    os.path.join(base, r"resources\app\node_modules\@open-design\daemon\dist\cli.js"),
    "mcp",
]
env = os.environ.copy()
od_data = os.environ.get("OD_DATA_DIR", os.path.join(os.environ.get("APPDATA", ""), "Open Design", "data"))
env["OD_DATA_DIR"] = od_data
env["OD_SIDECAR_NAMESPACE"] = "release-stable-win"
env["ELECTRON_RUN_AS_NODE"] = "1"

proc = subprocess.Popen(
    cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, env=env
)

def reader(stream, label):
    for line in iter(stream.readline, ""):
        sys.stdout.write(f"[{label}] {line}")
        sys.stdout.flush()

threading.Thread(target=reader, args=(proc.stdout, "OUT"), daemon=True).start()
threading.Thread(target=reader, args=(proc.stderr, "ERR"), daemon=True).start()

def send(msg):
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()

send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "py-client", "version": "1.0"}, "initializationOptions": {"bloom": False}}})
send({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "list_projects", "arguments": {}}})
time.sleep(1.0)
proc.terminate()
