import asyncio
import sys
import threading

import pytest


@pytest.fixture(scope="module")
def ex(load):
    return load("ex09_concurrency_and_async")


# 1 SafeCounter
def test_safe_counter_basic(ex):
    c = ex.SafeCounter()
    assert c.value == 0
    c.increment()
    c.increment(5)
    assert c.value == 6


def test_safe_counter_negative_amount(ex):
    c = ex.SafeCounter()
    c.increment(10)
    c.increment(-4)
    assert c.value == 6


def test_safe_counter_many_threads_lose_nothing(ex):
    old = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)  # switch threads very often to expose missing locks
    try:
        c = ex.SafeCounter()

        def work():
            for _ in range(2000):
                c.increment()

        threads = [threading.Thread(target=work) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    finally:
        sys.setswitchinterval(old)
    assert c.value == 16000


# 2 parallel_map
def test_parallel_map_keeps_order(ex):
    assert ex.parallel_map(lambda x: x * x, [1, 2, 3, 4], workers=3) == [1, 4, 9, 16]


def test_parallel_map_empty(ex):
    assert ex.parallel_map(len, []) == []


def test_parallel_map_really_runs_in_parallel(ex):
    barrier = threading.Barrier(3, timeout=2)  # only passes if 3 calls run at once

    def meet(x):
        barrier.wait()
        return x

    assert ex.parallel_map(meet, [1, 2, 3], workers=3) == [1, 2, 3]


def test_parallel_map_error_propagates(ex):
    def boom(x):
        if x == 2:
            raise ValueError("two")
        return x

    with pytest.raises(ValueError):
        ex.parallel_map(boom, [1, 2, 3])


# 3 collect_results
def test_collect_results_splits_good_and_bad(ex):
    results, errors = ex.collect_results([lambda: 1, lambda: 1 / 0, lambda: 3])
    assert results == [1, 3]
    assert len(errors) == 1 and isinstance(errors[0], ZeroDivisionError)


def test_collect_results_all_good_and_empty(ex):
    assert ex.collect_results([lambda: "a", lambda: "b"]) == (["a", "b"], [])
    assert ex.collect_results([]) == ([], [])


def test_collect_results_errors_keep_order(ex):
    def fail(msg):
        def f():
            raise RuntimeError(msg)

        return f

    _, errors = ex.collect_results([fail("one"), lambda: 0, fail("two")])
    assert [str(e) for e in errors] == ["one", "two"]


# 4 producer_consumer
def test_producer_consumer_results_sorted(ex):
    assert ex.producer_consumer([3, 1, 2], lambda x: x * 10, n_workers=2) == [10, 20, 30]


def test_producer_consumer_empty_input(ex):
    assert ex.producer_consumer([], str) == []


def test_producer_consumer_uses_worker_threads_and_stops_them(ex):
    before = threading.active_count()
    seen = set()
    lock = threading.Lock()

    def note(x):
        with lock:
            seen.add(threading.current_thread().name)
        return x

    out = ex.producer_consumer(list(range(50)), note, n_workers=4)
    assert out == list(range(50))
    assert threading.current_thread().name not in seen  # work ran in worker threads
    assert threading.active_count() == before  # all workers were stopped


def test_producer_consumer_more_workers_than_items(ex):
    assert ex.producer_consumer([5], lambda x: x + 1, n_workers=6) == [6]


# 5 gather_squares
def test_gather_squares_basic(ex):
    assert asyncio.run(ex.gather_squares([1, 2, 3])) == [1, 4, 9]


def test_gather_squares_empty_and_negative(ex):
    assert asyncio.run(ex.gather_squares([])) == []
    assert asyncio.run(ex.gather_squares([-3])) == [9]


def test_gather_squares_returns_a_list(ex):
    assert isinstance(asyncio.run(ex.gather_squares([2])), list)


# 6 fetch_all_safe
def test_fetch_all_safe_mixed(ex):
    async def good():
        return 1

    async def bad():
        raise ValueError("bad")

    out = asyncio.run(ex.fetch_all_safe([good, bad, good]))
    assert out[0] == (True, 1) and out[2] == (True, 1)
    assert out[1][0] is False and isinstance(out[1][1], ValueError)


def test_fetch_all_safe_empty(ex):
    assert asyncio.run(ex.fetch_all_safe([])) == []


def test_fetch_all_safe_keeps_order_when_finish_order_differs(ex):
    async def run():
        gate = asyncio.Event()

        async def slow():
            await gate.wait()
            return "slow"

        async def fast():
            gate.set()
            return "fast"

        return await ex.fetch_all_safe([slow, fast])

    assert asyncio.run(run()) == [(True, "slow"), (True, "fast")]


# 7 with_timeout
def test_with_timeout_returns_result(ex):
    async def quick():
        return 42

    assert asyncio.run(ex.with_timeout(quick, 1)) == 42


def test_with_timeout_returns_default_and_cancels(ex):
    state = {"cancelled": False}

    async def never():
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            state["cancelled"] = True
            raise

    assert asyncio.run(ex.with_timeout(never, 0.01, "late")) == "late"
    assert state["cancelled"] is True


def test_with_timeout_default_is_none_and_errors_not_hidden(ex):
    async def never():
        await asyncio.Event().wait()

    async def bad():
        raise KeyError("k")

    assert asyncio.run(ex.with_timeout(never, 0.01)) is None
    with pytest.raises(KeyError):
        asyncio.run(ex.with_timeout(bad, 1))


# 8 limited_gather
def test_limited_gather_respects_limit_and_order(ex):
    stats = {"running": 0, "peak": 0}

    def make(i):
        async def job():
            stats["running"] += 1
            stats["peak"] = max(stats["peak"], stats["running"])
            for _ in range(3):
                await asyncio.sleep(0)
            stats["running"] -= 1
            return i

        return job

    out = asyncio.run(ex.limited_gather([make(i) for i in range(6)], 2))
    assert out == list(range(6))
    assert stats["peak"] == 2


def test_limited_gather_limit_one_is_sequential(ex):
    stats = {"running": 0, "peak": 0}

    async def job():
        stats["running"] += 1
        stats["peak"] = max(stats["peak"], stats["running"])
        await asyncio.sleep(0)
        stats["running"] -= 1

    asyncio.run(ex.limited_gather([job] * 4, 1))
    assert stats["peak"] == 1


def test_limited_gather_bad_limit_and_empty(ex):
    with pytest.raises(ValueError):
        asyncio.run(ex.limited_gather([], 0))
    assert asyncio.run(ex.limited_gather([], 3)) == []


# 9 blocking_in_thread
def test_blocking_in_thread_result(ex):
    assert asyncio.run(ex.blocking_in_thread(sum, [1, 2, 3])) == 6


def test_blocking_in_thread_runs_off_the_loop_thread(ex):
    main_id = threading.get_ident()
    assert asyncio.run(ex.blocking_in_thread(threading.get_ident)) != main_id


def test_blocking_in_thread_does_not_block_the_loop(ex):
    async def run():
        flag = threading.Event()

        def wait_blocking():
            return flag.wait(timeout=2)  # blocks the thread until the loop sets the flag

        async def release():
            await asyncio.sleep(0)
            flag.set()

        result, _ = await asyncio.gather(ex.blocking_in_thread(wait_blocking), release())
        return result

    assert asyncio.run(run()) is True


def test_blocking_in_thread_error_propagates(ex):
    with pytest.raises(ZeroDivisionError):
        asyncio.run(ex.blocking_in_thread(lambda: 1 / 0))


# 10 async_pipeline
def test_async_pipeline_keeps_order(ex):
    async def double(x):
        await asyncio.sleep(0)
        return x * 2

    assert asyncio.run(ex.async_pipeline([1, 2, 3, 4, 5], double, 2)) == [2, 4, 6, 8, 10]


def test_async_pipeline_empty_and_single(ex):
    async def ident(x):
        return x

    assert asyncio.run(ex.async_pipeline([], ident)) == []
    assert asyncio.run(ex.async_pipeline(["a"], ident, 5)) == ["a"]


def test_async_pipeline_order_kept_when_finish_order_differs(ex):
    async def run():
        gate = asyncio.Event()

        async def func(x):
            if x == "first":
                await gate.wait()  # finishes last
            else:
                gate.set()
            return x

        return await ex.async_pipeline(["first", "second"], func, 2)

    assert asyncio.run(run()) == ["first", "second"]


def test_async_pipeline_leaves_no_tasks_behind(ex):
    async def run():
        async def ident(x):
            await asyncio.sleep(0)
            return x

        await ex.async_pipeline(list(range(10)), ident, 3)
        return [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    assert asyncio.run(run()) == []


# 11 ping_pong
def test_ping_pong_two_rounds(ex):
    assert asyncio.run(ex.ping_pong(2)) == ["ping", "pong", "ping", "pong"]


def test_ping_pong_zero_and_one(ex):
    assert asyncio.run(ex.ping_pong(0)) == []
    assert asyncio.run(ex.ping_pong(1)) == ["ping", "pong"]


def test_ping_pong_long_alternation(ex):
    assert asyncio.run(ex.ping_pong(50)) == ["ping", "pong"] * 50


# 12 first_result
def test_first_result_returns_winner_and_cancels_losers(ex):
    cancelled = []

    def blocked(name):
        async def f():
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                cancelled.append(name)
                raise

        return f

    async def winner():
        return "won"

    result = asyncio.run(ex.first_result([blocked("a"), winner, blocked("b")]))
    assert result == "won"
    assert sorted(cancelled) == ["a", "b"]  # already cancelled when the call returns


def test_first_result_prefers_earlier_when_both_ready(ex):
    async def one():
        return 1

    async def two():
        return 2

    assert asyncio.run(ex.first_result([one, two])) == 1


def test_first_result_empty_rejected(ex):
    with pytest.raises(ValueError):
        asyncio.run(ex.first_result([]))


def test_first_result_error_of_winner_propagates(ex):
    async def bad():
        raise KeyError("x")

    async def blocked():
        await asyncio.Event().wait()

    with pytest.raises(KeyError):
        asyncio.run(ex.first_result([blocked, bad]))


def test_async_pipeline_failure_cleans_up_other_workers(ex):
    async def run():
        started = asyncio.Event()
        cleaned = []
        async def work(item):
            if item == "fail":
                await started.wait()
                raise ValueError("failed")
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                cleaned.append(item)
        with pytest.raises(ValueError):
            await ex.async_pipeline(["fail", "waiting"], work, 2)
        assert cleaned == ["waiting"]
        assert not [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    asyncio.run(run())


def test_async_pipeline_caller_cancellation_cleans_up(ex):
    async def run():
        started = asyncio.Event()
        async def work(item):
            started.set()
            await asyncio.Event().wait()
        task = asyncio.create_task(ex.async_pipeline([1, 2], work, 2))
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert not [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    asyncio.run(run())
