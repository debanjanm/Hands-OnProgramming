"""SQLite persistence for tasks."""
from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import date

from .dates import is_overdue

log = logging.getLogger("taskman")

PRIORITY_NAMES = {1: "low", 2: "normal", 3: "high"}
PRIORITIES = {name: num for num, name in PRIORITY_NAMES.items()}

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    title    TEXT    NOT NULL,
    priority INTEGER NOT NULL DEFAULT 2 CHECK (priority BETWEEN 1 AND 3),
    due      TEXT,
    tags     TEXT    NOT NULL DEFAULT '',
    done     INTEGER NOT NULL DEFAULT 0
)
"""


class TaskNotFound(LookupError):
    """Raised when a task id does not exist."""


@dataclass
class Task:
    """One to-do item. ``priority`` is 1 (low), 2 (normal) or 3 (high)."""

    id: int
    title: str
    priority: int = 2
    due: date | None = None
    tags: list[str] = field(default_factory=list)
    done: bool = False

    def to_dict(self) -> dict:
        """Plain dict for exporting. Priority as a name, due as ISO text or None.

        Milestone 4: export.
        """
        # TODO (Milestone 4: export): implement this, then run the tests.
        raise NotImplementedError


def _row_to_task(row: sqlite3.Row) -> Task:
    """Convert a database row into a Task (tags are stored as ``a,b,c``).

    Milestone 2: storage.
    """
    # TODO (Milestone 2: storage): implement this, then run the tests.
    raise NotImplementedError


class TaskStore:
    """Wraps one sqlite3 database file. Use it as a context manager."""

    def __init__(self, path: str) -> None:
        """Open (and create if needed) the database at ``path``.

        Milestone 2: storage. Create the table with SCHEMA and make rows
        accessible by column name (``sqlite3.Row``).
        """
        # TODO (Milestone 2: storage. Create the table with SCHEMA and make rows): implement this, then run the tests.
        raise NotImplementedError

    def __enter__(self) -> "TaskStore":
        """Return self.

        Milestone 2: storage.
        """
        # TODO (Milestone 2: storage): implement this, then run the tests.
        raise NotImplementedError

    def __exit__(self, *exc) -> None:
        """Close the connection.

        Milestone 2: storage.
        """
        # TODO (Milestone 2: storage): implement this, then run the tests.
        raise NotImplementedError

    def close(self) -> None:
        """Close the database connection.

        Milestone 2: storage.
        """
        # TODO (Milestone 2: storage): implement this, then run the tests.
        raise NotImplementedError

    def add(self, title: str, priority: int = 2, due: date | None = None,
            tags: tuple[str, ...] | list[str] = ()) -> Task:
        """Insert a task and return it (with its new id).

        Milestone 2: storage. Reject an empty title or a priority outside 1..3
        with ``ValueError``. Tags are lower-cased, stripped, de-duplicated
        and sorted.
        """
        # TODO (Milestone 2: storage. Reject an empty title or a priority outside 1..3): implement this, then run the tests.
        raise NotImplementedError

    def get(self, task_id: int) -> Task:
        """Return one task or raise ``TaskNotFound``.

        Milestone 2: storage.
        """
        # TODO (Milestone 2: storage): implement this, then run the tests.
        raise NotImplementedError

    def list(self, include_done: bool = False, tag: str | None = None,
             overdue_only: bool = False, today: date | None = None) -> list[Task]:
        """Return tasks, filtered and sorted.

        Milestone 3: priorities, tags and overdue. Sort order: tasks with a
        due date first (earliest first), then higher priority first, then id.
        """
        # TODO (Milestone 3: priorities, tags and overdue. Sort order: tasks with a): implement this, then run the tests.
        raise NotImplementedError

    def mark_done(self, task_id: int) -> Task:
        """Mark a task done and return it. Raises ``TaskNotFound``.

        Milestone 2: storage.
        """
        # TODO (Milestone 2: storage): implement this, then run the tests.
        raise NotImplementedError

    def delete(self, task_id: int) -> None:
        """Delete a task. Raises ``TaskNotFound``.

        Milestone 2: storage.
        """
        # TODO (Milestone 2: storage): implement this, then run the tests.
        raise NotImplementedError

    def search(self, text: str) -> list[Task]:
        """Tasks (done or not) whose title or tags contain ``text``, ignoring case.

        Milestone 3: search.
        """
        # TODO (Milestone 3: search): implement this, then run the tests.
        raise NotImplementedError
