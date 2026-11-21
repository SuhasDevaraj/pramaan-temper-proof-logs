from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import json, hashlib, datetime, threading, webbrowser

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
LOGS_FILE = DATA / "logs.json"
ANCHOR_FILE = DATA / "integrity_anchor.json"
LOCK = threading.Lock()

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

def read_logs():
    if not LOGS_FILE.exists():
        return []
    try:
        return json.loads(LOGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

def write_logs(logs):
    LOGS_FILE.write_text(json.dumps(logs, indent=2), encoding="utf-8")

def record_hash(record):
    payload = {k: v for k, v in record.items() if k != "hash"}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()

def verify(logs=None):
    logs = read_logs() if logs is None else logs
    previous = "GENESIS"
    issues = []
    for i, item in enumerate(logs):
        expected = record_hash(item)
        if item.get("previous_hash") != previous:
            issues.append({"index": i, "reason": "Previous-hash link does not match"})
        if item.get("hash") != expected:
            issues.append({"index": i, "reason": "Record content hash does not match"})
        previous = item.get("hash", "")
    anchor = None
    if ANCHOR_FILE.exists():
        try:
            anchor = json.loads(ANCHOR_FILE.read_text(encoding="utf-8"))
            if anchor.get("count") > len(logs):
                issues.append({"index": None, "reason": "Logs are missing records covered by the checkpoint"})
            elif anchor.get("count", 0) > 0:
                idx = anchor["count"] - 1
                if logs[idx].get("hash") != anchor.get("last_hash"):
                    issues.append({"index": idx, "reason": "Checkpoint does not match the stored log chain"})
        except Exception:
            issues.append({"index": None, "reason": "Checkpoint file is unreadable"})
    return {"valid": not issues, "total": len(logs), "issues": issues, "anchor": anchor,
            "latest_hash": logs[-1].get("hash") if logs else None}

def add_log(event, actor, severity, details):
    logs = read_logs()
    item = {"id": len(logs) + 1, "timestamp": now(), "event": event, "actor": actor,
            "severity": severity, "details": details,
            "previous_hash": logs[-1]["hash"] if logs else "GENESIS"}
    item["hash"] = record_hash(item)
    logs.append(item)
    write_logs(logs)

def seed():
    if read_logs():
        return
    samples = [
        ("User login", "admin@company.in", "INFO", "Successful login from workstation WS-04"),
        ("File access", "analyst@company.in", "INFO", "Accessed finance/report-Q4.xlsx"),
        ("Failed login", "unknown", "WARNING", "Three failed login attempts detected"),
        ("Permission change", "admin@company.in", "WARNING", "Read permission granted to audit folder"),
        ("Configuration update", "system", "INFO", "Endpoint monitoring policy refreshed"),
    ]
    for e, a, s, d in samples:
        add_log(e, a, s, d)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass
    def send_json(self, obj, code=200):
        data = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data))); self.send_header("Cache-Control", "no-store")
        self.end_headers(); self.wfile.write(data)
    def body(self):
        n = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(n) or b"{}")
    def do_GET(self):
        path = urlparse(self.path).path
        static_files = {"/style.css": ("style.css", "text/css; charset=utf-8"),
                        "/app.js": ("app.js", "application/javascript; charset=utf-8")}
        if path == "/":
            data = (ROOT / "static" / "index.html").read_bytes()
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data); return
        if path in static_files:
            filename, content_type = static_files[path]
            data = (ROOT / "static" / filename).read_bytes()
            self.send_response(200); self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data); return
        if path == "/api/state":
            with LOCK:
                self.send_json({"logs": read_logs(), "verification": verify()})
            return
        self.send_json({"error": "Not found"}, 404)
    def do_POST(self):
        path = urlparse(self.path).path
        with LOCK:
            if path == "/api/seed":
                (DATA / "logs.json").unlink(missing_ok=True); ANCHOR_FILE.unlink(missing_ok=True)
                seed(); self.send_json({"ok": True, "message": "Demo activity logs loaded"}); return
            if path == "/api/checkpoint":
                logs = read_logs()
                if not logs:
                    self.send_json({"error": "Load sample logs first"}, 400); return
                anchor = {"created_at": now(), "count": len(logs), "last_hash": logs[-1]["hash"],
                          "note": "Local prototype checkpoint; not an external blockchain anchor"}
                ANCHOR_FILE.write_text(json.dumps(anchor, indent=2), encoding="utf-8")
                self.send_json({"ok": True, "message": "Integrity checkpoint created"}); return
            if path == "/api/tamper":
                logs = read_logs()
                if not logs:
                    self.send_json({"error": "Load sample logs first"}, 400); return
                logs[-1]["details"] = "ALTERED by simulated attacker"
                write_logs(logs)
                self.send_json({"ok": True, "message": "Latest log altered for demonstration"}); return
            if path == "/api/add":
                b = self.body()
                logs = read_logs()
                item = {"id": len(logs)+1, "timestamp": now(), "event": b.get("event","Manual event"),
                        "actor": b.get("actor","demo-user"), "severity": b.get("severity","INFO"),
                        "details": b.get("details","Demo activity"),
                        "previous_hash": logs[-1]["hash"] if logs else "GENESIS"}
                item["hash"] = record_hash(item); logs.append(item); write_logs(logs)
                self.send_json({"ok": True}); return
            if path == "/api/reset":
                (DATA / "logs.json").unlink(missing_ok=True); ANCHOR_FILE.unlink(missing_ok=True)
                self.send_json({"ok": True, "message": "Demo reset"}); return
        self.send_json({"error": "Not found"}, 404)
    def do_HEAD(self):
        self.send_response(200); self.end_headers()

if __name__ == "__main__":
    seed()
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("\\nLogShield is running at http://127.0.0.1:8000")
    print("Keep this window open. Press Ctrl+C to stop.\\n")
    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:8000")).start()
    try: server.serve_forever()
    except KeyboardInterrupt: print("\\nLogShield stopped.")
    finally: server.server_close()
