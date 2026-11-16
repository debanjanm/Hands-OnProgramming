"""Turn tasks into JSON or CSV text."""
from __future__ import annotations

import csv
import io
import json
from typing import Iterable

from .store import Task

CSV_COLUMNS = ["id", "title", "priority", "due", "tags", "done"]


def to_json(tasks: Iterable[Task]) -> str:
    """A JSON array of ``task.to_dict()`` objects, indented by 2 spaces.

    Milestone 4: export.
    """
    # TODO (Milestone 4: export): implement this, then run the tests.
    raise NotImplementedError


def to_csv(tasks: Iterable[Task]) -> str:
    """CSV text with a header row (see CSV_COLUMNS).

    Milestone 4: export. Tags are joined with ``;``; ``done`` is written as
    ``true``/``false``; a missing due date is an empty cell. Use ``\\n`` line ends.
    """
    # TODO (Milestone 4: export. Tags are joined with ``;``; ``done`` is written as): implement this, then run the tests.
    raise NotImplementedError
