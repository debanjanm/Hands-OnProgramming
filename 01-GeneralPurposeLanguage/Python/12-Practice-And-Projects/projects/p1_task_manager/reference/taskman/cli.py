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
    return arg or os.environ.get(ENV_DB) or DEFAULT_DB


def format_task(task: Task, today: date) -> str:
    """One display line, e.g. `  3 [ ] high   2025-01-10 Pay rent #home OVERDUE`.

    Milestone 3: listing.
    """
    due = task.due.isoformat() if task.due else "-"
    tags = "".join(f" #{t}" for t in task.tags)
    flag = " OVERDUE" if is_overdue(task.due, task.done, today) else ""
    mark = "x" if task.done else " "
    return f"{task.id:>3} [{mark}] {PRIORITY_NAMES[task.priority]:<6} {due:<10} {task.title}{tags}{flag}"


def build_parser() -> argparse.ArgumentParser:
    """Build the parser with subcommands add/list/done/delete/search/export.

    Milestone 5: CLI. Each subparser stores its handler with
    ``set_defaults(func=...)``. Global options: ``--db PATH`` and ``-v``.
    """
    p = argparse.ArgumentParser(prog="taskman", description="A tiny to-do manager.")
    p.add_argument("--db", help=f"database file (default: ${ENV_DB} or {DEFAULT_DB})")
    p.add_argument("-v", "--verbose", action="store_true", help="log what happens to stderr")
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("add", help="add a task")
    a.add_argument("title")
    a.add_argument("-p", "--priority", choices=list(PRIORITIES), default="normal")
    a.add_argument("-d", "--due", help="YYYY-MM-DD, today, tomorrow or +Nd")
    a.add_argument("-t", "--tag", action="append", default=[], help="repeatable")
    a.set_defaults(func=cmd_add)

    ls = sub.add_parser("list", help="list open tasks")
    ls.add_argument("--all", action="store_true", help="include finished tasks")
    ls.add_argument("--tag")
    ls.add_argument("--overdue", action="store_true")
    ls.set_defaults(func=cmd_list)

    for name, func, helptext in (("done", cmd_done, "mark a task done"),
                                 ("delete", cmd_delete, "delete a task")):
        s = sub.add_parser(name, help=helptext)
        s.add_argument("id", type=int)
        s.set_defaults(func=func)

    s = sub.add_parser("search", help="search titles and tags")
    s.add_argument("text")
    s.set_defaults(func=cmd_search)

    e = sub.add_parser("export", help="export all tasks")
    e.add_argument("--format", choices=["json", "csv"], default="json")
    e.add_argument("-o", "--output", help="write to a file instead of stdout")
    e.set_defaults(func=cmd_export)
    return p


def cmd_add(store: TaskStore, args: argparse.Namespace, today: date) -> int:
    """Handle ``add``. Milestone 5: CLI."""
    due = parse_due(args.due, today) if args.due else None
    task = store.add(args.title, PRIORITIES[args.priority], due, args.tag)
    print(f"added task {task.id}: {task.title}")
    return EXIT_OK


def cmd_list(store: TaskStore, args: argparse.Namespace, today: date) -> int:
    """Handle ``list``. Milestone 5: CLI."""
    tasks = store.list(args.all, args.tag, args.overdue, today)
    return _print_tasks(tasks, today, "no tasks")


def cmd_done(store: TaskStore, args: argparse.Namespace, today: date) -> int:
    """Handle ``done``. Milestone 5: CLI."""
    store.mark_done(args.id)
    print(f"completed task {args.id}")
    return EXIT_OK


def cmd_delete(store: TaskStore, args: argparse.Namespace, today: date) -> int:
    """Handle ``delete``. Milestone 5: CLI."""
    store.delete(args.id)
    print(f"deleted task {args.id}")
    return EXIT_OK


def cmd_search(store: TaskStore, args: argparse.Namespace, today: date) -> int:
    """Handle ``search``. Milestone 5: CLI."""
    return _print_tasks(store.search(args.text), today, "no matches")


def cmd_export(store: TaskStore, args: argparse.Namespace, today: date) -> int:
    """Handle ``export``. Milestone 5: CLI."""
    tasks = store.list(include_done=True)
    text = to_json(tasks) if args.format == "json" else to_csv(tasks)
    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        print(f"exported {len(tasks)} tasks to {args.output}")
    else:
        print(text, end="" if text.endswith("\n") else "\n")
    return EXIT_OK


def _print_tasks(tasks: list[Task], today: date, empty: str) -> int:
    """Print one line per task, or ``empty`` if there are none. Milestone 3: listing."""
    if not tasks:
        print(empty)
    for t in tasks:
        print(format_task(t, today))
    return EXIT_OK


def main(argv: list[str] | None = None, today: date | None = None) -> int:
    """Run the CLI and return an exit code (never calls ``sys.exit``).

    Milestone 6: errors and logging.
    0 ok; 1 task not found; 2 bad input (including argparse errors);
    3 database/file problem. Errors go to stderr as ``error: <message>``.
    ``-v`` turns on DEBUG logging to stderr. ``today`` exists so tests can
    freeze the date.
    """
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:  # argparse exits on bad usage / --help
        return int(exc.code or 0)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING,
                        stream=sys.stderr, format="%(levelname)s %(name)s: %(message)s")
    today = today or date.today()
    try:
        with TaskStore(resolve_db_path(args.db)) as store:
            return args.func(store, args, today)
    except TaskNotFound as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_NOT_FOUND
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    except (sqlite3.Error, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_IO
