# 01. Iterators - Introduction
# ------------------------------------
# - An iterable is any object you can loop over (list, tuple, str, dict, ...).
# - An iterator is the object that actually produces values one at a time.
# - Every iterator is an iterable, but not every iterable is an iterator.

print("# 01. Iterators - Introduction")
print("# ------------------------------------")

# 02. Iterable vs Iterator
# ------------------------------------
numbers = [1, 2, 3]  # this is an iterable
print("\n# 02. Iterable vs Iterator")
print("is list iterable:", hasattr(numbers, "__iter__"))
print("does list have __next__:", hasattr(numbers, "__next__"))

iterator = iter(numbers)  # iter() gets an iterator FROM an iterable
print("iterator object:", iterator)
print("does iterator have __next__:", hasattr(iterator, "__next__"))

# 03. The Iterator Protocol - next() and StopIteration
# ------------------------------------
print("\n# 03. The Iterator Protocol")
print(next(iterator))  # 1
print(next(iterator))  # 2
print(next(iterator))  # 3
try:
    print(next(iterator))  # exhausted -> raises StopIteration
except StopIteration:
    print("StopIteration raised - iterator exhausted")

# 04. How a `for` Loop Really Works (behind the scenes)
# ------------------------------------
print("\n# 04. How a `for` Loop Really Works")
it = iter(numbers)
while True:
    try:
        item = next(it)
    except StopIteration:
        break
    print("manual for-loop equivalent:", item)
# This is exactly what `for item in numbers:` does internally.

# 05. Writing a Custom Iterator Class
# ------------------------------------
# - Implement __iter__ (returns self) and __next__ (returns next value or raises StopIteration).
class CountDown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value

print("\n# 05. Writing a Custom Iterator Class")
for num in CountDown(5):
    print("countdown:", num)

# 06. Separating Iterable from Iterator (best practice)
# ------------------------------------
# - Iterable class returns a NEW iterator each time __iter__ is called,
#   so the same collection can be looped over multiple times independently.
class EvenNumbers:
    def __init__(self, limit):
        self.limit = limit

    def __iter__(self):
        return EvenNumbersIterator(self.limit)

class EvenNumbersIterator:
    def __init__(self, limit):
        self.limit = limit
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > self.limit:
            raise StopIteration
        value = self.current
        self.current += 2
        return value

print("\n# 06. Separating Iterable from Iterator")
evens = EvenNumbers(10)
print("first loop:", list(evens))
print("second loop (works again):", list(evens))

# 07. iter() with a Sentinel Value
# ------------------------------------
# - iter(callable, sentinel) keeps calling callable() until it returns sentinel.
def make_counter():
    count = 0
    def counter():
        nonlocal count
        count += 1
        return count
    return counter

print("\n# 07. iter() with a Sentinel Value")
counter_fn = make_counter()
for value in iter(counter_fn, 4):  # stops when counter_fn() returns 4
    print("sentinel-based iteration:", value)

# 08. Iterators Are Consumed Once
# ------------------------------------
print("\n# 08. Iterators Are Consumed Once")
it = iter([1, 2, 3])
print("as list first time:", list(it))
print("as list second time (empty, already exhausted):", list(it))

# 09. Built-in Functions That Work with Iterators
# ------------------------------------
print("\n# 09. Built-in Functions That Work with Iterators")
print("sum:", sum(iter([1, 2, 3, 4])))
print("max:", max(iter([5, 1, 9, 3])))
print("sorted:", sorted(iter([3, 1, 2])))
print("enumerate:", list(enumerate(iter(["a", "b"]))))

# 10. itertools.tee() - Splitting One Iterator into Independent Copies
# ------------------------------------
# - Once an iterator is consumed, it's gone (see section 08). tee() solves the
#   case where you need to iterate the SAME source more than once.
# - It returns n independent iterators; internally they share a buffer so
#   values aren't recomputed, but each copy tracks its own position.
# - Caveat: don't keep using the original iterator after teeing it - only use
#   the returned copies, and don't let one copy run far ahead (memory grows).
import itertools

print("\n# 10. itertools.tee() - Splitting One Iterator")
source = iter([1, 2, 3, 4, 5])
evens_view, odds_view, all_view = itertools.tee(source, 3)
print("evens:", [n for n in evens_view if n % 2 == 0])
print("odds:", [n for n in odds_view if n % 2 != 0])
print("all (independent copy):", list(all_view))

# 11. Why You Can't Reuse a Consumed Iterator (common bug)
# ------------------------------------
# - A very common bug: passing the SAME iterator to two functions/loops,
#   expecting both to see all the values. The second one gets nothing.
print("\n# 11. Reusing a Consumed Iterator - Common Bug")
shared_iterator = iter([10, 20, 30])
first_pass = list(shared_iterator)
second_pass = list(shared_iterator)  # already exhausted
print("first pass:", first_pass)
print("second pass (bug - empty):", second_pass)
print("fix: re-create the iterator, or tee() it, or iterate the ORIGINAL LIST (iterable), not the iterator")
fixed_first = list([10, 20, 30])
fixed_second = list([10, 20, 30])
print("fixed first:", fixed_first)
print("fixed second:", fixed_second)

# 12. Building a Lazy Pipeline of Multiple Custom Iterators
# ------------------------------------
# - Iterators can be chained together, each wrapping the previous one, so
#   nothing is computed until values are actually pulled through the chain.
class Squarer:
    """Wraps an iterator and yields the square of each value."""
    def __init__(self, source):
        self.source = iter(source)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.source) ** 2

class Filterer:
    """Wraps an iterator and skips values that fail a predicate."""
    def __init__(self, source, predicate):
        self.source = iter(source)
        self.predicate = predicate

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            value = next(self.source)  # lets StopIteration propagate naturally
            if self.predicate(value):
                return value

print("\n# 12. Lazy Pipeline of Custom Iterators")
pipeline = Filterer(Squarer(CountDown(6)), lambda x: x > 10)
print("countdown -> square -> keep > 10:", list(pipeline))

# 13. __length_hint__ (briefly)
# ------------------------------------
# - Some iterators can report an ESTIMATE of remaining items via __length_hint__.
# - It's a hint, not a guarantee (used internally by list()/tuple() to
#   pre-allocate memory) - unlike __len__, it's allowed to be wrong.
print("\n# 13. __length_hint__ (briefly)")
range_iterator = iter(range(5))
print("length hint before consuming:", range_iterator.__length_hint__())
next(range_iterator)
print("length hint after one next():", range_iterator.__length_hint__())

# 14. Iterator-based vs List-based Memory Usage
# ------------------------------------
# - A list holds every element in memory at once; an iterator/generator only
#   holds enough state to produce the NEXT value, regardless of how "long"
#   the sequence conceptually is.
import sys

print("\n# 14. Iterator vs List Memory Usage")
big_list = list(range(1_000_000))
big_range_iterator = iter(range(1_000_000))
print("size of list with 1,000,000 ints:", sys.getsizeof(big_list), "bytes")
print("size of the equivalent range iterator:", sys.getsizeof(big_range_iterator), "bytes")
print("range itself (lazy, not even an iterator yet):", sys.getsizeof(range(1_000_000)), "bytes")
