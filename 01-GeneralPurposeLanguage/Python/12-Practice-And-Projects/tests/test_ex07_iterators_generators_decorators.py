import types

import pytest


@pytest.fixture(scope="module")
def ex(load):
    return load("ex07_iterators_generators_decorators")


# 1 Countdown
def test_countdown_counts_down(ex):
    assert list(ex.Countdown(3)) == [3, 2, 1]


def test_countdown_zero_and_negative_are_empty(ex):
    assert list(ex.Countdown(0)) == []
    assert list(ex.Countdown(-2)) == []


def test_countdown_is_a_real_iterator(ex):
    c = ex.Countdown(2)
    assert iter(c) is c
    assert next(c) == 2
    assert next(c) == 1
    with pytest.raises(StopIteration):
        next(c)


# 2 chunked
def test_chunked_last_chunk_is_shorter(ex):
    assert list(ex.chunked([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]


def test_chunked_exact_and_empty(ex):
    assert list(ex.chunked([1, 2, 3, 4], 2)) == [[1, 2], [3, 4]]
    assert list(ex.chunked([], 3)) == []


def test_chunked_is_lazy_and_accepts_generators(ex):
    source = (i for i in range(10**9))
    gen = ex.chunked(source, 3)
    assert isinstance(gen, types.GeneratorType)
    assert next(gen) == [0, 1, 2]
    assert next(gen) == [3, 4, 5]


def test_chunked_rejects_bad_size(ex):
    with pytest.raises(ValueError):
        list(ex.chunked([1, 2], 0))


# 3 flatten
def test_flatten_deep_nesting(ex):
    assert list(ex.flatten([1, [2, [3, (4, 5)]], 6])) == [1, 2, 3, 4, 5, 6]


def test_flatten_keeps_strings_whole(ex):
    assert list(ex.flatten(["ab", ["cd", ["e"]]])) == ["ab", "cd", "e"]


def test_flatten_empty_pieces(ex):
    assert list(ex.flatten([])) == []
    assert list(ex.flatten([[], [[]]])) == []


# 4 parse_log_lines
def test_parse_log_lines_basic(ex):
    lines = ["info: started", "", "# note", "Error: disk: full"]
    assert list(ex.parse_log_lines(lines)) == [("INFO", "started"), ("ERROR", "disk: full")]


def test_parse_log_lines_skips_junk_and_strips(ex):
    lines = ["   ", "no colon here", "  warn :  low memory  ", "   # indented comment"]
    assert list(ex.parse_log_lines(lines)) == [("WARN", "low memory")]


def test_parse_log_lines_is_lazy(ex):
    def source():
        yield "info: one"
        raise AssertionError("read too far")

    gen = ex.parse_log_lines(source())
    assert next(gen) == ("INFO", "one")


# 5 sliding_window
def test_sliding_window_pairs(ex):
    assert list(ex.sliding_window([1, 2, 3, 4], 2)) == [(1, 2), (2, 3), (3, 4)]


def test_sliding_window_whole_input_and_too_short(ex):
    assert list(ex.sliding_window("abc", 3)) == [("a", "b", "c")]
    assert list(ex.sliding_window([1, 2], 3)) == []


def test_sliding_window_one_shot_iterator_and_size_one(ex):
    assert list(ex.sliding_window(iter([7, 8]), 1)) == [(7,), (8,)]


def test_sliding_window_bad_size(ex):
    with pytest.raises(ValueError):
        list(ex.sliding_window([1, 2], 0))


# 6 averager
def test_averager_running_average(ex):
    avg = ex.averager()
    next(avg)
    assert avg.send(10) == 10.0
    assert avg.send(20) == 15.0
    assert avg.send(30) == 20.0


def test_averager_instances_are_independent(ex):
    a, b = ex.averager(), ex.averager()
    next(a)
    next(b)
    a.send(100)
    assert b.send(2) == 2.0


def test_averager_handles_negatives(ex):
    avg = ex.averager()
    next(avg)
    avg.send(-4)
    assert avg.send(4) == 0.0


# 7 log_calls
def test_log_calls_records_calls_and_returns_result(ex):
    @ex.log_calls
    def add(a, b=0):
        "Add."
        return a + b

    assert add(1, b=2) == 3
    assert add(5) == 5
    assert add.calls == [("add", (1,), {"b": 2}), ("add", (5,), {})]


def test_log_calls_keeps_metadata(ex):
    @ex.log_calls
    def greet():
        "Say hi."

    assert greet.__name__ == "greet"
    assert greet.__doc__ == "Say hi."


def test_log_calls_separate_lists_per_function(ex):
    @ex.log_calls
    def a():
        pass

    @ex.log_calls
    def b():
        pass

    a()
    assert a.calls != [] and b.calls == []


# 8 repeat
def test_repeat_runs_n_times_and_collects(ex):
    counter = []

    @ex.repeat(3)
    def tick(x):
        counter.append(x)
        return len(counter)

    assert tick("a") == [1, 2, 3]
    assert counter == ["a", "a", "a"]


def test_repeat_once_and_metadata(ex):
    @ex.repeat(1)
    def roll():
        "Roll."
        return 4

    assert roll() == [4]
    assert roll.__name__ == "roll" and roll.__doc__ == "Roll."


def test_repeat_rejects_zero(ex):
    with pytest.raises(ValueError):
        ex.repeat(0)


# 9 timed
def test_timed_records_durations_with_fake_clock(ex):
    ticks = iter([0, 5, 10, 12])

    @ex.timed(lambda: next(ticks))
    def work():
        return "ok"

    assert work() == "ok"
    assert work() == "ok"
    assert work.durations == [5, 2]


def test_timed_records_even_when_function_fails(ex):
    ticks = iter([100, 107])

    @ex.timed(lambda: next(ticks))
    def boom():
        raise RuntimeError("x")

    with pytest.raises(RuntimeError):
        boom()
    assert boom.durations == [7]


def test_timed_passes_arguments_and_keeps_name(ex):
    ticks = iter(range(100))

    @ex.timed(lambda: next(ticks))
    def mul(a, b):
        return a * b

    assert mul(3, b=4) == 12
    assert mul.__name__ == "mul"


# 10 retry
def make_flaky(fail_times, error=ValueError):
    state = {"calls": 0}

    def flaky():
        state["calls"] += 1
        if state["calls"] <= fail_times:
            raise error("nope")
        return "done"

    return flaky, state


def test_retry_succeeds_after_failures_and_sleeps_between(ex):
    flaky, state = make_flaky(2)
    sleeps = []
    wrapped = ex.retry(3, (ValueError,), delay=2, sleep=sleeps.append)(flaky)
    assert wrapped() == "done"
    assert state["calls"] == 3
    assert sleeps == [2, 2]


def test_retry_gives_up_and_raises_last_error_without_final_sleep(ex):
    flaky, state = make_flaky(10)
    sleeps = []
    wrapped = ex.retry(3, (ValueError,), delay=1, sleep=sleeps.append)(flaky)
    with pytest.raises(ValueError):
        wrapped()
    assert state["calls"] == 3
    assert sleeps == [1, 1]


def test_retry_ignores_other_exception_types(ex):
    flaky, state = make_flaky(1, error=KeyError)
    sleeps = []
    wrapped = ex.retry(5, (ValueError,), sleep=sleeps.append)(flaky)
    with pytest.raises(KeyError):
        wrapped()
    assert state["calls"] == 1 and sleeps == []


def test_retry_no_sleep_when_first_call_works(ex):
    sleeps = []

    @ex.retry(3, sleep=sleeps.append)
    def fine(x):
        "Doc."
        return x

    assert fine(9) == 9
    assert sleeps == []
    assert fine.__name__ == "fine"


# 11 memoize
def test_memoize_counts_hits_and_misses(ex):
    calls = []

    @ex.memoize
    def square(x):
        calls.append(x)
        return x * x

    assert square(4) == 16
    assert square(4) == 16
    assert square(5) == 25
    assert calls == [4, 5]
    assert (square.hits, square.misses) == (1, 2)


def test_memoize_keyword_order_does_not_matter(ex):
    @ex.memoize
    def f(a, b):
        return a - b

    assert f(a=5, b=2) == 3
    assert f(b=2, a=5) == 3
    assert (f.hits, f.misses) == (1, 1)


def test_memoize_clear_resets(ex):
    calls = []

    @ex.memoize
    def f(x):
        calls.append(x)
        return x

    f(1)
    f(1)
    f.clear()
    assert (f.hits, f.misses) == (0, 0)
    f(1)
    assert calls == [1, 1]


def test_memoize_does_not_cache_errors_and_keeps_name(ex):
    state = {"n": 0}

    @ex.memoize
    def shaky(x):
        state["n"] += 1
        if state["n"] == 1:
            raise ValueError
        return x

    with pytest.raises(ValueError):
        shaky(1)
    assert shaky(1) == 1
    assert shaky.__name__ == "shaky"


# 12 collect_errors
def test_collect_errors_swallows_and_records(ex):
    errors = []
    with ex.collect_errors(errors, ValueError):
        int("x")
    assert len(errors) == 1 and isinstance(errors[0], ValueError)


def test_collect_errors_other_exceptions_propagate(ex):
    errors = []
    with pytest.raises(KeyError):
        with ex.collect_errors(errors, ValueError):
            {}["missing"]
    assert errors == []


def test_collect_errors_default_is_exception_and_no_error_is_fine(ex):
    errors = []
    with ex.collect_errors(errors):
        raise RuntimeError("a")
    with ex.collect_errors(errors):
        pass
    assert [str(e) for e in errors] == ["a"]
