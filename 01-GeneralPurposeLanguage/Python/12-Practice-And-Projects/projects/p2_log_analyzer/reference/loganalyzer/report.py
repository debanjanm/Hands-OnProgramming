"""Render results as text or JSON."""
from __future__ import annotations

import json

from .anomalies import Spike
from .stats import Stats


def _ms(value: float | None) -> str:
    """Format a latency, or ``n/a``. Milestone 5: report."""
    return "n/a" if value is None else f"{value:g} ms"


def text_report(stats: Stats, spikes: list[Spike], malformed: int = 0) -> str:
    """A human-readable report ending in a newline.

    Milestone 5: report. Sections: summary (requests, error rate as a
    percentage with 1 decimal, p50/p95, malformed lines), requests per status,
    top endpoints, requests per hour, top IPs, spikes (or ``none``).
    """
    out = [
        "== Summary ==",
        f"requests:        {stats.total}",
        f"malformed lines: {malformed}",
        f"error rate:      {stats.error_rate * 100:.1f}% (status >= 500)",
        f"latency p50/p95: {_ms(stats.p50)} / {_ms(stats.p95)}",
        "",
        "== Status codes ==",
        *(f"  {k}: {v}" for k, v in sorted(stats.by_status.items())),
        "",
        "== Top endpoints ==",
        *(f"  {n:>6}  {path}" for path, n in stats.by_endpoint.most_common(stats.top_n)),
        "",
        "== Requests per hour ==",
        *(f"  {h}: {n}" for h, n in sorted(stats.by_hour.items())),
        "",
        "== Top IPs ==",
        *(f"  {n:>6}  {ip}" for ip, n in stats.top_ips),
        "",
        "== Spikes ==",
        *([f"  {s.hour}: {s.count} requests (median {s.baseline:g})" for s in spikes] or ["  none"]),
    ]
    return "\n".join(out) + "\n"


def json_report(stats: Stats, spikes: list[Spike], malformed: int = 0) -> str:
    """The same information as JSON (2-space indent, trailing newline).

    Milestone 5: report. Start from ``stats.to_dict()`` and add
    ``malformed`` and ``spikes`` (a list of dicts with hour, count, baseline).
    """
    data = stats.to_dict()
    data["malformed"] = malformed
    data["spikes"] = [{"hour": s.hour, "count": s.count, "baseline": s.baseline} for s in spikes]
    return json.dumps(data, indent=2) + "\n"
