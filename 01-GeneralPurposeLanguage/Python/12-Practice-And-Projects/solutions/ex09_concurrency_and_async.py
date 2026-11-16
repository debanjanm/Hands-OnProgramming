"""Exercise set 09: threads, executors and asyncio.

Work from top to bottom. Each problem is marked easy, medium or hard.
The tests never depend on timing: they use Events, Barriers and ordering.
Async functions are run by the tests with asyncio.run(...).
"""
import asyncio
import queue
import threading
from concurrent.futures import ThreadPoolExecutor


# ---------------------------------------------------------------- 1 (easy)
class SafeCounter:
    """Level: easy. (threading.Lock)

    A counter that many threads can use at the same time without losing updates.
    `increment(amount=1)` adds to it; the `value` attribute-style property
    (read with `counter.value`) returns the current total. Starts at 0.

        c = SafeCounter(); c.increment(); c.increment(5); c.value -> 6

    Hint: `with self._lock:` around the read-modify-write; `value += 1` is not atomic.
    """

    # Idea: a Lock makes "read, add, write" one step that no other thread can interrupt.
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def increment(self, amount=1):
        with self._lock:
            self._value += amount

    @property
    def value(self):
        with self._lock:
            return self._value


# ---------------------------------------------------------------- 2 (easy)
def parallel_map(func, items, workers=4):
    """Level: easy. (ThreadPoolExecutor)

    Apply `func` to every item using a pool of `workers` threads. Return the
    results as a list in the SAME order as `items`. If `func` raises, the
    exception comes out of parallel_map.

        parallel_map(lambda x: x * x, [1, 2, 3]) -> [1, 4, 9]
        parallel_map(len, []) -> []

    Hint: `with ThreadPoolExecutor(max_workers=workers) as pool: list(pool.map(func, items))`.
    """
    # Idea: executor.map keeps input order even if tasks finish in another order.
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(func, items))


# --------------------------------------------------------------- 3 (medium)
def collect_results(tasks, workers=4):
    """Level: medium. (Future, submit)

    `tasks` is a list of zero-argument functions. Run them all in a thread
    pool. Return `(results, errors)`: `results` has the return values of the
    tasks that worked, `errors` has the exceptions of those that failed. Both
    keep the original task order. One failing task must not stop the others.

        collect_results([lambda: 1, lambda: 1 / 0, lambda: 3]) -> ([1, 3], [ZeroDivisionError(...)])

    Hint: futures = [pool.submit(t) ...]; then future.exception() is None when it worked.
    """
    # Idea: submit everything first, then look at each future in order.
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(task) for task in tasks]
        results, errors = [], []
        for future in futures:
            error = future.exception()
            if error is None:
                results.append(future.result())
            else:
                errors.append(error)
    return results, errors


# --------------------------------------------------------------- 4 (medium)
def producer_consumer(items, func, n_workers=3):
    """Level: medium. (queue.Queue, threads, sentinel)

    One producer (the calling thread) puts every item on a queue.Queue.
    `n_workers` consumer threads take items, compute `func(item)` and keep the
    results. When all items are done, stop the workers cleanly (send one
    sentinel per worker), join them and return the results sorted.

        producer_consumer([3, 1, 2], lambda x: x * 10, n_workers=2) -> [10, 20, 30]
        producer_consumer([], str) -> []

    Hint: a sentinel is a unique marker, e.g. `None`; each worker stops when it gets it.
    """
    # Idea: workers loop on queue.get(); a sentinel per worker tells each one to stop.
    stop = object()
    jobs = queue.Queue()
    results = []
    lock = threading.Lock()

    def worker():
        while True:
            item = jobs.get()
            if item is stop:
                return
            value = func(item)
            with lock:
                results.append(value)

    threads = [threading.Thread(target=worker) for _ in range(n_workers)]
    for t in threads:
        t.start()
    for item in items:
        jobs.put(item)
    for _ in threads:
        jobs.put(stop)
    for t in threads:
        t.join()
    return sorted(results)


# ---------------------------------------------------------------- 5 (easy)
async def gather_squares(numbers):
    """Level: easy. (asyncio.gather)

    Square every number "at the same time" with a small coroutine and return
    the results in input order. Use `await asyncio.sleep(0)` inside the helper
    to make it a real coroutine.

        asyncio.run(gather_squares([1, 2, 3])) -> [1, 4, 9]
        asyncio.run(gather_squares([])) -> []

    Hint: `await asyncio.gather(*(square(n) for n in numbers))`.
    """
    # Idea: gather runs all coroutines together and returns results in the order given.
    async def square(n):
        await asyncio.sleep(0)
        return n * n

    return list(await asyncio.gather(*(square(n) for n in numbers)))


# --------------------------------------------------------------- 6 (medium)
async def fetch_all_safe(funcs):
    """Level: medium. (gather with return_exceptions)

    `funcs` is a list of zero-argument async functions. Run them all. Return a
    list with one entry per function, in order: `(True, result)` if it worked
    or `(False, exception)` if it raised. One failure must not hide the others.

        [(True, 1), (False, ValueError('bad'))]

    Hint: asyncio.gather(..., return_exceptions=True) returns exceptions as values.
    """
    # Idea: return_exceptions=True turns raised errors into ordinary list items.
    outcomes = await asyncio.gather(*(f() for f in funcs), return_exceptions=True)
    return [(not isinstance(o, BaseException), o) for o in outcomes]


# --------------------------------------------------------------- 7 (medium)
async def with_timeout(func, seconds, default=None):
    """Level: medium. (asyncio.wait_for, TimeoutError)

    `func` is a zero-argument async function. Await it, but give up after
    `seconds` and return `default` instead. Other exceptions are not hidden.
    When it times out, the unfinished work must be cancelled.

        asyncio.run(with_timeout(quick, 1)) -> its result
        asyncio.run(with_timeout(never_finishes, 0.01, "late")) -> "late"

    Hint: `await asyncio.wait_for(func(), seconds)` raises TimeoutError (asyncio.TimeoutError).
    """
    # Idea: wait_for cancels the inner coroutine for us when the time runs out.
    try:
        return await asyncio.wait_for(func(), seconds)
    except asyncio.TimeoutError:
        return default


# --------------------------------------------------------------- 8 (medium)
async def limited_gather(funcs, limit):
    """Level: medium. (asyncio.Semaphore)

    `funcs` is a list of zero-argument async functions. Run them all, but never
    more than `limit` at the same moment. Return results in input order.
    ValueError if limit < 1.

        asyncio.run(limited_gather([f1, f2, f3, f4], 2))  # at most 2 running together

    Hint: `sem = asyncio.Semaphore(limit)`; wrap each call in `async with sem:`.
    """
    # Idea: every task must hold a semaphore slot while it runs.
    if limit < 1:
        raise ValueError("limit must be at least 1")
    sem = asyncio.Semaphore(limit)

    async def guarded(func):
        async with sem:
            return await func()

    return list(await asyncio.gather(*(guarded(f) for f in funcs)))


# --------------------------------------------------------------- 9 (medium)
async def blocking_in_thread(func, *args):
    """Level: medium. (asyncio.to_thread)

    `func` is a normal (blocking) function. Run it in a worker thread so the
    event loop stays free, and return its result. Exceptions from `func`
    must come out of the await.

        await blocking_in_thread(sum, [1, 2, 3]) -> 6

    Hint: `await asyncio.to_thread(func, *args)`.
    """
    # Idea: to_thread moves blocking work off the loop thread.
    return await asyncio.to_thread(func, *args)


# --------------------------------------------------------------- 10 (hard)
async def async_pipeline(items, func, n_workers=3):
    """Level: hard. (asyncio.Queue, worker tasks)

    `func` is an async function taking one item. Start `n_workers` worker
    tasks that read items from an asyncio.Queue and call `await func(item)`.
    Return the results as a list in the SAME order as `items`, whatever order
    they finish in. Stop the workers cleanly (no tasks left running).

        asyncio.run(async_pipeline([1, 2, 3], double, 2)) -> [2, 4, 6]
        asyncio.run(async_pipeline([], double)) -> []

    Hint: put (index, item) on the queue; workers store results[index]; use a sentinel or queue.join() then cancel.
    """
    # Idea: the index travels with the item, so order is easy to restore.
    jobs = asyncio.Queue()
    results = [None] * len(items)
    for pair in enumerate(items):
        jobs.put_nowait(pair)

    async def worker():
        while True:
            try:
                index, item = jobs.get_nowait()
            except asyncio.QueueEmpty:
                return
            results[index] = await func(item)

    await asyncio.gather(*(worker() for _ in range(n_workers)))
    return results


# --------------------------------------------------------------- 11 (hard)
async def ping_pong(rounds):
    """Level: hard. (asyncio.Event)

    Two coroutines take turns. "ping" always goes first, then "pong", and so on
    for `rounds` rounds. Return the trace list, e.g. rounds=2 ->
    ["ping", "pong", "ping", "pong"]. No sleeping: the order must come from
    Events, not from timing. rounds=0 -> [].

    Hint: one Event per player; wait for yours, clear it, record, then set the other's.
    """
    # Idea: each player waits for its own "my turn" flag and then hands the turn over.
    trace = []
    ping_turn, pong_turn = asyncio.Event(), asyncio.Event()
    ping_turn.set()

    async def player(name, mine, other):
        for _ in range(rounds):
            await mine.wait()
            mine.clear()
            trace.append(name)
            other.set()

    await asyncio.gather(player("ping", ping_turn, pong_turn), player("pong", pong_turn, ping_turn))
    return trace


# --------------------------------------------------------------- 12 (hard)
async def first_result(funcs):
    """Level: hard. (asyncio.wait, cancellation)

    `funcs` is a list of zero-argument async functions. Start them all, return
    the result of the first one to finish, and CANCEL all the others (and wait
    until the cancellation is done). If several are already finished, prefer
    the earlier one in the list. ValueError if `funcs` is empty. If the winner
    raised, that exception comes out.

    Hint: asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED); then task.cancel() and await the losers.
    """
    # Idea: wait for the first one, then clean up every loser so nothing keeps running.
    if not funcs:
        raise ValueError("need at least one function")
    tasks = [asyncio.ensure_future(f()) for f in funcs]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
    await asyncio.gather(*pending, return_exceptions=True)
    winner = next(t for t in tasks if t in done)
    return winner.result()
