import itertools
import functools

# 01. itertools & functools - Introduction
# ------------------------------------
# - itertools: fast, memory-efficient tools for working with iterators.
# - functools: tools for working with functions (caching, composition, etc).

print("# 01. itertools & functools - Introduction")
print("# ------------------------------------")

# 02. itertools.chain() - Combine Multiple Iterables
# ------------------------------------
combined = list(itertools.chain([1, 2], [3, 4], [5]))
print("\n# 02. itertools.chain()")
print(combined)

# 03. itertools.cycle() - Repeat an Iterable Forever
# ------------------------------------
print("\n# 03. itertools.cycle()")
counter = 0
for item in itertools.cycle(["A", "B", "C"]):
    if counter >= 6:
        break
    print(item, end=" ")
    counter += 1
print()

# 04. itertools.count() - Infinite Counter
# ------------------------------------
print("\n# 04. itertools.count()")
for i in itertools.count(start=10, step=5):
    if i > 30:
        break
    print(i, end=" ")
print()

# 05. itertools.product() - Cartesian Product
# ------------------------------------
print("\n# 05. itertools.product()")
print(list(itertools.product([1, 2], ["a", "b"])))

# 06. itertools.permutations() and combinations()
# ------------------------------------
print("\n# 06. itertools.permutations() and combinations()")
print("permutations:", list(itertools.permutations([1, 2, 3], 2)))
print("combinations:", list(itertools.combinations([1, 2, 3], 2)))

# 07. itertools.groupby() - Group Consecutive Items
# ------------------------------------
print("\n# 07. itertools.groupby()")
data = [1, 1, 2, 2, 2, 3, 1, 1]
for key, group in itertools.groupby(data):
    print(key, "->", list(group))

# 08. itertools.islice() - Slice an Iterator
# ------------------------------------
print("\n# 08. itertools.islice()")
print(list(itertools.islice(itertools.count(1), 5)))  # first 5 natural numbers

# 09. functools.reduce() - Cumulative Reduction
# ------------------------------------
print("\n# 09. functools.reduce()")
total = functools.reduce(lambda acc, x: acc + x, [1, 2, 3, 4, 5])
print("sum via reduce:", total)

product = functools.reduce(lambda acc, x: acc * x, [1, 2, 3, 4], 1)
print("product via reduce:", product)

# 10. functools.lru_cache() - Memoization
# ------------------------------------
@functools.lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print("\n# 10. functools.lru_cache()")
print("fibonacci(30):", fibonacci(30))
print("cache info:", fibonacci.cache_info())

# 11. functools.partial() - Pre-fill Function Arguments
# ------------------------------------
def power(base, exponent):
    return base ** exponent

square = functools.partial(power, exponent=2)
cube = functools.partial(power, exponent=3)
print("\n# 11. functools.partial()")
print("square(5):", square(5))
print("cube(2):", cube(2))

# 12. More itertools Recipes
# ------------------------------------
print("\n# 12. More itertools Recipes")

# accumulate() - running totals (or running result of any binary function)
print("accumulate (running total):", list(itertools.accumulate([1, 2, 3, 4])))
print("accumulate (running max):", list(itertools.accumulate([3, 1, 4, 1, 5], max)))

# starmap() - like map(), but unpacks each item as *args
pairs = [(2, 3), (4, 5), (6, 7)]
print("starmap (multiply pairs):", list(itertools.starmap(lambda a, b: a * b, pairs)))

# zip_longest() - like zip(), but pads shorter iterables instead of truncating
print("zip (truncates):", list(zip([1, 2, 3], ["a", "b"])))
print("zip_longest (pads):", list(itertools.zip_longest([1, 2, 3], ["a", "b"], fillvalue="?")))

# filterfalse() - opposite of filter(): keeps items where predicate is False
print("filterfalse (keep non-even):", list(itertools.filterfalse(lambda x: x % 2 == 0, range(10))))

# tee() - split one iterator into n independent copies (see 01-Iterators.py for depth)
copy_a, copy_b = itertools.tee(range(3), 2)
print("tee (two independent copies):", list(copy_a), list(copy_b))

# 13. functools.singledispatch - Type-Based Dispatch
# ------------------------------------
# - Lets a function have different implementations depending on the TYPE of
#   its first argument, registered with @func.register - avoids a long
#   isinstance() if/elif chain.
@functools.singledispatch
def describe(value):
    return f"generic value: {value!r}"

@describe.register
def _(value: int):
    return f"an integer: {value}"

@describe.register
def _(value: list):
    return f"a list with {len(value)} items"

print("\n# 13. functools.singledispatch")
print(describe(42))
print(describe([1, 2, 3]))
print(describe(3.14))  # falls back to the generic implementation

# 14. functools.cache vs functools.lru_cache
# ------------------------------------
# - functools.cache (3.9+) is a simpler alias for lru_cache(maxsize=None) -
#   unbounded caching, no eviction, slightly less overhead since it doesn't
#   track a max size or usage order.
# - Use lru_cache(maxsize=N) when you want the cache to stay bounded.
@functools.cache
def add_cached(a, b):
    return a + b

print("\n# 14. functools.cache vs functools.lru_cache")
print("cache() result:", add_cached(2, 3))
print("cache() is unbounded, equivalent to lru_cache(maxsize=None)")
print("lru_cache(maxsize=128) instead bounds the cache to 128 entries, evicting oldest")

# 15. functools.cmp_to_key - Legacy Comparator-Style Sorting
# ------------------------------------
# - Modern sorted() uses a `key` function, but some comparisons only make
#   sense as a two-argument comparator (negative/zero/positive). cmp_to_key
#   adapts an old-style comparator into a key function.
def compare_by_length_then_reverse_alpha(a, b):
    if len(a) != len(b):
        return len(a) - len(b)  # shorter strings first
    return -1 if a > b else (1 if a < b else 0)  # longer-first alpha within same length

print("\n# 15. functools.cmp_to_key")
words = ["banana", "kiwi", "fig", "apple", "date"]
print(sorted(words, key=functools.cmp_to_key(compare_by_length_then_reverse_alpha)))

# 16. operator Module - Functional-Style Alternative to Lambdas
# ------------------------------------
# - operator provides function versions of built-in operators, often
#   clearer and faster than an equivalent lambda.
import operator

print("\n# 16. operator Module")
print("operator.add(2, 3):", operator.add(2, 3))
print("reduce with operator.add:", functools.reduce(operator.add, [1, 2, 3, 4]))

people = [{"name": "Bob", "age": 25}, {"name": "Ann", "age": 30}, {"name": "Cy", "age": 20}]
print("sorted by age via operator.itemgetter:", sorted(people, key=operator.itemgetter("age")))
print("just the names via itemgetter:", list(map(operator.itemgetter("name"), people)))
