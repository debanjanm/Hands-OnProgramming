# Python

A from-scratch to advanced Python track. Every topic is one Jupyter notebook:
a short plain-English cheat sheet at the top (what it covers, key points,
gotchas, when it matters), then the runnable code in numbered sections with its
output saved, so it reads well on GitHub and is easy to experiment with.

```bash
pip install -r requirements.txt
jupyter lab "01-Python Fundamentals/02-Fundamentals.ipynb"
```

## Requirements

- **Python 3.10+** (tested on 3.12). A few files use newer features and print a
  skip message on older versions: `match-case` needs 3.10, `except*` and
  `StrEnum` need 3.11.
- Only the NumPy, Pandas and Visualization folders need third-party packages, and
  `09-Tooling-And-Quality` demos dev tools (pytest, mypy, black, flake8, isort,
  build). Install with `pip install -r requirements.txt`; each file skips a
  tool that is missing instead of failing.
- Everything else uses the standard library only. Notebooks clean up their own
  scratch files and never touch the internet (networking demos stay on
  `127.0.0.1`).

## How to study

1. Read the **Quick notes** cell at the top of a notebook for the idea, then go
   through the sections: run each cell and read it next to its output.
2. Go in folder order; notebooks inside a folder are numbered in reading order.
3. Revisit the **Gotchas** in each note - that is where the bugs live.
4. Edit freely. Your changes are saved in the notebook; use `git restore` to get
   the original back.

## Notebooks and the few scripts

The notebooks are the source - there is no separate `.py` per topic. Outputs are
saved in the files; refresh them after editing with:

```bash
python3 tools/run_notebooks.py                # run every notebook and report failures
python3 tools/run_notebooks.py --save         # ...and save the outputs into the files
python3 tools/run_notebooks.py --only Sets    # just one topic
python3 tools/run_notebooks.py --clear        # remove saved outputs
```

Plain `.py` files exist only where a notebook cannot do the job:

- `05-Python Advanced/09-Multithreading-And-Multiprocessing.py` and
  `12-Multiprocessing-Pool-And-Shared-State.py` - worker processes must re-import
  the code, which functions defined in a notebook cell cannot do. Their
  notebooks run and import the scripts.
- `05-Python Advanced/demo_package/` - a small package that the modules notebook imports.
- `12-Practice-And-Projects/` - exercises and projects are real code with `pytest` tests.
- `tools/run_notebooks.py` - the helper above.

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
- [10-Visualization](10-Visualization/README.md)

### Stage 5 — Professional practice

- [09-Tooling-And-Quality](09-Tooling-And-Quality/README.md)
- [11-Applied-Python](11-Applied-Python/README.md)
- [12-Practice-And-Projects](12-Practice-And-Projects/README.md)

## Progress checklist

Tick items as you finish them (edit this file).


**01-Python Fundamentals**

- [ ] [01-Setup-And-Tooling](01-Python%20Fundamentals/01-Setup-And-Tooling.ipynb)
- [ ] [02-Fundamentals](01-Python%20Fundamentals/02-Fundamentals.ipynb)
- [ ] [03-Control-Flow](01-Python%20Fundamentals/03-Control-Flow.ipynb)

**02-Data Types**

- [ ] [01-Primitive](02-Data%20Types/01-Primitive.ipynb)
- [ ] [02-Strings](02-Data%20Types/02-Strings.ipynb)
- [ ] [03-List](02-Data%20Types/03-List.ipynb)
- [ ] [04-Tuples](02-Data%20Types/04-Tuples.ipynb)
- [ ] [05-Sets](02-Data%20Types/05-Sets.ipynb)
- [ ] [06-Dictionary](02-Data%20Types/06-Dictionary.ipynb)
- [ ] [07-Type-Casting](02-Data%20Types/07-Type-Casting.ipynb)
- [ ] [08-Comprehensions](02-Data%20Types/08-Comprehensions.ipynb)
- [ ] [09-Unpacking-And-Packing](02-Data%20Types/09-Unpacking-And-Packing.ipynb)
- [ ] [10-Bytes-And-Bytearray](02-Data%20Types/10-Bytes-And-Bytearray.ipynb)
- [ ] [11-Range-And-Slice-Objects](02-Data%20Types/11-Range-And-Slice-Objects.ipynb)
- [ ] [12-Mutability-And-Memory-Model](02-Data%20Types/12-Mutability-And-Memory-Model.ipynb)

**03-Functions**

- [ ] [01-Built-in-Functions](03-Functions/01-Built-in-Functions.ipynb)
- [ ] [02-Functions](03-Functions/02-Functions.ipynb)
- [ ] [03-Scope-And-Namespaces](03-Functions/03-Scope-And-Namespaces.ipynb)
- [ ] [04-Functional-Programming](03-Functions/04-Functional-Programming.ipynb)
- [ ] [05-Decorators](03-Functions/05-Decorators.ipynb)

**04-OOPs**

- [ ] [01-Class-Object](04-OOPs/01-Class-Object.ipynb)
- [ ] [02-Encapsulation](04-OOPs/02-Encapsulation.ipynb)
- [ ] [03-Inheritance](04-OOPs/03-Inheritance.ipynb)
- [ ] [04-Polymorphism](04-OOPs/04-Polymorphism.ipynb)
- [ ] [05-Abstraction](04-OOPs/05-Abstraction.ipynb)
- [ ] [06-Dataclasses-And-Operator-Overloading](04-OOPs/06-Dataclasses-And-Operator-Overloading.ipynb)
- [ ] [07-Custom-Containers-And-ABCs](04-OOPs/07-Custom-Containers-And-ABCs.ipynb)
- [ ] [08-SOLID-Principles](04-OOPs/08-SOLID-Principles.ipynb)
- [ ] [09-Descriptors-And-Properties](04-OOPs/09-Descriptors-And-Properties.ipynb)
- [ ] [10-Attribute-Access-Hooks](04-OOPs/10-Attribute-Access-Hooks.ipynb)
- [ ] [11-Metaclasses-And-Class-Creation](04-OOPs/11-Metaclasses-And-Class-Creation.ipynb)
- [ ] [12-Object-Lifecycle-Copy-And-Serialization](04-OOPs/12-Object-Lifecycle-Copy-And-Serialization.ipynb)
- [ ] [13-Composition-Vs-Inheritance](04-OOPs/13-Composition-Vs-Inheritance.ipynb)
- [ ] [14-Creational-Design-Patterns](04-OOPs/14-Creational-Design-Patterns.ipynb)
- [ ] [15-Structural-Design-Patterns](04-OOPs/15-Structural-Design-Patterns.ipynb)
- [ ] [16-Behavioral-Design-Patterns](04-OOPs/16-Behavioral-Design-Patterns.ipynb)
- [ ] [17-Pythonic-Patterns-And-Anti-Patterns](04-OOPs/17-Pythonic-Patterns-And-Anti-Patterns.ipynb)

**05-Python Advanced**

- [ ] [01-Iterators](05-Python%20Advanced/01-Iterators.ipynb)
- [ ] [02-Generators](05-Python%20Advanced/02-Generators.ipynb)
- [ ] [03-Error-And-Exception-Handling](05-Python%20Advanced/03-Error-And-Exception-Handling.ipynb)
- [ ] [04-File-Handling](05-Python%20Advanced/04-File-Handling.ipynb)
- [ ] [05-Modules-And-Packages](05-Python%20Advanced/05-Modules-And-Packages.ipynb)
- [ ] [06-Context-Managers](05-Python%20Advanced/06-Context-Managers.ipynb)
- [ ] [07-Regular-Expressions](05-Python%20Advanced/07-Regular-Expressions.ipynb)
- [ ] [08-Itertools-And-Functools](05-Python%20Advanced/08-Itertools-And-Functools.ipynb)
- [ ] [09-Multithreading-And-Multiprocessing](05-Python%20Advanced/09-Multithreading-And-Multiprocessing.ipynb) · [script](05-Python%20Advanced/09-Multithreading-And-Multiprocessing.py)
- [ ] [10-Async-Await](05-Python%20Advanced/10-Async-Await.ipynb)
- [ ] [11-Threading-Primitives](05-Python%20Advanced/11-Threading-Primitives.ipynb)
- [ ] [12-Multiprocessing-Pool-And-Shared-State](05-Python%20Advanced/12-Multiprocessing-Pool-And-Shared-State.ipynb) · [script](05-Python%20Advanced/12-Multiprocessing-Pool-And-Shared-State.py)
- [ ] [13-Asyncio-Advanced](05-Python%20Advanced/13-Asyncio-Advanced.ipynb)

**06-Standard Library**

- [ ] [01-Collections-Module](06-Standard%20Library/01-Collections-Module.ipynb)
- [ ] [02-Datetime-Module](06-Standard%20Library/02-Datetime-Module.ipynb)
- [ ] [03-Os-And-Sys](06-Standard%20Library/03-Os-And-Sys.ipynb)
- [ ] [04-Json-And-Csv](06-Standard%20Library/04-Json-And-Csv.ipynb)
- [ ] [05-Pathlib-Module](06-Standard%20Library/05-Pathlib-Module.ipynb)
- [ ] [06-Typing-And-Type-Hints](06-Standard%20Library/06-Typing-And-Type-Hints.ipynb)
- [ ] [07-Logging](06-Standard%20Library/07-Logging.ipynb)
- [ ] [08-Enum](06-Standard%20Library/08-Enum.ipynb)
- [ ] [09-Unittest-Basics](06-Standard%20Library/09-Unittest-Basics.ipynb)
- [ ] [10-Argparse](06-Standard%20Library/10-Argparse.ipynb)
- [ ] [11-Math-And-Numeric-Modules](06-Standard%20Library/11-Math-And-Numeric-Modules.ipynb)
- [ ] [12-Random-And-Secrets](06-Standard%20Library/12-Random-And-Secrets.ipynb)
- [ ] [13-Time-Module](06-Standard%20Library/13-Time-Module.ipynb)
- [ ] [14-Heapq-Bisect-Array-Queue](06-Standard%20Library/14-Heapq-Bisect-Array-Queue.ipynb)
- [ ] [15-Hashing-And-Encoding](06-Standard%20Library/15-Hashing-And-Encoding.ipynb)
- [ ] [16-Serialization-And-Config](06-Standard%20Library/16-Serialization-And-Config.ipynb)
- [ ] [17-Sqlite3](06-Standard%20Library/17-Sqlite3.ipynb)
- [ ] [18-Text-Utilities](06-Standard%20Library/18-Text-Utilities.ipynb)
- [ ] [19-File-Utils-And-Archives](06-Standard%20Library/19-File-Utils-And-Archives.ipynb)
- [ ] [20-Subprocess-And-Signals](06-Standard%20Library/20-Subprocess-And-Signals.ipynb)
- [ ] [21-Inspect-AST-And-Dis](06-Standard%20Library/21-Inspect-AST-And-Dis.ipynb)
- [ ] [22-Networking-Basics](06-Standard%20Library/22-Networking-Basics.ipynb)
- [ ] [23-Ctypes-And-Memory-Mapped-Files](06-Standard%20Library/23-Ctypes-And-Memory-Mapped-Files.ipynb)
- [ ] [24-Graphlib-Codecs-And-Misc-Modules](06-Standard%20Library/24-Graphlib-Codecs-And-Misc-Modules.ipynb)
- [ ] [25-Modern-Python-Features-3.10-To-3.13](06-Standard%20Library/25-Modern-Python-Features-3.10-To-3.13.ipynb)

**07-NumPy**

- [ ] [01-Array-Basics](07-NumPy/01-Array-Basics.ipynb)
- [ ] [02-Indexing-And-Slicing](07-NumPy/02-Indexing-And-Slicing.ipynb)
- [ ] [03-Reshaping-And-Manipulation](07-NumPy/03-Reshaping-And-Manipulation.ipynb)
- [ ] [04-Operations-And-Broadcasting](07-NumPy/04-Operations-And-Broadcasting.ipynb)
- [ ] [05-Statistical-And-Math-Functions](07-NumPy/05-Statistical-And-Math-Functions.ipynb)
- [ ] [06-Linear-Algebra](07-NumPy/06-Linear-Algebra.ipynb)
- [ ] [07-Random-Module](07-NumPy/07-Random-Module.ipynb)
- [ ] [08-Performance-And-Vectorization](07-NumPy/08-Performance-And-Vectorization.ipynb)
- [ ] [09-File-IO](07-NumPy/09-File-IO.ipynb)
- [ ] [10-Advanced-NumPy](07-NumPy/10-Advanced-NumPy.ipynb)
- [ ] [11-Strides-And-Memory-Layout](07-NumPy/11-Strides-And-Memory-Layout.ipynb)
- [ ] [12-Advanced-Indexing-Ufuncs-And-Sorting](07-NumPy/12-Advanced-Indexing-Ufuncs-And-Sorting.ipynb)
- [ ] [13-NumPy-Recipes-And-Real-Patterns](07-NumPy/13-NumPy-Recipes-And-Real-Patterns.ipynb)

**08-Pandas**

- [ ] [01-Series-And-DataFrame-Basics](08-Pandas/01-Series-And-DataFrame-Basics.ipynb)
- [ ] [02-Selection-And-Indexing](08-Pandas/02-Selection-And-Indexing.ipynb)
- [ ] [03-Data-Cleaning](08-Pandas/03-Data-Cleaning.ipynb)
- [ ] [04-Data-Transformation](08-Pandas/04-Data-Transformation.ipynb)
- [ ] [05-GroupBy-And-Aggregation](08-Pandas/05-GroupBy-And-Aggregation.ipynb)
- [ ] [06-Merging-And-Joining](08-Pandas/06-Merging-And-Joining.ipynb)
- [ ] [07-Reshaping](08-Pandas/07-Reshaping.ipynb)
- [ ] [08-Time-Series](08-Pandas/08-Time-Series.ipynb)
- [ ] [09-Input-Output](08-Pandas/09-Input-Output.ipynb)
- [ ] [10-Performance-And-Best-Practices](08-Pandas/10-Performance-And-Best-Practices.ipynb)
- [ ] [11-MultiIndex-And-Advanced-Indexing](08-Pandas/11-MultiIndex-And-Advanced-Indexing.ipynb)
- [ ] [12-Dtypes-Categorical-And-Nullable](08-Pandas/12-Dtypes-Categorical-And-Nullable.ipynb)
- [ ] [13-Advanced-GroupBy-Window-And-Method-Chaining](08-Pandas/13-Advanced-GroupBy-Window-And-Method-Chaining.ipynb)
- [ ] [14-Text-And-Datetime-Deep-Dive](08-Pandas/14-Text-And-Datetime-Deep-Dive.ipynb)
- [ ] [15-End-To-End-Data-Analysis](08-Pandas/15-End-To-End-Data-Analysis.ipynb)

**09-Tooling-And-Quality**

- [ ] [01-Pytest-In-Depth](09-Tooling-And-Quality/01-Pytest-In-Depth.ipynb)
- [ ] [02-Debugging-With-Pdb](09-Tooling-And-Quality/02-Debugging-With-Pdb.ipynb)
- [ ] [03-Profiling-And-Benchmarking](09-Tooling-And-Quality/03-Profiling-And-Benchmarking.ipynb)
- [ ] [04-Packaging-And-Pyproject](09-Tooling-And-Quality/04-Packaging-And-Pyproject.ipynb)
- [ ] [05-Code-Quality](09-Tooling-And-Quality/05-Code-Quality.ipynb)
- [ ] [06-Documentation-And-Doctest](09-Tooling-And-Quality/06-Documentation-And-Doctest.ipynb)
- [ ] [07-Security-Basics](09-Tooling-And-Quality/07-Security-Basics.ipynb)

**10-Visualization**

- [ ] [01-Matplotlib-Basics](10-Visualization/01-Matplotlib-Basics.ipynb)
- [ ] [02-Matplotlib-Advanced](10-Visualization/02-Matplotlib-Advanced.ipynb)
- [ ] [03-Pandas-Plotting-And-Seaborn](10-Visualization/03-Pandas-Plotting-And-Seaborn.ipynb)
- [ ] [04-Visualization-Best-Practices](10-Visualization/04-Visualization-Best-Practices.ipynb)

**11-Applied-Python**

- [ ] [01-HTTP-Clients-And-Local-Servers](11-Applied-Python/01-HTTP-Clients-And-Local-Servers.ipynb)
- [ ] [02-Building-REST-APIs](11-Applied-Python/02-Building-REST-APIs.ipynb)
- [ ] [03-Async-HTTP-And-Concurrency](11-Applied-Python/03-Async-HTTP-And-Concurrency.ipynb)
- [ ] [04-Web-Scraping-On-Local-HTML](11-Applied-Python/04-Web-Scraping-On-Local-HTML.ipynb)
- [ ] [05-SQLite-With-Python](11-Applied-Python/05-SQLite-With-Python.ipynb)
- [ ] [06-SQLAlchemy-Core-And-ORM](11-Applied-Python/06-SQLAlchemy-Core-And-ORM.ipynb)
- [ ] [07-Data-Validation-And-Serialization](11-Applied-Python/07-Data-Validation-And-Serialization.ipynb)
- [ ] [08-CLI-Apps-And-Configuration](11-Applied-Python/08-CLI-Apps-And-Configuration.ipynb)
- [ ] [09-Automation-And-Scripting](11-Applied-Python/09-Automation-And-Scripting.ipynb)

**12-Practice-And-Projects** - exercises with tests and four capstone projects: [README](12-Practice-And-Projects/README.md)
