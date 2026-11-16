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
    today = today or date.today()
    t = text.strip().lower()
    if t == "today":
        return today
    if t == "tomorrow":
        return today + timedelta(days=1)
    m = _RELATIVE.match(t)
    if m:
        return today + timedelta(days=int(m.group(1)))
    if _ISO.match(t):
        try:
            return date.fromisoformat(t)
        except ValueError:
            pass  # e.g. 2025-02-30: right shape, not a real day
    raise ValueError(f"invalid date {text!r}: use YYYY-MM-DD, today, tomorrow or +Nd")


def is_overdue(due: date | None, done: bool, today: date | None = None) -> bool:
    """True when a task is not done and its due date is before today.

    Milestone 1: dates.
    """
    today = today or date.today()
    return due is not None and not done and due < today
