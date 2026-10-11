"""A tiny task-list web app using only Python's standard library."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import csv
import json
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
DATA_FILE = ROOT / "tasks.csv"
FIELDS = ["id", "title", "done"]


def read_tasks():
    with DATA_FILE.open("r", newline="", encoding="utf-8") as file:
        return [{**row, "done": row["done"].lower() == "true"}
                for row in csv.DictReader(file)]


def save_tasks(tasks):
    with DATA_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        for task in tasks:
            writer.writerow({**task, "done": str(task["done"]).lower()})


class AppHandler(BaseHTTPRequestHandler):
    def send_json(self, value, status=200):
        body = json.dumps(value).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/tasks":
            return self.send_json(read_tasks())
        filename = "index.html" if path == "/" else path.lstrip("/")
        target = (STATIC / filename).resolve()
        if not target.is_relative_to(STATIC.resolve()) or not target.is_file():
            self.send_error(404, "File not found")
            return
        content_type = {".html": "text/html", ".css": "text/css", ".js": "text/javascript"}.get(target.suffix, "application/octet-stream")
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if urlparse(self.path).path != "/api/tasks":
            return self.send_json({"error": "Not found"}, 404)
        try:
            payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        except (json.JSONDecodeError, ValueError):
            return self.send_json({"error": "Invalid JSON"}, 400)
        title = str(payload.get("title", "")).strip() if isinstance(payload, dict) else ""
        if not title:
            return self.send_json({"error": "Please enter a task."}, 400)
        tasks = read_tasks()
        task = {"id": str(max((int(t["id"]) for t in tasks), default=0) + 1), "title": title, "done": False}
        tasks.append(task)
        save_tasks(tasks)
        return self.send_json(task, 201)

    def do_PATCH(self):
        parts = urlparse(self.path).path.strip("/").split("/")
        if len(parts) != 3 or parts[:2] != ["api", "tasks"]:
            return self.send_json({"error": "Not found"}, 404)
        tasks = read_tasks()
        task = next((t for t in tasks if t["id"] == parts[2]), None)
        if task is None:
            return self.send_json({"error": "Task not found"}, 404)
        task["done"] = not task["done"]
        save_tasks(tasks)
        return self.send_json(task)

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}")


if __name__ == "__main__":
    address = ("127.0.0.1", 8000)
    print(f"Task app running at http://{address[0]}:{address[1]}")
    ThreadingHTTPServer(address, AppHandler).serve_forever()
