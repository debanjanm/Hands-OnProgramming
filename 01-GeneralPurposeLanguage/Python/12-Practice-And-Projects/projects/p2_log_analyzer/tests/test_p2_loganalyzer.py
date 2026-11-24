"""Tests for the log analyzer, grouped by milestone."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

GOOD = '203.0.113.9 - alice [10/Oct/2023:13:55:36 -0700] "GET /a/b?x=1&y=2 HTTP/1.1" 404 - 87.5ms'


# ---- Milestone 1: parsing one line -----------------------------------------
class TestParseLine:
    def test_fields(self, parser_mod):
        r = parser_mod.parse_line(GOOD)
        assert (r.ip, r.user, r.method, r.protocol) == ("203.0.113.9", "alice", "GET", "HTTP/1.1")
        assert r.path == "/a/b?x=1&y=2"
        assert r.status == 404
        assert r.size == 0
        assert r.latency_ms == 87.5

    def test_endpoint_strips_query(self, parser_mod):
        assert parser_mod.parse_line(GOOD).endpoint == "/a/b"

    def test_time_is_timezone_aware(self, parser_mod):
        r = parser_mod.parse_line(GOOD)
        assert r.time.utcoffset() == timedelta(hours=-7)
        assert r.time.astimezone(timezone.utc).hour == 20

    def test_hour_bucket(self, parser_mod):
        assert parser_mod.parse_line(GOOD).hour == "2023-10-10 20:00"

    def test_without_latency(self, parser_mod):
        line = '1.2.3.4 - - [10/Oct/2023:13:55:36 +0000] "GET / HTTP/1.0" 200 10'
        r = parser_mod.parse_line(line)
        assert r.latency_ms is None and r.size == 10

    def test_trailing_newline_ok(self, parser_mod):
        assert parser_mod.parse_line(GOOD + "\n").status == 404

    @pytest.mark.parametrize("bad", [
        "",
        "hello world",
        '1.2.3.4 - - [10/Oct/2023:13:55:36 +0000] "GET / HTTP/1.1" abc 10',
        '1.2.3.4 - - [10/Foo/2023:13:55:36 +0000] "GET / HTTP/1.1" 200 10',
        '1.2.3.4 - - [10/Oct/2023:13:55:36 +0000] "GET /" 200 10',
        GOOD + " extra junk",
    ])
    def test_malformed_raises_value_error(self, parser_mod, bad):
        with pytest.raises(ValueError):
            parser_mod.parse_line(bad)


# ---- Milestone 2: the streaming pipeline -----------------------------------
class TestPipeline:
    def test_parse_lines_skips_bad_and_blank(self, parser_mod):
        bad = []
        out = list(parser_mod.parse_lines([GOOD, "", "junk", GOOD], bad))
        assert len(out) == 2 and bad == ["junk"]

    def test_parse_lines_is_lazy(self, parser_mod):
        import types
        pulled = []

        def source():
            for i in range(1000):
                pulled.append(i)
                yield GOOD

        gen = parser_mod.parse_lines(source())
        assert isinstance(gen, types.GeneratorType)
        next(gen)
        assert len(pulled) == 1  # only what was needed, not the whole input

    def test_read_lines_is_a_lazy_generator(self, pipeline, small_log):
        import types
        gen = pipeline.read_lines(small_log)
        assert isinstance(gen, types.GeneratorType)
        assert next(gen).startswith("10.0.0.1")

    def test_read_lines_missing_file(self, pipeline, tmp_path):
        with pytest.raises(OSError):
            list(pipeline.read_lines(str(tmp_path / "nope.log")))

    def test_bad_utf8_does_not_crash(self, pipeline, tmp_path):
        p = tmp_path / "x.log"
        p.write_bytes(b"\xff\xfe junk\n")
        assert len(list(pipeline.read_lines(str(p)))) == 1


# ---- Milestone 3: statistics -----------------------------------------------
class TestStats:
    @pytest.fixture
    def stats(self, parser_mod, stats_mod, small_lines):
        return stats_mod.compute_stats(parser_mod.parse_lines(small_lines), top_n=2)

    def test_percentile(self, stats_mod):
        assert stats_mod.percentile([5, 12, 40, 80, 200], 50) == 40
        assert stats_mod.percentile([5, 12, 40, 80, 200], 95) == 200
        assert stats_mod.percentile([3, 1, 2], 100) == 3
        assert stats_mod.percentile([7], 0) == 7
        assert stats_mod.percentile([], 50) is None

    def test_total_and_status(self, stats):
        assert stats.total == 6
        assert dict(stats.by_status) == {200: 3, 201: 1, 404: 1, 500: 1}

    def test_endpoints(self, stats):
        assert stats.by_endpoint["/api/items"] == 3
        assert stats.by_endpoint["/index.html"] == 2
        assert stats.by_endpoint["/missing"] == 1

    def test_hours(self, stats):
        assert dict(stats.by_hour) == {"2023-10-10 13:00": 2, "2023-10-10 14:00": 3, "2023-10-10 15:00": 1}

    def test_top_ips(self, stats):
        assert stats.top_ips == [("10.0.0.1", 3), ("10.0.0.2", 2)]

    def test_error_rate_counts_only_5xx(self, stats):
        assert stats.error_rate == pytest.approx(1 / 6)

    def test_latency_percentiles_ignore_missing(self, stats):
        assert stats.p50 == 40 and stats.p95 == 200

    def test_empty_input(self, stats_mod):
        s = stats_mod.compute_stats(iter([]))
        assert s.total == 0 and s.error_rate == 0.0
        assert s.p50 is None and s.p95 is None and s.top_ips == []

    def test_accepts_a_generator(self, parser_mod, stats_mod, make_log, pipeline):
        records = parser_mod.parse_lines(pipeline.read_lines(make_log(n=200)))
        assert stats_mod.compute_stats(records).total == 200


# ---- Milestone 4: filters --------------------------------------------------
class TestFilters:
    @pytest.fixture
    def records(self, parser_mod, small_lines):
        return list(parser_mod.parse_lines(small_lines))

    def test_exact_status(self, pipeline, records):
        assert [r.status for r in pipeline.filter_status(records, "404")] == [404]

    def test_status_class(self, pipeline, records):
        assert [r.status for r in pipeline.filter_status(records, "2xx")] == [200, 200, 201, 200]
        assert [r.status for r in pipeline.filter_status(records, "5XX")] == [500]

    @pytest.mark.parametrize("bad", ["", "abc", "99", "6xx", "2x"])
    def test_bad_status_spec(self, pipeline, records, bad):
        with pytest.raises(ValueError):
            list(pipeline.filter_status(records, bad))

    def test_parse_since(self, pipeline):
        assert pipeline.parse_since("2023-10-10") == datetime(2023, 10, 10, tzinfo=timezone.utc)
        assert pipeline.parse_since("2023-10-10T14:30") == datetime(2023, 10, 10, 14, 30, tzinfo=timezone.utc)
        with pytest.raises(ValueError):
            pipeline.parse_since("yesterday")

    def test_filter_since(self, pipeline, records):
        since = pipeline.parse_since("2023-10-10T14:00")
        assert len(list(pipeline.filter_since(records, since))) == 4

    def test_filters_chain(self, pipeline, records):
        out = pipeline.filter_status(pipeline.filter_since(records, pipeline.parse_since("2023-10-10T14:00")), "2xx")
        assert [r.status for r in out] == [201, 200]


# ---- Milestone 5: reports --------------------------------------------------
class TestReports:
    @pytest.fixture
    def stats(self, parser_mod, stats_mod, small_lines):
        return stats_mod.compute_stats(parser_mod.parse_lines(small_lines))

    def test_text_report(self, report, stats):
        text = report.text_report(stats, [], malformed=1)
        assert text.endswith("\n")
        assert "requests:        6" in text
        assert "malformed lines: 1" in text
        assert "error rate:      16.7%" in text
        assert "40 ms / 200 ms" in text
        assert "404: 1" in text and "/api/items" in text and "10.0.0.1" in text
        assert "none" in text  # no spikes

    def test_json_report(self, report, anomalies, stats):
        spike = anomalies.Spike("2023-10-10 14:00", 99, 5.0)
        data = json.loads(report.json_report(stats, [spike], malformed=2))
        assert data["total"] == 6 and data["malformed"] == 2
        assert data["by_status"] == {"200": 3, "201": 1, "404": 1, "500": 1}
        assert data["top_ips"][0] == {"ip": "10.0.0.1", "count": 3}
        assert data["latency_ms"] == {"p50": 40, "p95": 200}
        assert data["spikes"] == [{"hour": "2023-10-10 14:00", "count": 99, "baseline": 5.0}]

    def test_report_without_latency(self, report, stats_mod):
        text = report.text_report(stats_mod.compute_stats(iter([])), [])
        assert "n/a / n/a" in text


# ---- Milestone 6: anomalies ------------------------------------------------
class TestAnomalies:
    def test_spike_found(self, anomalies):
        spikes = anomalies.detect_spikes({"h1": 10, "h2": 12, "h3": 11, "h4": 100})
        assert [(s.hour, s.count) for s in spikes] == [("h4", 100)]
        assert spikes[0].baseline == 11.5

    def test_no_spike(self, anomalies):
        assert anomalies.detect_spikes({"h1": 10, "h2": 12, "h3": 11}) == []

    def test_needs_enough_buckets(self, anomalies):
        assert anomalies.detect_spikes({"h1": 1, "h2": 1000}) == []

    def test_factor_changes_result(self, anomalies):
        data = {"a": 10, "b": 10, "c": 10, "d": 25}
        assert anomalies.detect_spikes(data, factor=2.0)
        assert not anomalies.detect_spikes(data, factor=3.0)

    def test_on_generated_log(self, parser_mod, pipeline, stats_mod, anomalies, make_log):
        path = make_log(n=300, seed=7, spike_hour=3)
        s = stats_mod.compute_stats(parser_mod.parse_lines(pipeline.read_lines(path)))
        assert [x.hour for x in anomalies.detect_spikes(dict(s.by_hour))] == ["2023-10-10 03:00"]

    def test_quiet_generated_log_has_no_spike(self, parser_mod, pipeline, stats_mod, anomalies, make_log):
        s = stats_mod.compute_stats(parser_mod.parse_lines(pipeline.read_lines(make_log(n=600, seed=2))))
        assert anomalies.detect_spikes(dict(s.by_hour)) == []


# ---- Milestone 7: the CLI --------------------------------------------------
class TestCli:
    def test_text_output(self, cli, small_log, capsys):
        assert cli.main([small_log]) == 0
        out = capsys.readouterr().out
        assert "requests:        6" in out and "malformed lines: 1" in out

    def test_json_output(self, cli, small_log, capsys):
        assert cli.main([small_log, "--json", "--top", "1"]) == 0
        data = json.loads(capsys.readouterr().out)
        assert data["total"] == 6 and len(data["top_ips"]) == 1 and data["malformed"] == 1

    def test_status_filter(self, cli, small_log, capsys):
        cli.main([small_log, "--status", "5xx", "--json"])
        data = json.loads(capsys.readouterr().out)
        assert data["total"] == 1 and data["by_status"] == {"500": 1}
        assert data["malformed"] == 1  # still counted

    def test_since_filter(self, cli, small_log, capsys):
        cli.main([small_log, "--since", "2023-10-10T14:00", "--json"])
        assert json.loads(capsys.readouterr().out)["total"] == 4

    def test_missing_file(self, cli, tmp_path, capsys):
        assert cli.main([str(tmp_path / "nope.log")]) == 2
        assert capsys.readouterr().err.startswith("error:")

    @pytest.mark.parametrize("extra", [["--status", "abc"], ["--since", "soon"]])
    def test_bad_filter_values(self, cli, small_log, capsys, extra):
        assert cli.main([small_log, *extra]) == 2
        assert "error:" in capsys.readouterr().err

    def test_usage_error(self, cli, capsys):
        assert cli.main([]) == 2

    def test_generated_log_end_to_end(self, cli, make_log, capsys):
        path = make_log(n=400, seed=3, spike_hour=2, malformed=7)
        assert cli.main([path, "--json"]) == 0
        data = json.loads(capsys.readouterr().out)
        assert data["total"] == 400 + 800
        assert data["malformed"] == 7
        assert [s["hour"] for s in data["spikes"]] == ["2023-10-10 02:00"]
        assert 0 < data["error_rate"] < 0.15
        assert data["latency_ms"]["p50"] <= data["latency_ms"]["p95"]

    def test_generator_is_deterministic(self, make_log):
        a, b = make_log(seed=5), make_log(seed=5)
        c = make_log(seed=6)
        read = lambda p: Path(p).read_text()
        assert read(a) == read(b) != read(c)


def test_same_instant_uses_same_hour(parser_mod, stats_mod):
    other = GOOD.replace("13:55:36 -0700", "20:55:36 +0000")
    stats = stats_mod.compute_stats(parser_mod.parse_lines([GOOD, other]))
    assert dict(stats.by_hour) == {"2023-10-10 20:00": 2}


def test_malformed_callback_counts_without_retaining_lines(parser_mod):
    count = 0
    def count_bad(line):
        nonlocal count
        assert line == "invalid"
        count += 1
    assert list(parser_mod.parse_lines(("invalid" for _ in range(10000)), on_bad=count_bad)) == []
    assert count == 10000
