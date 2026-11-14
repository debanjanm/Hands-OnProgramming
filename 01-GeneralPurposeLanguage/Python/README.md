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

- [ ] [01-Setup-And-Tooling](01-Python%20Fundamentals/01-Setup-And-Tooling.py) · [notes](01-Python%20Fundamentals/01-Setup-And-Tooling.md)
- [ ] [02-Fundamentals](01-Python%20Fundamentals/02-Fundamentals.py) · [notes](01-Python%20Fundamentals/02-Fundamentals.md)
- [ ] [03-Control-Flow](01-Python%20Fundamentals/03-Control-Flow.py) · [notes](01-Python%20Fundamentals/03-Control-Flow.md)

**02-Data Types**

- [ ] [01-Primitive](02-Data%20Types/01-Primitive.py) · [notes](02-Data%20Types/01-Primitive.md)
- [ ] [02-Strings](02-Data%20Types/02-Strings.py) · [notes](02-Data%20Types/02-Strings.md)
- [ ] [03-List](02-Data%20Types/03-List.py) · [notes](02-Data%20Types/03-List.md)
- [ ] [04-Tuples](02-Data%20Types/04-Tuples.py) · [notes](02-Data%20Types/04-Tuples.md)
- [ ] [05-Sets](02-Data%20Types/05-Sets.py) · [notes](02-Data%20Types/05-Sets.md)
- [ ] [06-Dictionary](02-Data%20Types/06-Dictionary.py) · [notes](02-Data%20Types/06-Dictionary.md)
- [ ] [07-Type-Casting](02-Data%20Types/07-Type-Casting.py) · [notes](02-Data%20Types/07-Type-Casting.md)
- [ ] [08-Comprehensions](02-Data%20Types/08-Comprehensions.py) · [notes](02-Data%20Types/08-Comprehensions.md)
- [ ] [09-Unpacking-And-Packing](02-Data%20Types/09-Unpacking-And-Packing.py) · [notes](02-Data%20Types/09-Unpacking-And-Packing.md)
- [ ] [10-Bytes-And-Bytearray](02-Data%20Types/10-Bytes-And-Bytearray.py) · [notes](02-Data%20Types/10-Bytes-And-Bytearray.md)
- [ ] [11-Range-And-Slice-Objects](02-Data%20Types/11-Range-And-Slice-Objects.py) · [notes](02-Data%20Types/11-Range-And-Slice-Objects.md)
- [ ] [12-Mutability-And-Memory-Model](02-Data%20Types/12-Mutability-And-Memory-Model.py) · [notes](02-Data%20Types/12-Mutability-And-Memory-Model.md)

**03-Functions**

- [ ] [01-Built-in-Functions](03-Functions/01-Built-in-Functions.py) · [notes](03-Functions/01-Built-in-Functions.md)
- [ ] [02-Functions](03-Functions/02-Functions.py) · [notes](03-Functions/02-Functions.md)
- [ ] [03-Scope-And-Namespaces](03-Functions/03-Scope-And-Namespaces.py) · [notes](03-Functions/03-Scope-And-Namespaces.md)
- [ ] [04-Functional-Programming](03-Functions/04-Functional-Programming.py) · [notes](03-Functions/04-Functional-Programming.md)
- [ ] [05-Decorators](03-Functions/05-Decorators.py) · [notes](03-Functions/05-Decorators.md)

**04-OOPs**

- [ ] [01-Class-Object](04-OOPs/01-Class-Object.py) · [notes](04-OOPs/01-Class-Object.md)
- [ ] [02-Encapsulation](04-OOPs/02-Encapsulation.py) · [notes](04-OOPs/02-Encapsulation.md)
- [ ] [03-Inheritance](04-OOPs/03-Inheritance.py) · [notes](04-OOPs/03-Inheritance.md)
- [ ] [04-Polymorphism](04-OOPs/04-Polymorphism.py) · [notes](04-OOPs/04-Polymorphism.md)
- [ ] [05-Abstraction](04-OOPs/05-Abstraction.py) · [notes](04-OOPs/05-Abstraction.md)
- [ ] [06-Dataclasses-And-Operator-Overloading](04-OOPs/06-Dataclasses-And-Operator-Overloading.py) · [notes](04-OOPs/06-Dataclasses-And-Operator-Overloading.md)
- [ ] [07-Custom-Containers-And-ABCs](04-OOPs/07-Custom-Containers-And-ABCs.py) · [notes](04-OOPs/07-Custom-Containers-And-ABCs.md)
- [ ] [08-SOLID-Principles](04-OOPs/08-SOLID-Principles.py) · [notes](04-OOPs/08-SOLID-Principles.md)

**05-Python Advanced**

- [ ] [01-Iterators](05-Python%20Advanced/01-Iterators.py) · [notes](05-Python%20Advanced/01-Iterators.md)
- [ ] [02-Generators](05-Python%20Advanced/02-Generators.py) · [notes](05-Python%20Advanced/02-Generators.md)
- [ ] [03-Error-And-Exception-Handling](05-Python%20Advanced/03-Error-And-Exception-Handling.py) · [notes](05-Python%20Advanced/03-Error-And-Exception-Handling.md)
- [ ] [04-File-Handling](05-Python%20Advanced/04-File-Handling.py) · [notes](05-Python%20Advanced/04-File-Handling.md)
- [ ] [05-Modules-And-Packages](05-Python%20Advanced/05-Modules-And-Packages.py) · [notes](05-Python%20Advanced/05-Modules-And-Packages.md)
- [ ] [06-Context-Managers](05-Python%20Advanced/06-Context-Managers.py) · [notes](05-Python%20Advanced/06-Context-Managers.md)
- [ ] [07-Regular-Expressions](05-Python%20Advanced/07-Regular-Expressions.py) · [notes](05-Python%20Advanced/07-Regular-Expressions.md)
- [ ] [08-Itertools-And-Functools](05-Python%20Advanced/08-Itertools-And-Functools.py) · [notes](05-Python%20Advanced/08-Itertools-And-Functools.md)
- [ ] [09-Multithreading-And-Multiprocessing](05-Python%20Advanced/09-Multithreading-And-Multiprocessing.py) · [notes](05-Python%20Advanced/09-Multithreading-And-Multiprocessing.md)
- [ ] [10-Async-Await](05-Python%20Advanced/10-Async-Await.py) · [notes](05-Python%20Advanced/10-Async-Await.md)
- [ ] [11-Threading-Primitives](05-Python%20Advanced/11-Threading-Primitives.py) · [notes](05-Python%20Advanced/11-Threading-Primitives.md)
- [ ] [12-Multiprocessing-Pool-And-Shared-State](05-Python%20Advanced/12-Multiprocessing-Pool-And-Shared-State.py) · [notes](05-Python%20Advanced/12-Multiprocessing-Pool-And-Shared-State.md)
- [ ] [13-Asyncio-Advanced](05-Python%20Advanced/13-Asyncio-Advanced.py) · [notes](05-Python%20Advanced/13-Asyncio-Advanced.md)

**06-Standard Library**

- [ ] [01-Collections-Module](06-Standard%20Library/01-Collections-Module.py) · [notes](06-Standard%20Library/01-Collections-Module.md)
- [ ] [02-Datetime-Module](06-Standard%20Library/02-Datetime-Module.py) · [notes](06-Standard%20Library/02-Datetime-Module.md)
- [ ] [03-Os-And-Sys](06-Standard%20Library/03-Os-And-Sys.py) · [notes](06-Standard%20Library/03-Os-And-Sys.md)
- [ ] [04-Json-And-Csv](06-Standard%20Library/04-Json-And-Csv.py) · [notes](06-Standard%20Library/04-Json-And-Csv.md)
- [ ] [05-Pathlib-Module](06-Standard%20Library/05-Pathlib-Module.py) · [notes](06-Standard%20Library/05-Pathlib-Module.md)
- [ ] [06-Typing-And-Type-Hints](06-Standard%20Library/06-Typing-And-Type-Hints.py) · [notes](06-Standard%20Library/06-Typing-And-Type-Hints.md)
- [ ] [07-Logging](06-Standard%20Library/07-Logging.py) · [notes](06-Standard%20Library/07-Logging.md)
- [ ] [08-Enum](06-Standard%20Library/08-Enum.py) · [notes](06-Standard%20Library/08-Enum.md)
- [ ] [09-Unittest-Basics](06-Standard%20Library/09-Unittest-Basics.py) · [notes](06-Standard%20Library/09-Unittest-Basics.md)
- [ ] [10-Argparse](06-Standard%20Library/10-Argparse.py) · [notes](06-Standard%20Library/10-Argparse.md)
- [ ] [11-Math-And-Numeric-Modules](06-Standard%20Library/11-Math-And-Numeric-Modules.py) · [notes](06-Standard%20Library/11-Math-And-Numeric-Modules.md)
- [ ] [12-Random-And-Secrets](06-Standard%20Library/12-Random-And-Secrets.py) · [notes](06-Standard%20Library/12-Random-And-Secrets.md)
- [ ] [13-Time-Module](06-Standard%20Library/13-Time-Module.py) · [notes](06-Standard%20Library/13-Time-Module.md)
- [ ] [14-Heapq-Bisect-Array-Queue](06-Standard%20Library/14-Heapq-Bisect-Array-Queue.py) · [notes](06-Standard%20Library/14-Heapq-Bisect-Array-Queue.md)
- [ ] [15-Hashing-And-Encoding](06-Standard%20Library/15-Hashing-And-Encoding.py) · [notes](06-Standard%20Library/15-Hashing-And-Encoding.md)
- [ ] [16-Serialization-And-Config](06-Standard%20Library/16-Serialization-And-Config.py) · [notes](06-Standard%20Library/16-Serialization-And-Config.md)
- [ ] [17-Sqlite3](06-Standard%20Library/17-Sqlite3.py) · [notes](06-Standard%20Library/17-Sqlite3.md)
- [ ] [18-Text-Utilities](06-Standard%20Library/18-Text-Utilities.py) · [notes](06-Standard%20Library/18-Text-Utilities.md)
- [ ] [19-File-Utils-And-Archives](06-Standard%20Library/19-File-Utils-And-Archives.py) · [notes](06-Standard%20Library/19-File-Utils-And-Archives.md)
- [ ] [20-Subprocess-And-Signals](06-Standard%20Library/20-Subprocess-And-Signals.py) · [notes](06-Standard%20Library/20-Subprocess-And-Signals.md)
- [ ] [21-Inspect-AST-And-Dis](06-Standard%20Library/21-Inspect-AST-And-Dis.py) · [notes](06-Standard%20Library/21-Inspect-AST-And-Dis.md)
- [ ] [22-Networking-Basics](06-Standard%20Library/22-Networking-Basics.py) · [notes](06-Standard%20Library/22-Networking-Basics.md)

**07-NumPy**

- [ ] [01-Array-Basics](07-NumPy/01-Array-Basics.py) · [notes](07-NumPy/01-Array-Basics.md)
- [ ] [02-Indexing-And-Slicing](07-NumPy/02-Indexing-And-Slicing.py) · [notes](07-NumPy/02-Indexing-And-Slicing.md)
- [ ] [03-Reshaping-And-Manipulation](07-NumPy/03-Reshaping-And-Manipulation.py) · [notes](07-NumPy/03-Reshaping-And-Manipulation.md)
- [ ] [04-Operations-And-Broadcasting](07-NumPy/04-Operations-And-Broadcasting.py) · [notes](07-NumPy/04-Operations-And-Broadcasting.md)
- [ ] [05-Statistical-And-Math-Functions](07-NumPy/05-Statistical-And-Math-Functions.py) · [notes](07-NumPy/05-Statistical-And-Math-Functions.md)
- [ ] [06-Linear-Algebra](07-NumPy/06-Linear-Algebra.py) · [notes](07-NumPy/06-Linear-Algebra.md)
- [ ] [07-Random-Module](07-NumPy/07-Random-Module.py) · [notes](07-NumPy/07-Random-Module.md)
- [ ] [08-Performance-And-Vectorization](07-NumPy/08-Performance-And-Vectorization.py) · [notes](07-NumPy/08-Performance-And-Vectorization.md)
- [ ] [09-File-IO](07-NumPy/09-File-IO.py) · [notes](07-NumPy/09-File-IO.md)
- [ ] [10-Advanced-NumPy](07-NumPy/10-Advanced-NumPy.py) · [notes](07-NumPy/10-Advanced-NumPy.md)

**08-Pandas**

- [ ] [01-Series-And-DataFrame-Basics](08-Pandas/01-Series-And-DataFrame-Basics.py) · [notes](08-Pandas/01-Series-And-DataFrame-Basics.md)
- [ ] [02-Selection-And-Indexing](08-Pandas/02-Selection-And-Indexing.py) · [notes](08-Pandas/02-Selection-And-Indexing.md)
- [ ] [03-Data-Cleaning](08-Pandas/03-Data-Cleaning.py) · [notes](08-Pandas/03-Data-Cleaning.md)
- [ ] [04-Data-Transformation](08-Pandas/04-Data-Transformation.py) · [notes](08-Pandas/04-Data-Transformation.md)
- [ ] [05-GroupBy-And-Aggregation](08-Pandas/05-GroupBy-And-Aggregation.py) · [notes](08-Pandas/05-GroupBy-And-Aggregation.md)
- [ ] [06-Merging-And-Joining](08-Pandas/06-Merging-And-Joining.py) · [notes](08-Pandas/06-Merging-And-Joining.md)
- [ ] [07-Reshaping](08-Pandas/07-Reshaping.py) · [notes](08-Pandas/07-Reshaping.md)
- [ ] [08-Time-Series](08-Pandas/08-Time-Series.py) · [notes](08-Pandas/08-Time-Series.md)
- [ ] [09-Input-Output](08-Pandas/09-Input-Output.py) · [notes](08-Pandas/09-Input-Output.md)
- [ ] [10-Performance-And-Best-Practices](08-Pandas/10-Performance-And-Best-Practices.py) · [notes](08-Pandas/10-Performance-And-Best-Practices.md)

**09-Tooling-And-Quality**

- [ ] [01-Pytest-In-Depth](09-Tooling-And-Quality/01-Pytest-In-Depth.py) · [notes](09-Tooling-And-Quality/01-Pytest-In-Depth.md)
- [ ] [02-Debugging-With-Pdb](09-Tooling-And-Quality/02-Debugging-With-Pdb.py) · [notes](09-Tooling-And-Quality/02-Debugging-With-Pdb.md)
- [ ] [03-Profiling-And-Benchmarking](09-Tooling-And-Quality/03-Profiling-And-Benchmarking.py) · [notes](09-Tooling-And-Quality/03-Profiling-And-Benchmarking.md)
- [ ] [04-Packaging-And-Pyproject](09-Tooling-And-Quality/04-Packaging-And-Pyproject.py) · [notes](09-Tooling-And-Quality/04-Packaging-And-Pyproject.md)
- [ ] [05-Code-Quality](09-Tooling-And-Quality/05-Code-Quality.py) · [notes](09-Tooling-And-Quality/05-Code-Quality.md)
- [ ] [06-Documentation-And-Doctest](09-Tooling-And-Quality/06-Documentation-And-Doctest.py) · [notes](09-Tooling-And-Quality/06-Documentation-And-Doctest.md)
- [ ] [07-Security-Basics](09-Tooling-And-Quality/07-Security-Basics.py) · [notes](09-Tooling-And-Quality/07-Security-Basics.md)

## Not covered yet (planned)

- OOP depth: descriptors, `__getattr__`, `__init_subclass__`, composition vs
  inheritance, design patterns.
- NumPy/Pandas deepening and plotting (matplotlib).
- Applied Python: HTTP/web APIs, scraping, databases, automation.
- Practice exercises with solutions and capstone projects.

