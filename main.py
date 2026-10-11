"""Command-line entry point for the Library Inventory Application.

Examples::

    python main.py add-book --title "Things Fall Apart" --author "Chinua Achebe" \
        --isbn 9780385474542 --genre Novel --year 1958
    python main.py search achebe --field author
    python main.py list
    python main.py add-borrower --name "Ama Mensah" --email ama@example.com
    python main.py borrow B001 M001
    python main.py return B001
    python main.py history --borrower M001
    python main.py health
    python main.py serve-health --port 8080
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from library import __version__
from library.exceptions import LibraryError
from library.health import OK, check_health, create_health_server
from library.inventory import SEARCH_FIELDS, Library
from library.logging_config import configure_logging, default_log_file, verbosity_to_level
from library.storage import default_data_file, load_library, save_library

logger = logging.getLogger("library.cli")


def print_books(books: Sequence, empty_message: str = "No books found.") -> None:
    if not books:
        print(empty_message)
        return
    for book in books:
        print(book.describe())


# --- command handlers: each returns True when the library was modified --------------------


def cmd_add_book(library: Library, args: argparse.Namespace) -> bool:
    book = library.add_book(args.title, args.author, args.isbn, args.genre, args.year)
    print(f"Added {book.describe()}")
    return True


def cmd_search(library: Library, args: argparse.Namespace) -> bool:
    print_books(library.search_books(args.term, field=args.field))
    return False


def cmd_list(library: Library, args: argparse.Namespace) -> bool:
    print_books(library.list_books(), empty_message="The library is empty.")
    return False


def cmd_add_borrower(library: Library, args: argparse.Namespace) -> bool:
    borrower = library.add_borrower(args.name, args.email)
    print(f"Registered {borrower.describe()}")
    return True


def cmd_borrowers(library: Library, args: argparse.Namespace) -> bool:
    borrowers = library.list_borrowers()
    if not borrowers:
        print("No borrowers registered.")
    for borrower in borrowers:
        print(borrower.describe())
    return False


def cmd_borrow(library: Library, args: argparse.Namespace) -> bool:
    record = library.borrow_book(args.book_id, args.borrower_id)
    book = library.get_book(record.book_id)
    borrower = library.get_borrower(record.borrower_id)
    print(f"{book.title!r} ({book.id}) lent to {borrower.name} ({borrower.id})")
    return True


def cmd_return(library: Library, args: argparse.Namespace) -> bool:
    record = library.return_book(args.book_id)
    book = library.get_book(record.book_id)
    borrower = library.get_borrower(record.borrower_id)
    print(f"{book.title!r} ({book.id}) returned by {borrower.name} ({borrower.id})")
    return True


def cmd_history(library: Library, args: argparse.Namespace) -> bool:
    records = library.get_history(args.borrower)
    if not records:
        print("No borrowing history.")
    for record in records:
        book = library.books.get(record.book_id)
        borrower = library.borrowers.get(record.borrower_id)
        returned = record.returned_at or "on loan"
        print(
            f"{record.borrowed_at} -> {returned:<25} "
            f"{record.book_id} {book.title if book else '?'!r} | "
            f"{record.borrower_id} {borrower.name if borrower else '?'}"
        )
    return False


# --- monitoring commands: run without loading the library, return an exit code -------------


def cmd_health(data_file: Path, args: argparse.Namespace) -> int:
    report = check_health(data_file)
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == OK else 1


def cmd_serve_health(data_file: Path, args: argparse.Namespace) -> int:
    server = create_health_server(data_file, host=args.host, port=args.port)
    host, port = server.server_address[:2]
    logger.info("Health endpoint listening on http://%s:%s/health", host, port)
    print(f"Serving health checks on http://{host}:{port}/health (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Health endpoint stopped")
    finally:
        server.server_close()
    return 0


# --- argument parsing -------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="library", description="Library Inventory Application")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--data",
        type=Path,
        default=None,
        help="path to the JSON data file (default: data/library.json or $LIBRARY_DATA_FILE)",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="path to the log file (default: logs/library.log or $LIBRARY_LOG_FILE)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="also print logs to the console (-v = INFO, -vv = DEBUG)",
    )
    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    add = sub.add_parser("add-book", help="catalogue a new book")
    add.add_argument("--title", required=True)
    add.add_argument("--author", action="append", required=True, help="repeat for co-authors")
    add.add_argument("--isbn", required=True)
    add.add_argument("--genre", required=True)
    add.add_argument("--year", type=int, required=True)
    add.set_defaults(handler=cmd_add_book)

    search = sub.add_parser("search", help="search books by title and/or author")
    search.add_argument("term")
    search.add_argument("--field", choices=SEARCH_FIELDS, default="all")
    search.set_defaults(handler=cmd_search)

    listing = sub.add_parser("list", help="list every book")
    listing.set_defaults(handler=cmd_list)

    add_borrower = sub.add_parser("add-borrower", help="register a borrower")
    add_borrower.add_argument("--name", required=True)
    add_borrower.add_argument("--email", required=True)
    add_borrower.set_defaults(handler=cmd_add_borrower)

    borrowers = sub.add_parser("borrowers", help="list registered borrowers")
    borrowers.set_defaults(handler=cmd_borrowers)

    borrow = sub.add_parser("borrow", help="lend a book to a borrower")
    borrow.add_argument("book_id")
    borrow.add_argument("borrower_id")
    borrow.set_defaults(handler=cmd_borrow)

    give_back = sub.add_parser("return", help="record the return of a borrowed book")
    give_back.add_argument("book_id")
    give_back.set_defaults(handler=cmd_return)

    history = sub.add_parser("history", help="show the borrowing history")
    history.add_argument("--borrower", metavar="BORROWER_ID", default=None)
    history.set_defaults(handler=cmd_history)

    health = sub.add_parser("health", help="check the data store and print a JSON status")
    health.set_defaults(monitor=cmd_health)

    serve = sub.add_parser("serve-health", help="expose GET /health over HTTP")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8080)
    serve.set_defaults(monitor=cmd_serve_health)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    log_file = args.log_file or default_log_file()
    console_level = verbosity_to_level(args.verbose)
    if args.command == "serve-health" and console_level is None:
        console_level = logging.INFO  # a long-running server should show its access log
    configure_logging(console_level=console_level, log_file=log_file)
    data_file = args.data or default_data_file()
    logger.debug("Running %r with data file %s", args.command, data_file)
    try:
        if hasattr(args, "monitor"):
            return args.monitor(data_file, args)
        library = load_library(data_file)
        if args.handler(library, args):
            save_library(library, data_file)
    except (LibraryError, ValueError) as exc:
        logger.warning("Command %r rejected: %s", args.command, exc)
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # error tracking: keep the traceback, show a friendly message
        logger.exception("Unexpected error while running %r", args.command)
        where = f" Details were logged to {log_file}." if log_file else ""
        print(f"Unexpected error ({type(exc).__name__}).{where}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
