"""Tests for the health check command and HTTP endpoint (US-08: AC8.1, AC8.2)."""

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from library.health import check_health, create_health_server
from library.storage import save_library
from main import main


@pytest.fixture
def data_file(tmp_path, library):
    path = tmp_path / "library.json"
    save_library(library, path)
    return path


@pytest.fixture
def corrupt_file(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{ this is not json", encoding="utf-8")
    return path


def test_healthy_data_file_reports_ok_with_counts(data_file):
    report = check_health(data_file)
    assert report["status"] == "ok"
    assert report["checks"]["data_file_valid"]["status"] == "ok"
    assert report["checks"]["data_directory_writable"]["status"] == "ok"
    assert report["counts"] == {"books": 4, "authors": 4, "borrowers": 0}
    assert {"version", "timestamp", "data_file"} <= report.keys()


def test_missing_data_file_is_healthy(tmp_path):
    report = check_health(tmp_path / "not-yet" / "library.json")
    assert report["status"] == "ok"
    assert "not created yet" in report["checks"]["data_file_valid"]["detail"]


def test_corrupt_data_file_reports_error(corrupt_file):
    report = check_health(corrupt_file)
    assert report["status"] == "error"
    assert "not valid JSON" in report["checks"]["data_file_valid"]["detail"]


def test_health_command_prints_json_and_exit_code(data_file, corrupt_file, capsys):
    assert main(["--data", str(data_file), "health"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "ok"
    assert main(["--data", str(corrupt_file), "health"]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "error"


def test_health_check_is_logged(data_file, isolated_log_file):
    main(["--data", str(data_file), "health"])
    assert "INFO     | library.health | Health check ok" in isolated_log_file.read_text(
        encoding="utf-8"
    )


# --- HTTP endpoint ------------------------------------------------------------------------


@pytest.fixture
def serve():
    servers = []

    def _serve(path):
        server = create_health_server(path, port=0)  # port 0 = pick a free port
        threading.Thread(target=server.serve_forever, daemon=True).start()
        servers.append(server)
        host, port = server.server_address[:2]
        return f"http://{host}:{port}"

    yield _serve
    for server in servers:
        server.shutdown()
        server.server_close()


def http_get(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status, response.headers, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, error.headers, json.loads(error.read())


def test_http_health_returns_200_when_healthy(serve, data_file):
    status, headers, body = http_get(serve(data_file) + "/health")
    assert status == 200
    assert headers["Content-Type"] == "application/json"
    assert body["status"] == "ok"
    assert body["counts"]["books"] == 4


def test_http_health_returns_503_when_unhealthy(serve, corrupt_file):
    status, _, body = http_get(serve(corrupt_file) + "/health")
    assert status == 503
    assert body["status"] == "error"


def test_http_unknown_path_returns_404(serve, data_file):
    status, _, body = http_get(serve(data_file) + "/nope")
    assert status == 404
    assert body["error"] == "not found"


def test_serve_health_command_starts_and_stops_cleanly(data_file, capsys, monkeypatch):
    def interrupt(self, *args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(ThreadingHTTPServer, "serve_forever", interrupt)
    assert main(["--data", str(data_file), "serve-health", "--port", "0"]) == 0
    captured = capsys.readouterr()
    assert "Serving health checks on http://127.0.0.1:" in captured.out
    assert "Health endpoint listening" in captured.err  # console access log on by default
