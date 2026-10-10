"""Command-line entry point for the Library Inventory Application.

Examples::

    python main.py add-book --title "Things Fall Apart" --author "Chinua Achebe" \
        --isbn 9780385474542 --genre Novel --year 1958
    python main.py search achebe --field author
    python main.py list
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from library import __version__
from library.exceptions import LibraryError
from library.inventory import SEARCH_FIELDS, Library
from library.storage import default_data_file, load_library, save_library


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

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    data_file = args.data or default_data_file()
    try:
        library = load_library(data_file)
        if args.handler(library, args):
            save_library(library, data_file)
    except (LibraryError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
