"""Health checks for monitoring: is the data store present, valid and writable?"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from library import __version__
from library.exceptions import StorageError
from library.storage import load_library

logger = logging.getLogger(__name__)

OK = "ok"
ERROR = "error"


def _nearest_existing_dir(path: Path) -> Path:
    """The closest existing ancestor (the data directory may not be created yet)."""
    for candidate in [path, *path.parents]:
        if candidate.exists():
            return candidate
    return Path.cwd()


def check_health(data_file: Path | str) -> dict[str, Any]:
    """Run every check and return a JSON-serialisable status report."""
    data_file = Path(data_file)
    checks: dict[str, dict[str, str]] = {}
    counts: dict[str, int] = {}

    directory = _nearest_existing_dir(data_file.parent)
    writable = os.access(directory, os.W_OK)
    checks["data_directory_writable"] = {
        "status": OK if writable else ERROR,
        "detail": str(directory),
    }

    if not data_file.exists():
        checks["data_file_valid"] = {"status": OK, "detail": "not created yet (empty library)"}
    else:
        try:
            library = load_library(data_file)
        except StorageError as exc:
            checks["data_file_valid"] = {"status": ERROR, "detail": str(exc)}
        else:
            checks["data_file_valid"] = {
                "status": OK,
                "detail": f"{data_file.stat().st_size} bytes",
            }
            counts = {
                "books": len(library.books),
                "authors": len(library.authors),
                "borrowers": len(library.borrowers),
            }
        if not os.access(data_file, os.W_OK):
            checks["data_file_writable"] = {"status": ERROR, "detail": "file is read-only"}

    status = OK if all(check["status"] == OK for check in checks.values()) else ERROR
    report = {
        "status": status,
        "version": __version__,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data_file": str(data_file),
        "checks": checks,
        "counts": counts,
    }
    log = logger.info if status == OK else logger.error
    log("Health check %s: %s", status, {name: c["status"] for name, c in checks.items()})
    return report


def create_health_server(
    data_file: Path | str, host: str = "127.0.0.1", port: int = 8080
) -> ThreadingHTTPServer:
    """Build (but do not start) an HTTP server exposing ``GET /health``."""

    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 (name required by BaseHTTPRequestHandler)
            if urlsplit(self.path).path.rstrip("/") != "/health":
                self._send_json(404, {"error": "not found", "path": self.path})
                return
            report = check_health(data_file)
            self._send_json(200 if report["status"] == OK else 503, report)

        def _send_json(self, code: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            logger.info("%s %s", self.address_string(), format % args)

    return ThreadingHTTPServer((host, port), HealthHandler)
