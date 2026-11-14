# Python

A from-scratch to advanced Python track. Every topic is one self-contained,
runnable `.py` file plus a plain-English `.md` cheat sheet (what it covers, key
points, gotchas, when it matters) for revision.

```bash
python3 "01-Python Fundamentals/02-Fundamentals.py"
```

## Requirements

- **Python 3.10+** (tested on 3.12). A few files use newer features and print a
  skip message on older versions: `match-case` needs 3.10, `except*` and
  `StrEnum` need 3.11.
- Only the NumPy and Pandas folders need third-party packages, and
  `09-Tooling-And-Quality` demos dev tools (pytest, mypy, black, flake8, isort,
  build). Install with `pip install -r requirements.txt`; each file skips a
  tool that is missing instead of failing.
- Everything else uses the standard library only. Files clean up their own
  scratch files and never touch the internet (networking demos stay on
  `127.0.0.1`).

## How to study

1. Read the `.md` notes first for the idea, then run the `.py` and read the
   code next to its output.
2. Go in folder order; files inside a folder are numbered in reading order.
3. Revisit the **Gotchas** section of each note — that is where the bugs live.

## Notebooks

Every topic also has a notebook (`.ipynb`) next to its `.py`, for reading and
experimenting: one markdown cell per section, then a code cell you can edit and
re-run. The `.py` file is the source of truth — notebooks are **generated**
from it (plus the `.md` notes) and saved without outputs.

```bash
jupyter lab                                   # open and run the notebooks
python3 tools/build_notebooks.py              # rebuild all notebooks from the .py files
python3 tools/build_notebooks.py --only Sets  # rebuild just one topic
python3 tools/build_notebooks.py --check      # rebuild, then execute all of them
```

Experiment freely in a notebook, but copy anything you want to keep back into
the `.py` — the next build overwrites the notebook. The two multiprocessing
topics (`09-Multithreading-And-Multiprocessing`, `12-Multiprocessing-Pool-And-Shared-State`)
must stay scripts, so their notebooks *run* and *import* the `.py` instead.

## Learning path


### Stage 1 — Beginner: the language itself

- [01-Python Fundamentals](01-Python%20Fundamentals/README.md)
- [02-Data Types](02-Data%20Types/README.md)
- [03-Functions](03-Functions/README.md)

### Stage 2 — Intermediate: structuring programs

- [04-OOPs](04-OOPs/README.md)
- [05-Python Advanced](05-Python%20Advanced/README.md)

### Stage 3 — Toolbox: standard library

- [06-Standard Library](06-Standard%20Library/README.md)

### Stage 4 — Data libraries

- [07-NumPy](07-NumPy/README.md)
- [08-Pandas](08-Pandas/README.md)

### Stage 5 — Professional practice

- [09-Tooling-And-Quality](09-Tooling-And-Quality/README.md)

## Progress checklist

Tick items as you finish them (edit this file).


**01-Python Fundamentals**

- [ ] [01-Setup-And-Tooling](01-Python%20Fundamentals/01-Setup-And-Tooling.py) · [notes](01-Python%20Fundamentals/01-Setup-And-Tooling.md) · [notebook](01-Python%20Fundamentals/01-Setup-And-Tooling.ipynb)
- [ ] [02-Fundamentals](01-Python%20Fundamentals/02-Fundamentals.py) · [notes](01-Python%20Fundamentals/02-Fundamentals.md) · [notebook](01-Python%20Fundamentals/02-Fundamentals.ipynb)
- [ ] [03-Control-Flow](01-Python%20Fundamentals/03-Control-Flow.py) · [notes](01-Python%20Fundamentals/03-Control-Flow.md) · [notebook](01-Python%20Fundamentals/03-Control-Flow.ipynb)

**02-Data Types**

- [ ] [01-Primitive](02-Data%20Types/01-Primitive.py) · [notes](02-Data%20Types/01-Primitive.md) · [notebook](02-Data%20Types/01-Primitive.ipynb)
- [ ] [02-Strings](02-Data%20Types/02-Strings.py) · [notes](02-Data%20Types/02-Strings.md) · [notebook](02-Data%20Types/02-Strings.ipynb)
- [ ] [03-List](02-Data%20Types/03-List.py) · [notes](02-Data%20Types/03-List.md) · [notebook](02-Data%20Types/03-List.ipynb)
- [ ] [04-Tuples](02-Data%20Types/04-Tuples.py) · [notes](02-Data%20Types/04-Tuples.md) · [notebook](02-Data%20Types/04-Tuples.ipynb)
- [ ] [05-Sets](02-Data%20Types/05-Sets.py) · [notes](02-Data%20Types/05-Sets.md) · [notebook](02-Data%20Types/05-Sets.ipynb)
- [ ] [06-Dictionary](02-Data%20Types/06-Dictionary.py) · [notes](02-Data%20Types/06-Dictionary.md) · [notebook](02-Data%20Types/06-Dictionary.ipynb)
- [ ] [07-Type-Casting](02-Data%20Types/07-Type-Casting.py) · [notes](02-Data%20Types/07-Type-Casting.md) · [notebook](02-Data%20Types/07-Type-Casting.ipynb)
- [ ] [08-Comprehensions](02-Data%20Types/08-Comprehensions.py) · [notes](02-Data%20Types/08-Comprehensions.md) · [notebook](02-Data%20Types/08-Comprehensions.ipynb)
- [ ] [09-Unpacking-And-Packing](02-Data%20Types/09-Unpacking-And-Packing.py) · [notes](02-Data%20Types/09-Unpacking-And-Packing.md) · [notebook](02-Data%20Types/09-Unpacking-And-Packing.ipynb)
- [ ] [10-Bytes-And-Bytearray](02-Data%20Types/10-Bytes-And-Bytearray.py) · [notes](02-Data%20Types/10-Bytes-And-Bytearray.md) · [notebook](02-Data%20Types/10-Bytes-And-Bytearray.ipynb)
- [ ] [11-Range-And-Slice-Objects](02-Data%20Types/11-Range-And-Slice-Objects.py) · [notes](02-Data%20Types/11-Range-And-Slice-Objects.md) · [notebook](02-Data%20Types/11-Range-And-Slice-Objects.ipynb)
- [ ] [12-Mutability-And-Memory-Model](02-Data%20Types/12-Mutability-And-Memory-Model.py) · [notes](02-Data%20Types/12-Mutability-And-Memory-Model.md) · [notebook](02-Data%20Types/12-Mutability-And-Memory-Model.ipynb)

**03-Functions**

- [ ] [01-Built-in-Functions](03-Functions/01-Built-in-Functions.py) · [notes](03-Functions/01-Built-in-Functions.md) · [notebook](03-Functions/01-Built-in-Functions.ipynb)
- [ ] [02-Functions](03-Functions/02-Functions.py) · [notes](03-Functions/02-Functions.md) · [notebook](03-Functions/02-Functions.ipynb)
- [ ] [03-Scope-And-Namespaces](03-Functions/03-Scope-And-Namespaces.py) · [notes](03-Functions/03-Scope-And-Namespaces.md) · [notebook](03-Functions/03-Scope-And-Namespaces.ipynb)
- [ ] [04-Functional-Programming](03-Functions/04-Functional-Programming.py) · [notes](03-Functions/04-Functional-Programming.md) · [notebook](03-Functions/04-Functional-Programming.ipynb)
- [ ] [05-Decorators](03-Functions/05-Decorators.py) · [notes](03-Functions/05-Decorators.md) · [notebook](03-Functions/05-Decorators.ipynb)

**04-OOPs**

- [ ] [01-Class-Object](04-OOPs/01-Class-Object.py) · [notes](04-OOPs/01-Class-Object.md) · [notebook](04-OOPs/01-Class-Object.ipynb)
- [ ] [02-Encapsulation](04-OOPs/02-Encapsulation.py) · [notes](04-OOPs/02-Encapsulation.md) · [notebook](04-OOPs/02-Encapsulation.ipynb)
- [ ] [03-Inheritance](04-OOPs/03-Inheritance.py) · [notes](04-OOPs/03-Inheritance.md) · [notebook](04-OOPs/03-Inheritance.ipynb)
- [ ] [04-Polymorphism](04-OOPs/04-Polymorphism.py) · [notes](04-OOPs/04-Polymorphism.md) · [notebook](04-OOPs/04-Polymorphism.ipynb)
- [ ] [05-Abstraction](04-OOPs/05-Abstraction.py) · [notes](04-OOPs/05-Abstraction.md) · [notebook](04-OOPs/05-Abstraction.ipynb)
- [ ] [06-Dataclasses-And-Operator-Overloading](04-OOPs/06-Dataclasses-And-Operator-Overloading.py) · [notes](04-OOPs/06-Dataclasses-And-Operator-Overloading.md) · [notebook](04-OOPs/06-Dataclasses-And-Operator-Overloading.ipynb)
- [ ] [07-Custom-Containers-And-ABCs](04-OOPs/07-Custom-Containers-And-ABCs.py) · [notes](04-OOPs/07-Custom-Containers-And-ABCs.md) · [notebook](04-OOPs/07-Custom-Containers-And-ABCs.ipynb)
- [ ] [08-SOLID-Principles](04-OOPs/08-SOLID-Principles.py) · [notes](04-OOPs/08-SOLID-Principles.md) · [notebook](04-OOPs/08-SOLID-Principles.ipynb)

**05-Python Advanced**

- [ ] [01-Iterators](05-Python%20Advanced/01-Iterators.py) · [notes](05-Python%20Advanced/01-Iterators.md) · [notebook](05-Python%20Advanced/01-Iterators.ipynb)
- [ ] [02-Generators](05-Python%20Advanced/02-Generators.py) · [notes](05-Python%20Advanced/02-Generators.md) · [notebook](05-Python%20Advanced/02-Generators.ipynb)
- [ ] [03-Error-And-Exception-Handling](05-Python%20Advanced/03-Error-And-Exception-Handling.py) · [notes](05-Python%20Advanced/03-Error-And-Exception-Handling.md) · [notebook](05-Python%20Advanced/03-Error-And-Exception-Handling.ipynb)
- [ ] [04-File-Handling](05-Python%20Advanced/04-File-Handling.py) · [notes](05-Python%20Advanced/04-File-Handling.md) · [notebook](05-Python%20Advanced/04-File-Handling.ipynb)
- [ ] [05-Modules-And-Packages](05-Python%20Advanced/05-Modules-And-Packages.py) · [notes](05-Python%20Advanced/05-Modules-And-Packages.md) · [notebook](05-Python%20Advanced/05-Modules-And-Packages.ipynb)
- [ ] [06-Context-Managers](05-Python%20Advanced/06-Context-Managers.py) · [notes](05-Python%20Advanced/06-Context-Managers.md) · [notebook](05-Python%20Advanced/06-Context-Managers.ipynb)
- [ ] [07-Regular-Expressions](05-Python%20Advanced/07-Regular-Expressions.py) · [notes](05-Python%20Advanced/07-Regular-Expressions.md) · [notebook](05-Python%20Advanced/07-Regular-Expressions.ipynb)
- [ ] [08-Itertools-And-Functools](05-Python%20Advanced/08-Itertools-And-Functools.py) · [notes](05-Python%20Advanced/08-Itertools-And-Functools.md) · [notebook](05-Python%20Advanced/08-Itertools-And-Functools.ipynb)
- [ ] [09-Multithreading-And-Multiprocessing](05-Python%20Advanced/09-Multithreading-And-Multiprocessing.py) · [notes](05-Python%20Advanced/09-Multithreading-And-Multiprocessing.md) · [notebook](05-Python%20Advanced/09-Multithreading-And-Multiprocessing.ipynb)
- [ ] [10-Async-Await](05-Python%20Advanced/10-Async-Await.py) · [notes](05-Python%20Advanced/10-Async-Await.md) · [notebook](05-Python%20Advanced/10-Async-Await.ipynb)
- [ ] [11-Threading-Primitives](05-Python%20Advanced/11-Threading-Primitives.py) · [notes](05-Python%20Advanced/11-Threading-Primitives.md) · [notebook](05-Python%20Advanced/11-Threading-Primitives.ipynb)
- [ ] [12-Multiprocessing-Pool-And-Shared-State](05-Python%20Advanced/12-Multiprocessing-Pool-And-Shared-State.py) · [notes](05-Python%20Advanced/12-Multiprocessing-Pool-And-Shared-State.md) · [notebook](05-Python%20Advanced/12-Multiprocessing-Pool-And-Shared-State.ipynb)
- [ ] [13-Asyncio-Advanced](05-Python%20Advanced/13-Asyncio-Advanced.py) · [notes](05-Python%20Advanced/13-Asyncio-Advanced.md) · [notebook](05-Python%20Advanced/13-Asyncio-Advanced.ipynb)

**06-Standard Library**

- [ ] [01-Collections-Module](06-Standard%20Library/01-Collections-Module.py) · [notes](06-Standard%20Library/01-Collections-Module.md) · [notebook](06-Standard%20Library/01-Collections-Module.ipynb)
- [ ] [02-Datetime-Module](06-Standard%20Library/02-Datetime-Module.py) · [notes](06-Standard%20Library/02-Datetime-Module.md) · [notebook](06-Standard%20Library/02-Datetime-Module.ipynb)
- [ ] [03-Os-And-Sys](06-Standard%20Library/03-Os-And-Sys.py) · [notes](06-Standard%20Library/03-Os-And-Sys.md) · [notebook](06-Standard%20Library/03-Os-And-Sys.ipynb)
- [ ] [04-Json-And-Csv](06-Standard%20Library/04-Json-And-Csv.py) · [notes](06-Standard%20Library/04-Json-And-Csv.md) · [notebook](06-Standard%20Library/04-Json-And-Csv.ipynb)
- [ ] [05-Pathlib-Module](06-Standard%20Library/05-Pathlib-Module.py) · [notes](06-Standard%20Library/05-Pathlib-Module.md) · [notebook](06-Standard%20Library/05-Pathlib-Module.ipynb)
- [ ] [06-Typing-And-Type-Hints](06-Standard%20Library/06-Typing-And-Type-Hints.py) · [notes](06-Standard%20Library/06-Typing-And-Type-Hints.md) · [notebook](06-Standard%20Library/06-Typing-And-Type-Hints.ipynb)
- [ ] [07-Logging](06-Standard%20Library/07-Logging.py) · [notes](06-Standard%20Library/07-Logging.md) · [notebook](06-Standard%20Library/07-Logging.ipynb)
- [ ] [08-Enum](06-Standard%20Library/08-Enum.py) · [notes](06-Standard%20Library/08-Enum.md) · [notebook](06-Standard%20Library/08-Enum.ipynb)
- [ ] [09-Unittest-Basics](06-Standard%20Library/09-Unittest-Basics.py) · [notes](06-Standard%20Library/09-Unittest-Basics.md) · [notebook](06-Standard%20Library/09-Unittest-Basics.ipynb)
- [ ] [10-Argparse](06-Standard%20Library/10-Argparse.py) · [notes](06-Standard%20Library/10-Argparse.md) · [notebook](06-Standard%20Library/10-Argparse.ipynb)
- [ ] [11-Math-And-Numeric-Modules](06-Standard%20Library/11-Math-And-Numeric-Modules.py) · [notes](06-Standard%20Library/11-Math-And-Numeric-Modules.md) · [notebook](06-Standard%20Library/11-Math-And-Numeric-Modules.ipynb)
- [ ] [12-Random-And-Secrets](06-Standard%20Library/12-Random-And-Secrets.py) · [notes](06-Standard%20Library/12-Random-And-Secrets.md) · [notebook](06-Standard%20Library/12-Random-And-Secrets.ipynb)
- [ ] [13-Time-Module](06-Standard%20Library/13-Time-Module.py) · [notes](06-Standard%20Library/13-Time-Module.md) · [notebook](06-Standard%20Library/13-Time-Module.ipynb)
- [ ] [14-Heapq-Bisect-Array-Queue](06-Standard%20Library/14-Heapq-Bisect-Array-Queue.py) · [notes](06-Standard%20Library/14-Heapq-Bisect-Array-Queue.md) · [notebook](06-Standard%20Library/14-Heapq-Bisect-Array-Queue.ipynb)
- [ ] [15-Hashing-And-Encoding](06-Standard%20Library/15-Hashing-And-Encoding.py) · [notes](06-Standard%20Library/15-Hashing-And-Encoding.md) · [notebook](06-Standard%20Library/15-Hashing-And-Encoding.ipynb)
- [ ] [16-Serialization-And-Config](06-Standard%20Library/16-Serialization-And-Config.py) · [notes](06-Standard%20Library/16-Serialization-And-Config.md) · [notebook](06-Standard%20Library/16-Serialization-And-Config.ipynb)
- [ ] [17-Sqlite3](06-Standard%20Library/17-Sqlite3.py) · [notes](06-Standard%20Library/17-Sqlite3.md) · [notebook](06-Standard%20Library/17-Sqlite3.ipynb)
- [ ] [18-Text-Utilities](06-Standard%20Library/18-Text-Utilities.py) · [notes](06-Standard%20Library/18-Text-Utilities.md) · [notebook](06-Standard%20Library/18-Text-Utilities.ipynb)
- [ ] [19-File-Utils-And-Archives](06-Standard%20Library/19-File-Utils-And-Archives.py) · [notes](06-Standard%20Library/19-File-Utils-And-Archives.md) · [notebook](06-Standard%20Library/19-File-Utils-And-Archives.ipynb)
- [ ] [20-Subprocess-And-Signals](06-Standard%20Library/20-Subprocess-And-Signals.py) · [notes](06-Standard%20Library/20-Subprocess-And-Signals.md) · [notebook](06-Standard%20Library/20-Subprocess-And-Signals.ipynb)
- [ ] [21-Inspect-AST-And-Dis](06-Standard%20Library/21-Inspect-AST-And-Dis.py) · [notes](06-Standard%20Library/21-Inspect-AST-And-Dis.md) · [notebook](06-Standard%20Library/21-Inspect-AST-And-Dis.ipynb)
- [ ] [22-Networking-Basics](06-Standard%20Library/22-Networking-Basics.py) · [notes](06-Standard%20Library/22-Networking-Basics.md) · [notebook](06-Standard%20Library/22-Networking-Basics.ipynb)

**07-NumPy**

- [ ] [01-Array-Basics](07-NumPy/01-Array-Basics.py) · [notes](07-NumPy/01-Array-Basics.md) · [notebook](07-NumPy/01-Array-Basics.ipynb)
- [ ] [02-Indexing-And-Slicing](07-NumPy/02-Indexing-And-Slicing.py) · [notes](07-NumPy/02-Indexing-And-Slicing.md) · [notebook](07-NumPy/02-Indexing-And-Slicing.ipynb)
- [ ] [03-Reshaping-And-Manipulation](07-NumPy/03-Reshaping-And-Manipulation.py) · [notes](07-NumPy/03-Reshaping-And-Manipulation.md) · [notebook](07-NumPy/03-Reshaping-And-Manipulation.ipynb)
- [ ] [04-Operations-And-Broadcasting](07-NumPy/04-Operations-And-Broadcasting.py) · [notes](07-NumPy/04-Operations-And-Broadcasting.md) · [notebook](07-NumPy/04-Operations-And-Broadcasting.ipynb)
- [ ] [05-Statistical-And-Math-Functions](07-NumPy/05-Statistical-And-Math-Functions.py) · [notes](07-NumPy/05-Statistical-And-Math-Functions.md) · [notebook](07-NumPy/05-Statistical-And-Math-Functions.ipynb)
- [ ] [06-Linear-Algebra](07-NumPy/06-Linear-Algebra.py) · [notes](07-NumPy/06-Linear-Algebra.md) · [notebook](07-NumPy/06-Linear-Algebra.ipynb)
- [ ] [07-Random-Module](07-NumPy/07-Random-Module.py) · [notes](07-NumPy/07-Random-Module.md) · [notebook](07-NumPy/07-Random-Module.ipynb)
- [ ] [08-Performance-And-Vectorization](07-NumPy/08-Performance-And-Vectorization.py) · [notes](07-NumPy/08-Performance-And-Vectorization.md) · [notebook](07-NumPy/08-Performance-And-Vectorization.ipynb)
- [ ] [09-File-IO](07-NumPy/09-File-IO.py) · [notes](07-NumPy/09-File-IO.md) · [notebook](07-NumPy/09-File-IO.ipynb)
- [ ] [10-Advanced-NumPy](07-NumPy/10-Advanced-NumPy.py) · [notes](07-NumPy/10-Advanced-NumPy.md) · [notebook](07-NumPy/10-Advanced-NumPy.ipynb)

**08-Pandas**

- [ ] [01-Series-And-DataFrame-Basics](08-Pandas/01-Series-And-DataFrame-Basics.py) · [notes](08-Pandas/01-Series-And-DataFrame-Basics.md) · [notebook](08-Pandas/01-Series-And-DataFrame-Basics.ipynb)
- [ ] [02-Selection-And-Indexing](08-Pandas/02-Selection-And-Indexing.py) · [notes](08-Pandas/02-Selection-And-Indexing.md) · [notebook](08-Pandas/02-Selection-And-Indexing.ipynb)
- [ ] [03-Data-Cleaning](08-Pandas/03-Data-Cleaning.py) · [notes](08-Pandas/03-Data-Cleaning.md) · [notebook](08-Pandas/03-Data-Cleaning.ipynb)
- [ ] [04-Data-Transformation](08-Pandas/04-Data-Transformation.py) · [notes](08-Pandas/04-Data-Transformation.md) · [notebook](08-Pandas/04-Data-Transformation.ipynb)
- [ ] [05-GroupBy-And-Aggregation](08-Pandas/05-GroupBy-And-Aggregation.py) · [notes](08-Pandas/05-GroupBy-And-Aggregation.md) · [notebook](08-Pandas/05-GroupBy-And-Aggregation.ipynb)
- [ ] [06-Merging-And-Joining](08-Pandas/06-Merging-And-Joining.py) · [notes](08-Pandas/06-Merging-And-Joining.md) · [notebook](08-Pandas/06-Merging-And-Joining.ipynb)
- [ ] [07-Reshaping](08-Pandas/07-Reshaping.py) · [notes](08-Pandas/07-Reshaping.md) · [notebook](08-Pandas/07-Reshaping.ipynb)
- [ ] [08-Time-Series](08-Pandas/08-Time-Series.py) · [notes](08-Pandas/08-Time-Series.md) · [notebook](08-Pandas/08-Time-Series.ipynb)
- [ ] [09-Input-Output](08-Pandas/09-Input-Output.py) · [notes](08-Pandas/09-Input-Output.md) · [notebook](08-Pandas/09-Input-Output.ipynb)
- [ ] [10-Performance-And-Best-Practices](08-Pandas/10-Performance-And-Best-Practices.py) · [notes](08-Pandas/10-Performance-And-Best-Practices.md) · [notebook](08-Pandas/10-Performance-And-Best-Practices.ipynb)

**09-Tooling-And-Quality**

- [ ] [01-Pytest-In-Depth](09-Tooling-And-Quality/01-Pytest-In-Depth.py) · [notes](09-Tooling-And-Quality/01-Pytest-In-Depth.md) · [notebook](09-Tooling-And-Quality/01-Pytest-In-Depth.ipynb)
- [ ] [02-Debugging-With-Pdb](09-Tooling-And-Quality/02-Debugging-With-Pdb.py) · [notes](09-Tooling-And-Quality/02-Debugging-With-Pdb.md) · [notebook](09-Tooling-And-Quality/02-Debugging-With-Pdb.ipynb)
- [ ] [03-Profiling-And-Benchmarking](09-Tooling-And-Quality/03-Profiling-And-Benchmarking.py) · [notes](09-Tooling-And-Quality/03-Profiling-And-Benchmarking.md) · [notebook](09-Tooling-And-Quality/03-Profiling-And-Benchmarking.ipynb)
- [ ] [04-Packaging-And-Pyproject](09-Tooling-And-Quality/04-Packaging-And-Pyproject.py) · [notes](09-Tooling-And-Quality/04-Packaging-And-Pyproject.md) · [notebook](09-Tooling-And-Quality/04-Packaging-And-Pyproject.ipynb)
- [ ] [05-Code-Quality](09-Tooling-And-Quality/05-Code-Quality.py) · [notes](09-Tooling-And-Quality/05-Code-Quality.md) · [notebook](09-Tooling-And-Quality/05-Code-Quality.ipynb)
- [ ] [06-Documentation-And-Doctest](09-Tooling-And-Quality/06-Documentation-And-Doctest.py) · [notes](09-Tooling-And-Quality/06-Documentation-And-Doctest.md) · [notebook](09-Tooling-And-Quality/06-Documentation-And-Doctest.ipynb)
- [ ] [07-Security-Basics](09-Tooling-And-Quality/07-Security-Basics.py) · [notes](09-Tooling-And-Quality/07-Security-Basics.md) · [notebook](09-Tooling-And-Quality/07-Security-Basics.ipynb)

## Not covered yet (planned)

- OOP depth: descriptors, `__getattr__`, `__init_subclass__`, composition vs
  inheritance, design patterns.
- NumPy/Pandas deepening and plotting (matplotlib).
- Applied Python: HTTP/web APIs, scraping, databases, automation.
- Practice exercises with solutions and capstone projects.

