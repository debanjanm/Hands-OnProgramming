import functools
import itertools
import operator
import sys
import types
from dataclasses import FrozenInstanceError, dataclass, replace

# 01. Functional Programming - Introduction
# ------------------------------------
# - "Functional style" = build programs by COMBINING FUNCTIONS that take values
#   in and give values out, instead of mutating shared state step by step.
# - Core ideas:
#     1. Functions are VALUES (store them, pass them, return them).
#     2. Prefer PURE functions: same input -> same output, no side effects.
#     3. Prefer immutable data: make a new value instead of changing the old.
#     4. Build big behaviour by composing small functions.
# - Python is MULTI-PARADIGM, not a functional language. It has no tail-call
#   optimisation, no immutable lists, and its lambdas are crippled on purpose.
#   Use the functional IDEAS where they help; do not force the whole style.
# - Already covered elsewhere (cross-reference, not repeated here):
#     * closures, nonlocal/global, higher-order basics, partial -> 02-Functions.py
#     * the full itertools/functools/operator tour -> 05-Python Advanced/08-Itertools-And-Functools.py
#     * generators in depth -> 05-Python Advanced/02-Generators.py

print("# 01. Functional Programming - Introduction")
print("# ------------------------------------")

# 02. Functions are values; pure vs impure
# ------------------------------------
# - A PURE function: output depends ONLY on its arguments, and it changes
#   nothing outside itself (no printing, no global writes, no mutating inputs).
# - Why pure is easier to test: no setup, no mocking, no hidden state. You
#   call it and compare the result - and the answer is the same every time.
# - Why pure is easier to reason about: you can read a call in isolation, cache it
#   (see lru_cache below), or run it in parallel without locks.

print("\n# 02. Functions are values; pure vs impure")


def shout(text):
    return text.upper() + "!"


ops = {"shout": shout, "len": len, "reverse": lambda t: t[::-1]}  # functions stored in a dict
print("functions as dict values:", {name: f("abc") for name, f in ops.items()})

cart_total = 0  # hidden, shared state


def add_to_total_impure(price):
    global cart_total
    cart_total += price  # side effect: changes a global
    return cart_total


def add_pure(total, price):
    return total + price  # everything it needs comes in, everything it gives goes out


print("impure, same call twice :", add_to_total_impure(10), add_to_total_impure(10), "<- answer depends on history")
print("pure,   same call twice :", add_pure(0, 10), add_pure(0, 10), "<- always equal")


def append_impure(items, x):
    items.append(x)  # mutates the CALLER's list
    return items


def append_pure(items, x):
    return [*items, x]  # builds a NEW list, original untouched


original = [1, 2]
append_pure(original, 3)
print("after append_pure   original =", original)
append_impure(original, 3)
print("after append_impure original =", original, "<- the caller's data changed behind its back")

# Testing a pure function needs nothing but assert:
assert add_pure(2, 3) == 5
assert append_pure([1], 2) == [1, 2]
print("pure functions test with plain asserts - no fixtures, no mocks.")
print("(print() is a side effect too. Keep it at the edges; keep the core pure.)")

# 03. Immutability helpers
# ------------------------------------
# - If data cannot change, no function can change it behind your back.
# - Python gives you: tuple, frozenset, str/bytes/int (already immutable),
#   frozen dataclasses, and read-only dict VIEWS (MappingProxyType).
# - Note "immutable" is SHALLOW: a tuple holding a list still lets that list change.

print("\n# 03. Immutability helpers")

point = (3, 4)
try:
    point[0] = 99
except TypeError as e:
    print("tuple item assignment      : TypeError:", e)
print("'change' a tuple by rebuilding:", (99, *point[1:]))

tags = frozenset({"a", "b"})
print("frozenset has no .add         :", hasattr(tags, "add"), "| union makes a NEW one:", sorted(tags | {"c"}), "| original:", sorted(tags))
print("frozenset is hashable (dict key OK):", {frozenset({1, 2}): "pair"}[frozenset({2, 1})])


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "INR"


price = Money(100)
try:
    price.amount = 200
except FrozenInstanceError as e:
    print("frozen dataclass assignment   : FrozenInstanceError:", e)
discounted = replace(price, amount=80)  # dataclasses.replace = "copy with changes"
print("replace() builds a new one    :", price, "->", discounted)
print("frozen dataclasses are hashable:", hash(price) == hash(Money(100)), "| usable in sets:", {price, Money(100), discounted})

defaults = {"theme": "dark", "lang": "en"}
view = types.MappingProxyType(defaults)  # read-only window onto a dict
try:
    view["theme"] = "light"
except TypeError as e:
    print("MappingProxyType assignment   : TypeError:", e)
defaults["lang"] = "hi"
print("but the view is LIVE          :", dict(view), "<- it only blocks writes THROUGH the view")
print("to get a true snapshot: MappingProxyType(dict(defaults)) (copy first)")

shallow = ("label", [1, 2])
shallow[1].append(3)
print("tuple is only shallowly immutable:", shallow, "<- the inner list changed")

# 04. map / filter / reduce vs comprehensions
# ------------------------------------
# - map(f, xs)       : apply f to every item        (lazy iterator)
# - filter(p, xs)    : keep items where p(item) true (lazy iterator)
# - reduce(f, xs, i) : fold many items into ONE value (functools.reduce)
# - Python's comprehensions do the same job and usually read better,
#   because there is no lambda and you can see the loop variable.

print("\n# 04. map / filter / reduce vs comprehensions")

nums = [1, 2, 3, 4, 5, 6]
print("map + lambda          :", list(map(lambda n: n * n, nums)))
print("comprehension         :", [n * n for n in nums])
print("filter + lambda       :", list(filter(lambda n: n % 2 == 0, nums)))
print("comprehension         :", [n for n in nums if n % 2 == 0])
print("chained map+filter    :", list(map(lambda n: n * n, filter(lambda n: n % 2 == 0, nums))))
print("same, comprehension   :", [n * n for n in nums if n % 2 == 0], "<- one pass, read left to right")

# When does map/filter read better? When you ALREADY have a named function:
words = ["  apple ", "Banana", " cherry"]
print("map(str.strip, ...)   :", list(map(str.strip, words)), "<- no lambda needed, clearer than a comprehension")
print("map(int, strings)     :", list(map(int, ["1", "2", "3"])))
print("filter(None, ...)     :", list(filter(None, [0, "a", "", None, 7])), "<- drop falsy values")
print("map, several iterables:", list(map(operator.add, [1, 2, 3], [10, 20, 30])))
print("Rule of thumb: named function -> map/filter is fine; needs a lambda -> use a comprehension.")

# Generators: swap [] for () to keep the comprehension lazy.
lazy_squares = (n * n for n in nums)
print("generator expression  :", type(lazy_squares).__name__, "->", sum(lazy_squares))

# 05. lambda limits and key=
# ------------------------------------
# - lambda args: expression -> a small anonymous function.
# - LIMITS: exactly ONE expression. No statements (no assignment, no return,
#   no for/while/try/raise/pass), and no annotations on its body.
# - Real home of lambda: the key= argument of sorted/min/max/sort.
# - If a lambda needs a name or a comment, write a def. (PEP 8 also says
#   never `f = lambda ...`; tracebacks then show '<lambda>' instead of a name.)

print("\n# 05. lambda limits and key=")

try:
    compile("lambda x: y = x + 1", "<demo>", "eval")
except SyntaxError as e:
    print("lambda body must be an expression ->", type(e).__name__ + ":", e.msg)
print("lambda traceback name   :", (lambda: 0).__name__, "(unhelpful when debugging)")
print("conditional expr OK     :", (lambda n: "even" if n % 2 == 0 else "odd")(7))

people = [("Asha", 30), ("Ben", 25), ("Chen", 30), ("Dev", 22)]
print("sorted(key=lambda)      :", sorted(people, key=lambda p: p[1]))
print("oldest (max key=)       :", max(people, key=lambda p: p[1]), "<- ties: FIRST wins")
print("multi-key, age desc/name:", sorted(people, key=lambda p: (-p[1], p[0])))
print("key=len on strings      :", sorted(["pear", "fig", "banana"], key=len))
print("key is called ONCE per item (cheap), unlike an old-style compare function.")

# 06. functools.reduce - fold with an initial value
# ------------------------------------
# - reduce(f, items, initial): f(f(f(initial, a), b), c) ...
# - Always give an INITIAL value when you can: it is the result for an empty
#   input. Without one, reduce on [] raises TypeError.
# - The accumulator and the items may have DIFFERENT types (initial sets the
#   accumulator type) - that's where reduce is genuinely useful.
# - But for sum/min/max/any/all/join there is a dedicated built-in: use it.

print("\n# 06. functools.reduce")

print("reduce product           :", functools.reduce(operator.mul, [1, 2, 3, 4], 1))
try:
    functools.reduce(operator.add, [])
except TypeError as e:
    print("reduce on [] with no initial: TypeError:", e)
print("reduce on [] with initial:", functools.reduce(operator.add, [], 0))

trace = []
functools.reduce(lambda acc, n: trace.append((acc, n)) or acc + n, [1, 2, 3], 100)
print("how the accumulator moves:", trace, "<- (acc, next item)")

# Different accumulator type: count characters into a dict.
counts = functools.reduce(lambda acc, ch: {**acc, ch: acc.get(ch, 0) + 1}, "banana", {})
print("reduce to a dict         :", counts, "(builds a new dict each step: O(n^2); collections.Counter is better)")

big = list(range(1, 6))
print("why NOT reduce for sum   :", functools.reduce(lambda a, b: a + b, big), "==", sum(big), "== sum(big): shorter, clearer, faster")
print("                           same for max/min/all/any/''.join - use the dedicated built-in")

# 07. functools.partial and partialmethod
# ------------------------------------
# - partial(func, *args, **kwargs) pre-fills some arguments -> a new callable.
# - (Basics are in 02-Functions.py section 15; here: how it fits FP.)
# - partialmethod does the same for METHODS: the first argument stays `self`.

print("\n# 07. functools.partial / partialmethod")

def power(base, exponent):
    return base ** exponent


square = functools.partial(power, exponent=2)
cube = functools.partial(power, exponent=3)
print("square(5), cube(2)       :", square(5), cube(2))
print("partial remembers        :", square.func.__name__, square.args, square.keywords)
print("partial in map           :", list(map(functools.partial(operator.mul, 10), [1, 2, 3])), "<- replaces lambda n: 10 * n")
print("int base-2 parser        :", functools.partial(int, base=2)("1011"))


class Light:
    def __init__(self):
        self.state = "off"

    def _set(self, state):
        self.state = state
        return self

    turn_on = functools.partialmethod(_set, "on")
    turn_off = functools.partialmethod(_set, "off")


lamp = Light()
print("partialmethod            :", lamp.turn_on().state, "->", lamp.turn_off().state)
print("a plain partial() in a class body would NOT bind self; partialmethod does.")

# 08. Function composition: compose and pipe
# ------------------------------------
# - compose(f, g, h)(x) == f(g(h(x)))   -> reads RIGHT to LEFT (maths style)
# - pipe(f, g, h)(x)    == h(g(f(x)))   -> reads LEFT to RIGHT (data flows like a pipeline)
# - Python has no built-in compose; two tiny reduce-based helpers do it.

print("\n# 08. compose and pipe")


def compose(*funcs):
    """compose(f, g, h)(x) == f(g(h(x)))"""
    def composed(x):
        for f in reversed(funcs):
            x = f(x)
        return x
    return composed


def pipe(*funcs):
    """pipe(f, g, h)(x) == h(g(f(x)))"""
    return lambda x: functools.reduce(lambda acc, f: f(acc), funcs, x)


def strip(s):
    return s.strip()


def lower(s):
    return s.lower()


def hyphenate(s):
    return "-".join(s.split())


slugify_c = compose(hyphenate, lower, strip)  # right to left: strip, then lower, then hyphenate
slugify_p = pipe(strip, lower, hyphenate)     # left to right: same steps, easier to read
title = "  Functional Programming In Python "
print("compose result :", slugify_c(title))
print("pipe result    :", slugify_p(title))
assert slugify_c(title) == slugify_p(title)
print("empty pipe is the identity:", pipe()(42), "(reduce with an initial value handles it)")
print("pipelines nest like any function:", pipe(slugify_p, str.upper)(title))
print("Limit: each step takes ONE argument and returns ONE value; use partial to fit others in.")
clean_numbers = pipe(functools.partial(map, int), functools.partial(filter, lambda n: n > 0), list)
print("partial + pipe :", clean_numbers(["3", "-1", "7", "0"]))

# 09. Currying by hand vs partial
# ------------------------------------
# - CURRYING turns f(a, b, c) into f(a)(b)(c): one argument at a time.
# - partial applies SOME arguments now and the rest later, in one step.
# - Python does not curry automatically. Currying by hand is mostly an
#   exercise; partial is what you use in real code.

print("\n# 09. Currying vs partial")


def add3_curried(a):
    def with_b(b):
        def with_c(c):
            return a + b + c
        return with_c
    return with_b


def add3(a, b, c):
    return a + b + c


print("curried   add3_curried(1)(2)(3) :", add3_curried(1)(2)(3))
add_to_1 = add3_curried(1)
print("partially applied add_to_1(2)(3):", add_to_1(2)(3))
print("with partial: partial(add3, 1)(2, 3) :", functools.partial(add3, 1)(2, 3), "<- any number of args at once")


def curry(func):
    """Generic currier: collects arguments until func has enough of them."""
    arity = func.__code__.co_argcount

    def collect(*args):
        if len(args) >= arity:
            return func(*args)
        return lambda *more: collect(*args, *more)
    return collect


print("generic curry(add3)(1)(2)(3)  :", curry(add3)(1)(2)(3), "| curry(add3)(1, 2)(3):", curry(add3)(1, 2)(3))
print("Verdict: partial() covers 95% of real needs; curry helpers are rarely worth the confusion.")

# 10. operator.itemgetter / attrgetter / methodcaller
# ------------------------------------
# - Fast, readable replacements for the most common lambdas:
#     lambda r: r[1]        ->  itemgetter(1)
#     lambda o: o.name      ->  attrgetter("name")
#     lambda s: s.lower()   ->  methodcaller("lower")
# - Several keys at once return a TUPLE, which is exactly what sorted() wants.

print("\n# 10. operator.itemgetter / attrgetter / methodcaller")

rows = [("Asha", "Pune", 30), ("Ben", "Delhi", 25), ("Chen", "Pune", 22), ("Dev", "Delhi", 25)]
print("itemgetter(2) one value      :", operator.itemgetter(2)(rows[0]))
print("itemgetter(1, 0) tuple       :", operator.itemgetter(1, 0)(rows[0]))
print("sort by age                  :", sorted(rows, key=operator.itemgetter(2)))
print("sort by city, then age       :", sorted(rows, key=operator.itemgetter(1, 2)))
print("works on dicts too           :", sorted([{"n": "b", "v": 2}, {"n": "a", "v": 9}], key=operator.itemgetter("n")))


@dataclass
class Employee:
    name: str
    dept: str
    salary: int


staff = [Employee("Asha", "IT", 90), Employee("Ben", "HR", 70), Employee("Chen", "IT", 80)]
print("attrgetter sort by salary    :", [e.name for e in sorted(staff, key=operator.attrgetter("salary"))])
print("attrgetter dept+salary       :", [e.name for e in sorted(staff, key=operator.attrgetter("dept", "salary"))])
print("methodcaller('lower') as key :", sorted(["b", "A", "c"], key=operator.methodcaller("lower")))
print("methodcaller with args       :", list(map(operator.methodcaller("replace", "a", "@"), ["banana", "data"])))
print("operator funcs for map/reduce:", operator.add(2, 3), operator.mul(4, 5), operator.neg(7), operator.contains([1, 2], 2))

# 11. A few itertools helpers (full tour: 05-Python Advanced/08-Itertools-And-Functools.py)
# ------------------------------------
# - itertools = lazy building blocks that fit FP style: they take iterables,
#   return iterators, and never mutate their input.

print("\n# 11. itertools in FP style")

print("accumulate (running total)  :", list(itertools.accumulate([1, 2, 3, 4])))
print("accumulate with func        :", list(itertools.accumulate([3, 1, 4, 1, 5], max)), "<- running maximum")
print("accumulate initial=100      :", list(itertools.accumulate([1, 2, 3], initial=100)))
print("starmap unpacks each tuple  :", list(itertools.starmap(pow, [(2, 3), (3, 2), (10, 3)])), "<- map(f, *zip(*pairs)) alternative is uglier")
print("takewhile (stop at 1st fail):", list(itertools.takewhile(lambda n: n < 4, [1, 2, 3, 6, 1, 2])))
print("dropwhile (skip while true) :", list(itertools.dropwhile(lambda n: n < 4, [1, 2, 3, 6, 1, 2])), "<- once it fails, EVERYTHING else is kept")
print("chain.from_iterable (flatten one level):", list(itertools.chain.from_iterable([[1, 2], [3], [], [4, 5]])))

# groupby GOTCHA: it only groups CONSECUTIVE equal keys. Sort by the same key first.
data = ["apple", "avocado", "banana", "blueberry", "apricot"]
unsorted_groups = [(k, list(g)) for k, g in itertools.groupby(data, key=lambda w: w[0])]
print("groupby on UNSORTED input   :", unsorted_groups, "<- 'a' appears twice!")
sorted_groups = [(k, list(g)) for k, g in itertools.groupby(sorted(data), key=lambda w: w[0])]
print("groupby after sorted()      :", sorted_groups)
group_iters = [g for _, g in itertools.groupby(sorted(data), key=lambda w: w[0])]
print("GOTCHA 2: each group is a lazy view of ONE shared iterator. Collected late, they are empty:", [list(g) for g in group_iters])
print("          fix: call list(g) INSIDE the loop, as the two lines above do.")

# 12. Lazy generators vs eager lists
# ------------------------------------
# - EAGER (list): computes everything immediately, holds all of it in memory.
# - LAZY (generator): computes one item at a time, only when asked.
# - Laziness wins when: data is huge, you only need the first few items,
#   or the stream is infinite. Eager wins when you need len(), indexing or
#   to loop several times.

print("\n# 12. Lazy generators vs eager lists")

N = 1_000_000
eager = [n * 2 for n in range(N)]
lazy = (n * 2 for n in range(N))
print(f"memory for {N:,} doubled numbers: list = {sys.getsizeof(eager):,} bytes (just the pointers) | generator = {sys.getsizeof(lazy)} bytes")
print("both give the same total      :", sum(eager) == sum(lazy))


def expensive_square(n):
    print(f"   computing {n}^2")
    return n * n


print("eager: all work happens up front:")
eager_vals = [expensive_square(n) for n in range(3)]
print("   (nothing left to compute) first value =", eager_vals[0])

print("lazy: nothing happens until we ask:")
lazy_vals = (expensive_square(n) for n in range(3))
print("   generator created, zero work done so far")
print("   asking for ONE value ->", next(lazy_vals))

print("lazy shines with 'first match' on a big search:")
first_big = next(n for n in itertools.count(1) if n * n > 5000)
print("   first n with n^2 > 5000 (infinite source):", first_big)
print("GOTCHA: a generator is single-use. Draining the rest now:")
rest = list(lazy_vals)
print("   remaining items:", rest, "| asking again:", list(lazy_vals), "<- second pass is empty")
print("GOTCHA: no len() or indexing on a generator:", hasattr(lazy_vals, "__len__"))

# 13. Recursion: the FP loop, and Python's missing tail-call optimisation
# ------------------------------------
# - Pure FP languages have no loops with a changing counter; they RECURSE.
# - Some of them optimise "tail calls" (a call in the very last position) so
#   the stack never grows. CPython deliberately does NOT (Guido wanted real
#   tracebacks). Every call = a new stack frame, limit ~1000 by default.
# - So deep recursion in Python crashes with RecursionError even when it is
#   written as a tail call. Use a loop, reduce, or a built-in instead.
#   (Basic recursion + recursion limit: 02-Functions.py sections 11 and 21.)

print("\n# 13. Recursion and no tail-call optimisation")


def sum_to_recursive(n, acc=0):
    if n == 0:
        return acc
    return sum_to_recursive(n - 1, acc + n)  # a TAIL call - Python still grows the stack


def sum_to_iterative(n):
    total = 0
    for k in range(1, n + 1):
        total += k
    return total


print("recursion limit               :", sys.getrecursionlimit())
print("sum_to_recursive(100)         :", sum_to_recursive(100))
try:
    sum_to_recursive(100_000)
except RecursionError as e:
    print("sum_to_recursive(100_000)     : RecursionError:", e)

print("fix 1, loop                   :", sum_to_iterative(100_000))
print("fix 2, reduce                 :", functools.reduce(operator.add, range(1, 100_001), 0))
print("fix 3, built-in               :", sum(range(1, 100_001)), "<- almost always the best answer")
print("fix 4, closed form (maths)    :", 100_000 * 100_001 // 2)
print("(Raising sys.setrecursionlimit() only risks a real crash of the interpreter. Prefer iteration.)")

nested = [1, [2, [3, [4]], 5]]


def flatten(item):
    """Recursion IS the natural fit for nested/tree data (depth is small)."""
    if isinstance(item, list):
        for sub in item:
            yield from flatten(sub)
    else:
        yield item


print("recursion fits trees/nesting  :", list(flatten(nested)), "<- depth = nesting level, not data size")

# 14. Higher-order functions that return functions
# ------------------------------------
# - A function that BUILDS a function = a "function factory". The returned
#   function remembers its settings via a closure (see 02-Functions.py section 10).
# - It lets you configure behaviour once and reuse it many times, with no class.

print("\n# 14. Higher-order functions returning functions")


def make_multiplier(factor):
    def multiply(x):
        return x * factor
    return multiply


def make_validator(minimum, maximum):
    def validate(value):
        return minimum <= value <= maximum
    return validate


double, triple = make_multiplier(2), make_multiplier(3)
print("double(7), triple(7)        :", double(7), triple(7))
is_valid_age = make_validator(0, 120)
print("validator                   :", [is_valid_age(a) for a in (-1, 30, 200)])
print("used with filter            :", list(filter(make_validator(10, 20), [5, 12, 18, 25])))


def negate(predicate):
    """Takes a function, returns the opposite function."""
    return lambda *args, **kwargs: not predicate(*args, **kwargs)


is_even = lambda n: n % 2 == 0  # noqa: E731
is_odd = negate(is_even)
print("negate(is_even)             :", [n for n in range(6) if is_odd(n)])


def logged(func):
    """A mini decorator: takes a function, returns a wrapped one. Full story: 05-Decorators.py."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"   {func.__name__}{args} -> {result}")
        return result
    return wrapper


logged_pow = logged(pow)
logged_pow(2, 8)

# 15. functools.lru_cache on a pure function
# ------------------------------------
# - Pure function = same input always gives same output, so caching is SAFE:
#   remember results, skip repeated work.
# - lru_cache(maxsize=N) keeps the N most recently used results; `cache` is unbounded.
# - Arguments must be HASHABLE (that's why immutable data pairs well with FP).
# - Never cache an impure function: it would freeze the "first" answer.

print("\n# 15. lru_cache on a pure function")

calls = 0


def fib_slow(n):
    global calls
    calls += 1
    return n if n < 2 else fib_slow(n - 1) + fib_slow(n - 2)


@functools.lru_cache(maxsize=None)
def fib_fast(n):
    return n if n < 2 else fib_fast(n - 1) + fib_fast(n - 2)


print("fib_slow(22)       :", fib_slow(22), "| calls made:", f"{calls:,}")
print("fib_fast(22)       :", fib_fast(22), "| cache_info:", fib_fast.cache_info())
print("fib_fast(80)       :", fib_fast(80), "(instant; the slow version would take years)")
fib_fast(80)
print("repeat call -> hit :", fib_fast.cache_info())
try:
    fib_fast([1, 2])
except TypeError as e:
    print("unhashable argument: TypeError:", e)
fib_fast.cache_clear()
print("after cache_clear():", fib_fast.cache_info())

import random  # noqa: E402  (kept next to the demo that needs it)

random.seed(1)


@functools.lru_cache(maxsize=None)
def impure_roll(sides):
    return random.randint(1, sides)


print("caching an IMPURE function:", [impure_roll(6) for _ in range(4)], "<- 'random' result frozen forever. Don't.")

# 16. Worked mini-pipeline: parse -> filter -> transform -> aggregate
# ------------------------------------
# - Task: from log-like lines, total the bytes served for successful (2xx)
#   requests, per endpoint, and show them largest first.
# - We write it THREE ways: imperative loop, comprehensions, functional pipeline.

print("\n# 16. Worked mini-pipeline, three ways")

log_lines = [
    "2025-01-15 GET /home 200 512",
    "2025-01-15 GET /api/users 200 2048",
    "2025-01-15 POST /api/users 500 128",
    "2025-01-15 GET /home 200 256",
    "malformed line",
    "2025-01-16 GET /about 404 64",
    "2025-01-16 GET /api/users 200 1024",
    "2025-01-16 GET /home 304 0",
]
print(f"input: {len(log_lines)} lines, one of them garbage")


def parse(line):
    """str -> (path, status, size) or None for a bad line."""
    parts = line.split()
    if len(parts) != 5:
        return None
    _date, _method, path, status, size = parts
    return path, int(status), int(size)


# (a) Imperative: explicit loop, a mutable accumulator, branches.
totals_a = {}
for line in log_lines:
    record = parse(line)
    if record is None:
        continue
    path, status, size = record
    if 200 <= status < 300:
        totals_a[path] = totals_a.get(path, 0) + size
result_a = sorted(totals_a.items(), key=lambda kv: -kv[1])
print("a) imperative loop  :", result_a)

# (b) Comprehensions: filter and transform in readable one-liners.
from collections import Counter  # noqa: E402

records = [r for r in map(parse, log_lines) if r is not None]
ok_sizes = [(path, size) for path, status, size in records if 200 <= status < 300]
totals_b = Counter()
for path, size in ok_sizes:
    totals_b[path] += size
result_b = totals_b.most_common()
print("b) comprehensions   :", result_b)

# (c) Functional pipeline: small pure functions composed with pipe.
is_valid = lambda r: r is not None  # noqa: E731
is_success = lambda r: 200 <= r[1] < 300  # noqa: E731
to_pair = operator.itemgetter(0, 2)  # (path, status, size) -> (path, size)


def total_by_key(pairs):
    """Pure fold: builds a NEW dict each step instead of mutating one."""
    return functools.reduce(lambda acc, kv: {**acc, kv[0]: acc.get(kv[0], 0) + kv[1]}, pairs, {})


top_first = lambda d: sorted(d.items(), key=operator.itemgetter(1), reverse=True)  # noqa: E731

report = pipe(
    functools.partial(map, parse),           # str      -> record | None
    functools.partial(filter, is_valid),     # drop garbage
    functools.partial(filter, is_success),   # keep 2xx only
    functools.partial(map, to_pair),         # record   -> (path, size)
    total_by_key,                            # fold into a dict
    top_first,                               # dict     -> sorted list
)
result_c = report(log_lines)
print("c) functional pipe  :", result_c)

assert result_a == result_b == result_c
print("all three agree     :", result_a == result_b == result_c)

print("""
Honest comparison:
  a) loop            - easiest for a beginner to step through and debug with print().
                       Mutates `totals_a`, but only locally, which is fine.
  b) comprehensions  - the most PYTHONIC middle ground: short, no lambdas for the
                       filter/transform, and Counter does the aggregation.
  c) pipe/reduce     - each step is tiny, pure and testable alone, and reads as a
                       recipe. But the partial(map/filter) plumbing and a
                       reduce that rebuilds a dict are NOISY and slower in Python.
  Verdict: for everyday Python choose (b), or (a) when logic branches a lot.
  Use (c)'s IDEA (small pure steps) even when you write (b).
""".rstrip())

# 17. Cheat sheet
# ------------------------------------
print("\n# 17. Cheat sheet")
print("# ------------------------------------")
print("# - Python is multi-paradigm: borrow functional ideas, don't force the whole style.")
print("# - Prefer comprehensions / generator expressions over long map/filter/lambda chains.")
print("# - Pure functions (no side effects) are easy to test, cache and reuse.")
print("# - Immutable helpers: tuple, frozenset, @dataclass(frozen=True), MappingProxyType (read-only VIEW).")
print("# - lambda = one expression; real use is key=. Use itemgetter/attrgetter/methodcaller instead.")
print("# - reduce: give an initial value; never use it where sum/max/min/any/all/join exist.")
print("# - partial pre-fills args; partialmethod does it for methods; compose/pipe chain one-arg steps.")
print("# - itertools: accumulate/starmap/takewhile/dropwhile/chain.from_iterable; sort BEFORE groupby.")
print("# - Generators are lazy and single-use; lists are eager and re-usable.")
print("# - No tail-call optimisation: deep recursion -> RecursionError; loop/reduce/sum instead.")
print("# - lru_cache only on pure functions with hashable arguments.")
print("# - Full tools tour: 05-Python Advanced/08-Itertools-And-Functools.py")
