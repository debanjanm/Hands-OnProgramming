import heapq
import itertools
import bisect
import array
import queue
import sys
import tempfile
import threading
import os
from collections import deque

# 01. heapq, bisect, array, queue - Introduction
# ------------------------------------
# - These four modules are "small data-structure toolkits" in the stdlib:
#   * heapq  : always get the SMALLEST item fast (priority queue, top-K).
#   * bisect : keep a list sorted and binary-search it.
#   * array  : compact typed arrays (numbers only) that use far less memory.
#   * queue  : thread-safe queues for passing work between threads.
# - WHY care? Picking the right structure turns an O(n) or O(n log n) step
#   into O(log n) or O(1). That is the difference between "instant" and
#   "freezes at a million items".

print("# 01. heapq, bisect, array, queue - Introduction")
print("# ------------------------------------")

# ====================================================================
# PART A - heapq
# ====================================================================

# 02. heapq Basics - A Min-Heap Living Inside a Plain List
# ------------------------------------
# - A heap is a list arranged so that heap[0] is ALWAYS the smallest item.
# - It is NOT fully sorted - only the "parent <= children" rule holds. That
#   weaker promise is exactly why push/pop cost only O(log n).
# - heappush: O(log n)   heappop: O(log n)   peek heap[0]: O(1)
print("\n# 02. heapq Basics")
heap = []
for n in [7, 2, 9, 1, 5]:
    heapq.heappush(heap, n)
print("heap list (NOT sorted):", heap)
print("smallest (peek, O(1)):", heap[0])
print("pop order:", [heapq.heappop(heap) for _ in range(len(heap))])

# 03. heapify - Turn an Existing List Into a Heap In-Place
# ------------------------------------
# - heapify is O(n) - cheaper than pushing n items one by one (O(n log n)).
print("\n# 03. heapify")
data = [9, 4, 7, 1, 8, 2]
heapq.heapify(data)
print("after heapify:", data, "-> data[0] =", data[0])

# 04. heappushpop vs heapreplace
# ------------------------------------
# - heappushpop(h, x): push x THEN pop smallest (faster than two calls).
#   If x is already the smallest, it is returned immediately.
# - heapreplace(h, x): pop smallest FIRST, then push x.
#   The popped value can be bigger than x - that is the difference!
print("\n# 04. heappushpop vs heapreplace")
h1 = [3, 5, 8]
heapq.heapify(h1)
print("heappushpop(h, 1) returns:", heapq.heappushpop(h1, 1), "| heap:", h1)
h2 = [3, 5, 8]
heapq.heapify(h2)
print("heapreplace(h, 1) returns:", heapq.heapreplace(h2, 1), "| heap:", h2)
print("# heapreplace popped 3 even though 1 < 3, then pushed 1.")

# 05. nlargest / nsmallest - Top-K Without Sorting Everything
# ------------------------------------
# - Both accept key=, just like sorted().
# - Rule of thumb: k == 1 -> min()/max();  k small -> nlargest/nsmallest;
#   k close to n -> sorted(...)[:k].
print("\n# 05. nlargest / nsmallest with key")
products = [
    {"name": "pen", "price": 5},
    {"name": "laptop", "price": 900},
    {"name": "phone", "price": 600},
    {"name": "desk", "price": 250},
    {"name": "mug", "price": 8},
]
print("3 cheapest:", [p["name"] for p in heapq.nsmallest(3, products, key=lambda p: p["price"])])
print("2 priciest:", [p["name"] for p in heapq.nlargest(2, products, key=lambda p: p["price"])])
print("3 largest numbers:", heapq.nlargest(3, [4, 99, 12, 7, 56]))

# 06. Max-Heap by Negating Values
# ------------------------------------
# - heapq is ONLY a min-heap. For "largest first", store negated numbers.
# - Remember to negate again when you read the value back.
print("\n# 06. Max-Heap by Negating")
max_heap = []
for score in [40, 95, 70, 88]:
    heapq.heappush(max_heap, -score)
print("largest first:", [-heapq.heappop(max_heap) for _ in range(len(max_heap))])

# 07. heapq.merge - Combine Already-Sorted Streams Lazily
# ------------------------------------
# - merge() does NOT sort; it assumes every input is already sorted.
# - It is lazy (returns an iterator) so it works for files/streams too big
#   for memory - the classic "external merge sort" building block.
print("\n# 07. heapq.merge")
log_a = [1, 4, 9]
log_b = [2, 3, 10]
log_c = [5, 6, 7]
merged = heapq.merge(log_a, log_b, log_c)
print("type:", type(merged).__name__)
print("merged:", list(merged))

# 08. Priority Queue Done Right: (priority, counter, item)
# ------------------------------------
# - Problem 1: if two priorities tie, Python compares the NEXT tuple field.
#   If that is a dict/custom object, you get TypeError.
# - Problem 2: even when it does not crash, ties come out in arbitrary order.
# - Fix: add an increasing counter as the middle field. It is unique, so the
#   comparison never reaches the item, and ties stay FIFO (stable).
print("\n# 08. Priority queue - the tie-break problem")
bad = []
heapq.heappush(bad, (1, {"task": "email"}))
try:
    heapq.heappush(bad, (1, {"task": "report"}))  # same priority -> compares dicts
except TypeError as e:
    print("TypeError without counter:", e)

counter = itertools.count()
pq = []
for prio, task in [(2, "write docs"), (1, "fix bug"), (2, "reply email"), (1, "deploy")]:
    heapq.heappush(pq, (prio, next(counter), {"task": task}))
print("order with counter (FIFO inside same priority):")
while pq:
    prio, _, item = heapq.heappop(pq)
    print("  priority", prio, "->", item["task"])

# 09. Lazy Deletion - Removing Items From the Middle of a Heap
# ------------------------------------
# - Removing an arbitrary item from a heap is O(n). Cheat: do not remove it.
#   Mark it as removed and skip it when it reaches the top.
# - Standard trick for "change priority" too: mark the old entry dead, push
#   a new entry. (This is the recipe in the official heapq docs.)
print("\n# 09. Lazy deletion")
REMOVED = "<removed>"
entries = {}  # task -> the list [priority, count, task] sitting inside the heap
lazy_heap = []
cnt = itertools.count()


def add_task(task, priority):
    if task in entries:
        remove_task(task)
    entry = [priority, next(cnt), task]
    entries[task] = entry
    heapq.heappush(lazy_heap, entry)


def remove_task(task):
    entry = entries.pop(task)
    entry[2] = REMOVED  # just mark - no O(n) search


def pop_task():
    while lazy_heap:
        priority, _, task = heapq.heappop(lazy_heap)
        if task is not REMOVED:
            del entries[task]
            return task
    raise KeyError("pop from an empty priority queue")


add_task("backup", 5)
add_task("email", 3)
add_task("deploy", 1)
add_task("backup", 0)  # re-prioritise: old entry marked dead, new one pushed
remove_task("email")  # cancelled
print("pop order:", [pop_task() for _ in range(2)])

# 10. Top-K From a Stream - Memory Stays at K
# ------------------------------------
# - Imagine a log with 10 million scores. You only want the best 3.
# - Keep a MIN-heap of size 3. For each new value: if it beats the smallest
#   of your current best, replace it. Memory: O(k), time: O(n log k).
print("\n# 10. Top-K streaming")


def top_k_stream(numbers, k):
    best = []
    for x in numbers:
        if len(best) < k:
            heapq.heappush(best, x)
        elif x > best[0]:
            heapq.heapreplace(best, x)  # drop the current smallest of the best
    return sorted(best, reverse=True)


def fake_stream():  # a generator: we never hold all values in memory
    value = 17
    for _ in range(1000):
        value = (value * 31 + 7) % 1009  # deterministic pseudo-random numbers
        yield value


print("top 3 of 1000 streamed values:", top_k_stream(fake_stream(), 3))

# 11. Dijkstra-lite: Shortest Path With a Heap
# ------------------------------------
# - Dijkstra always expands the CLOSEST unvisited node next - exactly what
#   a min-heap gives for free.
print("\n# 11. Dijkstra-lite (shortest distance in a small graph)")
graph = {
    "A": {"B": 4, "C": 1},
    "B": {"D": 1},
    "C": {"B": 2, "D": 5},
    "D": {},
}


def dijkstra(graph, start):
    dist = {start: 0}
    pq = [(0, start)]  # (distance so far, node) - node names are strings, comparable
    while pq:
        d, node = heapq.heappop(pq)
        if d > dist.get(node, float("inf")):
            continue  # stale entry (lazy deletion again!)
        for neighbour, weight in graph[node].items():
            nd = d + weight
            if nd < dist.get(neighbour, float("inf")):
                dist[neighbour] = nd
                heapq.heappush(pq, (nd, neighbour))
    return dist


print("distances from A:", dijkstra(graph, "A"))

# 12. Task Scheduler Example - Run Jobs by Due Time
# ------------------------------------
print("\n# 12. Task scheduler (by due time)")
jobs = []
for due, name in [(30, "send-report"), (10, "refresh-cache"), (20, "clean-temp")]:
    heapq.heappush(jobs, (due, name))
clock = 0
while jobs:
    due, name = heapq.heappop(jobs)
    clock = due  # pretend time jumps to the next due job
    print(f"t={clock:>3}s running {name}")

# ====================================================================
# PART B - bisect
# ====================================================================

# 13. bisect_left vs bisect_right
# ------------------------------------
# - Both do binary search (O(log n)) on an ALREADY SORTED list.
# - They return an INDEX where the value would be inserted to keep order.
# - bisect_left  -> insert BEFORE existing equal values.
# - bisect_right -> insert AFTER existing equal values (bisect = bisect_right).
print("\n# 13. bisect_left vs bisect_right")
nums = [10, 20, 20, 20, 30]
print("bisect_left(20): ", bisect.bisect_left(nums, 20), "(first 20)")
print("bisect_right(20):", bisect.bisect_right(nums, 20), "(just after last 20)")
print("count of 20s:", bisect.bisect_right(nums, 20) - bisect.bisect_left(nums, 20))
print("bisect_left(25): ", bisect.bisect_left(nums, 25), "(same as right when absent)")

# 14. insort - Insert While Keeping the List Sorted
# ------------------------------------
# - GOTCHA: finding the spot is O(log n), but list.insert shifts items,
#   so insort overall is still O(n). Fine for thousands, bad for millions
#   of insertions - then use a heap or a tree-based library instead.
print("\n# 14. insort")
sorted_list = [1, 3, 5, 7]
bisect.insort(sorted_list, 4)
bisect.insort(sorted_list, 3)  # insort_right: goes after existing 3
print("after insort:", sorted_list)

# 15. Binary Search Membership Test
# ------------------------------------
# - "x in list" is O(n). On a sorted list, bisect makes it O(log n).
print("\n# 15. Binary search membership")


def contains(sorted_seq, x):
    i = bisect.bisect_left(sorted_seq, x)
    return i < len(sorted_seq) and sorted_seq[i] == x


big = list(range(0, 1_000_000, 2))  # even numbers
print("contains 500000:", contains(big, 500000))
print("contains 500001:", contains(big, 500001))

# 16. Grade-Bucket Lookup (the classic real-world use)
# ------------------------------------
# - Map a number to a bucket using sorted boundaries - no long if/elif chain.
print("\n# 16. Grade buckets")
breakpoints = [60, 70, 80, 90]
letters = "FDCBA"


def grade(score):
    return letters[bisect.bisect_right(breakpoints, score)]


print([(s, grade(s)) for s in [33, 60, 65, 70, 89, 90, 100]])
print("# bisect_right makes 90 -> 'A' (boundary belongs to the higher bucket).")

# 17. key= Parameter (Python 3.10+)
# ------------------------------------
# - Lets you search a list of records by one field without building a
#   separate list of keys.
print("\n# 17. bisect with key= (3.10+)")
if sys.version_info >= (3, 10):
    people = [("asha", 21), ("ravi", 30), ("meera", 45)]  # sorted by age
    pos = bisect.bisect_left(people, 30, key=lambda p: p[1])
    print("first person aged >= 30 at index", pos, "->", people[pos])
    bisect.insort(people, ("kabir", 35), key=lambda p: p[1])
    print("after insort by age:", people)
else:
    print("SKIPPED: bisect key= needs Python 3.10+")

# ====================================================================
# PART C - array
# ====================================================================

# 18. array - Typed, Compact Number Arrays
# ------------------------------------
# - A list stores pointers to full Python objects (each int ~28 bytes).
# - array.array stores raw machine numbers side by side (like a C array).
# - Trade-off: ONE type only, numbers only, no fancy numpy maths.
# - Typecodes: 'b' signed char(1B)  'B' unsigned char(1B)  'h' short(2B)
#   'i' int(2-4B)  'l' long  'q' long long(8B)  'f' float(4B)  'd' double(8B)
print("\n# 18. array typecodes")
a = array.array("i", [1, 2, 3, 4])
print(a, "| typecode:", a.typecode, "| itemsize (bytes):", a.itemsize)
a.append(5)
a.extend([6, 7])
print("after append/extend:", a, "| a[2] =", a[2], "| slice:", a[1:3])
try:
    a.append(3.5)  # wrong type
except TypeError as e:
    print("TypeError:", e)
try:
    array.array("B", [300])  # 'B' holds 0..255 only
except OverflowError as e:
    print("OverflowError:", e)

# 19. Memory: list vs array
# ------------------------------------
print("\n# 19. Memory comparison (1000 ints)")
as_list = list(range(1000))
as_array = array.array("i", range(1000))
list_bytes = sys.getsizeof(as_list) + sum(sys.getsizeof(i) for i in as_list)
array_bytes = sys.getsizeof(as_array)
print("list  total bytes (container + int objects):", list_bytes)
print("array total bytes:", array_bytes)
print("array is about", round(list_bytes / array_bytes, 1), "x smaller")
print("# Note: sys.getsizeof(list) alone ignores the ints inside - add them up.")

# 20. tobytes / frombytes / tofile / fromfile
# ------------------------------------
# - Great for binary protocols, sensor data, or saving numbers quickly.
# - GOTCHA: byte order is the machine's own ('little' on most PCs). For
#   files shared across machines, call .byteswap() or use struct instead.
print("\n# 20. tobytes / frombytes / tofile")
nums_arr = array.array("h", [1, -2, 300])
raw = nums_arr.tobytes()
print("raw bytes:", raw, "| length:", len(raw), "(3 items x 2 bytes)")
restored = array.array("h")
restored.frombytes(raw)
print("restored:", restored, "| equal:", restored == nums_arr)

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "numbers.bin")
    with open(path, "wb") as f:
        nums_arr.tofile(f)
    from_file = array.array("h")
    with open(path, "rb") as f:
        from_file.fromfile(f, 3)  # read exactly 3 items
    print("file size:", os.path.getsize(path), "bytes | read back:", from_file)

# ====================================================================
# PART D - queue
# ====================================================================

# 21. queue Module - Why Not Just a List?
# ------------------------------------
# - list.pop(0) is O(n) and a plain list is NOT safe to share between
#   threads for "wait until something arrives" logic.
# - queue.Queue handles the LOCKING and the WAITING for you.
# - Four flavours:
#     Queue         FIFO  (first in, first out)
#     LifoQueue     LIFO  (stack: last in, first out)
#     PriorityQueue lowest value first (a heap + locks inside)
#     SimpleQueue   minimal FIFO, no maxsize, no task_done, always unbounded
print("\n# 21. Queue, LifoQueue, PriorityQueue, SimpleQueue")
q = queue.Queue()
lq = queue.LifoQueue()
pq2 = queue.PriorityQueue()
sq = queue.SimpleQueue()
for x in [3, 1, 2]:
    q.put(x)
    lq.put(x)
    pq2.put(x)
    sq.put(x)
print("Queue (FIFO):         ", [q.get() for _ in range(3)])
print("LifoQueue (stack):    ", [lq.get() for _ in range(3)])
print("PriorityQueue (min):  ", [pq2.get() for _ in range(3)])
print("SimpleQueue (FIFO):   ", [sq.get() for _ in range(3)])
print("# PriorityQueue has the SAME tie/comparison gotcha as heapq - use (prio, counter, item).")

# 22. maxsize, put_nowait / get_nowait, Full and Empty
# ------------------------------------
# - maxsize > 0 makes the queue BOUNDED: put() BLOCKS when it is full.
#   That is back-pressure - a fast producer is slowed to the consumer's pace
#   instead of eating all memory.
# - maxsize = 0 (default) means unlimited.
print("\n# 22. maxsize and non-blocking calls")
bounded = queue.Queue(maxsize=2)
bounded.put("a")
bounded.put("b")
print("full?", bounded.full(), "| qsize:", bounded.qsize())
try:
    bounded.put_nowait("c")
except queue.Full:
    print("queue.Full raised by put_nowait")
try:
    bounded.put("c", timeout=0.05)  # wait up to 50 ms, then give up
except queue.Full:
    print("queue.Full raised after put() timeout")
bounded.get_nowait()
bounded.get_nowait()
try:
    bounded.get_nowait()
except queue.Empty:
    print("queue.Empty raised by get_nowait")
print("# qsize()/empty()/full() are only snapshots - another thread may change them")
print("# right after you look. Do not write 'if not q.empty(): q.get()'; catch Empty.")

# 23. task_done() and join()
# ------------------------------------
# - get() removes an item, but the WORK on it may still be running.
# - The consumer calls task_done() when it has FINISHED the item.
# - q.join() blocks until every put item has a matching task_done().
print("\n# 23. task_done / join")
jq = queue.Queue()
for i in range(3):
    jq.put(i)
done_log = []


def one_worker():
    while True:
        try:
            item = jq.get_nowait()
        except queue.Empty:
            return
        done_log.append(item * 10)
        jq.task_done()


t = threading.Thread(target=one_worker)
t.start()
jq.join()  # returns once all 3 items are marked done
t.join()
print("results:", done_log)

# 24. Producer / Consumer With 2 Workers and Sentinel Shutdown
# ------------------------------------
# - A sentinel is a special value meaning "no more work - stop".
# - You need ONE sentinel PER worker, because each worker consumes one.
# - Output order between threads is non-deterministic, so we collect the
#   results and print them sorted after everything has finished.
print("\n# 24. Producer/consumer demo")
SENTINEL = None
work_q = queue.Queue(maxsize=3)  # bounded: producer waits if workers are slow
results = []
results_lock = threading.Lock()


def worker():
    while True:
        job = work_q.get()
        if job is SENTINEL:
            work_q.task_done()
            break
        square = job * job
        with results_lock:  # list.append is safe in CPython, lock is for clarity
            results.append((job, square))
        work_q.task_done()


def producer(n):
    for i in range(1, n + 1):
        work_q.put(i)
    for _ in range(2):  # one sentinel per worker
        work_q.put(SENTINEL)


workers = [threading.Thread(target=worker) for _ in range(2)]
for w in workers:
    w.start()
prod = threading.Thread(target=producer, args=(8,))
prod.start()
prod.join()
work_q.join()
for w in workers:
    w.join()
print("squares computed:", sorted(results))
print("all threads finished cleanly:", not any(w.is_alive() for w in workers))
print("# Never use daemon threads + 'while True' with no sentinel if you need clean shutdown.")

# ====================================================================
# PART E - deque recap and cheat table
# ====================================================================

# 25. collections.deque - The O(1) Queue Recap
# ------------------------------------
# - For SINGLE-thread code, deque is the fastest FIFO: append and popleft
#   are both O(1). (list.pop(0) is O(n).)
# - deque methods are atomic enough for simple thread use, but it has no
#   blocking get() and no task_done - that is what queue.Queue adds.
# - More on deque in 01-Collections-Module.py.
print("\n# 25. deque as an O(1) queue")
dq = deque()
dq.append("first")
dq.append("second")
dq.append("third")
print("popleft:", dq.popleft(), "| remaining:", list(dq))
window = deque(maxlen=3)  # bonus: fixed-size sliding window
for x in range(6):
    window.append(x)
print("last 3 seen (maxlen=3):", list(window))

# 26. Which Structure For Which Job? (cheat table)
# ------------------------------------
print("\n# 26. Cheat table")
print("# Job                               Use                    Cost")
print("# ---------------------------------------------------------------------------")
print("# Append/pop at the END             list                   O(1)")
print("# Insert/pop at the FRONT           deque                  O(1)  (list: O(n))")
print("# Membership test (unsorted)        set / dict             O(1)  (list: O(n))")
print("# Membership test (kept sorted)     bisect on sorted list  O(log n)")
print("# Keep list sorted while inserting  bisect.insort          O(n)  (shift cost)")
print("# Always get the smallest item      heapq                  push/pop O(log n), peek O(1)")
print("# Top-K of a big/streaming input    heapq.nlargest(k)      O(n log k)")
print("# Millions of plain numbers         array.array            ~4-8 bytes each")
print("# Hand work to other threads        queue.Queue            O(1), blocking + locks")
print("# Priority work across threads      queue.PriorityQueue    O(log n), blocking + locks")
print("# Stack (LIFO)                      list or LifoQueue      O(1) (LifoQueue = threads)")
print("# Heavy numeric maths               numpy (3rd party)      vectorised")

# 27. Common Gotchas Recap
# ------------------------------------
print("\n# 27. Gotchas recap")
print("# - heapq is a MIN-heap; negate values for max-heap behaviour.")
print("# - heap[1:] is NOT sorted; only heap[0] is guaranteed smallest.")
print("# - Tuples in a heap: add a counter so ties never compare the payload.")
print("# - bisect needs a SORTED list; on unsorted data it silently gives nonsense.")
print("# - insort is O(n) overall, not O(log n).")
print("# - array holds numbers of ONE typecode only.")
print("# - Queue.qsize()/empty() are unreliable under threads; use sentinels or timeouts.")
print("# - Every get() needs a task_done() if anyone calls join().")
