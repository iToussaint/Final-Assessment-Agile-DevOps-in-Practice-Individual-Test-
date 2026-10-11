"""Tests for logging and error tracking (US-08: AC8.3, AC8.4)."""

import logging
import sys

import pytest

import main as cli
from library.logging_config import (
    DEFAULT_LOG_FILE,
    ConciseFormatter,
    configure_logging,
    default_log_file,
    verbosity_to_level,
)

ADD_BOOK = [
    "add-book", "--title", "Things Fall Apart", "--author", "Chinua Achebe",
    "--isbn", "9780385474542", "--genre", "Novel", "--year", "1958",
]  # fmt: skip


def run_cli(tmp_path, *argv):
    return cli.main(["--data", str(tmp_path / "library.json"), *argv])


def test_configure_logging_writes_formatted_records_to_file(tmp_path):
    log_file = tmp_path / "app.log"
    logger = configure_logging(log_file=log_file)
    logging.getLogger("library.test").info("hello %s", "world")
    for handler in logger.handlers:
        handler.flush()
    line = log_file.read_text(encoding="utf-8").strip()
    assert line.endswith("| INFO     | library.test | hello world")


def test_configure_logging_is_idempotent(tmp_path):
    configure_logging(console_level=logging.INFO, log_file=tmp_path / "a.log")
    logger = configure_logging(console_level=logging.INFO, log_file=tmp_path / "a.log")
    kinds = sorted(type(handler).__name__ for handler in logger.handlers)
    assert kinds == ["NullHandler", "RotatingFileHandler", "StreamHandler"]


@pytest.mark.parametrize(
    ("verbosity", "level"), [(0, None), (1, logging.INFO), (2, logging.DEBUG), (5, logging.DEBUG)]
)
def test_verbosity_to_level(verbosity, level):
    assert verbosity_to_level(verbosity) == level


def test_default_log_file_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("LIBRARY_LOG_FILE", str(tmp_path / "x.log"))
    assert default_log_file() == tmp_path / "x.log"
    monkeypatch.setenv("LIBRARY_LOG_FILE", "")
    assert default_log_file() is None
    monkeypatch.delenv("LIBRARY_LOG_FILE")
    assert default_log_file() == DEFAULT_LOG_FILE


def test_concise_formatter_hides_traceback():
    try:
        raise RuntimeError("boom")
    except RuntimeError:
        record = logging.LogRecord("library", logging.ERROR, __file__, 1, "failed", None, None)
        record.exc_info = sys.exc_info()
    text = ConciseFormatter("%(levelname)s %(message)s").format(record)
    assert text == "ERROR failed"
    assert record.exc_info is not None  # restored for other handlers


def test_state_changes_are_logged_to_file(tmp_path, isolated_log_file):
    assert run_cli(tmp_path, *ADD_BOOK) == 0
    log = isolated_log_file.read_text(encoding="utf-8")
    assert "INFO     | library.inventory | Registered author A001 (Chinua Achebe)" in log
    assert "INFO     | library.inventory | Added book B001 'Things Fall Apart'" in log
    assert "INFO     | library.storage | Saved library (1 books)" in log


def test_console_is_quiet_by_default_and_verbose_with_v(tmp_path, capsys):
    run_cli(tmp_path, *ADD_BOOK)
    assert capsys.readouterr().err == ""
    run_cli(tmp_path, "-v", "list")
    assert "| INFO     | library.storage |" not in capsys.readouterr().err  # list does not save
    run_cli(tmp_path, "-vv", "list")
    assert "| DEBUG    | library.cli | Running 'list'" in capsys.readouterr().err


def test_rejected_command_is_logged_as_warning(tmp_path, isolated_log_file):
    run_cli(tmp_path, *ADD_BOOK)
    assert run_cli(tmp_path, *ADD_BOOK) == 1
    assert "WARNING  | library.cli | Command 'add-book' rejected" in isolated_log_file.read_text(
        encoding="utf-8"
    )


def test_unexpected_error_is_tracked_with_traceback(
    tmp_path, capsys, monkeypatch, isolated_log_file
):
    def explode(library, args):
        raise RuntimeError("disk on fire")

    monkeypatch.setattr(cli, "cmd_list", explode)
    assert run_cli(tmp_path, "list") == 2
    err = capsys.readouterr().err
    assert err.startswith("Unexpected error (RuntimeError).")
    assert "Traceback" not in err
    log = isolated_log_file.read_text(encoding="utf-8")
    assert "ERROR    | library.cli | Unexpected error while running 'list'" in log
    assert "Traceback (most recent call last)" in log
    assert "RuntimeError: disk on fire" in log
