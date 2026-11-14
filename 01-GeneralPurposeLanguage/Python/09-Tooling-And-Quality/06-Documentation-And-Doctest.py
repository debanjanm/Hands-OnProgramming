import argparse
import contextlib
import doctest
import importlib.util
import inspect
import io
import os
import pydoc
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

# 01. Documentation and doctest - Introduction
# ------------------------------------
# - Code is read many more times than it is written. Documentation is the
#   part of "reading" that the code itself cannot give you: WHY it exists,
#   HOW to call it, WHAT can go wrong.
# - The cheapest, most-likely-to-stay-correct documentation lives NEXT TO the
#   code: docstrings. Tools (help(), your editor, pydoc, Sphinx) read them.
# - doctest goes one step further: the examples in a docstring are RUN as
#   tests, so the documentation cannot silently go out of date.
# - Docs rot when they are far from the code and nobody checks them. Every
#   technique here is about keeping docs close, short, and verified.

print("# 01. Documentation and doctest - Introduction")
print("# ------------------------------------")

# 02. Helpers (a temp folder for generated sample modules)
# ------------------------------------
TMP_HOLDER = tempfile.TemporaryDirectory()
TMP = Path(TMP_HOLDER.name).resolve()
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", NO_COLOR="1")


def clean(text):
    text = text.replace(str(TMP), "<tmp>").replace(str(TMP.parent), "<tmpparent>")
    text = re.sub(r"\d+\.\d+s", "<time>", text)
    text = re.sub(r"0x[0-9a-f]{6,}", "0x<real-address>", text)
    text = re.sub(r'File "[^"]*doctest\.py", line \d+', 'File ".../doctest.py", line N', text)
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def show(text, limit=14, prefix="    | "):
    lines = text.rstrip("\n").splitlines()
    for line in lines[:limit]:
        print(prefix + line)
    if len(lines) > limit:
        print(f"{prefix}... ({len(lines) - limit} more lines)")


def load_module(name, source):
    """Write `source` to <tmp>/<name>.py and import it (no files outside TMP)."""
    path = TMP / f"{name}.py"
    path.write_text(source)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # doctest/pydoc look modules up here
    spec.loader.exec_module(module)
    return module


# 03. Docstrings - the first documentation
# ------------------------------------
# - A docstring is a string literal that is the FIRST statement of a module,
#   class, or function. Python stores it in the object's __doc__ attribute.
# - Everything that "shows help" reads __doc__: help(), editor hover tooltips,
#   pydoc, Sphinx, IDE autocomplete.
# - Use triple double quotes. One-liner for simple things; multi-line for more:
#       summary line (imperative: "Return ...", "Parse ...")
#       blank line
#       details / arguments / returns / raises / examples


def area(width, height):
    """Return the area of a rectangle."""
    return width * height


print("\n# 03. Docstrings are stored in __doc__")
print("  area.__doc__  ->", repr(area.__doc__))
print("  len.__doc__   ->", repr(len.__doc__))
print("# - Built-ins have docstrings too: that is what help(len) shows.")

# 04. The three common docstring styles - same function, three notations
# ------------------------------------
# - All three say the same things; they differ in how the sections look.
#   * Google style  - Args:/Returns:/Raises: with indented text. Easiest to
#                     read as PLAIN TEXT in the editor. A very good default.
#   * NumPy style   - sections with underlines (Parameters / ----------).
#                     Roomy and tabular; popular in scientific Python.
#   * reST/Sphinx   - ":param x:" field lists. Most verbose; the "native"
#                     Sphinx format. Fine, but noisy to read in plain text.
# - HOW TO PICK: choose ONE per project and enforce it (a linter or Sphinx's
#   napoleon extension understands Google and NumPy). New project and no
#   strong opinion? Google style. Data-science library? NumPy style.
# - These examples contain real doctests; section 20 runs them.


def convert_google(amount, rate, *, round_to=2):
    """Convert an amount using an exchange rate.

    Args:
        amount (float): Money in the source currency. Must not be negative.
        rate (float): How many target units one source unit buys.
        round_to (int): Decimal places in the result. Defaults to 2.

    Returns:
        float: The converted amount, rounded.

    Raises:
        ValueError: If ``amount`` is negative.

    Example:
        >>> convert_google(10, 1.5)
        15.0
    """
    if amount < 0:
        raise ValueError(f"amount must be >= 0, got {amount}")
    return round(amount * rate, round_to)


def convert_numpy(amount, rate, *, round_to=2):
    """
    Convert an amount using an exchange rate.

    Parameters
    ----------
    amount : float
        Money in the source currency. Must not be negative.
    rate : float
        How many target units one source unit buys.
    round_to : int, optional
        Decimal places in the result (default 2).

    Returns
    -------
    float
        The converted amount, rounded.

    Raises
    ------
    ValueError
        If ``amount`` is negative.

    Examples
    --------
    >>> convert_numpy(10, 1.5)
    15.0
    """
    if amount < 0:
        raise ValueError(f"amount must be >= 0, got {amount}")
    return round(amount * rate, round_to)


def convert_rest(amount, rate, *, round_to=2):
    """Convert an amount using an exchange rate.

    :param float amount: Money in the source currency. Must not be negative.
    :param float rate: How many target units one source unit buys.
    :param int round_to: Decimal places in the result. Defaults to 2.
    :returns: The converted amount, rounded.
    :rtype: float
    :raises ValueError: If ``amount`` is negative.

    >>> convert_rest(10, 1.5)
    15.0
    """
    if amount < 0:
        raise ValueError(f"amount must be >= 0, got {amount}")
    return round(amount * rate, round_to)


print("\n# 04. Three styles, one function")
for label, func in [("Google", convert_google), ("NumPy", convert_numpy), ("reST/Sphinx", convert_rest)]:
    print(f"  --- {label} ---")
    show(inspect.getdoc(func), 9, prefix="  ")
print("# - Same facts, different punctuation. Consistency matters more than the choice.")

# 05. What a GOOD docstring contains - and what it should NOT
# ------------------------------------
# - Contains:
#     1. Summary line   - one sentence, imperative, fits on one line.
#     2. Context        - WHY / WHEN to use it, if not obvious from the name.
#     3. Args           - meaning + units + allowed range (NOT just the type;
#                         the type already lives in the hint).
#     4. Returns        - what comes back, including special values (None, -1).
#     5. Raises         - which exceptions callers must be ready for.
#     6. Example        - a short, runnable call (see doctest below).
# - Should NOT:
#     * restate the code ("Adds a and b and returns the sum")
#     * describe HOW (internal steps) - that is what comments are for, and
#       the how changes more often than the contract
#     * repeat types that are already in the hints
#     * be a lie: an outdated docstring is worse than none


def tax_bad(price, rate):
    """Multiply price by rate and add it to price and return the result."""  # restates the code
    return price + price * rate


def tax_good(price, rate):
    """Return the price including sales tax.

    Args:
        price: Net price in rupees, before tax.
        rate: Tax as a fraction (0.18 for 18% GST), not a percentage.

    Returns:
        The gross price, unrounded. Round only when displaying it.
    """
    return price + price * rate


print("\n# 05. Good vs bad docstring")
print("  BAD :", tax_bad.__doc__)
print("  GOOD:", tax_good.__doc__.splitlines()[0])
print("        ...and tells the caller the unit (rupees), that rate is a FRACTION,")
print("        and that the result is unrounded - facts the code cannot say.")

# 06. Module, class, method and property docstrings
# ------------------------------------
# - Module docstring: first statement of the file. One paragraph: what the
#   module is for, plus a short usage example. Shown at the top of help(module).
# - Class docstring: what the class REPRESENTS and its public attributes.
#   Document __init__ arguments in the class docstring (the common convention).
# - Method docstring: same shape as a function; skip 'self'.
# - Property docstring: put it on the getter; it is what shows as the
#   attribute's description. Write it like a noun phrase ("The total..."),
#   not a verb phrase, because it is accessed like data.


class Account:
    """A bank account that can never go below zero.

    Attributes:
        owner: Name of the account holder.
    """

    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance

    @property
    def balance(self):
        """The current balance in rupees (read-only)."""
        return self._balance

    def withdraw(self, amount):
        """Remove money from the account.

        Raises:
            ValueError: If the account does not hold enough money.
        """
        if amount > self._balance:
            raise ValueError(f"cannot withdraw {amount}: balance is only {self._balance}")
        self._balance -= amount
        return self._balance


print("\n# 06. Class / method / property docstrings")
print("  Account.__doc__ first line :", Account.__doc__.splitlines()[0])
print("  Account.balance.__doc__    :", Account.balance.__doc__)
print("  Account.withdraw.__doc__   :", Account.withdraw.__doc__.splitlines()[0])

# 07. help(), inspect.getdoc() and the indentation clean-up
# ------------------------------------
# - __doc__ is the RAW text: it still contains the indentation of the source.
# - inspect.getdoc() (and inspect.cleandoc) removes that common indentation
#   and leading/trailing blank lines - this is what help() displays.
# - Bonus: getdoc() on a METHOD that has no docstring walks up to the parent
#   class's method docstring, so overriding a method inherits its docs.

print("\n# 07. __doc__ (raw) vs inspect.getdoc (cleaned)")
print("  raw   :", repr(Account.withdraw.__doc__))
print("  clean :", repr(inspect.getdoc(Account.withdraw)))


class Savings(Account):
    def withdraw(self, amount):  # no docstring on purpose
        return super().withdraw(amount)


print("  Savings.withdraw.__doc__ ->", Savings.withdraw.__doc__)
print("  inspect.getdoc(Savings.withdraw) first line ->", inspect.getdoc(Savings.withdraw).splitlines()[0])

print("\n  help(Account.withdraw) output (captured; in a terminal it opens a pager):")
buffer = io.StringIO()
with contextlib.redirect_stdout(buffer):
    help(Account.withdraw)
show(buffer.getvalue(), 8, prefix="  ")

# 08. pydoc - documentation generated from docstrings, no extra tools
# ------------------------------------
# - pydoc is in the standard library. From a shell:
#       python -m pydoc mymodule         show docs in the terminal
#       python -m pydoc -w mymodule      write mymodule.html in the CURRENT folder
#       python -m pydoc -b               start a local browser server of everything
# - pydoc.render_doc(obj) returns the same text as a string (used below).
# - It is rough but zero-setup. For polished sites see section 18.

SHOP_SOURCE = '''"""Shop helpers: prices, carts and receipts.

Typical use::

    cart = Cart()
    cart.add("pen", 2, 10.0)
    cart.total()
"""

__all__ = ["Cart", "apply_discount"]


def apply_discount(price: float, percent: float = 10.0) -> float:
    """Return `price` reduced by `percent` percent.

    Raises:
        ValueError: If `percent` is outside 0-100.
    """
    if not 0 <= percent <= 100:
        raise ValueError(f"percent must be between 0 and 100, got {percent}")
    return price * (1 - percent / 100)


def _internal_helper():
    """Not part of the public API (leading underscore)."""


class Cart:
    """A shopping cart holding (name, quantity, unit price) lines."""

    def __init__(self) -> None:
        self._lines: list[tuple[str, int, float]] = []

    def add(self, name: str, quantity: int, unit_price: float) -> None:
        """Add `quantity` units of `name` to the cart."""
        self._lines.append((name, quantity, unit_price))

    @property
    def count(self) -> int:
        """Number of distinct lines in the cart."""
        return len(self._lines)

    def total(self) -> float:
        """Return the sum of quantity * unit price over all lines."""
        return sum(q * p for _, q, p in self._lines)
'''
shop = load_module("shop", SHOP_SOURCE)

print("\n# 08. pydoc.render_doc(shop) - the terminal documentation page")
text = clean(pydoc.render_doc(shop, renderer=pydoc.plaintext))
show(text, 30, prefix="  ")

done = subprocess.run([sys.executable, "-m", "pydoc", "-w", "shop"], capture_output=True,
                      text=True, cwd=TMP, env=ENV, timeout=60)
html = (TMP / "shop.html").read_text()
print("  $ python -m pydoc -w shop   ->", done.stdout.strip(), f"(html page, {len(html)} chars)")
print("  html <title>:", re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip())
print("# - Note: _internal_helper is hidden because __all__ lists the public names.")

# 09. doctest - examples in docstrings that RUN as tests
# ------------------------------------
# - doctest scans docstrings for text that looks like an interactive session:
#       >>> add(2, 3)          <- a line starting with '>>> ' is code to run
#       5                      <- the lines after it are the EXPECTED output
#   It runs the code and compares the real output to the expected text.
# - '...' continues a multi-line statement.
# - Why bother: the docs show how to use the function AND prove it still
#   works that way. Change the behaviour, forget the docs -> the test fails.
# - Four ways to run them:
#     doctest.testmod()                 inside the module (the classic idiom)
#     python -m doctest -v file.py      from the shell
#     doctest.testfile("guide.txt")     examples inside a plain text file
#     pytest --doctest-modules          let pytest collect them too

MATHLIB_SOURCE = '''"""Tiny helpers used to demonstrate doctest."""


def add(a, b):
    """Return a + b.

    >>> add(2, 3)
    5
    >>> add("a", "b")
    'ab'
    """
    return a + b


def divide(a, b):
    """Return a / b.

    >>> divide(10, 4)
    2.5

    Expected exceptions: write the traceback HEADER, then '...', then the
    exception line. doctest ignores the lines in between.

    >>> divide(1, 0)
    Traceback (most recent call last):
        ...
    ZeroDivisionError: division by zero
    """
    return a / b


def slugify(text):
    """Turn text into a lowercase, hyphen-separated slug.

    >>> slugify("Hello,  World!")
    'hello-world'
    >>> for word in ["a", "b"]:      # '...' continues a block
    ...     print(slugify(word))
    a
    b
    """
    words = "".join(c if c.isalnum() else " " for c in text.lower()).split()
    return "-".join(words)


def unique_sorted(words):
    """Return the distinct words in sorted order.

    A set has no stable order for strings, so we sort before showing it:

    >>> unique_sorted(["pear", "apple", "pear"])
    ['apple', 'pear']
    """
    return sorted(set(words))


if __name__ == "__main__":
    import doctest

    print(doctest.testmod())  # the classic "run my own examples" idiom
'''
mathlib = load_module("mathlib", MATHLIB_SOURCE)

print("\n# 09. doctest.testmod() on a sample module")
buffer = io.StringIO()
with contextlib.redirect_stdout(buffer):
    results = doctest.testmod(mathlib, verbose=False)
print("  result:", results, "<- (failed, attempted); silence means all passed")
print("  collected tests:", [t.name for t in doctest.DocTestFinder().find(mathlib)])
print("  examples attempted:", results.attempted, "| failures:", results.failed)

# 10. Running doctest from the shell - passing, then a deliberately failing one
# ------------------------------------
# - python -m doctest file.py           quiet on success, prints failures
# - python -m doctest -v file.py        verbose: lists every example
# - Exit code is 1 if any example fails (so CI can use it).

print("\n# 10. python -m doctest from the shell")
done = subprocess.run([sys.executable, "-m", "doctest", "-v", "mathlib.py"],
                      capture_output=True, text=True, cwd=TMP, env=ENV, timeout=60)
lines = done.stdout.splitlines()
print("  $ python -m doctest -v mathlib.py   (first 7 and last 8 lines)")
show("\n".join(lines[:7]), 7)
print("    | ...")
show("\n".join(lines[-8:]), 8)
print(f"    [exit code {done.returncode}]")

BROKEN_SOURCE = '''def double(x):
    """Return x doubled.

    >>> double(2)
    5
    """
    return x * 2
'''
(TMP / "broken.py").write_text(BROKEN_SOURCE)
done = subprocess.run([sys.executable, "-m", "doctest", "broken.py"], capture_output=True,
                      text=True, cwd=TMP, env=ENV, timeout=60)
print("\n  $ python -m doctest broken.py   (the docstring claims double(2) == 5)")
show(clean(done.stdout + done.stderr), 16)
print(f"    [exit code {done.returncode}] -> a CI job would turn red")
print("# - Read a failure as: 'Failed example' = the code, 'Expected' = what the docs")
print("#   claimed, 'Got' = what really happened. Either fix the code or fix the docs.")

# 11. optionflags - tell doctest how strictly to compare
# ------------------------------------
# - By default the output must match EXACTLY, character by character.
# - Flags relax that. Pass them to testmod(optionflags=...), or switch them on
#   for ONE example with a directive comment:   >>> f()  # doctest: +ELLIPSIS
#     ELLIPSIS                 '...' in expected output matches any text
#     NORMALIZE_WHITESPACE     any run of spaces/newlines matches any other
#     IGNORE_EXCEPTION_DETAIL  only exception TYPE must match, not its message
#     SKIP                     do not run this example (documentation only)


def run_examples(name, docstring, flags=0):
    """Run the examples in `docstring`; return (failed, attempted, report text)."""
    test = doctest.DocTestParser().get_doctest(docstring, {}, name, None, 0)
    report = io.StringIO()
    runner = doctest.DocTestRunner(optionflags=flags, verbose=False)
    result = runner.run(test, out=report.write, clear_globs=True)
    return result.failed, result.attempted, report.getvalue()


def compare(title, docstring, flag=0, flag_name="(no flags)"):
    failed, attempted, report = run_examples(title, docstring, flag)
    status = "PASS" if failed == 0 else "FAIL"
    print(f"  [{status}] {title:34} {flag_name}")
    if failed:
        show("\n".join(clean(report).splitlines()[3:]), 10, prefix="         ")


print("\n# 11. optionflags")
ADDR_EXAMPLE = ">>> object()\n<object object at 0x...>\n"
compare("object address, exact match", ADDR_EXAMPLE)
compare("object address + ELLIPSIS", ADDR_EXAMPLE, doctest.ELLIPSIS, "ELLIPSIS")

WS_EXAMPLE = ">>> print(1, 2, 3, sep='\\n')\n1 2 3\n"
compare("whitespace, exact match", WS_EXAMPLE)
compare("whitespace + NORMALIZE_WHITESPACE", WS_EXAMPLE, doctest.NORMALIZE_WHITESPACE, "NORMALIZE_WHITESPACE")

EXC_EXAMPLE = (
    ">>> int('abc')\n"
    "Traceback (most recent call last):\n"
    "    ...\n"
    "ValueError: this message is not the real one\n"
)
compare("exception message differs", EXC_EXAMPLE)
compare("exception + IGNORE_EXCEPTION_DETAIL", EXC_EXAMPLE, doctest.IGNORE_EXCEPTION_DETAIL, "IGNORE_EXCEPTION_DETAIL")
print("# - Use flags sparingly: each one makes the test blind to something. Prefer")
print("#   making the OUTPUT deterministic (sort it, round it, print a field).")

# 12. Doctest gotchas (each one is a real trap)
# ------------------------------------
print("\n# 12. Doctest gotchas")

# 12a. Floating point repr
compare("float repr: expects 0.3", ">>> 0.1 + 0.2\n0.3\n")
compare("float fix: round() or compare", ">>> round(0.1 + 0.2, 2)\n0.3\n>>> 0.1 + 0.2 == 0.3\nFalse\n")
print("      -> floats are inexact (see 'Math And Numeric Modules'); round() or use math.isclose.")

# 12b. Trailing whitespace is part of the output
compare("trailing space in output", ">>> print('hi ')\nhi\n")
compare("fix: show repr() instead", ">>> repr('hi ')\n\"'hi '\"\n")
print("      Expected 'hi' but Got 'hi ' - the difference is INVISIBLE in the failure report.")
print("      -> editors strip trailing spaces from docs, so the expected text no longer matches.")

# 12c. A blank line ends the expected output -> <BLANKLINE>
compare("blank line inside output", ">>> print('a\\n\\nb')\na\n\nb\n")
compare("fix: <BLANKLINE> marker", ">>> print('a\\n\\nb')\na\n<BLANKLINE>\nb\n")

# 12d. Sets (and dicts when order matters) - make output deterministic
compare("fix: sorted() makes set output stable", ">>> sorted({'b', 'a'})\n['a', 'b']\n")
for seed in ("1", "2"):
    out = subprocess.run([sys.executable, "-c", "print({'apple', 'pear', 'fig', 'kiwi'})"],
                         capture_output=True, text=True, env=dict(ENV, PYTHONHASHSEED=seed), timeout=30)
    print(f"      same code, PYTHONHASHSEED={seed}: {out.stdout.strip()}")
print("      -> string sets change order between runs (hash randomization). Always sorted(...).")
print("      -> dicts keep insertion order since 3.7, so printing them is fine; but if the order")
print("         is irrelevant, compare:  >>> d == {'a': 1, 'b': 2}   ->  True")

# 12e. Backslashes in docstrings -> use a RAW docstring (r\"\"\"...\"\"\")
ESCAPE_BAD = '''def shout(): \x22\x22\x22Print two lines.

    >>> print("a\\nb")
    a
    b
    \x22\x22\x22
'''
ESCAPE_GOOD = ESCAPE_BAD.replace("\x22\x22\x22Print", 'r\x22\x22\x22Print')
for label, src in [("non-raw docstring with \\n", ESCAPE_BAD), ("raw docstring r\"\"\" ... \"\"\"", ESCAPE_GOOD)]:
    mod = load_module("escdemo", src)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            res = doctest.testmod(mod)
        print(f"  [{'PASS' if res.failed == 0 else 'FAIL'}] {label:34} {res}")
    except ValueError as exc:  # doctest cannot even parse the broken example
        print(f"  [FAIL] {label:34} ValueError: {str(exc)[:58]}...")
print("      -> in a normal docstring Python turns \\n into a REAL newline BEFORE doctest")
print("         sees it, which breaks the example. Docstring with backslashes -> r\"\"\".")

# 13. Documenting expected exceptions - the traceback header
# ------------------------------------
# - Required shape:
#       >>> call()
#       Traceback (most recent call last):
#         ...                      <- anything here is ignored (indent is free)
#       SomeError: exact message
# - The message must match unless IGNORE_EXCEPTION_DETAIL is on.
# - An exception you did NOT document fails the test and prints the traceback.

print("\n# 13. Expected exceptions")
compare("documented exception", ">>> int('abc')\nTraceback (most recent call last):\n    ...\n"
        "ValueError: invalid literal for int() with base 10: 'abc'\n")
compare("forgot to document it", ">>> int('abc')\n42\n")

# 14. doctest.testfile - examples in a plain text/Markdown guide
# ------------------------------------
# - testfile treats a WHOLE text file as one big docstring: prose around the
#   examples is ignored. Good for a tutorial/README whose examples must work.

GUIDE = """\
Quick start
===========

Import the helpers and add two numbers:

>>> from mathlib import add
>>> add(20, 22)
42

Slugs are lowercase and hyphen-separated:

>>> from mathlib import slugify
>>> slugify("Docs Are Code")
'docs-are-code'
"""
(TMP / "guide.txt").write_text(GUIDE)
print("\n# 14. doctest.testfile()")
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    res = doctest.testfile(str(TMP / "guide.txt"), module_relative=False)
print("  testfile(guide.txt) ->", res, "(the examples in a README-style text file ran)")
print("# - The 'from mathlib import ...' worked because mathlib is already in sys.modules.")

# 15. doctest vs pytest - which tool for which job
# ------------------------------------
# - doctest is RIGHT for:
#     * tiny, pure functions (input -> output) where an example IS the doc
#     * "living examples" in the README/tutorial that must never go stale
#     * showing REPL-style usage to a reader
# - Use pytest (or unittest) when:
#     * you need setup/teardown, fixtures, temp files, mocks, databases
#     * you want to check many edge cases (parametrization) - too long for docs
#     * you test errors, timing, side effects, or large outputs
#     * you want clear failure diffs and assertion rewriting
# - Healthy split: doctest = 1-3 examples that TEACH; pytest = the exhaustive
#   edge cases that PROVE. Run both: pytest --doctest-modules.
# - Never put secrets, network calls, or randomness into a doctest.

print("\n# 15. doctest vs pytest")
print("  doctest : 1-3 teaching examples per function, README snippets")
print("  pytest  : fixtures, parametrized edge cases, mocks, I/O, big outputs")
print("  both    : pytest --doctest-modules")

# 16. Type hints are documentation too
# ------------------------------------
# - def apply_discount(price: float, percent: float = 10.0) -> float
#   already tells the reader the types, so docstrings need not repeat them.
# - Unlike a comment, a hint is CHECKED (by mypy) and shows up in editors,
#   help(), and generated docs. See "06-Standard Library/06-Typing-And-Type-Hints.py"
#   for the syntax, and "05-Code-Quality.py" for running mypy.
# - Division of labour: hints say WHAT TYPE; the docstring says WHAT IT MEANS
#   (units, ranges, side effects, why).

print("\n# 16. Type hints as documentation")
print("  inspect.signature(shop.apply_discount) ->", inspect.signature(shop.apply_discount))
print("  inspect.signature(shop.Cart.add)       ->", inspect.signature(shop.Cart.add))

# 17. Project documentation layout
# ------------------------------------
# - Docstrings explain the CODE. A project also needs documents about the
#   PROJECT. The usual files, at the repository root:
#     README.md        the front door: what, why, how to run (checklist below)
#     CHANGELOG.md     what changed in each release, for USERS
#     CONTRIBUTING.md  how to set up, test, style rules, how to send a PR
#     LICENSE          what others may do with your code (without one: all rights reserved)
#     docs/            longer guides, API reference, ADRs

README_CHECKLIST = [
    "Title + one-sentence description (what problem does it solve?)",
    "Badges (CI status, version) - optional, never decoration only",
    "Installation:  pip install ...   (copy-paste runnable)",
    "Quick start: the smallest working example, with its output",
    "Usage / features / configuration",
    "Project structure (for libraries: where the main code is)",
    "Development: how to set up, run tests, run linters",
    "Contributing + License + how to get help",
]
print("\n# 17. README checklist")
for item in README_CHECKLIST:
    print("  [ ]", item)

CHANGELOG_SAMPLE = """\
# Changelog
All notable changes to this project are documented here.
Format: Keep a Changelog (https://keepachangelog.com); versions: Semantic Versioning.

## [Unreleased]
### Added
- `Cart.remove()` to delete a line.

## [1.1.0] - 2026-03-02
### Added
- Discount support via `apply_discount()`.
### Changed
- `Cart.total()` now returns a float, not a Decimal.
### Fixed
- Crash when the cart was empty.

## [1.0.0] - 2026-01-10
### Added
- First public release.
"""
print("\n  CHANGELOG.md (Keep a Changelog format):")
show(CHANGELOG_SAMPLE, 20, prefix="  ")
print("# - Sections: Added / Changed / Deprecated / Removed / Fixed / Security.")
print("# - Semantic Versioning: MAJOR.MINOR.PATCH - breaking.feature.fix.")
print("# - Written for HUMANS: do not paste 'git log'. Newest first; 'Unreleased' on top.")

print("\n  LICENSE one-liners (pick one, copy the official text, do not write your own):")
for name, line in [
    ("MIT", "very permissive: do anything, keep the copyright notice"),
    ("Apache-2.0", "permissive + explicit patent grant; common for company projects"),
    ("BSD-3-Clause", "like MIT, plus 'do not use our name to endorse'"),
    ("GPL-3.0", "copyleft: anything built on it must also be GPL"),
    ("Unlicense/CC0", "public-domain dedication"),
]:
    print(f"    {name:14} {line}")
print("  (not legal advice - ask a lawyer for anything commercial)")

print("\n  CONTRIBUTING.md outline: dev setup -> run tests/linters -> branch & commit style ->")
print("  how to open a PR -> what reviewers look for -> where to ask questions.")

ADR_SAMPLE = """\
# ADR 0007: Use SQLite for local storage

Status: Accepted (2026-02-14)

## Context
The CLI must keep a few thousand records offline. Users cannot install a database server.

## Decision
Use the standard-library sqlite3 module with a single file in the user's data folder.

## Consequences
+ Zero dependencies, ACID transactions, easy backups (copy one file).
- Weak concurrency: only one writer at a time; revisit if we add a server mode.
"""
print("\n  ADR (Architecture Decision Record) - one short file per decision in docs/adr/:")
show(ADR_SAMPLE, 14, prefix="  ")
print("# - An ADR records WHY a decision was made, so in two years nobody re-debates it blind.")

# 18. Documentation generators (printed reference - not installed here)
# ------------------------------------
# - Sphinx: the long-time standard (Python's own docs use it).
#       pip install sphinx
#       sphinx-quickstart docs          # creates conf.py, index.rst, Makefile
#       # in docs/conf.py:
#       extensions = ["sphinx.ext.autodoc",    # pulls docstrings into pages
#                     "sphinx.ext.napoleon",   # understands Google + NumPy style
#                     "sphinx.ext.viewcode"]   # links to highlighted source
#       # in docs/index.rst:   .. automodule:: shop\n   :members:
#       make -C docs html               # output: docs/_build/html
# - MkDocs + mkdocstrings: Markdown pages, modern look, simple config.
#       pip install mkdocs mkdocs-material "mkdocstrings[python]"
#       # mkdocs.yml:  site_name: Shop / plugins: [search, mkdocstrings]
#       # a page containing the line:   ::: shop.Cart     renders its docstring
#       mkdocs serve   (live preview)   |   mkdocs build
# - pdoc: the quickest "just document my package" tool.
#       pip install pdoc && pdoc shop         # local web server
#       pdoc -o html_docs shop                # static HTML
# - Hosting: Read the Docs or GitHub Pages; build them in CI so docs
#   are always from the latest commit (and a docs build error fails the PR).

print("\n# 18. Doc generators (reference)")
print("  Sphinx     : sphinx-quickstart docs  + autodoc/napoleon  -> make html")
print("  MkDocs     : mkdocs.yml + mkdocstrings (::: package.module)  -> mkdocs serve")
print("  pdoc       : pdoc package   (zero config)")
print("  pydoc      : built in, see section 8")

# 19. Error messages and --help text are documentation too
# ------------------------------------
# - A good error message answers three questions: WHAT went wrong, with WHICH
#   value, and what the user can DO about it. Never "Invalid input".
# - Never include secrets in messages (see 07-Security-Basics.py).

print("\n# 19. Writing good error messages")


def set_age_bad(age):
    if not isinstance(age, int) or age < 0:
        raise ValueError("invalid age")
    return age


def set_age_good(age):
    if not isinstance(age, int) or isinstance(age, bool):
        raise TypeError(f"age must be an int, got {type(age).__name__} ({age!r})")
    if not 0 <= age <= 150:
        raise ValueError(f"age must be between 0 and 150, got {age}")
    return age


for label, func in [("bad ", set_age_bad), ("good", set_age_good)]:
    for value in (-5, "ten"):
        try:
            func(value)
        except (TypeError, ValueError) as exc:
            print(f"  {label} {value!r:6} -> {type(exc).__name__}: {exc}")

# - --help text: the first thing users read about a CLI. Include a description,
#   a help string per argument (with defaults), and examples in the epilog.
#   (argparse basics: "06-Standard Library/10-Argparse.py".)
os.environ["COLUMNS"] = "78"  # fix the wrap width so output is the same everywhere
parser = argparse.ArgumentParser(
    prog="shop-cli",
    description="Total up a shopping list.",
    epilog="Examples:\n  shop-cli pen:2:10.0 book:1:250\n  shop-cli --discount 15 pen:2:10.0",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
parser.add_argument("lines", nargs="+", metavar="NAME:QTY:PRICE", help="items to buy, e.g. pen:2:10.0")
parser.add_argument("--discount", type=float, default=0.0, metavar="PERCENT",
                    help="percent off the total (default: %(default)s)")
print("\n  A helpful --help screen:")
show(parser.format_help(), 16, prefix="  ")

# 20. Running THIS file's own doctests
# ------------------------------------
# - The three convert_* functions above carry doctests. testmod() with no
#   argument tests the module it is called from (here: this script).
print("\n# 20. doctest on this very script")
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    res = doctest.testmod(sys.modules["__main__"])
print("  doctest.testmod() ->", res)
print("# - Idiom at the bottom of a module:  if __name__ == '__main__': doctest.testmod()")

# 21. Comments, TODOs and docs - the guidelines
# ------------------------------------
# - Docstring = the CONTRACT for users of the function (what it does).
#   Comment   = the REASONING for maintainers (why this way). Do not mix them.
# - Comment when: a business rule, a workaround for a bug in another library
#   (link the issue), a non-obvious performance choice, a regex (explain it!).
# - Do NOT comment: what a line does, closed-over history ('removed by Bob in
#   2019' - git remembers), commented-out code (delete it; git remembers).
# - TODO convention: '# TODO(owner): what to do and why (link)'. Searchable,
#   owned, and a linter/CI job can list them. A TODO without an owner is
#   wishful thinking. Others: FIXME (known bug), HACK (ugly but needed), NOTE.

SOURCE_WITH_TODOS = """\
price = base * 1.18  # GST rate fixed by law until the next budget (see ticket FIN-12)
# TODO(asha): switch to the tax service once it ships (FIN-90)
# FIXME(raj): rounding is wrong for negative values
# HACK: vendor API returns 200 on errors, so we parse the body (vendor bug #441)
# TODO: make this faster
"""
print("\n# 21. TODO scan with a regex")
for lineno, line in enumerate(SOURCE_WITH_TODOS.splitlines(), 1):
    m = re.search(r"#\s*(TODO|FIXME|HACK|NOTE)(?:\((\w+)\))?:?\s*(.*)", line)
    if m:
        kind, owner, msg = m.groups()
        flag = "" if owner else "   <- no owner!"
        print(f"  line {lineno}: {kind:5} owner={owner or '-':5} {msg[:45]}{flag}")

# 22. A tiny docs generator built on inspect
# ------------------------------------
# - Doc tools are not magic: they import your module, walk its public names,
#   and format each object's signature + docstring. Here is the whole idea in
#   ~35 lines, producing Markdown.
# - Rules we follow (the same ones real tools follow):
#     * honour __all__ if present, else skip names starting with '_'
#     * only document objects DEFINED in this module (not imported ones)
#     * use inspect.signature (includes hints) and inspect.getdoc (cleaned)


def public_names(module):
    if hasattr(module, "__all__"):
        return list(module.__all__)
    return [n for n in vars(module) if not n.startswith("_")]


def md_for_callable(name, obj, level="###"):
    lines = [f"{level} `{name}{inspect.signature(obj)}`", ""]
    lines += [inspect.getdoc(obj) or "*(no documentation)*", ""]
    return lines


def module_to_markdown(module):
    out = [f"# {module.__name__}", "", inspect.getdoc(module) or "", ""]
    for name in public_names(module):
        obj = getattr(module, name)
        if getattr(obj, "__module__", None) != module.__name__:
            continue  # imported from somewhere else
        if inspect.isfunction(obj):
            out += md_for_callable(name, obj, "##")
        elif inspect.isclass(obj):
            out += [f"## class `{name}`", "", inspect.getdoc(obj) or "", ""]
            for mname, member in vars(obj).items():
                if mname.startswith("_"):
                    continue
                if isinstance(member, property):
                    out += [f"### property `{mname}`", "", inspect.getdoc(member) or "", ""]
                elif inspect.isfunction(member):
                    out += md_for_callable(f"{name}.{mname}", member)
    return "\n".join(out).rstrip() + "\n"


md_path = TMP / "shop_api.md"
md_path.write_text(module_to_markdown(shop))
print("\n# 22. A tiny docs generator (inspect -> Markdown)")
print(f"  wrote {md_path.name} ({md_path.stat().st_size} bytes) in the temp folder; first 30 lines:")
show(md_path.read_text(), 30, prefix="  ")
print("# - Real tools add cross-links, search, versioning, themes - the core loop is this.")
print("# - Because docs come FROM docstrings + hints, fixing the docstring fixes the site.")

# 23. Documentation checklist and recap
# ------------------------------------
# - Daily habits:
#     [ ] every public function/class has a one-line summary docstring
#     [ ] anything non-obvious has Args/Returns/Raises with UNITS and RANGES
#     [ ] one runnable example for functions people will copy-paste
#     [ ] comments explain WHY; stale comments are deleted, not "fixed later"
#     [ ] README quick start actually runs (put it in a doctest or CI step)
#     [ ] CHANGELOG updated in the same PR as the change
#     [ ] error messages say what / which value / what to do
# - Gotchas to remember:
#     * doctest compares TEXT exactly: floats, set order, addresses, trailing spaces
#     * raw docstrings (r""") for anything with a backslash
#     * pick ONE docstring style and let a tool enforce it
#     * docs that are not run or built in CI will rot

# 24. Cleanup
# ------------------------------------
sys.modules.pop("shop", None)
sys.modules.pop("mathlib", None)
sys.modules.pop("escdemo", None)
TMP_HOLDER.cleanup()
print("\n# 23-24. Checklist above; cleanup")
print("temp folder removed:", not TMP.exists())
