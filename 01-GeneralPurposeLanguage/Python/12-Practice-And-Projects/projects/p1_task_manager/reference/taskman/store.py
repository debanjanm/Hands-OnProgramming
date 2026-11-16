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
        return {
            "id": self.id,
            "title": self.title,
            "priority": PRIORITY_NAMES[self.priority],
            "due": self.due.isoformat() if self.due else None,
            "tags": list(self.tags),
            "done": self.done,
        }


def _row_to_task(row: sqlite3.Row) -> Task:
    """Convert a database row into a Task (tags are stored as ``a,b,c``).

    Milestone 2: storage.
    """
    return Task(
        id=row["id"],
        title=row["title"],
        priority=row["priority"],
        due=date.fromisoformat(row["due"]) if row["due"] else None,
        tags=[t for t in row["tags"].split(",") if t],
        done=bool(row["done"]),
    )


class TaskStore:
    """Wraps one sqlite3 database file. Use it as a context manager."""

    def __init__(self, path: str) -> None:
        """Open (and create if needed) the database at ``path``.

        Milestone 2: storage. Create the table with SCHEMA and make rows
        accessible by column name (``sqlite3.Row``).
        """
        self._db = sqlite3.connect(path)
        self._db.row_factory = sqlite3.Row
        self._db.execute(SCHEMA)
        self._db.commit()

    def __enter__(self) -> "TaskStore":
        """Return self.

        Milestone 2: storage.
        """
        return self

    def __exit__(self, *exc) -> None:
        """Close the connection.

        Milestone 2: storage.
        """
        self.close()

    def close(self) -> None:
        """Close the database connection.

        Milestone 2: storage.
        """
        self._db.close()

    def add(self, title: str, priority: int = 2, due: date | None = None,
            tags: tuple[str, ...] | list[str] = ()) -> Task:
        """Insert a task and return it (with its new id).

        Milestone 2: storage. Reject an empty title or a priority outside 1..3
        with ``ValueError``. Tags are lower-cased, stripped, de-duplicated
        and sorted.
        """
        title = title.strip()
        if not title:
            raise ValueError("title must not be empty")
        if priority not in PRIORITY_NAMES:
            raise ValueError(f"priority must be 1, 2 or 3, got {priority!r}")
        clean = sorted({t.strip().lower() for t in tags if t.strip()})
        cur = self._db.execute(
            "INSERT INTO tasks (title, priority, due, tags) VALUES (?, ?, ?, ?)",
            (title, priority, due.isoformat() if due else None, ",".join(clean)),
        )
        self._db.commit()
        log.info("added task %s", cur.lastrowid)
        return self.get(cur.lastrowid)

    def get(self, task_id: int) -> Task:
        """Return one task or raise ``TaskNotFound``.

        Milestone 2: storage.
        """
        row = self._db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise TaskNotFound(f"no task with id {task_id}")
        return _row_to_task(row)

    def list(self, include_done: bool = False, tag: str | None = None,
             overdue_only: bool = False, today: date | None = None) -> list[Task]:
        """Return tasks, filtered and sorted.

        Milestone 3: priorities, tags and overdue. Sort order: tasks with a
        due date first (earliest first), then higher priority first, then id.
        """
        tasks = [_row_to_task(r) for r in self._db.execute("SELECT * FROM tasks")]
        if not include_done:
            tasks = [t for t in tasks if not t.done]
        if tag:
            tasks = [t for t in tasks if tag.strip().lower() in t.tags]
        if overdue_only:
            tasks = [t for t in tasks if is_overdue(t.due, t.done, today)]
        tasks.sort(key=lambda t: (t.due is None, t.due or date.max, -t.priority, t.id))
        return tasks

    def mark_done(self, task_id: int) -> Task:
        """Mark a task done and return it. Raises ``TaskNotFound``.

        Milestone 2: storage.
        """
        self.get(task_id)
        self._db.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
        self._db.commit()
        log.info("completed task %s", task_id)
        return self.get(task_id)

    def delete(self, task_id: int) -> None:
        """Delete a task. Raises ``TaskNotFound``.

        Milestone 2: storage.
        """
        self.get(task_id)
        self._db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self._db.commit()
        log.info("deleted task %s", task_id)

    def search(self, text: str) -> list[Task]:
        """Tasks (done or not) whose title or tags contain ``text``, ignoring case.

        Milestone 3: search.
        """
        needle = text.strip().lower()
        return [
            t for t in self.list(include_done=True)
            if needle in t.title.lower() or any(needle in tag for tag in t.tags)
        ]
