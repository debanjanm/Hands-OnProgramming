"""Command line: ``python3 -m loganalyzer access.log --status 5xx --json``."""
from __future__ import annotations

import argparse
import sys

from .anomalies import detect_spikes
from .parser import parse_lines
from .pipeline import filter_since, filter_status, parse_since, read_lines
from .report import json_report, text_report
from .stats import compute_stats


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser.

    Milestone 7: CLI. Positional ``logfile``; options ``--status``,
    ``--since``, ``--top N`` (default 5), ``--spike-factor F`` (default 2.0),
    ``--json``.
    """
    p = argparse.ArgumentParser(prog="loganalyzer", description="Summarise a web-server access log.")
    p.add_argument("logfile")
    p.add_argument("--status", help="keep only this status, e.g. 404 or 5xx")
    p.add_argument("--since", help="keep only requests at/after YYYY-MM-DD[THH:MM[:SS]] (UTC if no zone)")
    p.add_argument("--top", type=int, default=5, help="how many endpoints / IPs to list")
    p.add_argument("--spike-factor", type=float, default=2.0)
    p.add_argument("--json", action="store_true", help="print JSON instead of text")
    return p


def main(argv: list[str] | None = None) -> int:
    """Run the analyzer; returns 0 on success, 2 for bad input or a missing file.

    Milestone 7: CLI. Chain: read_lines -> parse_lines -> filters -> compute_stats.
    Errors are printed to stderr as ``error: ...``.
    """
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exc:
        return int(exc.code or 0)
    bad: list[str] = []
    try:
        records = parse_lines(read_lines(args.logfile), bad)
        if args.status:
            records = filter_status(records, args.status)
        if args.since:
            records = filter_since(records, parse_since(args.since))
        stats = compute_stats(records, top_n=args.top)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    spikes = detect_spikes(dict(stats.by_hour), args.spike_factor)
    render = json_report if args.json else text_report
    print(render(stats, spikes, len(bad)), end="")
    return 0
