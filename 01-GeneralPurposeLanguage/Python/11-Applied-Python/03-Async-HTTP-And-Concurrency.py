# 01. The Async Mental Model: Coroutines, Tasks, The Event Loop
# 02. Running Coroutines: asyncio.run, await, create_task
# 03. A Local Server To Talk To (127.0.0.1, Port 0)
# 04. Sequential vs Concurrent: Measured By The Server
# 05. asyncio.gather: Order And Errors
# 06. asyncio.TaskGroup: Structured Concurrency
# 07. Semaphore: Rate Limiting Concurrency
# 08. Timeouts: asyncio.timeout And wait_for
# 09. Retries With Backoff (Async)
# 10. Cancellation
# 11. Async Context Managers
# 12. aiohttp Client
# 13. Completion Order: as_completed
# 14. Blocking Calls: asyncio.to_thread
# 15. ThreadPoolExecutor For Blocking Libraries
# 16. Producer / Consumer With asyncio.Queue
# 17. Async Gotchas
# 18. Clean Shutdown

# LOCAL ONLY: the server is a stdlib ThreadingHTTPServer on 127.0.0.1:0.
# Results are shown through call counts, ordering and the server's own
# "max in flight" counter - never wall-clock timings (those vary per run).

import asyncio
import contextlib
import json
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    import httpx
except ImportError:
    httpx = None

try:
    import aiohttp
except ImportError:
    aiohttp = None

# 01. The Async Mental Model: Coroutines, Tasks, The Event Loop
# ----------------------------
# - async/await gives CONCURRENCY on ONE thread: while one coroutine waits
#   (for the network, a sleep), the event loop runs another.
# - Great for I/O-bound work (many HTTP calls). Useless for CPU-bound work
#   (a busy loop blocks everything) - use processes for that.
# - "async def f()" returns a coroutine object; nothing runs until awaited
#   or wrapped in a Task. A Task = a coroutine scheduled on the loop.
# - await = "pause me here until this finishes, loop may run others."
# - Concurrency is not parallelism: only one line of Python runs at a time.

async def hello():
    return "hi"

coro = hello()
print("calling an async def gives:", type(coro).__name__, "(nothing has run yet)")
print("run it:", asyncio.run(coro))

# 02. Running Coroutines: asyncio.run, await, create_task
# ----------------------------
# - asyncio.run(main()) creates a loop, runs main to completion, closes
#   the loop. Call it ONCE at the top level of your program.
# - await coro        -> run it now, wait for the result (sequential).
# - asyncio.create_task(coro) -> start it in the background, keep going;
#   await the task later to get the result.
# - Gotcha: calling asyncio.run() inside a running loop (e.g. Jupyter,
#   or from async code) raises RuntimeError. There, just use await.

async def step(name, log, delay):
    log.append(f"{name} start")
    await asyncio.sleep(delay)
    log.append(f"{name} end")
    return name


async def demo_basics():
    log = []
    await step("A", log, 0.02)           # sequential: A fully finishes first
    await step("B", log, 0.01)
    print("awaited one by one:", log)
    log = []
    t1 = asyncio.create_task(step("A", log, 0.03))   # both start now
    t2 = asyncio.create_task(step("B", log, 0.01))
    await t1
    await t2
    print("as tasks (overlapping):", log)

asyncio.run(demo_basics())

# 03. A Local Server To Talk To (127.0.0.1, Port 0)
# ----------------------------
# - Port 0 = OS picks a free port; read it back from server_address.
# - The server records: total hits, requests currently in flight, and the
#   MAXIMUM in flight ever seen. That counter proves real concurrency
#   without any timing measurement.
# - Routes: /item/N?delay=S (sleeps S seconds, returns JSON),
#   /flaky?key=K (503 twice, then 200), /status/N.
# - It runs in a daemon thread; handler threads are daemons too.

LOCK = threading.Lock()
STATS = {"hits": 0, "inflight": 0, "max_inflight": 0, "flaky": {}}


def reset_stats():
    with LOCK:
        STATS.update(hits=0, inflight=0, max_inflight=0)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        with LOCK:
            STATS["hits"] += 1
            STATS["inflight"] += 1
            STATS["max_inflight"] = max(STATS["max_inflight"], STATS["inflight"])
        try:
            url = urllib.parse.urlsplit(self.path)
            q = urllib.parse.parse_qs(url.query)
            status, payload = 200, None
            if url.path.startswith("/item/"):
                time.sleep(float(q.get("delay", ["0.1"])[0]))
                payload = {"n": int(url.path.rsplit("/", 1)[1])}
            elif url.path == "/flaky":
                key = q["key"][0]
                with LOCK:
                    STATS["flaky"][key] = STATS["flaky"].get(key, 0) + 1
                    count = STATS["flaky"][key]
                status, payload = (503, {"error": "busy"}) if count <= 2 else (200, {"ok": True, "attempt": count})
            elif url.path.startswith("/status/"):
                status = int(url.path.rsplit("/", 1)[1])
                payload = {"status": status}
            else:
                status, payload = 404, {"error": "not found"}
            body = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        finally:
            with LOCK:
                STATS["inflight"] -= 1


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
server.daemon_threads = True
server.handle_error = lambda *a: None  # clients that time out / cancel reset the socket
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
BASE = f"http://127.0.0.1:{server.server_address[1]}"  # never printed
print("server running in a daemon thread:", thread.is_alive())

URLS = [f"{BASE}/item/{n}?delay=0.1" for n in range(1, 6)]


async def main():
    # 04. Sequential vs Concurrent: Measured By The Server
    # ----------------------------
    # - httpx.AsyncClient is the async twin of httpx.Client. Use it as an
    #   "async with" so connections are closed.
    # - Same 5 requests, two strategies. Total hits are identical; what
    #   differs is how many were IN FLIGHT at once on the server.
    # - Sequential (await in a loop): max in flight = 1.
    # - Concurrent (gather): max in flight > 1. No stopwatch needed.
    # - Reuse ONE client for many requests (connection pool).

    if httpx is None:
        print("SKIP: httpx is not installed (pip install httpx)")
        return
    async with httpx.AsyncClient(trust_env=False, timeout=5.0) as client:
        reset_stats()
        seq = [(await client.get(u)).json()["n"] for u in URLS]
        print("sequential results:", seq, "| hits:", STATS["hits"], "| max in flight:", STATS["max_inflight"])

        reset_stats()
        responses = await asyncio.gather(*(client.get(u) for u in URLS))
        print("concurrent results:", [r.json()["n"] for r in responses], "| hits:", STATS["hits"],
              "| overlapped:", STATS["max_inflight"] > 1)

        # 05. asyncio.gather: Order And Errors
        # ----------------------------
        # - gather(*aws) runs them concurrently and returns results IN THE
        #   ORDER YOU PASSED THEM, not completion order.
        # - If one raises, gather re-raises the first exception right away -
        #   but the OTHER awaitables keep running (they are not cancelled!).
        # - return_exceptions=True puts exceptions in the result list
        #   instead, so one failure does not hide the other results.

        slow_first = [client.get(f"{BASE}/item/1?delay=0.15"), client.get(f"{BASE}/item/2?delay=0.01")]
        res = await asyncio.gather(*slow_first)
        print("gather order = input order:", [r.json()["n"] for r in res])

        async def boom():
            raise ValueError("bad item")

        mixed = await asyncio.gather(client.get(f"{BASE}/status/200"), boom(), return_exceptions=True)
        print("return_exceptions=True ->", [type(m).__name__ for m in mixed])
        try:
            await asyncio.gather(client.get(f"{BASE}/status/200"), boom())
        except ValueError as e:
            print("without it, first error raised:", e)

        # 06. asyncio.TaskGroup: Structured Concurrency
        # ----------------------------
        # - Python 3.11+: "async with asyncio.TaskGroup() as tg:" - all tasks
        #   created via tg.create_task are awaited when the block exits.
        # - If ANY task fails, the rest are cancelled and the failures arrive
        #   together as an ExceptionGroup - catch with "except*".
        # - Safer than bare create_task/gather: no task is left orphaned.
        # - Results: keep the task objects and call .result() after the block.

        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(client.get(u)) for u in URLS[:3]]
        print("TaskGroup results:", [t.result().json()["n"] for t in tasks])

        finished = []

        async def worker(name, delay, fail=False):
            try:
                await asyncio.sleep(delay)
                if fail:
                    raise ValueError(f"{name} failed")
                finished.append(name)
            except asyncio.CancelledError:
                finished.append(f"{name} cancelled")
                raise

        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(worker("fast-ok", 0.01))
                tg.create_task(worker("fails", 0.03, fail=True))
                tg.create_task(worker("slow", 0.5))
        except* ValueError as eg:
            print("ExceptionGroup caught:", [str(e) for e in eg.exceptions])
        print("what finished / got cancelled:", finished)

        # 07. Semaphore: Rate Limiting Concurrency
        # ----------------------------
        # - Launching 1000 requests at once can overwhelm the server (or you:
        #   file descriptors, rate limits). A Semaphore(N) lets at most N
        #   coroutines inside the guarded block.
        # - "async with sem:" acquires and always releases.
        # - Create the semaphore inside the running loop (inside main),
        #   not at import time.
        # - This limits concurrency, not requests-per-second; for a true
        #   rate (e.g. 10/sec) add a sleep or a token bucket.

        sem = asyncio.Semaphore(2)

        async def limited_get(url):
            async with sem:
                return (await client.get(url)).json()["n"]

        reset_stats()
        out = await asyncio.gather(*(limited_get(u) for u in URLS))
        print("results:", out, "| hits:", STATS["hits"], "| never more than 2 in flight:", STATS["max_inflight"] <= 2)

        # 08. Timeouts: asyncio.timeout And wait_for
        # ----------------------------
        # - "async with asyncio.timeout(seconds):" (3.11+) cancels the body
        #   when time runs out and raises TimeoutError. It can cover MANY
        #   awaits as one total deadline.
        # - asyncio.wait_for(coro, timeout) does the same for one awaitable.
        # - The HTTP client has its own timeouts too (httpx.AsyncClient(timeout=)).
        #   Use client timeouts for each call, asyncio.timeout for a whole
        #   operation's deadline.
        # - Catch TimeoutError (builtin since 3.11; asyncio.TimeoutError is an alias).

        try:
            async with asyncio.timeout(0.1):
                await client.get(f"{BASE}/item/1?delay=0.6")
        except TimeoutError:
            print("asyncio.timeout fired -> TimeoutError")
        try:
            await asyncio.wait_for(client.get(f"{BASE}/item/1?delay=0.6"), timeout=0.1)
        except TimeoutError:
            print("wait_for fired -> TimeoutError")
        try:
            await client.get(f"{BASE}/item/1?delay=0.6", timeout=0.1)
        except httpx.TimeoutException as e:
            print("httpx per-request timeout ->", type(e).__name__)

        # 09. Retries With Backoff (Async)
        # ----------------------------
        # - Same idea as sync: retry transient failures (network error, 429,
        #   502, 503, 504) with growing waits, a cap on attempts.
        # - Use "await asyncio.sleep(...)" for the wait. NEVER time.sleep
        #   in async code - it freezes the whole loop.
        # - Add random jitter in production; omitted here for determinism.
        # - Only retry idempotent requests (or use idempotency keys).

        async def get_retry(url, attempts=4, base=0.01):
            for attempt in range(1, attempts + 1):
                try:
                    r = await client.get(url)
                    if r.status_code not in (429, 502, 503, 504):
                        return r, attempt
                except httpx.TransportError:
                    if attempt == attempts:
                        raise
                await asyncio.sleep(base * 2 ** (attempt - 1))
            return r, attempts

        r, tries = await get_retry(f"{BASE}/flaky?key=a")
        print("flaky key a ->", r.status_code, "after", tries, "attempts")
        r, tries = await get_retry(f"{BASE}/flaky?key=b", attempts=2)
        print("flaky key b, only 2 attempts ->", r.status_code, "after", tries)

        # 10. Cancellation
        # ----------------------------
        # - task.cancel() asks the task to stop: a CancelledError is raised at
        #   its current await. The task may clean up in try/finally.
        # - CancelledError derives from BaseException (not Exception), so a
        #   plain "except Exception" does NOT swallow it - good.
        # - Gotcha: if you catch CancelledError, re-raise it unless you really
        #   mean to ignore the cancel; swallowing breaks timeouts/TaskGroups.
        # - Awaiting a cancelled task raises CancelledError for the waiter.

        events = []

        async def cancellable():
            try:
                events.append("started")
                await client.get(f"{BASE}/item/1?delay=0.5")
                events.append("finished (should not happen)")
            except asyncio.CancelledError:
                events.append("cleanup on cancel")
                raise
            finally:
                events.append("finally ran")

        t = asyncio.create_task(cancellable())
        await asyncio.sleep(0.05)     # let it start the request
        t.cancel()
        try:
            await t
        except asyncio.CancelledError:
            events.append("waiter saw CancelledError")
        print("events:", events, "| task.cancelled():", t.cancelled())

        # 11. Async Context Managers
        # ----------------------------
        # - "async with" calls __aenter__/__aexit__ (both awaitable), for
        #   resources whose setup/teardown needs awaiting: connections,
        #   sessions, locks, transactions.
        # - Write your own class with those dunders, or use the decorator
        #   contextlib.asynccontextmanager on an async generator.
        # - Cleanup in finally runs even when the body raises or is cancelled.
        # - Same idea as sync "with" (see 05-Python Advanced).

        class Tracked:
            async def __aenter__(self):
                await asyncio.sleep(0)
                print("  enter (acquire)")
                return self

            async def __aexit__(self, exc_type, exc, tb):
                await asyncio.sleep(0)
                print("  exit (release); error:", exc_type.__name__ if exc_type else None)
                return False  # do not suppress

        @contextlib.asynccontextmanager
        async def counted(label):
            print(f"  {label}: open")
            try:
                yield label.upper()
            finally:
                print(f"  {label}: closed")

        async with Tracked():
            print("  inside class-based block")
        try:
            async with Tracked():
                raise RuntimeError("boom")
        except RuntimeError:
            print("  error propagated after cleanup")
        async with counted("conn") as name:
            print("  using", name)

    # 12. aiohttp Client
    # ----------------------------
    # - aiohttp (pip install aiohttp) is an async-only HTTP client AND
    #   server framework. Often a bit faster than httpx for heavy loads.
    # - Pattern: ONE ClientSession for the program, "async with" it; each
    #   request is also "async with session.get(...) as resp".
    # - Reading the body is an await: await resp.json() / .text().
    # - aiohttp does not raise for 404/500 unless raise_for_status=True.
    # - Timeouts: aiohttp.ClientTimeout(total=...).
    # - Gotcha: a new ClientSession per request defeats connection reuse
    #   and may warn about unclosed sessions.

    if aiohttp is None:
        print("SKIP: aiohttp is not installed (pip install aiohttp)")
    else:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout, trust_env=False) as session:
            async def aget(url):
                async with session.get(url) as resp:
                    return resp.status, await resp.json()

            reset_stats()
            results = await asyncio.gather(*(aget(u) for u in URLS))
            print("aiohttp gather:", [body["n"] for _, body in results], "| overlapped:", STATS["max_inflight"] > 1)
            status, _ = await aget(f"{BASE}/status/404")
            print("404 does not raise by default:", status)
            try:
                async with session.get(f"{BASE}/status/500", raise_for_status=True):
                    pass
            except aiohttp.ClientResponseError as e:
                print("raise_for_status=True ->", e.status)
            try:
                async with session.get(f"{BASE}/item/1?delay=0.6", timeout=aiohttp.ClientTimeout(total=0.1)):
                    pass
            except TimeoutError:
                print("aiohttp timeout -> TimeoutError")

    # 13. Completion Order: as_completed
    # ----------------------------
    # - gather returns in INPUT order. If you want to handle each result
    #   as soon as it is ready, iterate asyncio.as_completed(...).
    # - Results arrive in COMPLETION order - here the shortest sleep first.
    # - Tag your results (return the id with the value) because order no
    #   longer tells you which is which.
    # - Delays differ by 0.05+ seconds so the order is stable.

    async def tagged(n, delay):
        await asyncio.sleep(delay)
        return n

    order = []
    for fut in asyncio.as_completed([tagged("slow", 0.15), tagged("fast", 0.01), tagged("mid", 0.08)]):
        order.append(await fut)
    print("completion order:", order)
    print("gather order    :", await asyncio.gather(tagged("slow", 0.1), tagged("fast", 0.01), tagged("mid", 0.05)))

    # 14. Blocking Calls: asyncio.to_thread
    # ----------------------------
    # - A blocking call (time.sleep, requests.get, urllib, a big file read,
    #   CPU loops) inside a coroutine FREEZES the whole event loop: every
    #   other task stalls until it returns.
    # - asyncio.to_thread(fn, *args) runs fn in a worker thread and gives you
    #   an awaitable - the loop stays free for other coroutines.
    # - Great for wrapping sync-only libraries (requests, many SDKs).
    # - Threads still share the GIL: this helps I/O-bound code, not CPU-bound.

    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def blocking_fetch(n):
        with opener.open(f"{BASE}/item/{n}?delay=0.1", timeout=5) as resp:
            return json.loads(resp.read())["n"]

    ticks = 0
    stop = asyncio.Event()

    async def ticker():
        nonlocal ticks
        while not stop.is_set():
            ticks += 1
            await asyncio.sleep(0.005)

    tick_task = asyncio.create_task(ticker())
    reset_stats()
    res = await asyncio.gather(*(asyncio.to_thread(blocking_fetch, n) for n in range(1, 5)))
    stop.set()
    await tick_task
    print("blocking urllib via to_thread:", res, "| hits:", STATS["hits"],
          "| loop stayed responsive (ticks > 0):", ticks > 0, "| overlapped:", STATS["max_inflight"] > 1)
    print("# Gotcha: calling blocking_fetch(n) directly inside 'async def' would block the loop.")

    # 15. ThreadPoolExecutor For Blocking Libraries
    # ----------------------------
    # - concurrent.futures.ThreadPoolExecutor is the classic, non-async way
    #   to run blocking calls concurrently. No event loop needed at all.
    # - pool.map(fn, items) returns results in input order.
    # - max_workers caps concurrency (like the Semaphore).
    # - From async code: await loop.run_in_executor(pool, fn, arg) - and
    #   to_thread is just shorthand using the default pool.
    # - Always use "with" so threads are joined and the pool is shut down.

    reset_stats()
    with ThreadPoolExecutor(max_workers=3) as pool:
        mapped = list(pool.map(blocking_fetch, range(1, 7)))
    print("pool.map (input order):", mapped, "| hits:", STATS["hits"], "| at most 3 at once:", STATS["max_inflight"] <= 3)
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=2) as pool:
        got = await asyncio.gather(*(loop.run_in_executor(pool, blocking_fetch, n) for n in (7, 8)))
    print("run_in_executor:", got)

    # 16. Producer / Consumer With asyncio.Queue
    # ----------------------------
    # - A Queue decouples "finding work" from "doing work". One producer
    #   puts jobs; N consumers (workers) take and process them.
    # - Number of workers = your concurrency limit (an alternative to a
    #   Semaphore) - and the queue can be bounded: Queue(maxsize=N) makes
    #   put() wait, giving back-pressure so memory does not balloon.
    # - Shutdown pattern: send one sentinel (None) per worker, then await
    #   the workers; or queue.join() with task_done() calls.
    # - Results come in non-deterministic order, so sort before printing.

    queue = asyncio.Queue(maxsize=4)
    results = []
    WORKERS = 3

    async def producer():
        for n in range(1, 9):
            await queue.put(n)           # waits if the queue is full
        for _ in range(WORKERS):
            await queue.put(None)        # one stop signal per worker

    async def consumer(client):
        while True:
            n = await queue.get()
            try:
                if n is None:
                    return
                r = await client.get(f"{BASE}/item/{n}?delay=0.02")
                results.append(r.json()["n"])
            finally:
                queue.task_done()

    if httpx is not None:
        reset_stats()
        async with httpx.AsyncClient(trust_env=False, timeout=5.0) as client:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(producer())
                for _ in range(WORKERS):
                    tg.create_task(consumer(client))
        print("processed (sorted):", sorted(results), "| hits:", STATS["hits"], "| workers cap held:", STATS["max_inflight"] <= WORKERS)

    # 17. Async Gotchas
    # ----------------------------
    # - Forgetting await: "x = client.get(url)" gives a coroutine, not a
    #   response - and Python warns "coroutine ... was never awaited".
    # - Fire-and-forget create_task: the loop keeps only a WEAK reference;
    #   store the task in a set/list or it may be garbage-collected mid-run.
    # - Exceptions inside a task that nobody awaits are only logged late
    #   ("Task exception was never retrieved"). Await tasks or use TaskGroup.
    # - time.sleep / requests / big CPU loops in a coroutine block everyone.
    # - Do not share one asyncio.Queue/Lock/Semaphore across different loops.
    # - Mixing sync and async: a sync function cannot "await"; bridge with
    #   asyncio.run (at the top) or to_thread (async calling sync).
    # - Debug mode: asyncio.run(main(), debug=True) or PYTHONASYNCIODEBUG=1
    #   shows slow callbacks and unawaited coroutines.

    background = set()

    async def fire_and_forget():
        await asyncio.sleep(0.01)
        return "done"

    t = asyncio.create_task(fire_and_forget())
    background.add(t)                       # keep a strong reference
    t.add_done_callback(background.discard)
    print("task result held safely:", await t)
    try:
        print(await asyncio.wait_for(fire_and_forget(), timeout=1))
    except TimeoutError:
        pass
    print("tasks still pending after all awaits:", len([x for x in asyncio.all_tasks() if x is not asyncio.current_task()]))

asyncio.run(main())

# 18. Clean Shutdown
# ----------------------------
# - asyncio.run() already cancels leftover tasks and closes the loop; async
#   clients are closed by their "async with" blocks.
# - The thread-based test server: shutdown() -> server_close() -> join().
# - daemon threads (and daemon_threads=True on the server) make sure a
#   handler still sleeping for a cancelled request cannot delay exit.
# - Stop anything you started; leave no threads, sockets, or files behind.

server.shutdown()
server.server_close()
thread.join(timeout=5)
print("server stopped:", not thread.is_alive())
print("other threads left:", [t.name for t in threading.enumerate() if t is not threading.main_thread() and not t.daemon])
