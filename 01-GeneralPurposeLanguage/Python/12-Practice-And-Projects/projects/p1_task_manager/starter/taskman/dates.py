"""Date parsing and the overdue rule."""
from __future__ import annotations

import re
from datetime import date, timedelta

_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_RELATIVE = re.compile(r"^\+(\d+)d$")


def parse_due(text: str, today: date | None = None) -> date:
    """Turn what the user typed into a date.

    Milestone 1: dates.
    Accepts ``YYYY-MM-DD``, ``today``, ``tomorrow`` and ``+Nd`` (N days from
    today). Anything else raises ``ValueError`` with a helpful message.
    """
    # TODO (Milestone 1: dates): implement this, then run the tests.
    raise NotImplementedError


def is_overdue(due: date | None, done: bool, today: date | None = None) -> bool:
    """True when a task is not done and its due date is before today.

    Milestone 1: dates.
    """
    # TODO (Milestone 1: dates): implement this, then run the tests.
    raise NotImplementedError
