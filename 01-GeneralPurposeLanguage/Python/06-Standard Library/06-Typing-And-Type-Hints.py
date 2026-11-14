from typing import List, Dict, Optional, Union, Tuple, Callable, TypeVar, Protocol, TypedDict

# 01. Typing Module - Introduction
# ------------------------------------
# - Type hints document expected types; Python does NOT enforce them at
#   runtime (no error if violated) - tools like mypy check them statically.
# - Basic annotations (x: int) covered in 03-Functions/02-Functions.py #12; this file
#   covers the `typing` module's generic/composite types.

print("# 01. Typing Module - Introduction")
print("# ------------------------------------")

def add(a: int, b: int) -> int:
    return a + b

print("\nbasic annotation recap:", add(2, 3))
print("runtime does NOT enforce it:", add("2", "3"))  # no error, just string concat

# 02. Generic Collection Types
# ------------------------------------
def total(numbers: List[int]) -> int:
    return sum(numbers)

def user_ages(ages: Dict[str, int]) -> None:
    print(ages)

print("\n# 02. Generic Collection Types")
print(total([1, 2, 3]))
user_ages({"Debanjan": 25})

# 03. Optional - a Value or None
# ------------------------------------
def find_user(user_id: int) -> Optional[str]:  # same as Union[str, None]
    return "Debanjan" if user_id == 1 else None

print("\n# 03. Optional")
print(find_user(1))
print(find_user(2))

# 04. Union - One of Several Types
# ------------------------------------
def process(value: Union[int, str]) -> str:
    return f"processed {value}"

print("\n# 04. Union")
print(process(5))
print(process("five"))

# 05. Tuple with Fixed Structure
# ------------------------------------
def get_point() -> Tuple[int, int]:
    return (3, 4)

print("\n# 05. Tuple")
print(get_point())

# 06. Callable - Function Signatures as Types
# ------------------------------------
def apply(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

print("\n# 06. Callable")
print(apply(add, 4, 5))

# 07. TypeVar - Generic Functions
# ------------------------------------
T = TypeVar("T")

def first_item(items: List[T]) -> T:
    return items[0]

print("\n# 07. TypeVar")
print(first_item([1, 2, 3]))
print(first_item(["a", "b"]))

# 08. Protocol - Structural Typing (duck typing, but checkable)
# ------------------------------------
class HasSpeak(Protocol):
    def speak(self) -> str: ...

class Dog:
    def speak(self) -> str:
        return "Woof!"

def make_it_speak(entity: HasSpeak) -> None:
    print(entity.speak())  # any object with .speak() satisfies HasSpeak

print("\n# 08. Protocol")
make_it_speak(Dog())

# 09. TypedDict - Dicts with a Known Shape
# ------------------------------------
class Movie(TypedDict):
    title: str
    year: int

print("\n# 09. TypedDict")
movie: Movie = {"title": "Inception", "year": 2010}
print(movie)

# 10. Modern Syntax (Python 3.9+/3.10+) - reference
# ------------------------------------
print("\n# 10. Modern Syntax (reference)")
print("# - list[int] instead of List[int]           (3.9+, no import needed)")
print("# - dict[str, int] instead of Dict[str, int]  (3.9+)")
print("# - int | None instead of Optional[int]       (3.10+)")
print("# - int | str instead of Union[int, str]      (3.10+)")

def modern_add(a: int | None, b: int) -> int:
    return (a or 0) + b

print(modern_add(None, 5))

# 11. Literal - Restrict to Specific Values
# ------------------------------------
from typing import Literal

def set_mode(mode: Literal["read", "write", "append"]) -> str:
    return f"mode set to {mode}"  # a type checker flags mode="delete" as invalid

print("\n# 11. Literal")
print(set_mode("write"))

# 12. Final - Constants That Shouldn't Be Reassigned
# ------------------------------------
from typing import Final

MAX_RETRIES: Final = 3   # a type checker flags any later "MAX_RETRIES = 5"
print("\n# 12. Final")
print("MAX_RETRIES:", MAX_RETRIES)

# 13. @overload - Multiple Valid Signatures for One Function
# ------------------------------------
from typing import overload

@overload
def stringify(value: int) -> str: ...
@overload
def stringify(value: list) -> str: ...
def stringify(value):  # the actual implementation, no @overload here
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value)

print("\n# 13. @overload")
print(stringify(42))
print(stringify([1, 2, 3]))

# 14. NewType - Lightweight Distinct Types
# ------------------------------------
# - UserId is still an int at runtime (zero overhead) but a type checker
#   treats it as distinct, so passing a raw int where UserId is expected
#   is flagged as an error even though ints and UserIds print identically.
from typing import NewType

UserId = NewType("UserId", int)

def get_user(user_id: UserId) -> str:
    return f"user #{user_id}"

print("\n# 14. NewType")
uid = UserId(42)
print(get_user(uid))
print("still just an int at runtime:", type(uid))

# 15. TYPE_CHECKING - Import Only for Type Checkers
# ------------------------------------
# - Imports under this guard never run at runtime (avoids circular imports
#   and import cost), but are visible to type checkers like mypy.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import collections  # only "imported" during static analysis

print("\n# 15. TYPE_CHECKING")
print("# - Code under `if TYPE_CHECKING:` never executes at runtime.")
print("# - Use it for imports needed only for type hints.")

# 16. Any vs object
# ------------------------------------
# - Any turns off type checking entirely for that value - anything goes.
# - object is a real type: a type checker requires narrowing/casting
#   before you can call type-specific methods on it.
from typing import Any

def accepts_any(value: Any) -> None:
    value.whatever_method()  # type checker allows this, may fail at runtime

def accepts_object(value: object) -> None:
    print(str(value))  # only methods common to all objects are allowed

print("\n# 16. Any vs object")
accepts_object("hello")
print("# - Any: no static checking at all. object: safest, most restrictive.")

# 17. Type Aliases - Give a Complex Type a Name
# ------------------------------------
# - An alias is just a name for a type, so signatures stay readable.
# - Three spellings:
#     1) plain assignment      Alias = dict[str, list[int]]      (any version)
#     2) explicit TypeAlias    Alias: TypeAlias = dict[...]       (3.10+, tells checkers "this IS an alias")
#     3) `type` statement      type Alias = dict[...]             (3.12+, NEW SYNTAX)
# - The 3.12 `type` line would be a SyntaxError on older Python, so it is
#   compiled from a string only after a version check - the file still parses.
import sys
import typing

print("\n# 17. Type aliases")

Scores = dict[str, list[int]]               # 1) plain alias


def best(scores: Scores) -> str:
    return max(scores, key=lambda name: max(scores[name]))


print("plain alias:", Scores, "->", best({"ann": [3, 9], "bob": [7]}))

if sys.version_info >= (3, 10):
    from typing import TypeAlias
    Scores2: TypeAlias = dict[str, list[int]]   # 2) explicit alias
    print("TypeAlias  :", Scores2, "| same type as Scores?", Scores2 == Scores)
else:
    print("TypeAlias skipped: needs Python 3.10+")

if sys.version_info >= (3, 12):
    exec(compile('''
type Scores3 = dict[str, list[int]]          # 3) `type` statement (lazily evaluated)
print("type stmt  :", Scores3, "| kind:", type(Scores3).__name__, "| value:", Scores3.__value__)
''', "<type-stmt>", "exec"))
else:
    print("`type` statement skipped: needs Python 3.12+, this interpreter is", sys.version_info[:3])

# 18. Complex / Nested Aliases
# ------------------------------------
# - Build big types from small aliases, each name explains its meaning.
# - Aliases are NOT new types (unlike NewType): `UserId = int` is just `int`.
from typing import Callable, Optional, Union

print("\n# 18. Complex / nested aliases")
Json = Union[str, int, float, bool, None, list, dict]        # simple recursive-ish JSON-ish alias
Row = dict[str, Union[int, str]]
Table = list[Row]
Handler = Callable[[Row], Optional[str]]                     # row in, message or None out
Registry = dict[str, list[Handler]]                          # alias built from aliases


def run_handlers(table: Table, registry: Registry) -> list[str]:
    out = []
    for row in table:
        for fn in registry.get(str(row["kind"]), []):
            msg = fn(row)
            if msg is not None:
                out.append(msg)
    return out


registry: Registry = {"user": [lambda r: f"hello {r['name']}"], "bot": []}
table: Table = [{"kind": "user", "name": "ann"}, {"kind": "bot", "name": "r2"}]
print("run_handlers ->", run_handlers(table, registry))
UserId = int
print("alias is not a new type: UserId is int ->", UserId is int)

# 19. typing.cast - A Promise to the Checker, Nothing at Runtime
# ------------------------------------
# - cast(T, value) tells the type checker "trust me, this is a T".
# - At runtime it just returns `value` unchanged - NO conversion, NO check.
#   If you are wrong, the bug shows up later. Prefer isinstance() narrowing.
from typing import cast

print("\n# 19. typing.cast")
raw: object = "hello"
as_int = cast(int, raw)                     # checker now thinks it is int
print("cast(int, 'hello') ->", repr(as_int), "| type:", type(as_int).__name__, "| same object:", as_int is raw)
try:
    as_int + 1
except TypeError as e:
    print("the lie surfaces later:", e)

# 20. Generic[T] - A Typed Container Class
# ------------------------------------
# - Generic[T] makes a CLASS parametrised by a type: Stack[int], Stack[str].
# - A checker then knows push() takes T and pop() returns T.
# - At runtime Stack[int] is only a label; any value still goes in.
from typing import Generic, TypeVar

print("\n# 20. Generic[T] Stack")
T = TypeVar("T")


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def __len__(self) -> int:
        return len(self._items)


ints: Stack[int] = Stack()
ints.push(1)
ints.push(2)
print("pop ->", ints.pop(), "| len:", len(ints), "| Stack[int] is a", type(Stack[int]).__name__)
ints.push("oops")  # mypy: Argument 1 has incompatible type "str"; Python does not care
print("runtime does not enforce T: items =", ints._items)

if sys.version_info >= (3, 12):
    exec(compile('''
class Stack312[T]:                          # 3.12 syntax: no TypeVar / Generic[T] needed
    def __init__(self) -> None:
        self._items: list[T] = []
    def push(self, item: T) -> None:
        self._items.append(item)
    def pop(self) -> T:
        return self._items.pop()

s = Stack312[str]()
s.push("a")
print("3.12 class Stack312[T]:", s.pop(), "| type params:", Stack312.__type_params__)
''', "<pep695>", "exec"))
else:
    print("class Stack[T]: syntax skipped: needs Python 3.12+")

# 21. TypeVar with bound= and Constraints
# ------------------------------------
# - bound=X   : T may be X or ANY subclass; return type keeps the exact subclass.
# - (A, B)    : T must be exactly one of the listed types (a "constrained" TypeVar).
# - Both are checker-only; at runtime nothing stops a wrong type.
print("\n# 21. TypeVar bound / constraints")


class Animal:
    def __init__(self, name: str) -> None:
        self.name = name


class Dog(Animal):
    def bark(self) -> str:
        return f"{self.name}: woof"


A = TypeVar("A", bound=Animal)              # any Animal or subclass; the exact type is kept
S = TypeVar("S", str, bytes)                # either str OR bytes, not mixed


def longest_name(a: A, b: A) -> A:
    return a if len(a.name) >= len(b.name) else b


def join_pair(a: S, b: S) -> S:
    return a + b


winner = longest_name(Dog("rex"), Dog("fido"))
print("bound keeps the subclass: result is", type(winner).__name__, "->", winner.bark())   # .bark() OK for the checker
print("join_pair:", join_pair("ab", "cd"), join_pair(b"ab", b"cd"))
print("bound:", A.__bound__.__name__, "| constraints:", S.__constraints__)
print("mixing str+bytes: the checker rejects it; at runtime it only fails when executed:")
try:
    join_pair("a", b"b")
except TypeError as e:
    print("  TypeError:", e)

# 22. ParamSpec + Callable[P, R] - A Typed Decorator
# ------------------------------------
# - A plain `Callable[..., R]` decorator loses the wrapped function's
#   parameter types. ParamSpec (3.10+) captures them so the checker still
#   knows `add(a: int, b: int)` after decoration.
print("\n# 22. ParamSpec decorator")
if sys.version_info >= (3, 10):
    import functools
    from typing import ParamSpec

    P = ParamSpec("P")
    R = TypeVar("R")

    def logged(fn: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            result = fn(*args, **kwargs)
            print(f"   {fn.__name__}{args} -> {result!r}")
            return result
        return wrapper

    @logged
    def add(a: int, b: int = 0) -> int:
        return a + b

    add(2, b=3)
    print("signature kept for tools:", add.__name__, "| annotations:", add.__annotations__)
else:
    print("skipped: ParamSpec needs Python 3.10+")

# 23. Self - Methods That Return "My Own Type"
# ------------------------------------
# - Self (3.11+) = "an instance of whatever class this is", so a method on a
#   base class returns the SUBCLASS when called on a subclass (fluent APIs).
print("\n# 23. Self")
if sys.version_info >= (3, 11):
    from typing import Self

    class Builder:
        def __init__(self) -> None:
            self.parts: list[str] = []

        def add(self, part: str) -> Self:
            self.parts.append(part)
            return self

    class HtmlBuilder(Builder):
        def bold(self) -> Self:
            self.parts[-1] = f"<b>{self.parts[-1]}</b>"
            return self

    b = HtmlBuilder().add("hi").bold().add("there")   # add() keeps the HtmlBuilder type, so .bold() is OK
    print("chain:", b.parts, "| type:", type(b).__name__)
else:
    print("skipped: typing.Self needs Python 3.11+, this interpreter is", sys.version_info[:3])

# 24. ClassVar - Shared by the Class, Not Per Instance
# ------------------------------------
# - ClassVar[int] says "this attribute belongs to the class". A checker flags
#   `obj.count = 5` (which would create a per-instance copy); Python allows it.
from typing import ClassVar

print("\n# 24. ClassVar")


class Counter:
    created: ClassVar[int] = 0              # class-level, shared
    name: str                               # instance-level

    def __init__(self, name: str) -> None:
        self.name = name
        Counter.created += 1


Counter("a")
Counter("b")
print("Counter.created =", Counter.created)
c = Counter("c")
c.created = 99                              # checker: error. Python: shadows the class value on this instance
print("instance copy:", c.created, "| class value untouched:", Counter.created)

# 25. NoReturn / Never - Functions That Never Come Back
# ------------------------------------
# - NoReturn: the function always raises (or exits), it never returns normally.
#   The checker then knows code after the call is unreachable.
# - Never (3.11+) is the same idea as a general "no value possible" type; it
#   is mainly used with assert_never() to prove every case was handled.
from typing import NoReturn

print("\n# 25. NoReturn / Never")


def fail(msg: str) -> NoReturn:
    raise RuntimeError(msg)


def to_int(text: str) -> int:
    if text.isdigit():
        return int(text)
    fail(f"not a number: {text!r}")         # no `return` needed after - the checker knows


print("to_int('7') =", to_int("7"))
try:
    to_int("x")
except RuntimeError as e:
    print("NoReturn function raised:", e)

if sys.version_info >= (3, 11):
    from typing import Literal, Never, assert_never

    def describe(mode: Literal["r", "w"]) -> str:
        if mode == "r":
            return "read"
        elif mode == "w":
            return "write"
        else:
            assert_never(mode)              # checker errors here if a new mode is added but not handled

    print("describe:", describe("r"), describe("w"), "| Never is", Never)
else:
    print("Never/assert_never skipped: needs Python 3.11+")

# 26. Parameters: Accept General, Return Specific
# ------------------------------------
# - Parameters: use the WIDEST abstract type that works (Iterable, Sequence,
#   Mapping) so callers can pass lists, tuples, sets, generators...
# - Returns: use the CONCRETE type you really give back (list, dict) so
#   callers know exactly what they can do with the result.
#     Iterable  - can loop once            (list, tuple, set, generator)
#     Sequence  - loop + index + len       (list, tuple, str, range)
#     Mapping   - read-only dict-like      (dict, MappingProxyType, ...)
from collections.abc import Iterable, Mapping, Sequence

print("\n# 26. Accept general, return specific")


def squares(nums: Iterable[int]) -> list[int]:          # in: anything iterable, out: a real list
    return [n * n for n in nums]


def middle(items: Sequence[int]) -> int:                # needs indexing + len, so Sequence not Iterable
    return items[len(items) // 2]


def total_price(prices: Mapping[str, float]) -> float:  # only READS, so Mapping promises no mutation
    return sum(prices.values())


print("squares(list)     :", squares([1, 2, 3]))
print("squares(tuple)    :", squares((4, 5)))
print("squares(set)      :", squares({6}))
print("squares(generator):", squares(n for n in range(3)))
print("middle(tuple)     :", middle((10, 20, 30)), "| total_price:", total_price({"a": 1.5, "b": 2.0}))
try:
    middle(n for n in range(3))             # checker flags: a generator is Iterable but not a Sequence
except TypeError as e:
    print("generator is not a Sequence:", e)

# 27. Optional Defaults: `= None` and the Mutable-Default Trap
# ------------------------------------
# - `Optional[list[int]] = None` means "a list or None; None if not given".
# - Never write `items: list[int] = []`: that ONE list is created at def time
#   and shared by every call (a classic bug).
# - Replace None inside the function - but test `is None`, NOT falsiness,
#   or you throw away a legitimate empty list the caller passed in.
print("\n# 27. Optional + mutable default")


def bad_append(x: int, bucket: list[int] = []) -> list[int]:   # noqa: B006 - the trap, on purpose
    bucket.append(x)
    return bucket


print("bad :", bad_append(1), bad_append(2), "<- shared list! second call sees the first value")


def good_append(x: int, bucket: Optional[list[int]] = None) -> list[int]:
    if bucket is None:                      # `is None`, not `if not bucket`
        bucket = []
    bucket.append(x)
    return bucket


print("good:", good_append(1), good_append(2))
mine: list[int] = []
good_append(5, mine)
print("caller's empty list is respected:", mine)


def sloppy_append(x: int, bucket: Optional[list[int]] = None) -> list[int]:
    bucket = bucket or []                   # BUG: an empty list is falsy, so it is replaced
    bucket.append(x)
    return bucket


theirs: list[int] = []
sloppy_append(5, theirs)
print("sloppy `or []` ignored the caller's list:", theirs)

# 28. Reading Hints at Runtime - __annotations__ and get_type_hints
# ------------------------------------
# - Hints are stored on the object: `fn.__annotations__` (raw), and
#   `typing.get_type_hints(fn)` (resolves string hints like "int" to real types).
# - Libraries (pydantic, dataclasses, FastAPI) are built on exactly this.
print("\n# 28. Reading hints at runtime")


def connect(host: str, port: int = 80, *, tags: Optional[list[str]] = None) -> bool:
    return True


print("__annotations__:", connect.__annotations__)
print("get_type_hints :", typing.get_type_hints(connect))
print("origin/args of list[str]:", typing.get_origin(list[str]), typing.get_args(list[str]))
print("args of Optional[list[str]]:", typing.get_args(Optional[list[str]]))

# A tiny runtime validator built on top of get_type_hints.
import inspect


def _matches(value, hint) -> bool:
    origin, args = typing.get_origin(hint), typing.get_args(hint)
    if hint is typing.Any:
        return True
    if origin is Union:                     # Optional[X] is Union[X, None]
        return any(_matches(value, a) for a in args)
    if origin is list:
        return isinstance(value, list) and all(_matches(v, args[0]) for v in value)
    if hint is type(None):
        return value is None
    return isinstance(value, hint)          # plain classes: int, str, ...


def validate(fn):
    hints = typing.get_type_hints(fn)
    sig = inspect.signature(fn)

    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        for name, value in bound.arguments.items():
            if name in hints and not _matches(value, hints[name]):
                raise TypeError(f"{name}={value!r} is not {hints[name]}")
        return fn(*args, **kwargs)
    return wrapper


@validate
def repeat(word: str, times: int, extras: Optional[list[str]] = None) -> str:
    return (word * times) + "".join(extras or [])


print("valid call  :", repeat("ab", 2, ["!"]))
for bad in (("ab", "2"), ("ab", 2, [1, 2])):
    try:
        repeat(*bad)
    except TypeError as e:
        print("rejected    :", e)
print("# - Hints do nothing by themselves; only code like this (or a checker) acts on them.")

# 29. `from __future__ import annotations` - Hints Become Strings
# ------------------------------------
# - With this import, annotations are NOT evaluated when the def runs; they
#   are stored as plain strings. Benefits: forward references work without
#   quotes, and no runtime cost for fancy hints.
# - Cost: `__annotations__` holds STRINGS; use get_type_hints() to resolve.
# - It must be the FIRST statement of a module, so this demo compiles a tiny
#   module from a string.
print("\n# 29. from __future__ import annotations")
source = '''
from __future__ import annotations
import typing

class Node:
    def link(self, other: Node) -> Node:      # Node is not defined yet - fine, it stays a string
        return other

def f(x: int, y: list[int] | None = None) -> str: ...

print("raw annotations :", Node.link.__annotations__)
print("f annotations   :", f.__annotations__)
'''
ns: dict = {"__name__": "future_demo"}
exec(compile(source, "<future-demo>", "exec"), ns)
print("resolved by get_type_hints:", typing.get_type_hints(ns["f"]) if sys.version_info >= (3, 10)
      else "skipped: `X | None` needs 3.10+ to resolve")

try:
    exec("class A:\n    def m(self) -> A: ...\n", {})
except NameError as e:
    print("WITHOUT the future import, a forward reference fails at def time:", e)

# 30. How to Actually Run a Type Checker
# ------------------------------------
# - Python never checks hints. A separate tool reads your code and reports
#   mismatches BEFORE you run it. Typical setup: run it in your editor and CI.
# - Reference (not executed here):
#       python -m pip install mypy            # the reference checker
#       mypy script.py                        # check one file
#       mypy src/                             # check a folder
#       mypy --strict script.py               # all optional checks on
#       python -m pip install pyright         # alternative (Microsoft); powers Pylance in VS Code
#       pyright script.py
#   Settings go in pyproject.toml under [tool.mypy] / [tool.pyright].
# - A checker reports e.g.  error: Incompatible types in assignment
#   (expression has type "str", variable has type "int").
print("\n# 30. Running a type checker (reference)")
print("   python -m pip install mypy && mypy script.py   |   mypy --strict script.py   |   pyright script.py")
print("   The snippets below each have a type error a checker would flag - yet Python runs them.")

# (a) wrong type in an annotated assignment
age: int = "forty"                          # mypy: Incompatible types in assignment
print("(a) age =", repr(age), "(annotation says int)")


# (b) function returns something other than its declared type
def label(n: int) -> str:
    return n                                # mypy: Incompatible return value type (got "int", expected "str")


print("(b) label(7) =", repr(label(7)), "-> type", type(label(7)).__name__)


# (c) forgetting that Optional can be None
def first_even(nums: list[int]) -> Optional[int]:
    for n in nums:
        if n % 2 == 0:
            return n
    return None


print("(c) first_even([2, 3]) + 1 =", first_even([2, 3]) + 1)    # mypy: Unsupported operand types for + ("None" and "int")
try:
    first_even([1, 3]) + 1                  # the real crash the checker predicted
except TypeError as e:
    print("(c) ...and with no even number:", e)
print("# - To silence ONE checker error on purpose: `# type: ignore[code]` (use rarely, with a reason).")
