import asyncio
import time

# 01. Async/Await - Introduction
# ------------------------------------
# - asyncio enables single-threaded concurrency using coroutines.
# - Great for I/O-bound tasks (network calls, file I/O) that spend time
#   waiting - while one task waits, another can run.
# - `async def` defines a coroutine function; `await` pauses it until the
#   awaited operation completes, letting other coroutines run meanwhile.

print("# 01. Async/Await - Introduction")
print("# ------------------------------------")

# 02. Defining and Running a Coroutine
# ------------------------------------
async def say_hello():
    print("Hello")
    await asyncio.sleep(1)  # non-blocking sleep - yields control
    print("World")

print("\n# 02. Defining and Running a Coroutine")
asyncio.run(say_hello())

# 03. Running Coroutines Sequentially (no concurrency gain)
# ------------------------------------
async def task(name, delay):
    print(f"{name} started")
    await asyncio.sleep(delay)
    print(f"{name} finished")
    return f"{name} result"

async def sequential_demo():
    start = time.perf_counter()
    await task("Task A", 1)
    await task("Task B", 1)
    print(f"Sequential total time: {time.perf_counter() - start:.2f}s")

print("\n# 03. Running Coroutines Sequentially")
asyncio.run(sequential_demo())

# 04. Running Coroutines Concurrently with asyncio.gather()
# ------------------------------------
async def concurrent_demo():
    start = time.perf_counter()
    results = await asyncio.gather(task("Task A", 1), task("Task B", 1))
    print(f"Concurrent total time: {time.perf_counter() - start:.2f}s")
    print("results:", results)

print("\n# 04. Running Coroutines Concurrently (asyncio.gather)")
asyncio.run(concurrent_demo())

# 05. Creating Tasks with asyncio.create_task()
# ------------------------------------
# - create_task() schedules a coroutine to run in the background immediately,
#   without waiting for it - useful for "fire it now, await result later".
async def create_task_demo():
    t1 = asyncio.create_task(task("Task A", 1))
    t2 = asyncio.create_task(task("Task B", 1))
    print("both tasks scheduled, doing other work...")
    result_a = await t1
    result_b = await t2
    print(result_a, result_b)

print("\n# 05. Creating Tasks with asyncio.create_task()")
asyncio.run(create_task_demo())

# 06. Handling Timeouts
# ------------------------------------
async def slow_task():
    await asyncio.sleep(2)
    return "done"

async def timeout_demo():
    try:
        result = await asyncio.wait_for(slow_task(), timeout=1)
        print(result)
    except asyncio.TimeoutError:
        print("Task timed out!")

print("\n# 06. Handling Timeouts")
asyncio.run(timeout_demo())

# 07. async for and Async Generators
# ------------------------------------
async def async_counter(limit):
    for i in range(limit):
        await asyncio.sleep(0.1)
        yield i

async def async_for_demo():
    async for number in async_counter(3):
        print("async generator yielded:", number)

print("\n# 07. async for and Async Generators")
asyncio.run(async_for_demo())

# 08. When to Use asyncio vs Threading vs Multiprocessing
# ------------------------------------
print("\n# 08. When to Use asyncio vs Threading vs Multiprocessing")
print("# - asyncio: many I/O-bound tasks, single-threaded, no shared-state race conditions")
print("# - threading: I/O-bound, simpler mental model, but GIL limits CPU parallelism")
print("# - multiprocessing: CPU-bound, true parallelism across cores")

# 09. Async Context Managers (__aenter__ / __aexit__, async with)
# ------------------------------------
# - The async equivalent of __enter__/__exit__ (see 06-Context-Managers.py
#   for the sync version). Both methods are coroutines, so setup/teardown
#   can themselves await other async operations (e.g. an async DB connection).
class AsyncResource:
    async def __aenter__(self):
        print("async acquiring resource...")
        await asyncio.sleep(0.1)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        print("async releasing resource...")
        await asyncio.sleep(0.1)
        return False

async def async_context_manager_demo():
    async with AsyncResource() as res:
        print("using async resource:", res)

print("\n# 09. Async Context Managers")
asyncio.run(async_context_manager_demo())

# 10. asyncio.Queue - Producer/Consumer Coroutines
# ------------------------------------
# - The async equivalent of queue.Queue (see 09-Multithreading file) - lets
#   coroutines hand off work without blocking the event loop.
async def async_producer(async_queue):
    for item in range(5):
        await async_queue.put(item)
        await asyncio.sleep(0.05)
    await async_queue.put(None)  # sentinel

async def async_consumer(async_queue, results):
    while True:
        item = await async_queue.get()
        if item is None:
            break
        results.append(item * 10)

async def async_queue_demo():
    async_queue = asyncio.Queue()
    results = []
    await asyncio.gather(async_producer(async_queue), async_consumer(async_queue, results))
    print("consumer collected:", results)

print("\n# 10. asyncio.Queue Producer/Consumer")
asyncio.run(async_queue_demo())

# 11. asyncio.Lock - Protecting Shared State Between Coroutines
# ------------------------------------
# - Even though asyncio is single-threaded, an `await` inside a critical
#   section can let another coroutine interleave and corrupt shared state.
#   asyncio.Lock prevents that, same idea as threading.Lock.
shared_balance = 0

async def unsafe_deposit(amount):
    global shared_balance
    current = shared_balance
    await asyncio.sleep(0)  # simulate an await point mid-operation
    shared_balance = current + amount  # another coroutine may have run here too

async def safe_deposit(amount, lock):
    global shared_balance
    async with lock:
        current = shared_balance
        await asyncio.sleep(0)
        shared_balance = current + amount

async def asyncio_lock_demo():
    global shared_balance
    shared_balance = 0
    await asyncio.gather(*(unsafe_deposit(10) for _ in range(5)))
    print("unsafe result (may be less than 50 due to lost updates):", shared_balance)

    shared_balance = 0
    lock = asyncio.Lock()
    await asyncio.gather(*(safe_deposit(10, lock) for _ in range(5)))
    print("safe result (always 50, protected by asyncio.Lock):", shared_balance)

print("\n# 11. asyncio.Lock for Shared State")
asyncio.run(asyncio_lock_demo())

# 12. Cancellation - task.cancel() and asyncio.CancelledError
# ------------------------------------
# - A running task can be cancelled from outside; the cancelled coroutine
#   receives asyncio.CancelledError at its current await point, and should
#   generally let it propagate after any cleanup (not swallow it silently).
async def cancellable_task():
    try:
        print("cancellable task started, working...")
        await asyncio.sleep(5)
        print("this line never runs if cancelled first")
    except asyncio.CancelledError:
        print("cancellable task caught CancelledError, cleaning up")
        raise  # re-raise so the cancellation still registers properly

async def cancellation_demo():
    t = asyncio.create_task(cancellable_task())
    await asyncio.sleep(0.2)  # let it start
    t.cancel()
    try:
        await t
    except asyncio.CancelledError:
        print("caller sees the task was cancelled")

print("\n# 12. Cancellation with task.cancel()")
asyncio.run(cancellation_demo())

# 13. Bridging Sync and Async - loop.run_in_executor()
# ------------------------------------
# - Blocking, CPU-bound, or legacy synchronous code would freeze the whole
#   event loop if awaited directly. run_in_executor() runs it in a thread
#   pool (default) instead, so the event loop keeps servicing other
#   coroutines while the blocking call runs in the background.
def blocking_sync_function(seconds):
    time.sleep(seconds)  # a real blocking call - NOT awaitable on its own
    return f"blocking work finished after {seconds}s"

async def run_in_executor_demo():
    loop = asyncio.get_running_loop()
    print("dispatching blocking work to a thread pool executor...")
    result = await loop.run_in_executor(None, blocking_sync_function, 0.3)
    print(result)

print("\n# 13. Bridging Sync and Async with run_in_executor")
asyncio.run(run_in_executor_demo())
