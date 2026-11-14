import collections
import dis
import queue
import subprocess
import sys
import threading
import time
from concurrent.futures import (
    FIRST_COMPLETED,
    FIRST_EXCEPTION,
    ALL_COMPLETED,
    CancelledError,
    ThreadPoolExecutor,
    as_completed,
    wait,
)

# 01. Threading Primitives - Why This File Exists
# ------------------------------------
# - 09-Multithreading-And-Multiprocessing.py showed Thread, Lock, Queue and
#   ThreadPoolExecutor in their simplest form. This file goes DEEPER: every
#   building block threading gives you, WHY it exists, and the traps.
# - Mental model: threads share ONE memory space. Sharing is what makes
#   threads cheap and convenient - and also what makes them dangerous. Every
#   primitive below is a tool for ONE of three jobs:
#       1. protect shared data          -> Lock, RLock
#       2. coordinate "who goes when"   -> Event, Condition, Barrier
#       3. limit how many do something  -> Semaphore, BoundedSemaphore
# - Every demo below is written to be DETERMINISTIC: we use Events and joins
#   to force the interleaving instead of hoping timing works out.

print("# 01. Threading Primitives - Why This File Exists")
print("# ------------------------------------")
print("python version:", sys.version.split()[0])


# 02. A Race Condition Made Visible
# ------------------------------------
# - `x += 1` LOOKS like one step. It is really THREE: read x, add 1, write x.
#   A thread can be paused between any two of those steps.
# - If thread A reads, then thread B reads+writes, then A writes - B's update
#   is silently overwritten. That is a "lost update" (a race condition).
print("\n# 02. A Race Condition Made Visible")

counter_global = 0


def bump():
    global counter_global
    counter_global += 1


ops = [i.opname for i in dis.get_instructions(bump)
       if i.opname in ("LOAD_GLOBAL", "BINARY_OP", "STORE_GLOBAL")]
print("bytecode steps of `counter += 1` (read, add, write):", ops)

# 2a. The race choreographed by hand so it ALWAYS happens.
shared = {"balance": 100}
a_has_read = threading.Event()
b_is_done = threading.Event()


def slow_depositor():
    seen = shared["balance"]      # step 1: read 100
    a_has_read.set()              # "OK thread B, go now"
    b_is_done.wait()              # ...we get paused here (B runs fully)...
    shared["balance"] = seen + 10  # step 3: write 110, erasing B's +50


def fast_depositor():
    a_has_read.wait()
    shared["balance"] += 50       # read, add, write all happen while A is paused
    b_is_done.set()


ta = threading.Thread(target=slow_depositor)
tb = threading.Thread(target=fast_depositor)
ta.start(); tb.start(); ta.join(); tb.join()
print("started with 100, deposited 10 and 50 -> expected 160, got:", shared["balance"])


# 2b. The same bug in a loop. time.sleep(0) is a "yield point" - it releases
#     the GIL so another thread can run between our read and our write. In
#     real code the yield point is anything: an I/O call, a function call,
#     even the interpreter's own periodic thread switch (sys.getswitchinterval()).
class UnsafeCounter:
    def __init__(self):
        self.n = 0

    def increment(self):
        tmp = self.n          # read
        time.sleep(0)         # forced yield point (simulates "real" work)
        self.n = tmp + 1      # write - may overwrite someone else's update


def hammer(counter, times):
    for _ in range(times):
        counter.increment()


unsafe = UnsafeCounter()
threads = [threading.Thread(target=hammer, args=(unsafe, 200)) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print("4 threads x 200 increments, expected 800 - lost updates happened:", unsafe.n < 800)
print("(the exact number differs every run, which is what makes races so hard to debug)")
print("switch interval (seconds between forced thread switches):", sys.getswitchinterval())
# - Gotcha: without the forced yield, a bare `counter += 1` loses updates only
#   RARELY (the GIL switches every 5ms by default). "It never failed in my
#   tests" proves nothing - races show up under load, on other machines, and
#   in production. Never rely on luck; protect shared mutable state.


# 03. Lock and `with lock`
# ------------------------------------
# - A Lock is a turnstile: only ONE thread can be inside the guarded section.
# - Always use `with lock:` - it releases the lock even if the body raises.
#   Manual acquire()/release() leaks the lock the day an exception appears.
print("\n# 03. Lock and `with lock`")


class SafeCounter:
    def __init__(self):
        self.n = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:          # the read-modify-write is now ONE atomic unit
            tmp = self.n
            time.sleep(0)         # same forced yield - but nobody else can enter
            self.n = tmp + 1


safe = SafeCounter()
threads = [threading.Thread(target=hammer, args=(safe, 200)) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print("with a lock, 4 threads x 200 ->", safe.n)

demo_lock = threading.Lock()
try:
    with demo_lock:
        print("inside with-block, locked() =", demo_lock.locked())
        raise RuntimeError("something broke inside the critical section")
except RuntimeError as exc:
    print("exception propagated:", exc)
print("after the exception, lock was released automatically: locked() =", demo_lock.locked())
# - Keep critical sections SMALL: work done while holding a lock is work
#   every other thread waits for. Do the slow part (I/O, computing) outside,
#   and lock only for the tiny shared-state update.


# 04. acquire(blocking=False) and acquire(timeout=...)
# ------------------------------------
# - By default acquire() waits forever. Two safer alternatives:
#     blocking=False  -> "try once, tell me if you got it"  (returns bool)
#     timeout=secs    -> "wait up to this long"             (returns bool)
# - These are how you DETECT trouble instead of hanging, and how you build
#   "skip this work if someone else is already doing it" logic.
print("\n# 04. acquire(blocking=False) and acquire(timeout=...)")

busy_lock = threading.Lock()
holder_ready = threading.Event()
holder_release = threading.Event()


def lock_holder():
    with busy_lock:
        holder_ready.set()
        holder_release.wait()      # sit on the lock until told to let go


holder = threading.Thread(target=lock_holder)
holder.start()
holder_ready.wait()
print("try without blocking ->", busy_lock.acquire(blocking=False))
print("try with 0.05s timeout ->", busy_lock.acquire(timeout=0.05))
holder_release.set()
holder.join()
print("holder finished; now it works ->", busy_lock.acquire(blocking=False))
busy_lock.release()


# 05. RLock - The Re-entrant Lock
# ------------------------------------
# - A plain Lock does not know WHO holds it. If the same thread tries to
#   acquire it again, it waits for itself - forever. That is a self-deadlock.
# - An RLock remembers the owning thread and a count, so the same thread may
#   acquire it repeatedly (it must release as many times). Other threads
#   still wait.
# - Typical need: a class whose public methods lock, and call each other.
print("\n# 05. RLock - The Re-entrant Lock")

plain = threading.Lock()
plain.acquire()
got_it_again = plain.acquire(timeout=0.05)   # same thread asks again...
print("plain Lock re-acquired by the SAME thread?", got_it_again,
      "(without timeout this would hang forever)")
plain.release()

reentrant = threading.RLock()
reentrant.acquire()
reentrant.acquire()                           # fine: same thread, count is now 2
print("RLock re-acquired by the same thread: OK")
reentrant.release()
reentrant.release()


class Wallet:
    """Public methods lock, and one calls another - needs an RLock."""

    def __init__(self):
        self._lock = threading.RLock()
        self.coins = 0

    def add(self, n):
        with self._lock:
            self.coins += n

    def add_many(self, items):
        with self._lock:                 # outer acquisition
            for n in items:
                self.add(n)              # inner acquisition by the same thread


wallet = Wallet()
workers = [threading.Thread(target=wallet.add_many, args=([1, 2, 3],)) for _ in range(5)]
for t in workers: t.start()
for t in workers: t.join()
print("wallet coins (5 threads x 6):", wallet.coins)
# - Prefer designing so you do not need RLock (a private unlocked helper
#   `_add_unlocked` called by locked public methods is clearer). Reach for
#   RLock when you cannot restructure, e.g. recursion or callbacks.


# 06. Event - Start Gate and Stop Flag
# ------------------------------------
# - An Event is a boolean flag threads can WAIT on. set() flips it to True
#   and wakes every waiter; clear() resets it; wait(timeout) returns the flag.
# - Pattern 1 - START GATE: many threads get ready, then all begin at once.
# - Pattern 2 - STOP FLAG: the clean way to ask a thread to quit. Python has
#   NO safe way to kill a thread from outside, so threads must COOPERATE:
#   they check the flag regularly and return on their own.
print("\n# 06. Event - Start Gate and Stop Flag")

N_WORKERS = 4
go = threading.Event()
stop = threading.Event()
all_parked = threading.Event()
state_lock = threading.Lock()
parked = 0
ticks = collections.Counter()
enough_ticks = threading.Event()


def gated_worker(worker_id):
    global parked
    with state_lock:
        parked += 1
        if parked == N_WORKERS:
            all_parked.set()
    go.wait()                                   # park here until the gate opens
    while not stop.is_set():                    # cooperative shutdown check
        with state_lock:
            ticks[worker_id] += 1
            if len(ticks) == N_WORKERS and min(ticks.values()) >= 3:
                enough_ticks.set()
        stop.wait(0.002)                        # an INTERRUPTIBLE sleep


workers = [threading.Thread(target=gated_worker, args=(i,)) for i in range(N_WORKERS)]
for t in workers: t.start()
all_parked.wait()
print("all workers parked at the gate before it opened:", parked == N_WORKERS)
print("any worker ticked before gate opened:", len(ticks) > 0)
go.set()                                        # the starting gun
enough_ticks.wait()
stop.set()                                      # ask everyone to finish
for t in workers: t.join()
print("every worker ticked at least 3 times:", min(ticks.values()) >= 3)
print("all workers stopped cleanly:", not any(t.is_alive() for t in workers))
print("Event.wait(timeout) on an unset event returns:", threading.Event().wait(0.01))
# - Why `stop.wait(0.002)` instead of `time.sleep(0.002)`? sleep cannot be
#   interrupted - a worker sleeping 60s would take 60s to notice the stop.
#   Event.wait(60) returns the INSTANT stop.set() is called.


# 07. Condition - "Wait Until Something Is True"
# ------------------------------------
# - A Condition = a Lock + a waiting room. A thread that finds the state
#   unsuitable calls wait(): it atomically RELEASES the lock and sleeps.
#   Another thread changes the state and calls notify()/notify_all(), which
#   wakes sleepers; each re-acquires the lock before wait() returns.
# - Rule: ALWAYS re-check the predicate after waking (spurious wake-ups,
#   or someone else got there first). `wait_for(predicate)` does that loop
#   for you - prefer it over a bare wait().
print("\n# 07. Condition - wait / notify / wait_for")

cond = threading.Condition()
inbox = []
received = []


def message_waiter():
    with cond:
        cond.wait_for(lambda: len(inbox) >= 2)   # sleeps until predicate True
        received.extend(inbox)


waiter = threading.Thread(target=message_waiter)
waiter.start()
for msg in ("hello", "world"):
    with cond:                  # must HOLD the lock to change state + notify
        inbox.append(msg)
        cond.notify_all()       # wake everyone; each re-checks the predicate
waiter.join()
print("waiter woke up only when the predicate held:", received)
with cond:
    print("wait_for with timeout on a false predicate returns:",
          cond.wait_for(lambda: False, timeout=0.02))


# 7b. A bounded buffer (producer/consumer) built from a Condition.
#     This is exactly what queue.Queue(maxsize=N) does internally:
#       - producers BLOCK when the buffer is full  (backpressure!)
#       - consumers BLOCK when the buffer is empty
class BoundedBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = collections.deque()
        self.cond = threading.Condition()
        self.closed = False
        self.max_seen = 0

    def put(self, item):
        with self.cond:
            self.cond.wait_for(lambda: len(self.items) < self.capacity)
            self.items.append(item)
            self.max_seen = max(self.max_seen, len(self.items))
            self.cond.notify_all()        # a consumer may be waiting

    def get(self):
        with self.cond:
            self.cond.wait_for(lambda: self.items or self.closed)
            if self.items:
                item = self.items.popleft()
                self.cond.notify_all()    # a producer may be waiting for room
                return item
            return None                   # closed AND empty -> no more items

    def close(self):
        with self.cond:
            self.closed = True
            self.cond.notify_all()


buffer = BoundedBuffer(capacity=3)
consumed = []
consumed_lock = threading.Lock()


def buffer_producer(start):
    for i in range(start, start + 10):
        buffer.put(i)


def buffer_consumer():
    while True:
        item = buffer.get()
        if item is None:
            return
        with consumed_lock:
            consumed.append(item)


producers = [threading.Thread(target=buffer_producer, args=(s,)) for s in (0, 100)]
consumers = [threading.Thread(target=buffer_consumer) for _ in range(3)]
for t in producers + consumers: t.start()
for t in producers: t.join()
buffer.close()                       # tell consumers: no more data is coming
for t in consumers: t.join()
print("items produced:", 20, "| items consumed:", len(consumed))
print("every item consumed exactly once:", sorted(consumed) == list(range(10)) + list(range(100, 110)))
print("buffer never exceeded its capacity of 3:", buffer.max_seen <= 3)
# - With one Condition and notify_all() this is simple and correct. Fancier
#   versions use two Conditions (not_full / not_empty) sharing ONE lock so
#   producers and consumers do not wake each other needlessly.
# - In real code just use queue.Queue(maxsize=N) - this was to show how it works.


# 08. Semaphore vs BoundedSemaphore - Limit Concurrency to N
# ------------------------------------
# - A Semaphore is a counter of "permits". acquire() takes one (waiting if
#   zero are left), release() gives one back. Use it to say "at most N at a
#   time": N database connections, N concurrent downloads, N API calls.
# - BoundedSemaphore additionally raises ValueError if you release MORE than
#   you acquired - it catches a classic bug (double release) that a plain
#   Semaphore would silently turn into extra permits.
print("\n# 08. Semaphore vs BoundedSemaphore")

LIMIT = 3
gate = threading.Semaphore(LIMIT)
in_flight = 0
max_in_flight = 0
flight_lock = threading.Lock()


def limited_job(_):
    global in_flight, max_in_flight
    with gate:                                  # at most LIMIT threads in here
        with flight_lock:
            in_flight += 1
            max_in_flight = max(max_in_flight, in_flight)
        time.sleep(0.01)                        # pretend to use the resource
        with flight_lock:
            in_flight -= 1


threads = [threading.Thread(target=limited_job, args=(i,)) for i in range(12)]
for t in threads: t.start()
for t in threads: t.join()
print(f"12 threads, Semaphore({LIMIT}) -> max ever running at once <= {LIMIT}:", max_in_flight <= LIMIT)
print("at least 1 ran, nobody left inside:", max_in_flight >= 1 and in_flight == 0)

plain_sem = threading.Semaphore(1)
plain_sem.release()                             # bug: released without acquire
print("plain Semaphore silently allowed an extra release (permits now 2)")
bounded = threading.BoundedSemaphore(1)
try:
    bounded.release()                           # same bug, caught
except ValueError as exc:
    print("BoundedSemaphore caught it -> ValueError:", exc)
# - Lock vs Semaphore(1): a Lock must be released by the thread that took
#   it (RLock enforces it); a Semaphore may be released by any thread, which
#   makes it usable as a "signal" but also easier to misuse.


# 09. Barrier - N Threads Rendezvous
# ------------------------------------
# - A Barrier(N) makes threads wait until N of them have arrived, then
#   releases them ALL at once. Perfect for phased algorithms ("everyone
#   finish phase 1 before anyone starts phase 2") and for synchronised starts.
# - wait() returns a unique index 0..N-1; an optional `action` runs once per
#   cycle in one of the threads. If it times out the barrier BREAKS and every
#   waiter gets BrokenBarrierError.
print("\n# 09. Barrier - N Threads Rendezvous")

PARTIES = 4
phase_log = []
arrived = 0
arrived_lock = threading.Lock()
barrier = threading.Barrier(PARTIES, action=lambda: phase_log.append("barrier action ran once"))
seen_after_barrier = []


def phased_worker(_):
    global arrived
    with arrived_lock:
        arrived += 1                  # phase 1 work
    barrier.wait()                    # nobody passes until all 4 got here
    seen_after_barrier.append(arrived)  # phase 2: everyone sees ALL phase-1 work


threads = [threading.Thread(target=phased_worker, args=(i,)) for i in range(PARTIES)]
for t in threads: t.start()
for t in threads: t.join()
print("each thread saw arrived =", sorted(set(seen_after_barrier)), "after the barrier")
print(phase_log)

lonely = threading.Barrier(2)
try:
    lonely.wait(timeout=0.02)         # the partner never shows up
except threading.BrokenBarrierError:
    print("only 1 of 2 arrived -> BrokenBarrierError after timeout; broken =", lonely.broken)


# 10. Timer - Run Something Later
# ------------------------------------
# - threading.Timer(delay, fn) is a Thread that sleeps, then calls fn once.
#   cancel() works only BEFORE it fires. Handy for simple timeouts and
#   debounce; for anything recurring use a loop with Event.wait(interval).
print("\n# 10. Timer")

fired = []
done_event = threading.Event()
timer_a = threading.Timer(0.02, lambda: (fired.append("timer A fired"), done_event.set()))
timer_b = threading.Timer(5.0, lambda: fired.append("timer B fired (never!)"))
timer_a.start(); timer_b.start()
timer_b.cancel()                       # cancelled before its 5 seconds are up
done_event.wait()
timer_a.join(); timer_b.join()
print(fired)
print("a Timer is just a Thread subclass:", isinstance(timer_a, threading.Thread))


# 11. threading.local - Per-Thread State
# ------------------------------------
# - Normal globals are shared by all threads. threading.local() gives each
#   thread its OWN private copy of the attributes you set on it. Use it for
#   per-thread database connections, request IDs, buffers.
# - (asyncio's equivalent is contextvars - see 13-Asyncio-Advanced.py.)
print("\n# 11. threading.local - Per-Thread State")

per_thread = threading.local()
results_by_thread = {}
results_lock = threading.Lock()


def remember_my_name(name):
    per_thread.name = name                     # visible ONLY inside this thread
    per_thread.calls = 0
    for _ in range(3):
        per_thread.calls += 1                  # no lock needed: it is private
    with results_lock:
        results_by_thread[name] = (per_thread.name, per_thread.calls)


threads = [threading.Thread(target=remember_my_name, args=(f"T{i}",)) for i in range(3)]
for t in threads: t.start()
for t in threads: t.join()
print(sorted(results_by_thread.items()))
print("main thread never saw those attributes:", not hasattr(per_thread, "name"))


# 12. Daemon vs Non-Daemon Threads - And What Happens At Exit
# ------------------------------------
# - When the main thread finishes, Python WAITS for every non-daemon thread.
#   Daemon threads are simply abandoned (killed abruptly) at interpreter exit
#   - no finally-blocks, no flushed files. Use daemon only for disposable
#   background work (heartbeats, caches); never for work that must finish.
# - daemon must be set BEFORE start().
# - We prove it by launching a child Python process and reading its output.
print("\n# 12. Daemon vs Non-Daemon Threads")

child_code = """
import threading, time
def daemon_job():
    time.sleep(5)
    print("daemon finished (you will never see this)")
def non_daemon_job():
    time.sleep(0.05)
    print("non-daemon finished AFTER main ended")
threading.Thread(target=daemon_job, daemon=True).start()
threading.Thread(target=non_daemon_job).start()
print("main is ending now")
"""
proc = subprocess.run([sys.executable, "-c", child_code], capture_output=True, text=True, timeout=30)
print("child exit code:", proc.returncode)
print("child output:", proc.stdout.strip().splitlines())

t = threading.Thread(target=lambda: None, daemon=True)
print("daemon flag before start:", t.daemon)
t.start(); t.join()
try:
    t.daemon = False
except RuntimeError as exc:
    print("changing daemon after start -> RuntimeError:", exc)
print("main thread name:", threading.current_thread().name,
      "| is main:", threading.current_thread() is threading.main_thread())
print("threads still alive (just main):", [x.name for x in threading.enumerate()])


# 13. Thread Subclass vs target Function
# ------------------------------------
# - Two styles, same result. Function style (target=) is the default choice.
#   Subclass style helps when the thread has its own state/results - note
#   that join() returns None, so a thread must STORE its result somewhere.
print("\n# 13. Thread Subclass vs target Function")


def square_target(n, out):
    out[n] = n * n


class SquareThread(threading.Thread):
    def __init__(self, n):
        super().__init__(name=f"square-{n}")
        self.n = n
        self.result = None

    def run(self):                       # override run(), call start() - NOT run()
        self.result = self.n * self.n


out = {}
fn_threads = [threading.Thread(target=square_target, args=(n, out)) for n in (2, 3, 4)]
for t in fn_threads: t.start()
for t in fn_threads: t.join()
print("target style  ->", dict(sorted(out.items())))

sub_threads = [SquareThread(n) for n in (2, 3, 4)]
for t in sub_threads: t.start()
for t in sub_threads: t.join()
print("subclass style->", {t.name: t.result for t in sub_threads})
print("Gotcha: calling t.run() directly runs it in the CALLER's thread, no new thread is made")
# - Use Futures (section 15) when you want the return value without storing it
#   by hand - that is what they are for.


# 14. Exceptions Inside Threads Are Lost By Default
# ------------------------------------
# - If a plain Thread's function raises, only THAT thread dies. Python prints
#   a traceback to stderr ("Exception in thread Thread-1 ...") and the main
#   thread carries on as if nothing happened - join() does NOT re-raise.
# - The hook threading.excepthook lets you capture/log/handle those errors.
#   We install one here so no noise reaches stderr, then restore the default.
# - ThreadPoolExecutor does it better: the exception is stored on the Future
#   and re-raised when you call .result().
print("\n# 14. Exceptions Inside Threads")

captured = []
original_hook = threading.excepthook


def collecting_hook(args):
    captured.append((args.thread.name, args.exc_type.__name__, str(args.exc_value)))


def explode():
    raise ValueError("boom inside a thread")


threading.excepthook = collecting_hook
try:
    bad = threading.Thread(target=explode, name="bad-thread")
    bad.start()
    bad.join()                               # returns normally - NO exception here!
finally:
    threading.excepthook = original_hook     # always restore the default
print("main thread kept going; join() raised nothing")
print("hook captured:", captured)

with ThreadPoolExecutor(max_workers=1) as pool:
    fut = pool.submit(explode)
    print("future.exception() ->", repr(fut.exception()))
    try:
        fut.result()
    except ValueError as exc:
        print("future.result() re-raises in the caller:", exc)
# - Real-world: wrap thread bodies in try/except that logs, or use the
#   executor and ALWAYS call result()/exception() - an un-inspected failed
#   Future fails silently too.


# 15. concurrent.futures Deeper
# ------------------------------------
# - A Future is a "promise of a result": done(), running(), cancelled(),
#   result(timeout), exception(), add_done_callback(fn), cancel().
print("\n# 15. concurrent.futures Deeper")

# 15a. as_completed (completion order) vs map (input order)
# - We FORCE completion order 4,3,2,1,0 with a chain of Events: task i
#   cannot finish until task i+1 has. All 5 run at once (5 workers).
finished_events = [threading.Event() for _ in range(6)]
finished_events[5].set()                    # sentinel so task 4 may go first


def staged(i):
    finished_events[i + 1].wait()           # wait for the task "after" me
    finished_events[i].set()
    return i


with ThreadPoolExecutor(max_workers=5) as pool:
    futs = {pool.submit(staged, i): i for i in range(5)}
    order = [futs[f] for f in as_completed(futs)]
print("as_completed yields in FINISH order:", order)

finished_events = [threading.Event() for _ in range(6)]
finished_events[5].set()
with ThreadPoolExecutor(max_workers=5) as pool:
    mapped = list(pool.map(staged, range(5)))
print("map yields in INPUT order:         ", mapped)
# - Use map for "apply f to each, keep order". Use submit+as_completed for
#   "handle each as soon as it is ready" (progress bars, early exit).
# - map() raises the first exception when you reach that item in iteration;
#   with submit you can handle each failure separately.

# 15b. wait(return_when=...)
release = threading.Event()


def quick():
    return "quick"


def slow():
    release.wait()
    return "slow"


with ThreadPoolExecutor(max_workers=3) as pool:
    f_quick = pool.submit(quick)
    f_slow1 = pool.submit(slow)
    f_slow2 = pool.submit(slow)
    done, not_done = wait([f_quick, f_slow1, f_slow2], return_when=FIRST_COMPLETED)
    print("FIRST_COMPLETED -> done:", [f.result() for f in done], "| still pending:", len(not_done))
    release.set()
    done, not_done = wait([f_quick, f_slow1, f_slow2], return_when=ALL_COMPLETED)
    print("ALL_COMPLETED   -> done:", sorted(f.result() for f in done), "| still pending:", len(not_done))

release = threading.Event()
with ThreadPoolExecutor(max_workers=3) as pool:
    f_fail = pool.submit(explode)
    f_wait = pool.submit(slow)
    done, not_done = wait([f_fail, f_wait], return_when=FIRST_EXCEPTION)
    print("FIRST_EXCEPTION -> returned as soon as one failed:",
          [type(f.exception()).__name__ for f in done], "| other still pending:", len(not_done))
    release.set()

# 15c. cancel(): only a Future that has NOT started can be cancelled.
started = threading.Event()
release = threading.Event()


def blocker():
    started.set()
    release.wait()
    return "blocker done"


with ThreadPoolExecutor(max_workers=1) as pool:
    running_f = pool.submit(blocker)
    queued_f = pool.submit(quick)             # waits in the queue (only 1 worker)
    started.wait()
    print("running future: running() =", running_f.running(), "| cancel() ->", running_f.cancel())
    print("queued future : cancel() ->", queued_f.cancel(),
          "| cancelled() =", queued_f.cancelled(), "| done() =", queued_f.done())
    try:
        queued_f.result()
    except CancelledError:
        print("result() of a cancelled future raises CancelledError")
    release.set()
    print("running future finished normally:", running_f.result())

# 15d. add_done_callback: runs in the worker thread when the future finishes
#      - or IMMEDIATELY in the calling thread if it is already done.
callback_log = []
cb_started = threading.Event()
cb_release = threading.Event()


def gated_task():
    cb_started.set()
    cb_release.wait()
    return 21


with ThreadPoolExecutor(max_workers=1, thread_name_prefix="cbpool") as pool:
    pending = pool.submit(gated_task)
    pending.add_done_callback(
        lambda f: callback_log.append((f.result() * 2, threading.current_thread().name.split("_")[0])))
    cb_started.wait()
    cb_release.set()
    pending.result()
    pool.submit(quick).result()               # worker has certainly finished the callback by now
    already_done = pool.submit(quick)
    already_done.result()
    already_done.add_done_callback(
        lambda f: callback_log.append((f.result(), threading.current_thread().name)))
print("callback ran in worker thread, then (for a finished future) in caller:", callback_log)
# - Keep callbacks tiny and non-blocking; an exception inside one is logged
#   and swallowed, never raised to you.

# 15e. initializer: per-worker setup run once in each worker thread.
init_seen = []
worker_state = threading.local()


def init_worker(label):
    worker_state.label = label                # e.g. open a DB connection per thread


def use_worker_state(_):
    return getattr(worker_state, "label", "MISSING")


with ThreadPoolExecutor(max_workers=3, initializer=init_worker, initargs=("ready",)) as pool:
    labels = set(pool.map(use_worker_state, range(9)))
print("every task found initialised per-thread state:", labels)
# - If the initializer raises, the pool becomes "broken" and every pending
#   future fails with BrokenThreadPool - test your initializer.

# 15f. shutdown(wait=, cancel_futures=)
started = threading.Event()
release = threading.Event()
pool = ThreadPoolExecutor(max_workers=1)
f_run = pool.submit(blocker)
f_q = [pool.submit(quick) for _ in range(3)]
started.wait()
pool.shutdown(wait=False, cancel_futures=True)   # returns immediately; drops queued work
print("after shutdown(wait=False, cancel_futures=True): queued cancelled =",
      [f.cancelled() for f in f_q])
release.set()                                    # let the running one finish
print("the already-running future was NOT cancelled:", f_run.result())
pool.shutdown(wait=True)                         # now actually wait for threads to exit
try:
    pool.submit(quick)
except RuntimeError as exc:
    print("submit after shutdown -> RuntimeError:", exc)
# - `with ThreadPoolExecutor()` == shutdown(wait=True) at the end of the block.
#   Python 3.9+: cancel_futures=True is the clean "abort the backlog" switch.


# 16. Deadlock - Detect It, Then Fix It
# ------------------------------------
# - Deadlock = every thread waits for a lock another one holds, so nobody
#   ever moves. The classic recipe: thread 1 takes A then B; thread 2 takes
#   B then A. If each grabs its first lock, both are stuck on the second.
# - We reproduce that EXACTLY (a Barrier guarantees both hold their first
#   lock) but use acquire(timeout=) so we can detect it instead of hanging.
print("\n# 16. Deadlock - Detect It, Then Fix It")

lock_a = threading.Lock()
lock_b = threading.Lock()


def grab_in_order(first, second, label, sync, outcomes):
    with first:
        sync.wait()                                 # both now hold their first lock
        if second.acquire(timeout=0.05):            # would block FOREVER without timeout
            second.release()
            outcomes[label] = "got both"
        else:
            outcomes[label] = "DEADLOCK detected (timed out waiting for 2nd lock)"
        sync.wait()                                 # keep holding until BOTH have given up


outcomes = {}
sync = threading.Barrier(2)
t1 = threading.Thread(target=grab_in_order, args=(lock_a, lock_b, "thread-1 (A then B)", sync, outcomes))
t2 = threading.Thread(target=grab_in_order, args=(lock_b, lock_a, "thread-2 (B then A)", sync, outcomes))
t1.start(); t2.start(); t1.join(); t2.join()
for label in sorted(outcomes):
    print(" ", label, "->", outcomes[label])


# Fix 1: a GLOBAL LOCK ORDER. Everyone takes locks in the same sorted order,
# no matter what order they "think" in. A cycle of waiting becomes impossible.
def locked_pair(x, y):
    first, second = sorted((x, y), key=id)          # any consistent ordering works
    return first, second


def ordered_worker(x, y, label, sync, outcomes):
    first, second = locked_pair(x, y)
    sync.wait()                                      # both start at the same instant
    with first:
        with second:
            outcomes[label] = "got both"


outcomes = {}
sync = threading.Barrier(2)
t1 = threading.Thread(target=ordered_worker, args=(lock_a, lock_b, "thread-1", sync, outcomes))
t2 = threading.Thread(target=ordered_worker, args=(lock_b, lock_a, "thread-2", sync, outcomes))
t1.start(); t2.start(); t1.join(); t2.join()
print("fix 1 (global lock order):", dict(sorted(outcomes.items())))


# Fix 2: TRY-ACQUIRE and BACK OFF. Take the first lock, TRY the second without
# blocking; if you cannot get it, release what you hold and retry later.
def backoff_worker(x, y, label, outcomes):
    attempts = 0
    while True:
        attempts += 1
        with x:
            if y.acquire(blocking=False):
                try:
                    outcomes[label] = "got both"
                finally:
                    y.release()
                return
        time.sleep(0.001 * attempts)                 # back off (real code: add random jitter)


outcomes = {}
t1 = threading.Thread(target=backoff_worker, args=(lock_a, lock_b, "thread-1", outcomes))
t2 = threading.Thread(target=backoff_worker, args=(lock_b, lock_a, "thread-2", outcomes))
t1.start(); t2.start(); t1.join(); t2.join()
print("fix 2 (try-acquire + back off):", dict(sorted(outcomes.items())))

# Related failures (short notes):
# - LIVELOCK: threads are not blocked, they keep reacting to each other and
#   make no progress (two people stepping aside in a corridor forever). Fix 2
#   above can livelock if both back off for the SAME time - add random jitter.
# - STARVATION: a thread never gets its turn because others keep winning the
#   lock/CPU (e.g. a writer starved by endless readers). Fair queues
#   (queue.Queue) and bounded work per turn help.
# - Other deadlock avoiders: hold one lock at a time; never call unknown code
#   (callbacks!) while holding a lock; always use timeouts in production.


# 17. What Is Thread-Safe? (Atomic Under the GIL vs Not)
# ------------------------------------
# - ATOMIC (cannot be interleaved mid-operation in CPython): a single call
#   into C code on one object: list.append, list.pop(), dict[key] = value,
#   dict.setdefault, deque.append/popleft, set.add, queue.Queue methods.
# - NOT atomic: anything made of several steps: x += 1, d[k] += 1,
#   `if k not in d: d[k] = v` (check-then-act), read-modify-write of any kind,
#   and anything spanning two operations on two objects.
# - The GIL is an implementation detail of CPython, not a promise. In the
#   FREE-THREADED build (3.13+ experimental, `python3.13t`) the GIL is gone;
#   built-in containers stay safe per operation via internal locks, but code
#   that "got away with it" thanks to GIL timing will break sooner. Write
#   explicit locking and you are correct on both.
print("\n# 17. What Is Thread-Safe?")

shared_list = []


def append_many(n):
    for i in range(n):
        shared_list.append(i)                   # one atomic C-level call


threads = [threading.Thread(target=append_many, args=(1000,)) for _ in range(8)]
for t in threads: t.start()
for t in threads: t.join()
print("8 threads x 1000 list.append ->", len(shared_list), "(no lost appends)")

gil_enabled = getattr(sys, "_is_gil_enabled", lambda: True)()
print("GIL enabled in this interpreter:", gil_enabled)

# 17b. queue.Queue vs collections.deque
# - deque.append()/popleft() are atomic => a deque is fine as a simple shared
#   buffer when the consumer can poll (raises IndexError when empty).
# - queue.Queue ADDS what a deque lacks: BLOCKING get/put with timeouts,
#   maxsize (backpressure), task_done()/join(). It is a deque + a Condition.
dq = collections.deque()
dq.append("job-1"); dq.append("job-2")
print("deque popleft:", dq.popleft(), "| deque has no blocking get - empty raises:", end=" ")
dq.clear()
try:
    dq.popleft()
except IndexError as exc:
    print("IndexError:", exc)

q = queue.Queue(maxsize=2)
q.put("a"); q.put("b")
try:
    q.put_nowait("c")
except queue.Full:
    print("Queue(maxsize=2).put_nowait on a full queue -> queue.Full (this is backpressure)")
print("get ->", q.get(), "| get ->", q.get())
try:
    q.get(timeout=0.02)
except queue.Empty:
    print("get(timeout=0.02) on empty queue -> queue.Empty")

processed = []


def queue_worker(work):
    while True:
        item = work.get()
        if item is None:
            work.task_done()
            return
        processed.append(item * 2)
        work.task_done()


jobs = queue.Queue()
worker_thread = threading.Thread(target=queue_worker, args=(jobs,))
worker_thread.start()
for n in range(5):
    jobs.put(n)
jobs.join()                       # blocks until EVERY item got task_done()
jobs.put(None)
worker_thread.join()
print("Queue.join() waited for all work:", processed)


# 18. The GIL - When Threads Help and When They Do Not
# ------------------------------------
# - The GIL lets only one thread run Python bytecode at a time. It is
#   RELEASED during blocking I/O (sockets, files, sleep) and by many C
#   extensions, so I/O-bound work overlaps well. CPU-bound pure Python
#   does NOT speed up with threads - it can even get a bit slower.
# - Rule of thumb:  I/O-bound -> threads (or asyncio).
#                   CPU-bound -> processes (see 12-Multiprocessing-...py).
# - Timings below are printed COARSELY and are never asserted on - they
#   depend on your machine (and a free-threaded build changes the CPU row).
print("\n# 18. The GIL - When Threads Help and When They Do Not")


def io_task(_):
    time.sleep(0.05)                       # stands in for a network/disk wait


def cpu_task(_):
    total = 0
    for i in range(150_000):
        total += i * i
    return total


def run_serial(fn, n):
    t0 = time.perf_counter()
    for i in range(n):
        fn(i)
    return time.perf_counter() - t0


def run_threaded(fn, n):
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=n) as pool:
        list(pool.map(fn, range(n)))
    return time.perf_counter() - t0


io_ratio = run_serial(io_task, 8) / run_threaded(io_task, 8)
cpu_ratio = run_serial(cpu_task, 4) / run_threaded(cpu_task, 4)
print(f"I/O-bound, 8 sleeps : threads are roughly {io_ratio:.0f}x faster -> big win")
verdict = "no real speedup (GIL)" if cpu_ratio < 1.5 else "speedup (free-threaded build?)"
print(f"CPU-bound, 4 loops  : threads vs serial is roughly {cpu_ratio:.1f}x -> {verdict}")


# 19. Worked Example - Thread-Pool URL Fetcher
# ------------------------------------
# - Simulates fetching many URLs with fake I/O (sleep). Combines:
#     * ThreadPoolExecutor        - run fetches concurrently
#     * Semaphore                 - rate limit: at most 3 in flight
#     * Event                     - graceful shutdown ("stop picking up work")
#     * Futures                   - collect results AND failures per URL
print("\n# 19. Worked Example - Thread-Pool URL Fetcher")


class Fetcher:
    def __init__(self, max_in_flight=3, stop_after=None):
        self.limit = threading.Semaphore(max_in_flight)
        self.stop = threading.Event()
        self.stop_after = stop_after
        self.lock = threading.Lock()
        self.in_flight = 0
        self.max_seen = 0
        self.completed = 0

    def fetch(self, url):
        if self.stop.is_set():
            return (url, "skipped (shutdown requested)")
        with self.limit:                                   # rate limit
            if self.stop.is_set():                         # re-check after waiting
                return (url, "skipped (shutdown requested)")
            with self.lock:
                self.in_flight += 1
                self.max_seen = max(self.max_seen, self.in_flight)
            try:
                time.sleep(0.01)                           # fake network round-trip
                if url.endswith("/broken"):
                    raise ConnectionError(f"cannot reach {url}")
                body = f"<html for {url}>"
            finally:
                with self.lock:
                    self.in_flight -= 1
            with self.lock:
                self.completed += 1
                if self.stop_after and self.completed >= self.stop_after:
                    self.stop.set()                        # graceful shutdown trigger
            return (url, body)


# 19a. Normal run: all URLs, one of which fails.
urls = [f"https://example.test/page{i}" for i in range(9)] + ["https://example.test/broken"]
fetcher = Fetcher(max_in_flight=3)
ok, failed = [], []
with ThreadPoolExecutor(max_workers=8) as pool:
    future_to_url = {pool.submit(fetcher.fetch, u): u for u in urls}
    for fut in as_completed(future_to_url):
        try:
            ok.append(fut.result()[0])
        except ConnectionError as exc:
            failed.append(str(exc))
print("fetched OK:", len(ok), "| failed:", failed)
print("sorted OK urls (first 3):", sorted(ok)[:3])
print("never more than 3 in flight (8 workers, semaphore of 3):", fetcher.max_seen <= 3)

# 19b. Graceful shutdown: stop handing out new work after 4 completions.
urls = [f"https://example.test/page{i}" for i in range(30)]
fetcher = Fetcher(max_in_flight=3, stop_after=4)
with ThreadPoolExecutor(max_workers=8) as pool:
    outcomes = list(pool.map(fetcher.fetch, urls))
skipped = [u for u, body in outcomes if body.startswith("skipped")]
fetched = [u for u, body in outcomes if not body.startswith("skipped")]
print("shutdown requested after 4 completions -> fetched >= 4:", len(fetched) >= 4)
print("some URLs were skipped instead of fetched:", len(skipped) > 0)
print("every URL accounted for (fetched + skipped == 30):", len(fetched) + len(skipped) == 30)
print("still within the rate limit:", fetcher.max_seen <= 3)
print("no threads left running:", threading.active_count() == 1)


# 20. Summary - Which Primitive For Which Job
# ------------------------------------
print("\n# 20. Summary - Which Primitive For Which Job")
print("# - Protect shared data .......... Lock (RLock if the same thread re-enters)")
print("# - 'Go!' / 'stop!' signals ...... Event")
print("# - Wait for a state change ...... Condition (or just queue.Queue)")
print("# - At most N at once ............ Semaphore / BoundedSemaphore")
print("# - N threads meet up ............ Barrier")
print("# - Hand over work/results ....... queue.Queue (best default)")
print("# - Run func, get result back .... ThreadPoolExecutor + Future")
print("# - Hang prevention .............. acquire(timeout=), Future.result(timeout=)")
