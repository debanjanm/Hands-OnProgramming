"""Command-line interface: argparse subcommands on top of TaskStore."""
from __future__ import annotations

import argparse
import logging
import os
import sqlite3
import sys
from datetime import date

from .dates import is_overdue, parse_due
from .export import to_csv, to_json
from .store import PRIORITIES, PRIORITY_NAMES, Task, TaskNotFound, TaskStore

EXIT_OK = 0
EXIT_NOT_FOUND = 1
EXIT_USAGE = 2
EXIT_IO = 3

ENV_DB = "TASKMAN_DB"
DEFAULT_DB = "tasks.db"


def resolve_db_path(arg: str | None) -> str:
    """Where is the database? ``--db`` wins, then $TASKMAN_DB, then tasks.db.

    Milestone 2: storage.
    """
    # TODO (Milestone 2: storage): implement this, then run the tests.
    raise NotImplementedError


def format_task(task: Task, today: date) -> str:
    """One display line, e.g. `  3 [ ] high   2025-01-10 Pay rent #home OVERDUE`.

    Milestone 3: listing.
    """
    # TODO (Milestone 3: listing): implement this, then run the tests.
    raise NotImplementedError


def build_parser() -> argparse.ArgumentParser:
    """Build the parser with subcommands add/list/done/delete/search/export.

    Milestone 5: CLI. Each subparser stores its handler with
    ``set_defaults(func=...)``. Global options: ``--db PATH`` and ``-v``.
    """
    # TODO (Milestone 5: CLI. Each subparser stores its handler with): implement this, then run the tests.
    raise NotImplementedError


def cmd_add(store: TaskStore, args: argparse.Namespace, today: date) -> int:
    """Handle ``add``. Milestone 5: CLI."""
    # TODO : implement this, then run the tests.
    raise NotImplementedError


def cmd_list(store: TaskStore, args: argparse.Namespace, today: date) -> int:
    """Handle ``list``. Milestone 5: CLI."""
    # TODO : implement this, then run the tests.
    raise NotImplementedError


def cmd_done(store: TaskStore, args: argparse.Namespace, today: date) -> int:
    """Handle ``done``. Milestone 5: CLI."""
    # TODO : implement this, then run the tests.
    raise NotImplementedError


def cmd_delete(store: TaskStore, args: argparse.Namespace, today: date) -> int:
    """Handle ``delete``. Milestone 5: CLI."""
    # TODO : implement this, then run the tests.
    raise NotImplementedError


def cmd_search(store: TaskStore, args: argparse.Namespace, today: date) -> int:
    """Handle ``search``. Milestone 5: CLI."""
    # TODO : implement this, then run the tests.
    raise NotImplementedError


def cmd_export(store: TaskStore, args: argparse.Namespace, today: date) -> int:
    """Handle ``export``. Milestone 5: CLI."""
    # TODO : implement this, then run the tests.
    raise NotImplementedError


def _print_tasks(tasks: list[Task], today: date, empty: str) -> int:
    """Print one line per task, or ``empty`` if there are none. Milestone 3: listing."""
    # TODO : implement this, then run the tests.
    raise NotImplementedError


def main(argv: list[str] | None = None, today: date | None = None) -> int:
    """Run the CLI and return an exit code (never calls ``sys.exit``).

    Milestone 6: errors and logging.
    0 ok; 1 task not found; 2 bad input (including argparse errors);
    3 database/file problem. Errors go to stderr as ``error: <message>``.
    ``-v`` turns on DEBUG logging to stderr. ``today`` exists so tests can
    freeze the date.
    """
    # TODO (Milestone 6: errors and logging): implement this, then run the tests.
    raise NotImplementedError
