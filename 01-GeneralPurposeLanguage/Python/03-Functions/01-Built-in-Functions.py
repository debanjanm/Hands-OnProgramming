import ast
import builtins
import contextlib
import io
import itertools
import math
import os
import subprocess
import sys
import tempfile

# 01. Built-in Functions - a guided tour
# ------------------------------------
# - Built-ins are names Python gives you with NO import: print, len, sorted...
# - They live in the `builtins` module. When you write `len`, Python looks in
#   your local scope, then globals, then `builtins` (the LEGB rule's "B").
# - Knowing them well is the cheapest way to write shorter, faster, more
#   "Pythonic" code. They are implemented in C, so they are usually faster
#   than hand-written loops.
# - Tour order: output/input -> numbers -> sequences -> types/introspection
#   -> objects -> text -> code execution -> misc -> the builtins module itself.

print("# 01. Built-in Functions - a guided tour")
print("# ------------------------------------")

# 02. print() - sep, end, file, flush
# ------------------------------------
# - print(*values, sep=" ", end="\n", file=sys.stdout, flush=False)
# - sep   : text put BETWEEN values.
# - end   : text put AFTER the last value (default newline).
# - file  : any object with .write() - a real file, sys.stderr, StringIO...
# - flush : push output out immediately (matters for progress bars / logs
#           when stdout is piped and normally buffered).

print("\n# 02. print()")
print("a", "b", "c")                # default: space between
print("a", "b", "c", sep="-")       # custom separator
print("loading", end="...")         # no newline
print("done")                       # continues the same line
items = ["x", "y", "z"]
print(*items, sep=", ")             # * unpacks a list into separate arguments
print("2025", "01", "15", sep="")   # sep="" glues values together
sink = io.StringIO()
print("captured, not shown", file=sink)
print("what went into the StringIO:", repr(sink.getvalue()))
print("to stderr (hidden from stdout)", file=sys.stderr, flush=True) if False else None
# - GOTCHA: print() returns None. `x = print("hi")` makes x None.
print("print() returns:", print("(side effect only)"))

# 03. input() - always returns a string
# ------------------------------------
# - input(prompt) shows the prompt, waits for Enter, returns the line WITHOUT
#   the newline - always as `str`, even if the user typed digits.
# - This file must run unattended, so we temporarily replace sys.stdin with
#   a StringIO holding "typed" answers. Real use: just call input().
# - At end of input it raises EOFError (e.g. when piped from an empty file).

print("\n# 03. input()")
real_stdin = sys.stdin
sys.stdin = io.StringIO("Asha\n21\n")
try:
    name = input("Name? ")
    age_text = input("Age? ")
finally:
    sys.stdin = real_stdin
print()  # the simulated user never pressed a real Enter on screen
print("name =", repr(name), "| age =", repr(age_text), "<- still a str!")
print("age + 1 =", int(age_text) + 1, "(convert before arithmetic)")
sys.stdin = io.StringIO("")
try:
    input()
except EOFError as e:
    print("empty stdin ->", type(e).__name__)
finally:
    sys.stdin = real_stdin

# 04. repr() vs str() vs ascii() vs format()
# ------------------------------------
# - str(x)   : friendly text for USERS (what print shows).
# - repr(x)  : unambiguous text for DEVELOPERS; ideally looks like code that
#              recreates x. Used by the REPL, debuggers, and inside containers.
# - ascii(x) : like repr but escapes every non-ASCII character.
# - format(x, spec) : apply the format mini-language (same as f"{x:spec}").

print("\n# 04. repr / str / ascii / format")
text = "café\ttab\nnewline"
print("str  :", str(text))
print("repr :", repr(text))
print("ascii:", ascii(text))
import datetime
d = datetime.date(2025, 1, 15)
print("str(date) :", str(d), "| repr(date):", repr(d))
print("list uses repr for its items:", ["a", 1, d.year], "<- note the quotes on 'a'")
print("format(1234567.891, ',.2f') :", format(1234567.891, ",.2f"))
print("format(255, '08b')          :", format(255, "08b"), "(8-bit binary)")
print("format(255, '#x')           :", format(255, "#x"))
print("format(0.256, '.1%')        :", format(0.256, ".1%"))
print("format('hi', '>8') / '^8'   :", repr(format("hi", ">8")), repr(format("hi", "^8")))

# 05. Numbers: abs, round, divmod, pow
# ------------------------------------
print("\n# 05. abs / round / divmod / pow")
print("abs(-7.5), abs(-3)      :", abs(-7.5), abs(-3))
print("abs(3+4j) (magnitude)   :", abs(3 + 4j))

# - round(x) uses BANKER'S ROUNDING: exact halves go to the nearest EVEN
#   number. This avoids a systematic upward bias when rounding lots of data.
print("round(0.5), round(1.5), round(2.5), round(3.5) :", round(0.5), round(1.5), round(2.5), round(3.5))
print("round(3.14159, 2)       :", round(3.14159, 2))
print("round(1234, -2)         :", round(1234, -2), "(negative digits round to hundreds)")
# - GOTCHA 2: floats can't store 2.675 exactly, so it is really 2.67499999...
print("round(2.675, 2)         :", round(2.675, 2), "<- not 2.68! (float representation)")
print("For 'school' rounding use decimal.Decimal(...).quantize(..., ROUND_HALF_UP).")

# - divmod(a, b) = (a // b, a % b) in ONE step. Floors toward -infinity.
print("divmod(17, 5)           :", divmod(17, 5))
print("divmod(-7, 2)           :", divmod(-7, 2), "<- floors down, not toward zero")
print("divmod(125, 60) as min/sec:", divmod(125, 60))

# - pow(base, exp) == base ** exp. The 3-argument form pow(b, e, m) computes
#   (b ** e) % m efficiently even for HUGE numbers (cryptography uses this).
print("pow(2, 10)              :", pow(2, 10))
print("pow(3, 4, 5)            :", pow(3, 4, 5), "(81 % 5)")
print("pow(2, 10**6, 97)       :", pow(2, 10**6, 97), "(instant; 2**1000000 first would be huge)")
print("pow(3, -1, 7)           :", pow(3, -1, 7), "(modular inverse: 3*5 % 7 == 1)")

# 06. Numbers: sum, min, max
# ------------------------------------
# - sum(iterable, start=0): the start value is the initial total, and also
#   decides the result type - which is how you can sum lists.
print("\n# 06. sum / min / max")
print("sum([1, 2, 3])          :", sum([1, 2, 3]))
print("sum([1, 2, 3], 100)     :", sum([1, 2, 3], 100), "(start=100)")
print("sum([[1], [2, 3]], [])  :", sum([[1], [2, 3]], []), "(flatten - but O(n^2), prefer itertools.chain)")
try:
    sum(["a", "b"])
except TypeError as e:
    print("sum of strings          : TypeError:", e)
    print("   use ''.join(['a', 'b']) ->", "".join(["a", "b"]))
print("sum([0.1] * 10)         :", sum([0.1] * 10), "<- float rounding error accumulates")
print("math.fsum([0.1] * 10)   :", math.fsum([0.1] * 10), "<- tracks lost digits, exact here")

print("min(3, 1, 2), max([4, 9, 2]) :", min(3, 1, 2), max([4, 9, 2]))
words = ["pear", "fig", "banana", "kiwi"]
print("max(words)              :", max(words), "(alphabetical)")
print("max(words, key=len)     :", max(words, key=len), "(key = how to compare)")
print("min(words, key=len)     :", min(words, key=len), "(ties -> FIRST one wins)")
try:
    max([])
except ValueError as e:
    print("max([])                 : ValueError:", e)
print("max([], default=None)   :", max([], default=None), "(default= avoids the crash)")
print("max of dict by value    :", max({"a": 3, "b": 9}.items(), key=lambda kv: kv[1]))

# 07. Number bases and constructors: bin / hex / oct / int / float / bool / complex
# ------------------------------------
print("\n# 07. bin / hex / oct / int(base) / complex")
print("bin(10), hex(255), oct(8)    :", bin(10), hex(255), oct(8), "(all return STRINGS)")
print("int('1010', 2)               :", int("1010", 2))
print("int('ff', 16), int('z', 36)  :", int("ff", 16), int("z", 36))
print("int('0x1f', 16), int('0b11', 0):", int("0x1f", 16), int("0b11", 0), "(base 0 = read the prefix)")
print("int(4.9), int(-4.9)          :", int(4.9), int(-4.9), "<- truncates toward ZERO (not floor/round)")
print("int(' 42 ')                  :", int(" 42 "), "(whitespace is fine)")
try:
    int("4.2")
except ValueError as e:
    print("int('4.2')                   : ValueError:", e, "-> use int(float('4.2'))")
print("float('3.5'), float('inf')   :", float("3.5"), float("inf"))
nan = float("nan")
print("nan == nan                   :", nan == nan, "<- NaN is never equal to itself; use math.isnan")
print("bool(0), bool(''), bool([]), bool('0'):", bool(0), bool(""), bool([]), bool("0"), "<- non-empty string '0' is True")
z = complex(3, 4)
print("complex(3, 4)                :", z, "| real/imag:", z.real, z.imag, "| abs:", abs(z))
print("(1+2j) * (3-1j)              :", (1 + 2j) * (3 - 1j))
print("complex('1+2j')              :", complex("1+2j"), "(no spaces allowed inside the string)")

# 08. Sequences: len / range / enumerate
# ------------------------------------
print("\n# 08. len / range / enumerate")
print("len('hello'), len([1, 2]), len({'a': 1}) :", len("hello"), len([1, 2]), len({"a": 1}))
# - range is LAZY: it stores only start/stop/step, not the numbers.
big = range(10**12)
print("len(range(10**12))           :", len(big), "(created instantly, uses almost no memory)")
print("999_999_999_999 in big       :", 999_999_999_999 in big, "(membership is arithmetic, not a scan)")
print("list(range(0, 10, 3))        :", list(range(0, 10, 3)))
print("list(range(5, 0, -1))        :", list(range(5, 0, -1)), "(stop is EXCLUDED)")
try:
    range(0, 1, 0.1)
except TypeError as e:
    print("range with float step        : TypeError:", e)

fruits = ["apple", "banana", "cherry"]
print("list(enumerate(fruits))      :", list(enumerate(fruits)))
for i, fruit in enumerate(fruits, start=1):
    print(f"   {i}. {fruit}")
print("(prefer enumerate over range(len(x)) - no manual indexing)")

# 09. Sequences: zip / reversed / sorted
# ------------------------------------
print("\n# 09. zip / reversed / sorted")
names = ["Asha", "Ben", "Chen"]
scores = [90, 85]
print("zip stops at the SHORTEST   :", list(zip(names, scores)), "<- Chen silently dropped!")
print("itertools.zip_longest       :", list(itertools.zip_longest(names, scores, fillvalue=0)))
if sys.version_info >= (3, 10):
    try:
        list(zip(names, scores, strict=True))
    except ValueError as e:
        print("zip(..., strict=True)       : ValueError:", e)
else:
    print("zip(strict=True) skipped: needs Python 3.10+")
matrix = [[1, 2, 3], [4, 5, 6]]
print("transpose with zip(*matrix) :", list(zip(*matrix)))
print("dict from two lists         :", dict(zip(["a", "b"], [1, 2])))

print("list(reversed([1, 2, 3]))   :", list(reversed([1, 2, 3])), "| reversed('abc'):", "".join(reversed("abc")))
print("reversed() returns an iterator:", reversed([1, 2]))
try:
    reversed(x for x in range(3))
except TypeError as e:
    print("reversed(generator)         : TypeError:", e)

nums = [5, 2, 9, 1]
print("sorted(nums)                :", sorted(nums), "| original untouched:", nums)
print("sorted(nums, reverse=True)  :", sorted(nums, reverse=True))
print("sorted(words, key=len)      :", sorted(words, key=len), "(stable: equal keys keep original order)")
print("sorted(words, key=str.lower):", sorted(["b", "A", "c"], key=str.lower), "vs default:", sorted(["b", "A", "c"]))
people = [("Asha", 30), ("Ben", 25), ("Chen", 30)]
print("sort by age desc, name asc  :", sorted(people, key=lambda p: (-p[1], p[0])))
try:
    sorted([3, "a"])
except TypeError as e:
    print("sorted([3, 'a'])            : TypeError:", e)
print("GOTCHA: nums.sort() sorts IN PLACE and returns None; sorted(nums) returns a NEW list.")

# 10. Sequences: iter / next / map / filter / any / all / slice
# ------------------------------------
print("\n# 10. iter / next / map / filter / any / all / slice")
it = iter([10, 20])
print("next(it), next(it)          :", next(it), next(it))
print("next(it, 'finished')        :", next(it, "finished"), "(default instead of StopIteration)")
try:
    next(it)
except StopIteration:
    print("next(it) without default    : StopIteration (the loop-ending signal)")
# Two-argument iter(callable, sentinel): call repeatedly until sentinel appears.
stream = io.StringIO("abcdefgh")
print("iter(read-3-chars, '')      :", list(iter(lambda: stream.read(3), "")))

doubled = map(lambda n: n * 2, [1, 2, 3])
print("map is lazy                 :", doubled)
print("list(map(...))              :", list(doubled))
print("map object is single-use    :", list(doubled), "<- already exhausted!")
print("map with two iterables      :", list(map(pow, [2, 3], [3, 2])))
print("filter(pred, data)          :", list(filter(lambda n: n % 2 == 0, range(10))))
print("filter(None, data)          :", list(filter(None, [0, 1, "", "a", None, [], [0]])), "<- keeps truthy values")
print("(comprehensions [f(x) for x in data if p(x)] are often clearer than map/filter)")

print("any([]), all([])            :", any([]), all([]), "<- empty: any is False, all is True (vacuous truth)")
print("any(n > 8 for n in nums)    :", any(n > 8 for n in nums))
print("all(n > 0 for n in nums)    :", all(n > 0 for n in nums))


def noisy(n):
    print(f"   checking {n}")
    return n > 1


print("any() short-circuits (stops at the first True):")
any(noisy(n) for n in [0, 1, 2, 3, 4])

s = slice(1, 6, 2)
print("slice(1, 6, 2) on 'abcdefgh':", "abcdefgh"[s], "| s.indices(4):", s.indices(4), "(clamped to a length-4 sequence)")
print("same as text[1:6:2]         :", "abcdefgh"[1:6:2])

# 11. Types: type / isinstance / issubclass
# ------------------------------------
print("\n# 11. type / isinstance / issubclass")
print("type(3), type(3.0), type('3'):", type(3), type(3.0), type("3"))
print("isinstance(3, int)          :", isinstance(3, int))
print("isinstance(3, (int, float)) :", isinstance(3, (int, float)), "(tuple of types = 'any of these')")
print("isinstance(True, int)       :", isinstance(True, int), "<- bool IS a subclass of int!")
print("type(True) == int           :", type(True) == int, "(type() ignores inheritance; isinstance respects it)")
print("issubclass(bool, int)       :", issubclass(bool, int))
print("issubclass(KeyError, LookupError):", issubclass(KeyError, LookupError))


class Animal: ...
class Dog(Animal): ...


pet = Dog()
print("isinstance(pet, Animal)     :", isinstance(pet, Animal), "| type(pet) is Animal:", type(pet) is Animal)
print("Prefer isinstance() for type checks; use type(x) is T only when you need the EXACT class.")

# 12. Types: id / hash / callable
# ------------------------------------
print("\n# 12. id / hash / callable")
a = [1, 2]
b = a
c = [1, 2]
print("b = a  -> id equal          :", id(a) == id(b), "| a is b:", a is b)
print("c = [1,2] -> same value, different object:", a == c, a is c, id(a) == id(c))
print("(id is the object's identity; in CPython it is its memory address)")

print("hash(42), hash(1) == hash(1.0):", hash(42), hash(1) == hash(1.0), "(equal values must hash equal)")
print("hash((1, 2)) works for tuples:", isinstance(hash((1, 2)), int))
try:
    hash([1, 2])
except TypeError as e:
    print("hash([1, 2])                : TypeError:", e)
    print("   -> mutable containers can't be dict keys or set members; use a tuple.")
outs = {subprocess.run([sys.executable, "-c", "print(hash('a'))"], capture_output=True, text=True).stdout for _ in range(2)}
print("hash('a') in two separate runs:", "DIFFERENT (randomised per process)" if len(outs) == 2 else "same (PYTHONHASHSEED is set)",
      "-> never store str hashes in files.")

print("callable(len), callable('x'), callable(int):", callable(len), callable("x"), callable(int), "(classes are callable)")


class Greeter:
    def __call__(self, who):
        return f"hi {who}"


print("callable(Greeter()) / Greeter()('Asha') :", callable(Greeter()), "/", Greeter()("Asha"))

# 13. Introspection: dir / vars / globals / locals
# ------------------------------------
# - dir(x)    : list of attribute NAMES (sorted). dir() alone = names in scope.
# - vars(x)   : x.__dict__ - the actual name -> value mapping of an instance.
# - globals() : dict of module-level names. locals(): names in current scope.
# - Brief here; scopes get full coverage in a later functions file.

print("\n# 13. dir / vars / globals / locals")


class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def norm(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5


p = Point(3, 4)
print("public names in dir(p) :", [n for n in dir(p) if not n.startswith("_")])
print("vars(p)                :", vars(p), "<- only instance data, not methods")
print("'p' in globals()       :", "p" in globals(), "| globals()['__name__']:", globals()["__name__"])


def show_locals(first, second=2):
    third = first + second
    return locals()  # snapshot of the function's local names


print("locals() in a function :", show_locals(1))

# 14. Introspection: getattr / setattr / hasattr / delattr
# ------------------------------------
# - Access attributes by NAME held in a string - handy for plugins, config
#   driven code and generic tools. getattr(p, "x") == p.x
print("\n# 14. getattr / setattr / hasattr / delattr")
print("getattr(p, 'x')              :", getattr(p, "x"))
print("getattr(p, 'z', 'missing')   :", getattr(p, "z", "missing"), "(3rd arg = default, no error)")
try:
    getattr(p, "z")
except AttributeError as e:
    print("getattr(p, 'z')              : AttributeError:", e)
setattr(p, "z", 99)
print("after setattr(p,'z',99)      :", vars(p))
print("hasattr(p, 'z'), hasattr(p, 'q'):", hasattr(p, "z"), hasattr(p, "q"))
delattr(p, "z")
print("after delattr(p,'z')         :", vars(p))
op = "norm"  # method chosen at runtime
print("getattr(p, op)()             :", getattr(p, op)(), "(call a method by name)")
print("GOTCHA: hasattr() only swallows AttributeError; EAFP (try/except) or getattr with default is often cleaner.")


class Base:
    def hello(self):
        return "Base.hello"


class Child(Base):
    def hello(self):
        return "Child -> " + super().hello()  # super(): proxy to the parent class


print("super() demo                 :", Child().hello(), "(full coverage in the OOPs files)")

# 15. Objects: object / property / classmethod / staticmethod / bytes
# ------------------------------------
print("\n# 15. object, property/classmethod/staticmethod, bytes types")
# - object is the root of every class. A bare object() is a handy unique
#   "sentinel" that can never equal real data (e.g. to tell None from missing).
MISSING = object()
print("sentinel is unique           :", MISSING is not None, MISSING == object(), "| isinstance(5, object):", isinstance(5, object))


class Temperature:
    unit = "C"

    def __init__(self, celsius):
        self._c = celsius

    @property  # attribute-style access that runs code
    def fahrenheit(self):
        return self._c * 9 / 5 + 32

    @classmethod  # receives the CLASS (cls) - alternative constructors
    def from_f(cls, f):
        return cls((f - 32) * 5 / 9)

    @staticmethod  # receives neither - just a function living in the class
    def is_valid(c):
        return c >= -273.15


t = Temperature(100)
print("property / classmethod / staticmethod:", t.fahrenheit, Temperature.from_f(212)._c, Temperature.is_valid(-300))
print("(details live in the OOPs folder)")

print("bytes('hé', 'utf-8')         :", bytes("hé", "utf-8"), "| immutable raw bytes")
ba = bytearray(b"abc")
ba[0] = ord("X")
print("bytearray is mutable         :", ba)
mv = memoryview(ba)
mv[1] = ord("Y")  # writes THROUGH to ba - no copy
print("memoryview shares memory     :", ba, "| slice copy-free:", bytes(mv[1:]))

# 16. Text: chr / ord, and what is NOT a builtin
# ------------------------------------
print("\n# 16. chr / ord and str methods")
print("ord('A'), ord('a'), ord('€')  :", ord("A"), ord("a"), ord("€"))
print("chr(65), chr(8364), chr(128512) :", chr(65), ascii(chr(8364)), ascii(chr(128512)))
print("shift a letter (Caesar +1)   :", "".join(chr(ord(ch) + 1) for ch in "HAL"))
print("alphabet via chr/range       :", "".join(chr(n) for n in range(ord("a"), ord("a") + 5)))
# - `upper`, `split`, `strip`, `join`... are METHODS of str, not built-in
#   functions. They need an object: "abc".upper(), never upper("abc").
print("'len' is a builtin           :", hasattr(builtins, "len"))
print("'upper' is a builtin         :", hasattr(builtins, "upper"))
try:
    upper("abc")  # noqa: F821
except NameError as e:
    print("upper('abc')                 : NameError:", e)
print("but via the class it works   :", str.upper("abc"), "(str.upper IS the method, called unbound)")

# 17. Code execution: eval / exec / compile
# ------------------------------------
# - eval(src)         : evaluate ONE EXPRESSION string, return its value.
# - exec(src)         : run any statements (assignments, defs, loops); returns None.
# - compile(src, name, mode) : turn text into a code object once; mode is
#   'eval' (expression), 'exec' (statements) or 'single' (REPL line).
# - Both take dicts as the "globals/locals" they run in, so they don't have
#   to touch your real variables.

print("\n# 17. eval / exec / compile")
print("eval('2 + 3 * 4')            :", eval("2 + 3 * 4"))
print("eval('x * y', {'x': 6, 'y': 7}) :", eval("x * y", {"x": 6, "y": 7}))
ns = {}
exec("total = 0\nfor n in range(5):\n    total += n\ndef sq(v):\n    return v * v", ns)
print("exec ran statements; namespace now has total =", ns["total"], "and sq(9) =", ns["sq"](9))
code_obj = compile("10 + 5", "<demo>", "eval")
print("compile(...,'eval') ->", type(code_obj).__name__, "| eval(code_obj):", eval(code_obj))
print("compile once, eval many times:", [eval(code_obj) for _ in range(2)])
try:
    eval("x = 5")  # eval only takes EXPRESSIONS
except SyntaxError as e:
    print("eval('x = 5')                : SyntaxError - statements need exec()")

# - WHY eval/exec on untrusted input is dangerous:
#   they run ARBITRARY CODE with all your program's privileges. If any part
#   of the string comes from a user, a file, a web form or a network
#   message, the author of that text controls your machine: read/delete
#   files, steal secrets, install malware. This is "code injection".
print("\n-- The danger (harmless demo: this just asks which directory we're in) --")
user_input = "__import__('os').getcwd()"  # imagine a stranger typed this "calculator expression"
print("eval(user_input) ran Python code:", os.path.basename(eval(user_input)) != "")
print("A hostile string could have done the same with os.remove / os.system / reading ~/.ssh.")
# - 'Restricting' eval does NOT make it safe. Emptying __builtins__ is a known
#   leaky sandbox - the object graph still leads back to dangerous classes:
leak = eval("().__class__.__base__.__subclasses__()", {"__builtins__": {}})
print("even with __builtins__ emptied, eval reached", len(leak), "classes via an empty tuple.")

# - Safe alternative for DATA: ast.literal_eval. It only parses Python
#   LITERALS (numbers, strings, lists, dicts, tuples, sets, booleans, None) and
#   refuses anything that would execute.
print("\n-- Safe alternative: ast.literal_eval --")
data = ast.literal_eval("[1, {'a': (2, 3)}, None, True, 'text']")
print("literal_eval parsed          :", data)
for evil in ["__import__('os').getcwd()", "1 + 2", "open('x')"]:
    try:
        ast.literal_eval(evil)
    except (ValueError, SyntaxError) as e:
        print(f"literal_eval({evil!r:30}) refused: {type(e).__name__}")
print("Rules of thumb: never eval/exec untrusted text; for JSON use json.loads;")
print("for arithmetic write a tiny parser (or use ast) instead of eval.")

# 18. Misc: open / __import__ / breakpoint / help
# ------------------------------------
print("\n# 18. open / __import__ / breakpoint / help")
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "note.txt")
    with open(path, "w") as f:  # open() returns a file object; `with` closes it
        f.write("hello from open()")
    with open(path) as f:
        print("open() round trip            :", f.read())
print("(modes, encodings, seek, binary I/O: see 05-Python Advanced/04-File-Handling.py)")

math_mod = __import__("math")
print("__import__('math')           :", math_mod.__name__, "| sqrt(16) =", math_mod.sqrt(16))
print("(that is what the `import` statement calls; in real code use `import x` or importlib.import_module)")

# - breakpoint() drops you into the debugger (pdb) at that line - type `c`
#   to continue, `n` for next line, `p var` to print, `q` to quit.
#   We do NOT call it here (it would freeze an unattended script).
# - Environment variable PYTHONBREAKPOINT controls it:
#     PYTHONBREAKPOINT=0            -> breakpoint() does nothing (safe in prod)
#     PYTHONBREAKPOINT=ipdb.set_trace -> use another debugger
cp = subprocess.run(
    [sys.executable, "-c", "breakpoint(); print('ran straight through')"],
    capture_output=True, text=True, env=dict(os.environ, PYTHONBREAKPOINT="0"),
)
print("PYTHONBREAKPOINT=0 + breakpoint():", cp.stdout.strip())

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    help(abs)
print("help(abs) first lines        :", " | ".join(l.strip() for l in buf.getvalue().splitlines() if l.strip())[:100])

# 19. How many builtins are there?
# ------------------------------------
print("\n# 19. The builtins module")
public = [n for n in dir(builtins) if not n.startswith("_")]
print("public names in builtins     :", len(public), "(varies a little between Python versions)")
exceptions = [n for n in public if isinstance(getattr(builtins, n), type) and issubclass(getattr(builtins, n), BaseException)]
classes = [n for n in public if isinstance(getattr(builtins, n), type) and n not in exceptions]
constants = [n for n in public if n in ("True", "False", "None", "Ellipsis", "NotImplemented")]
functions = [n for n in public if n not in exceptions and n not in classes and n not in constants and callable(getattr(builtins, n))]
print(f"  exceptions : {len(exceptions)}  e.g. {exceptions[:4]}")
print(f"  classes    : {len(classes)}  (the type-like 'functions': int, str, list, dict, zip, map, range, enumerate...)")
print("               ", classes)
print(f"  constants  : {len(constants)}  {constants}")
print(f"  functions  : {len(functions)}")
print("               ", functions)
print("Note: `zip`, `map`, `range`, `int`, `list`... are really CLASSES that you call like functions.")
print("exit/quit/help/copyright/credits/license are added by the `site` module (absent with python -S).")
print("'aiter'/'anext' present (3.10+)?:", hasattr(builtins, "aiter"))

# 20. Shadowing builtins - the classic self-inflicted bug
# ------------------------------------
# - Builtins are ordinary names in the LAST scope Python checks. If you
#   assign a variable with the same name, YOUR value is found first and the
#   builtin becomes unreachable in that scope - no warning is given.
# - Frequent victims: list, dict, str, sum, max, min, input, id, type, file, len.
# - Fix: choose another name (items, total, user_id...). In an emergency,
#   `del name` removes your variable and the builtin shows through again.

print("\n# 20. Shadowing builtins")
print("before: list('abc')          :", list("abc"))
list = [1]  # oops - we just hid the builtin `list`
try:
    list("abc")
except TypeError as e:
    print("after `list = [1]`           : TypeError:", e)
print("builtins.list is still fine  :", builtins.list("abc"), "(the real one survives in the builtins module)")
del list  # remove OUR variable -> lookup falls through to builtins again
print("after `del list`             :", list("abc"))

sum = 0  # tempting variable name for a running total...
try:
    sum([1, 2, 3])
except TypeError as e:
    print("after `sum = 0`              : TypeError:", e)
del sum
print("after `del sum`              :", sum([1, 2, 3]))
print("Spot it early: linters (ruff A001/A002) flag shadowed builtins; or check `name in dir(builtins)`.")
print("e.g. 'id' in dir(builtins):", "id" in dir(builtins), "| 'total' in dir(builtins):", "total" in dir(builtins))
