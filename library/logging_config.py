"""Application logging: a concise console stream plus a rotating log file."""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOGGER_NAME = "library"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DEFAULT_LOG_FILE = Path(__file__).resolve().parent.parent / "logs" / "library.log"
MAX_LOG_BYTES = 1_000_000
BACKUP_COUNT = 3


class ConciseFormatter(logging.Formatter):
    """Console formatter that leaves tracebacks out (they are kept in the log file)."""

    def format(self, record: logging.LogRecord) -> str:
        saved = record.exc_info, record.exc_text
        record.exc_info, record.exc_text = None, None
        try:
            return super().format(record)
        finally:
            record.exc_info, record.exc_text = saved


def default_log_file() -> Path | None:
    """Log file path; ``LIBRARY_LOG_FILE`` overrides it and an empty value disables it."""
    value = os.environ.get("LIBRARY_LOG_FILE")
    if value is None:
        return DEFAULT_LOG_FILE
    return Path(value) if value.strip() else None


def verbosity_to_level(verbosity: int) -> int | None:
    """Map ``-v`` flags to a console level: none=no console logs, -v=INFO, -vv=DEBUG.

    Without ``-v`` the user only sees friendly messages; everything is still logged to file.
    """
    if verbosity <= 0:
        return None
    return logging.INFO if verbosity == 1 else logging.DEBUG


def configure_logging(
    console_level: int | None = None,
    log_file: Path | None = None,
    file_level: int = logging.INFO,
) -> logging.Logger:
    """(Re)configure the ``library`` logger and return it.

    ``console_level=None`` disables console output. Safe to call more than once:
    existing handlers are replaced, not duplicated.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
    # NullHandler stops Python's "last resort" handler printing to stderr when
    # both console and file logging are disabled.
    logger.addHandler(logging.NullHandler())

    if console_level is not None:
        console = logging.StreamHandler()
        console.setLevel(console_level)
        console.setFormatter(ConciseFormatter(LOG_FORMAT))
        logger.addHandler(console)

    if log_file is not None:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                log_file, maxBytes=MAX_LOG_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
            )
        except OSError as exc:
            logger.warning("File logging disabled, cannot open %s: %s", log_file, exc)
        else:
            file_handler.setLevel(file_level)
            file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
            logger.addHandler(file_handler)

    return logger
