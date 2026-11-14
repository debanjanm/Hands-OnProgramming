# 01. Generators - Introduction
# ------------------------------------
# - A generator is a special kind of iterator, created with `yield` instead
#   of `return`, that produces values lazily (one at a time, on demand).
# - Much less memory than building a full list upfront.

print("# 01. Generators - Introduction")
print("# ------------------------------------")

# 02. A Basic Generator Function
# ------------------------------------
def count_up_to(limit):
    n = 1
    while n <= limit:
        yield n  # pauses here, returns n, resumes on next call
        n += 1

print("\n# 02. A Basic Generator Function")
gen = count_up_to(5)
print("generator object:", gen)
print(next(gen))
print(next(gen))
for value in gen:  # continues from where next() left off
    print("remaining:", value)

# 03. Generators vs Regular Functions with Lists
# ------------------------------------
def squares_list(n):
    return [x ** 2 for x in range(n)]  # builds entire list in memory

def squares_gen(n):
    for x in range(n):
        yield x ** 2  # produces one value at a time

print("\n# 03. Generators vs Regular Functions with Lists")
print("list version:", squares_list(5))
print("generator version:", list(squares_gen(5)))
print("# - For huge n, squares_gen uses far less memory than squares_list.")

# 04. Generator Expressions
# ------------------------------------
# - Same syntax as list comprehension but with () - lazily evaluated.
gen_expr = (x ** 2 for x in range(5))
print("\n# 04. Generator Expressions")
print(gen_expr)
print(list(gen_expr))

# 05. StopIteration Happens Automatically
# ------------------------------------
print("\n# 05. StopIteration Happens Automatically")
gen = count_up_to(2)
print(next(gen))
print(next(gen))
try:
    next(gen)
except StopIteration:
    print("StopIteration raised when generator is exhausted")

# 06. yield from - Delegating to Another Generator/Iterable
# ------------------------------------
def inner_gen():
    yield 1
    yield 2

def outer_gen():
    yield "start"
    yield from inner_gen()  # delegates - yields 1, then 2
    yield "end"

print("\n# 06. yield from")
print(list(outer_gen()))

# 07. send() - Sending Values Into a Generator
# ------------------------------------
def running_total():
    total = 0
    while True:
        value = yield total  # receives value sent via .send()
        total += value

print("\n# 07. send()")
gen = running_total()
next(gen)  # prime the generator (advance to first yield)
print(gen.send(10))
print(gen.send(5))
print(gen.send(20))

# 08. throw() and close() - Controlling a Generator
# ------------------------------------
def controllable_gen():
    try:
        while True:
            yield "running"
    except ValueError:
        yield "caught ValueError inside generator"
    finally:
        print("generator cleanup on close")

print("\n# 08. throw() and close()")
gen = controllable_gen()
print(next(gen))
print(gen.throw(ValueError))  # injects exception at the yield point
gen.close()  # stops the generator, runs finally block

# 09. Infinite Generators (safe because lazy)
# ------------------------------------
def natural_numbers():
    n = 1
    while True:
        yield n
        n += 1

print("\n# 09. Infinite Generators")
gen = natural_numbers()
first_five = [next(gen) for _ in range(5)]
print("first five naturals:", first_five)

# 10. Chaining Generators (pipeline style)
# ------------------------------------
def evens(iterable):
    for x in iterable:
        if x % 2 == 0:
            yield x

def doubled(iterable):
    for x in iterable:
        yield x * 2

print("\n# 10. Chaining Generators (pipeline style)")
pipeline = doubled(evens(range(10)))
print(list(pipeline))

# 11. Generator Memory Profiling vs List Comprehension
# ------------------------------------
# - A list comprehension materializes every value at once; a generator
#   expression holds only its current state. For large ranges this is the
#   difference between megabytes and a few dozen bytes.
import sys

print("\n# 11. Generator Memory Profiling vs List Comprehension")
big_list_comp = [x * 2 for x in range(1_000_000)]
big_gen_expr = (x * 2 for x in range(1_000_000))
print("list comprehension size:", sys.getsizeof(big_list_comp), "bytes")
print("generator expression size:", sys.getsizeof(big_gen_expr), "bytes")

# 12. Coroutine-style Two-Way Communication - Running Average
# ------------------------------------
# - A more realistic use of send(): a generator that keeps a running average
#   and yields stats back after every new value it receives.
def running_average():
    count = 0
    total = 0
    average = None
    while True:
        value = yield {"count": count, "total": total, "average": average}
        count += 1
        total += value
        average = total / count

print("\n# 12. Coroutine-style Running Average")
stats_gen = running_average()
next(stats_gen)  # prime it
print(stats_gen.send(10))
print(stats_gen.send(20))
print(stats_gen.send(30))

# 13. contextlib.contextmanager - Built on Generators (reference)
# ------------------------------------
# - @contextlib.contextmanager turns a generator function into a context
#   manager: code before `yield` is __enter__, code after is __exit__.
# - Full depth (including exception handling inside it) lives in the
#   Context-Managers file - this is just a note on WHY it works: a generator
#   naturally pauses/resumes exactly like __enter__/__exit__ needs.
import contextlib

@contextlib.contextmanager
def announce(name):
    print(f"entering {name}")   # this is the __enter__ half
    yield name
    print(f"exiting {name}")    # this is the __exit__ half

print("\n# 13. contextlib.contextmanager (built on generators)")
with announce("demo-block") as label:
    print("inside block:", label)

# 14. Generator Exhaustion Checks - next(gen, default)
# ------------------------------------
# - Instead of wrapping next() in try/except StopIteration, pass a default
#   value as the second argument - it's returned once the generator is done.
print("\n# 14. Generator Exhaustion Checks with next(gen, default)")
small_gen = count_up_to(2)
print(next(small_gen, "no more values"))
print(next(small_gen, "no more values"))
print(next(small_gen, "no more values"))  # exhausted -> sentinel instead of exception

# 15. Lazy ETL-style Pipeline - Filter -> Transform -> Aggregate
# ------------------------------------
# - Each stage is a generator that pulls from the previous one. Nothing runs
#   until the final aggregate step starts consuming - true lazy evaluation.
def extract(rows):
    yield from rows  # source data, could just as easily be a file or DB cursor

def filter_valid(rows):
    for row in rows:
        if row["amount"] > 0:  # drop bad/negative records
            yield row

def transform(rows):
    for row in rows:
        yield {**row, "amount_with_tax": round(row["amount"] * 1.1, 2)}

def aggregate_total(rows):
    total = 0
    for row in rows:
        total += row["amount_with_tax"]
    return total

print("\n# 15. Lazy ETL Pipeline (filter -> transform -> aggregate)")
raw_rows = [{"amount": 100}, {"amount": -5}, {"amount": 50}, {"amount": 25}]
etl_pipeline = transform(filter_valid(extract(raw_rows)))
print("final total after filter+transform+aggregate:", aggregate_total(etl_pipeline))
