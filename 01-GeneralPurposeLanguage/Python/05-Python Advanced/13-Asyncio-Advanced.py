import asyncio
import contextlib
import contextvars
import gc
import io
import logging
import sys
import threading
import time
import unittest
import warnings
import weakref
from concurrent.futures import ThreadPoolExecutor

# 01. Asyncio Advanced - What This File Adds To 10-Async-Await.py
# ------------------------------------
# - 10-Async-Await.py covered the basics: coroutines, gather, create_task,
#   Lock, Queue, cancel, run_in_executor. This file is about doing asyncio
#   WELL: structured concurrency, timeouts, backpressure, the classic
#   mistakes, streams, subprocesses, debugging and testing.
#
# THE EVENT LOOP IN PLAIN WORDS
# - asyncio runs everything on ONE thread. There is a single "event loop"
#   that keeps a to-do list of ready callbacks and a list of timers/IO waits.
# - A coroutine runs until it hits `await` on something that is not ready.
#   At that moment it hands control BACK to the loop, which runs something
#   else. `await` is therefore a YIELD POINT: the only place where another
#   task can run. That is called COOPERATIVE scheduling.
# - Consequences:
#     * between two awaits your code is never interrupted: no data races on
#       plain variables (but a race is possible ACROSS an await - see 10-...py);
#     * if a coroutine never awaits (CPU loop, time.sleep, blocking socket)
#       the WHOLE loop is frozen - every other task stalls;
#     * thousands of waiting tasks are cheap (no threads), which is why
#       asyncio shines for I/O-heavy servers and clients.
# - This file needs Python 3.11+ for a few features (TaskGroup, timeout(),
#   ExceptionGroup, Runner). Those sections check sys.version_info and print
#   a skip message on older versions.
#
# Every demo is deterministic: results are sorted, ordering is forced with
# Events/sleep(0)/well-separated delays, sleeps are tiny, and timings are only
# compared (never asserted).

PY311 = sys.version_info >= (3, 11)


def header(title):
    print(f"\n# {title}")


async def with_timeout(coro, seconds):
    """Version-neutral helper: asyncio.timeout() on 3.11+, wait_for before."""
    if hasattr(asyncio, "timeout"):
        async with asyncio.timeout(seconds):
            return await coro
    return await asyncio.wait_for(coro, seconds)


# 02. Cooperative Scheduling Made Visible
# ------------------------------------
# - Two tasks that `await asyncio.sleep(0)` (a pure "let others run" yield)
#   take turns. A task that never awaits runs to the end before anyone else.
async def polite(name, steps, log):
    for i in range(steps):
        log.append(f"{name}{i}")
        await asyncio.sleep(0)              # yield point: loop may run another task


async def hog(name, steps, log):
    for i in range(steps):
        log.append(f"{name}{i}")            # no await -> nobody else gets a turn


async def scheduling_demo():
    log = []
    await asyncio.gather(polite("A", 3, log), polite("B", 3, log))
    print("two polite tasks interleave :", " ".join(log))
    log = []
    await asyncio.gather(hog("A", 3, log), hog("B", 3, log))
    print("a task without await hogs it:", " ".join(log))


# 03. TaskGroup - Structured Concurrency (3.11+)
# ------------------------------------
# - `async with asyncio.TaskGroup() as tg:` is a scope for tasks: leaving the
#   block WAITS for all of them. If any task fails, the group CANCELS the
#   siblings, waits for them to finish cleaning up, and then raises an
#   ExceptionGroup holding every failure. Nothing is left running in the
#   background - that is "structured concurrency".
# - Compare gather() (section 05): by default it raises the first error but
#   leaves the OTHER tasks running unattended.
async def tg_worker(name, delay, log):
    try:
        await asyncio.sleep(delay)
        log.append(f"{name} finished")
        return name
    except asyncio.CancelledError:
        log.append(f"{name} cancelled")
        raise                                # ALWAYS re-raise cancellation


async def tg_bad(delay):
    await asyncio.sleep(delay)
    raise ValueError("tg_bad failed")


async def taskgroup_demo():
    log = []
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(tg_worker("a", 0.01, log))
        t2 = tg.create_task(tg_worker("b", 0.02, log))
    print("success: group waited for both ->", t1.result(), t2.result())

    log = []
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(tg_worker("slow1", 5, log))
            tg.create_task(tg_worker("slow2", 5, log))
            tg.create_task(tg_bad(0.01))
    except ExceptionGroup as eg:
        print("failure: one task raised ->", type(eg).__name__, [repr(e) for e in eg.exceptions])
    print("siblings were cancelled automatically:", sorted(log))

    # Cancelling ONE task inside a group does not fail the group.
    log = []
    async with asyncio.TaskGroup() as tg:
        victim = tg.create_task(tg_worker("victim", 5, log))
        tg.create_task(tg_worker("survivor", 0.02, log))
        await asyncio.sleep(0.005)
        victim.cancel()
    print("cancelling one task inside a group:", sorted(log), "| victim.cancelled() =", victim.cancelled())


# `except*` is NEW SYNTAX (3.11+): a file containing it will not even COMPILE
# on 3.10. To keep the rest of this file importable everywhere, the except*
# demo is kept as source text and only exec()'d on 3.11+. Read it as code.
# - `except* T` handles the T-members of the group; other members continue
#   to propagate. The same group may match several except* clauses.
EXCEPT_STAR_SRC = '''
async def immediate_failure(exc):
    raise exc                    # fails before any await, so BOTH tasks fail

async def except_star_demo():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(immediate_failure(ValueError("bad value")))
            tg.create_task(immediate_failure(TypeError("bad type")))
    except* ValueError as group:
        print("except* ValueError got:", [repr(e) for e in group.exceptions])
    except* TypeError as group:
        print("except* TypeError  got:", [repr(e) for e in group.exceptions])
'''


# 04. Timeouts: asyncio.timeout() and wait_for()
# ------------------------------------
# - timeout(seconds) (3.11+) is an async context manager around a BLOCK:
#   if the block takes too long the current task is cancelled and
#   TimeoutError is raised at the `async with`. It covers several awaits at
#   once, can be rescheduled, and can tell you whether it fired.
# - wait_for(awaitable, timeout) wraps ONE awaitable (works on every version).
#   On timeout it cancels the inner work and waits for it to finish.
# - Either way the slow work is CANCELLED, not left running.
async def timeouts_demo():
    if PY311:
        try:
            async with asyncio.timeout(0.02):
                await asyncio.sleep(1)
        except TimeoutError:
            print("asyncio.timeout(0.02) around a 1s sleep -> TimeoutError")

        async with asyncio.timeout(0.01) as scope:
            scope.reschedule(asyncio.get_running_loop().time() + 0.2)   # extend the deadline
            await asyncio.sleep(0.03)
        print("rescheduled deadline: finished OK, expired() =", scope.expired())
    else:
        print("asyncio.timeout() needs 3.11+ - skipped (wait_for works on all versions)")

    try:
        await asyncio.wait_for(asyncio.sleep(1), timeout=0.02)
    except asyncio.TimeoutError:
        print("wait_for(sleep(1), 0.02)      -> TimeoutError (the sleep was cancelled)")
    # Pattern: a deadline for a whole multi-step operation
    async def multi_step():
        await asyncio.sleep(0.01)
        await asyncio.sleep(0.01)
        await asyncio.sleep(1)
    try:
        await with_timeout(multi_step(), 0.05)
    except asyncio.TimeoutError:
        print("one deadline covered all three steps")


# 05. wait vs as_completed vs gather(return_exceptions=True)
# ------------------------------------
# - Same three jobs, four ways to collect them. Delays are far apart so the
#   completion order is stable: fast (0.01), bad (0.03, fails), slow (0.06).
#     gather                 -> results in INPUT order, one call
#     gather + default       -> first exception propagates; others KEEP RUNNING
#     as_completed           -> handle each as soon as it is ready
#     wait(FIRST_COMPLETED)  -> returns (done, pending) sets - no results order
async def job(name, delay, log, fail=False):
    await asyncio.sleep(delay)
    log.append(f"{name} finished")
    if fail:
        raise RuntimeError(f"{name} failed")
    return name


def make_jobs(log):
    return [job("slow", 0.06, log), job("fast", 0.01, log), job("bad", 0.03, log, fail=True)]


async def collection_demo():
    log = []
    res = await asyncio.gather(*make_jobs(log), return_exceptions=True)
    print("gather(return_exceptions=True):", [r if isinstance(r, str) else repr(r) for r in res], "<- input order")

    log = []
    try:
        await asyncio.gather(*make_jobs(log))
    except RuntimeError as exc:
        print("gather (default) raised:", exc, "| log at that moment:", log)
    await asyncio.sleep(0.08)
    print("...but 'slow' was NOT cancelled, it finished later:", log)

    log = []
    order = []
    for fut in asyncio.as_completed(make_jobs(log)):
        try:
            order.append(await fut)
        except RuntimeError as exc:
            order.append(f"ERROR({exc})")
    print("as_completed (finish order):", order)

    log = []
    tasks = [asyncio.create_task(c) for c in make_jobs(log)]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    print("wait FIRST_COMPLETED -> done:", [t.result() for t in done], "| pending:", len(pending))
    for t in pending:
        t.cancel()
    await asyncio.gather(*pending, return_exceptions=True)      # let cancellations finish

    log = []
    tasks = [asyncio.create_task(c) for c in make_jobs(log)]
    done, pending = await asyncio.wait(tasks)                   # ALL_COMPLETED is the default
    print("wait ALL_COMPLETED -> ok:", sorted(t.result() for t in done if t.exception() is None),
          "| failed:", [repr(t.exception()) for t in done if t.exception()])

    tasks = [asyncio.create_task(c) for c in make_jobs([])]
    done, pending = await asyncio.wait(tasks, timeout=0.02)
    print("wait(timeout=0.02) -> done:", len(done), "| pending:", len(pending), "(NOT cancelled - your job)")
    for t in pending:
        t.cancel()
    await asyncio.gather(*pending, return_exceptions=True)
    # Rule: asyncio.wait takes TASKS (not bare coroutines, 3.11+). It never
    # raises the tasks' exceptions - you inspect them yourself.


# 06. Semaphore - Bound The Concurrency
# ------------------------------------
# - Launching 10,000 requests at once will overwhelm a server (or your file
#   descriptor limit). An asyncio.Semaphore(N) lets only N coroutines be
#   inside the guarded block at a time; the rest wait their turn.
async def semaphore_demo():
    sem = asyncio.Semaphore(3)
    in_flight = 0
    max_in_flight = 0

    async def limited(i):
        nonlocal in_flight, max_in_flight
        async with sem:
            in_flight += 1
            max_in_flight = max(max_in_flight, in_flight)
            await asyncio.sleep(0.01)
            in_flight -= 1
        return i

    results = await asyncio.gather(*(limited(i) for i in range(10)))
    print("10 tasks through Semaphore(3): all done:", results == list(range(10)))
    print("max in flight was exactly the limit:", max_in_flight)
    # No lock needed around in_flight: no await between read and write.


# 07. Event and Condition
# ------------------------------------
async def event_condition_demo():
    gate = asyncio.Event()
    started = []

    async def waiter(i):
        await gate.wait()                  # parks until set()
        started.append(i)

    waiters = [asyncio.create_task(waiter(i)) for i in range(3)]
    await asyncio.sleep(0)
    print("before gate.set(), started:", started)
    gate.set()
    await asyncio.gather(*waiters)
    print("after gate.set(), started:", sorted(started))

    cond = asyncio.Condition()
    items = []
    seen = []

    async def consumer(name):
        async with cond:
            await cond.wait_for(lambda: len(items) >= 3)   # re-checks after every wake-up
            seen.append((name, len(items)))

    consumers = [asyncio.create_task(consumer(n)) for n in ("c1", "c2")]
    await asyncio.sleep(0)
    for x in range(3):
        async with cond:
            items.append(x)
            cond.notify_all()
    await asyncio.gather(*consumers)
    print("Condition: both consumers woke only once 3 items existed:", sorted(seen))


# 08. Cancellation Nuances and shield()
# ------------------------------------
# - cancel() does not stop a task - it schedules a CancelledError to be
#   RAISED at the task's current await. The task can run cleanup (finally).
# - CancelledError inherits from BaseException (not Exception) so a normal
#   `except Exception` does not swallow it. A bare `except:` or an
#   `except BaseException` DOES - never do that without re-raising.
# - If you catch CancelledError and do NOT re-raise, the task ends "normally":
#   the caller thinks the cancel failed and TaskGroup/timeout() break.
# - shield(x) protects the INNER task from cancellation of the OUTER await.
async def cancellation_demo():
    print("CancelledError is an Exception subclass?", issubclass(asyncio.CancelledError, Exception))
    log = []

    async def swallows():
        try:
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            log.append("swallowed it")          # BUG: forgot `raise`
        return "carried on as if nothing happened"

    async def cooperates():
        try:
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            log.append("cleanup after cancel")
            raise                               # propagate: task becomes 'cancelled'
        finally:
            log.append("finally always runs")

    bad = asyncio.create_task(swallows())
    await asyncio.sleep(0)                      # let it reach its await
    bad.cancel()
    print("swallowing task returned:", await bad, "| cancelled() =", bad.cancelled())

    good = asyncio.create_task(cooperates())
    await asyncio.sleep(0)
    good.cancel()
    try:
        await good
    except asyncio.CancelledError:
        print("cooperating task: await raised CancelledError | cancelled() =", good.cancelled())
    print("log:", log)

    # shield: cancel the waiter, keep the work.
    async def important_work():
        await asyncio.sleep(0.03)
        return "important result saved"

    inner = asyncio.create_task(important_work())   # keep a reference to the inner task!

    async def caller():
        return await asyncio.shield(inner)

    outer = asyncio.create_task(caller())
    await asyncio.sleep(0.01)
    outer.cancel()
    try:
        await outer
    except asyncio.CancelledError:
        print("outer awaiter cancelled:", outer.cancelled(), "| inner cancelled:", inner.cancelled())
    print("inner kept running ->", await inner)
    # Gotcha: shield protects against OUTER cancellation only. If the whole
    # loop shuts down, or someone cancels `inner` directly, it still dies.


# 09. Bridging Blocking Code: to_thread vs run_in_executor
# ------------------------------------
# - Calling blocking code (a sync DB driver, requests, file I/O, time.sleep)
#   inside a coroutine freezes the loop (see section 10). Move it to a thread.
# - asyncio.to_thread(fn, *args, **kwargs) (3.9+): the simple way. Uses the
#   loop's default thread pool and COPIES the current contextvars.
# - loop.run_in_executor(executor, fn, *args) (see 10-Async-Await.py): more
#   control - pick YOUR executor (e.g. a ProcessPoolExecutor for CPU work,
#   or a small dedicated ThreadPoolExecutor). No kwargs: use functools.partial.
def blocking_io(n):
    time.sleep(0.02)
    return (n * 2, threading.current_thread() is not threading.main_thread())


async def thread_bridge_demo():
    results = await asyncio.gather(*(asyncio.to_thread(blocking_io, i) for i in range(4)))
    print("to_thread x4 ran concurrently:", [r[0] for r in results], "| all off the main thread:", all(r[1] for r in results))
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="mypool") as pool:
        value, off_main = await loop.run_in_executor(pool, blocking_io, 21)
    print("run_in_executor with our own pool:", value, "| off main thread:", off_main)
    # Limits: threads cannot be cancelled. If you cancel the awaiting task
    # the thread keeps running to completion; only the WAIT is abandoned.


# 10. The Classic Mistakes (Tiny Reproductions)
# ------------------------------------
async def fetch_number():
    await asyncio.sleep(0.01)
    return 42


async def mistakes_demo():
    # 10a. Forgetting await: you get a coroutine OBJECT, and nothing runs.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        value = fetch_number()                       # missing `await`
        print("10a. without await you hold:", type(value).__name__, "- not 42")
        del value                                    # never awaited -> warning on cleanup
        gc.collect()
    print("     warning raised:", [str(w.message) for w in caught])
    print("     with await:", await fetch_number())

    # 10b. Blocking the loop: a heartbeat task shows the stall.
    ticks = []
    stop = asyncio.Event()

    async def heartbeat():
        while not stop.is_set():
            ticks.append(1)
            await asyncio.sleep(0.01)

    hb = asyncio.create_task(heartbeat())
    await asyncio.sleep(0.03)                        # let it start ticking

    async def ticks_during(coro_factory):
        before = len(ticks)
        await coro_factory()
        return len(ticks) - before

    async def blocking_sleep():
        time.sleep(0.2)                              # BLOCKS the whole loop
        await asyncio.sleep(0)

    async def polite_sleep():
        await asyncio.sleep(0.2)                     # yields; heartbeat keeps going

    async def threaded_sleep():
        await asyncio.to_thread(time.sleep, 0.2)     # blocking call moved off the loop

    blocked = await ticks_during(blocking_sleep)
    polite_ticks = await ticks_during(polite_sleep)
    threaded = await ticks_during(threaded_sleep)
    print("10b. heartbeat ticks (should be ~20 per 0.2s):")
    print("     time.sleep(0.2)       ->", "stalled (<=2 ticks)" if blocked <= 2 else f"{blocked} ticks?")
    print("     await asyncio.sleep   ->", "healthy (>=10 ticks)" if polite_ticks >= 10 else f"{polite_ticks} ticks?")
    print("     await to_thread(sleep)->", "healthy (>=10 ticks)" if threaded >= 10 else f"{threaded} ticks?")
    stop.set()
    await hb
    # CPU-heavy loops stall the loop exactly the same way: move them to
    # run_in_executor(ProcessPoolExecutor) or a process pool (see 12-...py).

    # 10c. Fire-and-forget create_task without a reference.
    # - The loop keeps only a WEAK reference to tasks. A task that nothing else
    #   references (and that waits on something unreachable) can be garbage
    #   collected mid-flight - the work silently vanishes. Documented fix:
    #   keep a strong reference (a set) and drop it on completion.
    loop = asyncio.get_running_loop()
    destroyed = []
    old_handler = loop.get_exception_handler()
    loop.set_exception_handler(lambda lp, ctx: destroyed.append(ctx.get("message", "")))

    async def waits_forever(fut):
        await fut

    probe = asyncio.create_task(waits_forever(loop.create_future()))   # NO reference kept
    ref = weakref.ref(probe)
    await asyncio.sleep(0)                           # task starts and suspends
    del probe
    gc.collect()
    print("10c. forgotten task was garbage collected:", ref() is None)
    print("     asyncio complained:", destroyed)
    loop.set_exception_handler(old_handler)

    background = set()

    def spawn(coro):
        task = asyncio.create_task(coro)
        background.add(task)                         # strong reference
        task.add_done_callback(background.discard)   # and tidy up when done
        return task

    spawn(fetch_number())
    print("     safe fire-and-forget: tracked while running:", len(background), "task(s)")
    await asyncio.sleep(0.03)
    print("     after it finished the set is empty again:", len(background) == 0)
    # In 3.11+ a TaskGroup is the better home for background tasks.

    # 10d. `await` in a loop is SEQUENTIAL. gather / TaskGroup is concurrent.
    async def nap():
        await asyncio.sleep(0.02)

    t0 = time.perf_counter()
    for _ in range(5):
        await nap()
    sequential = time.perf_counter() - t0
    t0 = time.perf_counter()
    await asyncio.gather(*(nap() for _ in range(5)))
    concurrent = time.perf_counter() - t0
    print(f"10d. 5 naps: sequential is roughly {sequential / concurrent:.0f}x slower than gather (coarse)")


# 11. Async Iterators, Generators, `async with`, Comprehensions
# ------------------------------------
# - async iterator: an object with __aiter__ and an `async def __anext__`
#   that raises StopAsyncIteration. Used with `async for`.
# - async generator: `async def` containing `yield` - the easy way.
# - async context manager: __aenter__/__aexit__, or @asynccontextmanager.
# - async comprehension: `[x async for x in agen()]`, `[await f(x) for x ...]`.
class Countdown:
    def __init__(self, start):
        self.current = start

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current <= 0:
            raise StopAsyncIteration
        await asyncio.sleep(0)
        self.current -= 1
        return self.current + 1


async def pages(log):
    try:
        for page in range(1, 6):
            await asyncio.sleep(0)
            yield page
    finally:
        log.append("generator closed")


@contextlib.asynccontextmanager
async def connection(name, log):
    log.append(f"open {name}")
    try:
        yield f"<{name}>"
    finally:
        await asyncio.sleep(0)                       # async cleanup is allowed
        log.append(f"close {name}")


async def async_iteration_demo():
    print("class-based async iterator:", [n async for n in Countdown(3)])

    lazy_log = []
    async for page in pages(lazy_log):
        if page == 2:
            break                                    # leaves the generator suspended!
    print("break without aclosing -> generator NOT finalised yet:", lazy_log)
    await asyncio.sleep(0)                           # (the loop finalises it eventually)
    log = []
    async with contextlib.aclosing(pages(log)) as stream:    # guarantees cleanup
        async for page in stream:
            if page == 2:
                break
    print("with aclosing(...)    -> cleanup ran right away:", log)

    log = []
    async with connection("db", log) as conn:
        log.append(f"using {conn}")
    print("asynccontextmanager:", log)

    squares = [await asyncio.sleep(0, i * i) for i in range(4)]       # await inside a comprehension
    evens = [n async for n in Countdown(6) if n % 2 == 0]
    print("async comprehensions:", squares, evens, "| anext():", await anext(Countdown(2)))


# 12. Producer / Consumer With Backpressure (Queue(maxsize))
# ------------------------------------
# - A bounded queue is the asyncio way to say "slow down": when it is full,
#   `await q.put()` SUSPENDS the producer until a consumer takes something.
#   Without a bound, a fast producer buffers unlimited data in memory.
# - task_done() once per item + `await q.join()` = "wait until everything put
#   has been fully processed". Then cancel the (infinite) consumers.
#   (3.13 adds Queue.shutdown() as a cleaner stop signal.)
async def pipeline_demo():
    q = asyncio.Queue(maxsize=2)
    results = []
    stats = {"producer_waited": 0, "max_size": 0}

    async def producer(count):
        for i in range(count):
            if q.full():
                stats["producer_waited"] += 1        # about to block: backpressure at work
            await q.put(i)
            stats["max_size"] = max(stats["max_size"], q.qsize())

    async def consumer():
        while True:
            item = await q.get()
            try:
                await asyncio.sleep(0.005)           # slow processing
                results.append(item * item)
            finally:
                q.task_done()                        # even if processing failed

    consumers = [asyncio.create_task(consumer()) for _ in range(2)]
    await producer(10)
    await q.join()                                   # all 10 items processed
    for c in consumers:
        c.cancel()
    await asyncio.gather(*consumers, return_exceptions=True)
    print("results:", sorted(results))
    print("queue never held more than maxsize (2):", stats["max_size"] <= 2)
    print("producer was made to wait (backpressure):", stats["producer_waited"] > 0)


# 13. contextvars - Per-Task Context (not thread-local!)
# ------------------------------------
# - threading.local() is per THREAD; but every asyncio task shares the single
#   loop thread, so thread-locals leak/clobber between tasks.
# - contextvars.ContextVar is per CONTEXT. Each task gets a COPY of the
#   context when created, so `var.set()` inside a task stays inside it.
#   Used for request IDs, user identity, tracing, logging context.
request_id = contextvars.ContextVar("request_id", default="-")


async def contextvars_demo():
    thread_local = threading.local()
    plain_global = {"request": "-"}
    outcomes = {}

    async def handle(name):
        request_id.set(name)                          # private to this task
        thread_local.request = name                   # shared by every task!
        plain_global["request"] = name
        await asyncio.sleep(0.01)                     # other tasks run and set theirs
        outcomes[name] = (request_id.get(), thread_local.request, plain_global["request"])

    await asyncio.gather(handle("r1"), handle("r2"), handle("r3"))
    print("task    contextvar  thread-local  global")
    for name in sorted(outcomes):
        cv, tl, gl = outcomes[name]
        print(f"{name}     {cv:<11} {tl:<13} {gl}")
    print("-> only the contextvar kept each task's own value")
    print("outside the tasks the var is untouched:", request_id.get())

    token = request_id.set("temp")
    request_id.reset(token)                           # restore the previous value
    print("set()/reset(token) restores:", request_id.get())

    async def reads_in_thread():
        return await asyncio.to_thread(request_id.get)

    request_id.set("from-main-task")
    print("to_thread copies the context into the worker thread:", await reads_in_thread())


# 14. Streams - A Localhost Echo Server and Client
# ------------------------------------
# - asyncio.start_server(handler, host, port) accepts connections and runs
#   `handler(reader, writer)` as a task per client. open_connection() is the
#   client side. Port 0 = "pick any free port" - never hard-code ports in
#   demos or tests. Everything stays on 127.0.0.1 (no external network).
# - writer.write() only buffers; `await writer.drain()` applies flow control.
# - Always close: writer.close(); await writer.wait_closed(); and close the
#   server (async with server) - otherwise sockets leak.
async def echo_handle(reader, writer):
    while line := await reader.readline():          # b'' means the client closed
        writer.write(line.upper())
        await writer.drain()
    writer.close()
    await writer.wait_closed()


async def streams_demo():
    server = await asyncio.start_server(echo_handle, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    print("server listening on an ephemeral 127.0.0.1 port:", port > 0)

    async def client(name):
        reader, writer = await asyncio.open_connection("127.0.0.1", port)
        replies = []
        for i in range(2):
            writer.write(f"{name} says hello {i}\n".encode())
            await writer.drain()
            replies.append((await reader.readline()).decode().strip())
        writer.close()
        await writer.wait_closed()
        return replies

    async with server:                               # closes the server on exit
        results = await with_timeout(asyncio.gather(*(client(n) for n in ("alice", "bob", "carol"))), 10)
    for replies in results:
        print("  client got:", replies)
    print("server closed cleanly, sockets left open:", len(server.sockets))


# 15. Async Subprocesses
# ------------------------------------
# - create_subprocess_exec runs a program WITHOUT blocking the loop and
#   lets you read its output as it arrives. communicate() sends stdin, reads
#   stdout/stderr fully, and waits for exit (avoids pipe-buffer deadlocks).
CHILD_PROGRAM = (
    "import sys, time\n"
    "name = sys.argv[1]\n"
    "time.sleep(0.05)\n"
    "print('hello from ' + name)\n"
    "print('warning from ' + name, file=sys.stderr)\n"
    "sys.exit(3 if name == 'child-b' else 0)\n"
)


async def run_child(name):
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-c", CHILD_PROGRAM, name,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    out, err = await proc.communicate()
    return name, proc.returncode, out.decode().strip(), err.decode().strip()


async def subprocess_demo():
    results = await asyncio.gather(run_child("child-a"), run_child("child-b"))
    for name, code, out, err in sorted(results):
        print(f"  {name}: exit={code} stdout={out!r} stderr={err!r}")
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-c", "print(input().upper())",
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    out, _ = await proc.communicate(b"piped through stdin\n")
    print("  feeding stdin:", out.decode().strip())


# 16. Scheduling Callbacks: call_soon / call_later / call_soon_threadsafe
# ------------------------------------
# - Low-level but good to recognise: call_soon(fn) = run on the next loop
#   iteration (FIFO); call_later(delay, fn) = timer; both return a handle with
#   cancel(). call_soon_threadsafe is the ONLY safe way for another thread to
#   poke the loop. Callbacks are plain functions - they cannot `await`.
async def callbacks_demo():
    loop = asyncio.get_running_loop()
    log = []
    loop.call_later(0.03, log.append, "later 0.03")
    cancelled = loop.call_later(0.02, log.append, "later 0.02 (cancelled)")
    loop.call_later(0.01, log.append, "later 0.01")
    loop.call_soon(log.append, "soon 1")
    loop.call_soon(log.append, "soon 2")
    cancelled.cancel()
    log.append("sync code runs first")
    await asyncio.sleep(0.05)
    print("callback order:", log)

    fut = loop.create_future()
    thread = threading.Thread(target=lambda: loop.call_soon_threadsafe(fut.set_result, "set from another thread"))
    thread.start()
    print("call_soon_threadsafe:", await fut)
    thread.join()


# 17. Debug Mode - Catching Slow Callbacks
# ------------------------------------
# - asyncio.run(main(), debug=True) (or PYTHONASYNCIODEBUG=1 / python -X dev)
#   turns on extra checks: logs any callback/step that hogs the loop longer
#   than loop.slow_callback_duration (default 0.1s), shows WHERE a never-
#   awaited coroutine was created, and flags calls from the wrong thread.
#   Keep it for development - it slows everything down.
class ListHandler(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


async def debug_demo(captured_flags):
    loop = asyncio.get_running_loop()
    captured_flags["debug"] = loop.get_debug()
    loop.slow_callback_duration = 0.05               # warn above 50 ms
    time.sleep(0.1)                                  # a blocking call inside a task step
    await asyncio.sleep(0)


# 18. Runner, and The Wider Ecosystem
# ------------------------------------
# - asyncio.Runner (3.11+) keeps ONE loop alive across several run() calls
#   (asyncio.run creates and destroys a loop every time) - handy for tests,
#   REPL tools and when contextvars/loop state must persist.
# - Beyond the stdlib (printed as reference only, not imported):
#     uvloop ... a faster drop-in event loop (Linux/macOS)
#     trio   ... a different async library built on structured concurrency
#     anyio  ... a compatibility layer: write once, run on asyncio OR trio
#     pytest-asyncio / anyio's pytest plugin ... async tests in pytest
async def loop_identity():
    return id(asyncio.get_running_loop())


async def seeded_var():
    request_id.set("set in first run()")


async def read_var():
    return request_id.get()


# 19. Testing Async Code - IsolatedAsyncioTestCase
# ------------------------------------
# - unittest.IsolatedAsyncioTestCase gives every test a fresh event loop and
#   lets test methods (and asyncSetUp/asyncTearDown) be `async def`.
class FakeDb:
    async def get(self, key):
        await asyncio.sleep(0)
        return {"answer": 42}[key]


class FakeDbTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db = FakeDb()

    async def test_reads_value(self):
        self.assertEqual(await self.db.get("answer"), 42)

    async def test_missing_key_raises(self):
        with self.assertRaises(KeyError):
            await self.db.get("nope")

    async def test_timeout_is_reported(self):
        with self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(asyncio.sleep(1), timeout=0.01)


# 20. Worked Example - An Async Crawler Simulation
# ------------------------------------
# - Fake pages, no real network. Combines:
#     * Semaphore            - concurrency limit (max 3 requests in flight)
#     * timeout              - per-request deadline
#     * retries + backoff    - transient failures retried, wait doubles
#     * graceful cancellation- cleanup runs and CancelledError propagates
class Crawler:
    BEHAVIOUR = {
        "/home": "ok", "/about": "ok", "/blog": "ok", "/news": "ok",
        "/flaky": "flaky",        # fails twice, then works
        "/slow": "slow",          # always exceeds the timeout
        "/broken": "broken",      # always fails
    }

    def __init__(self, limit=3, timeout=0.03, retries=3, base_delay=0.004):
        self.sem = asyncio.Semaphore(limit)
        self.timeout = timeout
        self.retries = retries
        self.base_delay = base_delay
        self.attempts = {}
        self.in_flight = 0
        self.max_in_flight = 0
        self.saturated = asyncio.Event()
        self.limit = limit

    async def fake_fetch(self, path):
        kind = self.BEHAVIOUR[path]
        self.attempts[path] = self.attempts.get(path, 0) + 1
        if kind == "slow":
            await asyncio.sleep(1)
        elif kind == "hang":
            await asyncio.sleep(30)
        else:
            await asyncio.sleep(0.005)
        if kind == "broken" or (kind == "flaky" and self.attempts[path] < 3):
            raise ConnectionError(f"{path}: connection reset")
        return f"<html {path}>"

    async def fetch_one(self, path):
        async with self.sem:                                  # concurrency limit
            self.in_flight += 1
            self.max_in_flight = max(self.max_in_flight, self.in_flight)
            if self.in_flight >= self.limit:
                self.saturated.set()
            try:
                for attempt in range(1, self.retries + 1):
                    try:
                        body = await with_timeout(self.fake_fetch(path), self.timeout)
                        return path, "ok", body
                    except (asyncio.TimeoutError, ConnectionError) as exc:
                        if attempt == self.retries:
                            return path, "failed", f"{type(exc).__name__} after {attempt} attempts"
                        await asyncio.sleep(self.base_delay * 2 ** (attempt - 1))   # backoff
            finally:
                self.in_flight -= 1                           # runs on success, failure AND cancel

    async def crawl(self, paths):
        return await asyncio.gather(*(self.fetch_one(p) for p in paths))


async def crawler_demo():
    crawler = Crawler()
    paths = ["/home", "/about", "/blog", "/news", "/flaky", "/slow", "/broken"]
    results = await crawler.crawl(paths)
    for path, status, detail in sorted(results):
        print(f"  {path:<8} {status:<7} {detail}   (attempts: {crawler.attempts[path]})")
    print("max requests in flight was within the limit:", crawler.max_in_flight <= 3)

    # Graceful cancellation: start a crawl of hanging pages, cancel it once the
    # limiter is saturated, and check every in-flight fetch ran its cleanup.
    Crawler.BEHAVIOUR.update({f"/hang{i}": "hang" for i in range(6)})
    crawler = Crawler(timeout=5)
    cleaned = []

    original_fetch = crawler.fake_fetch

    async def tracked_fetch(path):
        try:
            return await original_fetch(path)
        except asyncio.CancelledError:
            cleaned.append(path)                              # close sockets, flush state...
            raise

    crawler.fake_fetch = tracked_fetch
    crawl_task = asyncio.create_task(crawler.crawl([f"/hang{i}" for i in range(6)]))
    await crawler.saturated.wait()                            # 3 fetches are in flight
    crawl_task.cancel()
    try:
        await crawl_task
    except asyncio.CancelledError:
        print("crawl task cancelled:", crawl_task.cancelled())
    await asyncio.sleep(0.01)
    print("in-flight fetches that ran their cleanup:", len(cleaned), "| nothing left running:", crawler.in_flight == 0)
    print("the 3 queued fetches never started:", len(crawler.attempts) == 3)
    pending = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    print("tasks still alive after cancellation:", len(pending))


# 21. Which Concurrency Tool? (decision table)
# ------------------------------------
#   | Situation                                       | Best fit                         |
#   |-------------------------------------------------|----------------------------------|
#   | Thousands of sockets/requests, mostly waiting   | asyncio                          |
#   | A few dozen blocking calls, legacy sync libs    | ThreadPoolExecutor               |
#   | Heavy CPU (parsing, math, image work)           | ProcessPoolExecutor / mp.Pool    |
#   | Async app that must call blocking code          | asyncio.to_thread                |
#   | Async app that must do CPU work                 | run_in_executor(ProcessPool)     |
#   | Need shared mutable state, simple code          | one thread/loop + queues         |
#   | Want 'no data races' without locks              | asyncio (single thread)          |
#   | Strict ordering / latency of each step          | plain sync code                  |
# - asyncio's weakness: it is "all or nothing" - one blocking call or one
#   non-async library can stall everything. Its strength: cheap concurrency
#   and explicit yield points, which make reasoning about state easier.


def main():
    print("# 01. Asyncio Advanced - What This File Adds To 10-Async-Await.py")
    print("# ------------------------------------")
    print("python version:", sys.version.split()[0], "| 3.11+ features available:", PY311)

    header("02. Cooperative Scheduling Made Visible")
    asyncio.run(scheduling_demo())

    header("03. TaskGroup - Structured Concurrency")
    if PY311:
        asyncio.run(taskgroup_demo())
        namespace = {"asyncio": asyncio}
        exec(EXCEPT_STAR_SRC, namespace)                    # `except*` needs 3.11+ syntax
        asyncio.run(namespace["except_star_demo"]())
    else:
        print("TaskGroup / ExceptionGroup / except* need Python 3.11+ - skipped on", sys.version.split()[0])

    header("04. Timeouts: asyncio.timeout() and wait_for()")
    asyncio.run(timeouts_demo())

    header("05. wait vs as_completed vs gather")
    asyncio.run(collection_demo())

    header("06. Semaphore - Bound The Concurrency")
    asyncio.run(semaphore_demo())

    header("07. Event and Condition")
    asyncio.run(event_condition_demo())

    header("08. Cancellation Nuances and shield()")
    asyncio.run(cancellation_demo())

    header("09. Bridging Blocking Code: to_thread vs run_in_executor")
    asyncio.run(thread_bridge_demo())

    header("10. The Classic Mistakes")
    asyncio.run(mistakes_demo())

    header("11. Async Iterators, Generators, async with, Comprehensions")
    asyncio.run(async_iteration_demo())

    header("12. Producer / Consumer With Backpressure")
    asyncio.run(pipeline_demo())

    header("13. contextvars - Per-Task Context")
    asyncio.run(contextvars_demo())

    header("14. Streams - Localhost Echo Server and Client")
    asyncio.run(streams_demo())

    header("15. Async Subprocesses")
    asyncio.run(subprocess_demo())

    header("16. call_soon / call_later / call_soon_threadsafe")
    asyncio.run(callbacks_demo())

    header("17. Debug Mode - Catching Slow Callbacks")
    handler = ListHandler()
    asyncio_logger = logging.getLogger("asyncio")
    old_propagate, old_level = asyncio_logger.propagate, asyncio_logger.level
    asyncio_logger.addHandler(handler)
    asyncio_logger.propagate = False                       # keep stderr quiet
    flags = {}
    try:
        asyncio.run(debug_demo(flags), debug=True)
    finally:
        asyncio_logger.removeHandler(handler)
        asyncio_logger.propagate = old_propagate
        asyncio_logger.setLevel(old_level)
    print("loop.get_debug() inside the run:", flags["debug"])
    slow = [m for m in handler.messages if "took" in m and "seconds" in m]
    print("slow-callback warnings captured:", len(slow), "(message starts with:", repr(slow[0].split(" ")[0] + " <Task ...>") + ")" if slow else "(none)")

    header("18. Runner, and The Wider Ecosystem")
    if hasattr(asyncio, "Runner"):
        with asyncio.Runner() as runner:
            first = runner.run(loop_identity())
            second = runner.run(loop_identity())
            runner.run(seeded_var())
            persisted = runner.run(read_var())
        print("Runner keeps ONE loop across run() calls:", first == second)
        print("context set in one run() is visible in the next:", persisted)
        request_id.set("-")
    else:
        print("asyncio.Runner needs 3.11+ - skipped")
    print("# Ecosystem (not imported here): uvloop = faster event loop, trio = structured-")
    print("# concurrency library, anyio = one API over asyncio+trio, pytest-asyncio = pytest support")

    header("19. Testing Async Code - IsolatedAsyncioTestCase")
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FakeDbTests)
    result = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)
    print("ran", result.testsRun, "async tests | successful:", result.wasSuccessful(), "| failures:", len(result.failures), "| errors:", len(result.errors))

    header("20. Worked Example - An Async Crawler Simulation")
    asyncio.run(crawler_demo())

    header("21. Which Concurrency Tool?")
    print("# - waiting on many I/O ops ...... asyncio")
    print("# - blocking libs, few calls ..... threads (to_thread / ThreadPoolExecutor)")
    print("# - CPU-bound .................... processes (run_in_executor with ProcessPool)")
    print("# - rules of thumb ............... never block the loop; keep task references;")
    print("#                                  re-raise CancelledError; bound concurrency; set timeouts")


if __name__ == "__main__":
    main()
