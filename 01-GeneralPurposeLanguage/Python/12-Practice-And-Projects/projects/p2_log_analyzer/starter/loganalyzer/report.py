"""Render results as text or JSON."""
from __future__ import annotations

import json

from .anomalies import Spike
from .stats import Stats


def _ms(value: float | None) -> str:
    """Format a latency, or ``n/a``. Milestone 5: report."""
    # TODO : implement this, then run the tests.
    raise NotImplementedError


def text_report(stats: Stats, spikes: list[Spike], malformed: int = 0) -> str:
    """A human-readable report ending in a newline.

    Milestone 5: report. Sections: summary (requests, error rate as a
    percentage with 1 decimal, p50/p95, malformed lines), requests per status,
    top endpoints, requests per hour, top IPs, spikes (or ``none``).
    """
    # TODO (Milestone 5: report. Sections: summary (requests, error rate as a): implement this, then run the tests.
    raise NotImplementedError


def json_report(stats: Stats, spikes: list[Spike], malformed: int = 0) -> str:
    """The same information as JSON (2-space indent, trailing newline).

    Milestone 5: report. Start from ``stats.to_dict()`` and add
    ``malformed`` and ``spikes`` (a list of dicts with hour, count, baseline).
    """
    # TODO (Milestone 5: report. Start from ``stats.to_dict`` and add): implement this, then run the tests.
    raise NotImplementedError
