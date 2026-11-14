import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import textwrap
import tomllib
import venv
import zipfile
from pathlib import Path

# 01. Packaging - Introduction
# ------------------------------------
# - A script is one file you run. A PACKAGE is a folder of code with a
#   name, a version and a list of requirements that others (or you, on
#   another machine) can install with `pip install` and `import`.
# - Why bother packaging your own code?
#     * `import mytool` works from ANY folder, not only next to the file
#     * dependencies are declared once and installed automatically
#     * you get a command (`mytool --help`) instead of "python path/to/x.py"
#     * tests, CI and teammates all install it the same way
#     * you can publish it (PyPI, or a private index)
# - The modern recipe (PEP 517/518/621): ONE file, pyproject.toml, describes
#   the project. A "build backend" (setuptools, hatchling, flit, ...) turns
#   the folder into a distributable file.
# - This file builds a REAL package in a temporary folder, installs it
#   into a throwaway virtual environment OFFLINE, and inspects the result.
#   Nothing is written inside the repository and nothing is downloaded.

print("# 01. Packaging - Introduction")
print("# ------------------------------------")
print("# script -> package: pyproject.toml + src/ layout -> build -> wheel -> install")


def run(cmd, cwd, extra_env=None):
    """Run a command, capture text output, never write bytecode."""
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               PIP_DISABLE_PIP_VERSION_CHECK="1", PIP_NO_INPUT="1")
    env.update(extra_env or {})
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True,
                          cwd=str(cwd), timeout=120, env=env)


def last_line(proc):
    lines = [ln for ln in (proc.stdout + proc.stderr).strip().splitlines() if ln.strip()]
    return lines[-1] if lines else "(no output)"


# 02. Project Layout: flat vs src/
# ------------------------------------
# Flat layout:                      src layout (recommended):
#   myproj/                           myproj/
#     pyproject.toml                    pyproject.toml
#     greeter/                          src/
#       __init__.py                       greeter/
#     tests/                                __init__.py
#                                       tests/
#
# - FLAT: when you run Python or pytest from the project root, the folder
#   itself is on sys.path, so `import greeter` finds your WORKING COPY even if
#   packaging is broken (a file missing from the build, wrong package list).
#   Tests pass locally and fail for users - the classic "works on my machine".
# - SRC: the code is not importable from the project root. You must INSTALL
#   it (normally `pip install -e .`), so tests exercise what users get.
#   It also stops accidental `import` of stray top-level folders.
# - Both work; src layout is the safer default for libraries.

print("\n# 02. Project Layout: flat vs src/")

TOML = '''\
# ---- how to BUILD this project (PEP 517/518) --------------------------
[build-system]
requires = ["setuptools>=68"]          # tools pip installs before building
build-backend = "setuptools.build_meta"  # the module pip/build will call

# ---- what the project IS (PEP 621) -------------------------------------
[project]
name = "greeter-demo"                  # the name you `pip install` (the DISTRIBUTION name)
dynamic = ["version"]                  # version comes from the code (see [tool.setuptools.dynamic])
description = "A tiny demo package that says hello."
readme = "README.md"                   # shown on PyPI
requires-python = ">=3.9"              # refuse to install on older Pythons
license = {text = "MIT"}
authors = [{name = "Demo Author", email = "demo@example.com"}]
keywords = ["demo", "greeting"]
classifiers = [                        # search tags on PyPI
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
]
# Runtime dependencies: installed automatically with the package.
# The second line has an environment MARKER: only needed on old Pythons.
dependencies = [
    "tomli>=2.0; python_version < '3.11'",
]

[project.optional-dependencies]        # "extras": pip install greeter-demo[cli]
cli = ["colorama>=0.4"]
dev = ["pytest>=8", "build", "ruff"]

[project.urls]
Homepage = "https://example.com/greeter-demo"
Issues = "https://example.com/greeter-demo/issues"

[project.scripts]                      # becomes a command on PATH after install
greet = "greeter.cli:main"             # command = "module.path:function"

# ---- backend-specific settings (setuptools) -----------------------------
[tool.setuptools.packages.find]
where = ["src"]                        # packages live under src/

[tool.setuptools.package-data]
greeter = ["greetings.csv", "py.typed"]  # non-.py files to ship INSIDE the wheel

[tool.setuptools.dynamic]
version = {attr = "greeter.__version__"}  # single source of truth for the version
'''

FILES = {
    "pyproject.toml": TOML,
    "README.md": "# greeter-demo\n\nA tiny demo package that says hello.\n\n    greet --name Ada\n",
    "LICENSE": textwrap.dedent('''\
        MIT License

        Copyright (c) 2025 Demo Author

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT
        WARRANTY OF ANY KIND.
        '''),
    "CHANGELOG.md": "# Changelog\n\n## 0.1.0\n- First release.\n",
    "MANIFEST.in": "include CHANGELOG.md\n",
    ".gitignore": "__pycache__/\n*.py[cod]\n*.egg-info/\nbuild/\ndist/\n.venv/\n",
    "src/greeter/__init__.py": textwrap.dedent('''\
        """greeter - a tiny demo package."""
        from greeter.core import greet

        __version__ = "0.1.0"          # the ONE place the version is written
        __all__ = ["greet", "__version__"]   # the public API: what `from greeter import *` exports
        '''),
    "src/greeter/core.py": textwrap.dedent('''\
        """The actual logic. Reads a data file that ships inside the package."""
        from importlib import resources


        def _load_greetings() -> dict[str, str]:
            text = resources.files("greeter").joinpath("greetings.csv").read_text(encoding="utf-8")
            return dict(line.split(",") for line in text.splitlines() if line)


        def greet(name: str, lang: str = "en") -> str:
            greetings = _load_greetings()
            return f"{greetings.get(lang, greetings['en'])}, {name}!"
        '''),
    "src/greeter/greetings.csv": "en,Hello\nes,Hola\nfr,Bonjour\n",
    "src/greeter/py.typed": "",
    "src/greeter/cli.py": textwrap.dedent('''\
        """Command line entry point: `greet --name Ada`."""
        import argparse

        from greeter import __version__, greet


        def main(argv=None) -> int:
            parser = argparse.ArgumentParser(prog="greet", description="Say hello.")
            parser.add_argument("--name", default="world")
            parser.add_argument("--lang", default="en", choices=["en", "es", "fr"])
            parser.add_argument("--version", action="version", version=f"greet {__version__}")
            args = parser.parse_args(argv)
            print(greet(args.name, args.lang))
            return 0          # becomes the process exit code
        '''),
    "src/greeter/__main__.py": textwrap.dedent('''\
        """Makes `python -m greeter` work."""
        from greeter.cli import main

        raise SystemExit(main())
        '''),
    "tests/test_greeter.py": textwrap.dedent('''\
        import unittest

        from greeter import greet
        from greeter.cli import main


        class GreeterTests(unittest.TestCase):
            def test_default_language(self):
                self.assertEqual(greet("Ada"), "Hello, Ada!")

            def test_spanish(self):
                self.assertEqual(greet("Ada", "es"), "Hola, Ada!")

            def test_cli_returns_zero(self):
                self.assertEqual(main(["--name", "Ada"]), 0)


        if __name__ == "__main__":
            unittest.main()
        '''),
}


def write_project(root):
    for rel, content in FILES.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def print_tree(root):
    names = sorted(p.relative_to(root).as_posix() + ("/" if p.is_dir() else "")
                   for p in root.rglob("*"))
    for name in names:
        print("  " + name)


with tempfile.TemporaryDirectory() as tmp_name:
    tmp = Path(tmp_name)
    project = tmp / "greeter-demo"
    project.mkdir()
    write_project(project)

    # 03. The Generated Project
    # ------------------------------------
    print("\n# 03. The Generated Project (in a temp folder)")
    print_tree(project)

    # 04. pyproject.toml - Every Field in Plain Words
    # ------------------------------------
    # - It is TOML. Three tables matter:
    #     [build-system]  how to build (read by pip / build)
    #     [project]       metadata every tool understands (PEP 621)
    #     [tool.xxx]      settings private to ONE tool (setuptools, ruff,
    #                     pytest, mypy, black ...). One file for everything.
    # - The comments inside the file below are the explanation.
    print("\n# 04. pyproject.toml - Every Field in Plain Words")
    print(TOML.rstrip())
    parsed = tomllib.loads((project / "pyproject.toml").read_text())
    print("\n(parsed with tomllib; top-level tables:", sorted(parsed), ")")
    print("project fields:", sorted(parsed["project"]))
    print("""
Quick glossary:
  name              the name on PyPI / pip. Case-insensitive, '-' '_' '.' are equal.
                    (greeter-demo, greeter_demo, Greeter.Demo all mean the same)
  version           PEP 440 string. dynamic = ["version"] means "ask the backend".
  requires-python   the Python versions it supports; pip refuses others.
  dependencies      what must be installed for `import` to work (runtime only).
  optional-deps     extras; opt in with pip install "greeter-demo[dev]".
  scripts           console commands. "greet = greeter.cli:main" makes pip write
                    a tiny launcher that imports greeter.cli and calls main().
  readme / license  shown on the package page; LICENSE is copied into the wheel.
  distribution name != import name: you `pip install greeter-demo` and
                    `import greeter`. They are chosen independently (like
                    `pip install pillow` / `import PIL`).""")

    # 05. Run the Tests - and See Why src/ Matters
    # ------------------------------------
    print("\n# 05. src/ Layout - Not Importable Until Installed")
    proc = run([sys.executable, "-c", "import greeter"], project)
    print("python -c 'import greeter' from the project root (src layout, not installed):")
    print("  ->", last_line(proc))

    flat = tmp / "flat-demo"
    (flat / "greeter").mkdir(parents=True)
    (flat / "greeter" / "__init__.py").write_text("VERSION = 'works-by-accident'\n")
    proc = run([sys.executable, "-c", "import greeter; print(greeter.VERSION)"], flat)
    print("same import in a FLAT layout, nothing installed:")
    print("  ->", last_line(proc), "(the working copy leaked in - packaging bugs stay hidden)")

    proc = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"], project,
               {"PYTHONPATH": str(project / "src")})
    print("tests with PYTHONPATH=src (a quick hack, real projects use `pip install -e .`):")
    print("  ->", re.sub(r"in [\d.]+s", "in T s", last_line(proc)))

    # 06. python -m greeter vs the console script
    # ------------------------------------
    # - `python -m greeter` runs greeter/__main__.py. It works for ANY package
    #   that has one, and you control which Python runs it.
    # - `greet` (the console script) is a launcher pip writes into the
    #   environment's bin/ (Scripts\ on Windows). Nicer for users, and it
    #   uses the Python of the environment it was installed into.
    # - Both end up calling the same main().
    print("\n# 06. python -m greeter vs the console script")
    print("  python -m greeter  -> runs src/greeter/__main__.py")
    print("  greet              -> launcher generated from [project.scripts]")
    print("  both call greeter.cli:main - one function, two doors")

    # 07. Build: sdist and wheel
    # ------------------------------------
    # - sdist (.tar.gz) = SOURCE distribution: your source + pyproject +
    #   README/LICENSE/MANIFEST extras. Installing needs a build step.
    #   Good for archiving, distro packagers, and as the fallback.
    # - wheel (.whl) = BUILT distribution: a zip of the files exactly as they
    #   will be installed, with the name encoding compatibility tags:
    #       greeter_demo-0.1.0-py3-none-any.whl
    #       name   -version-python-abi-platform
    #   py3-none-any = pure Python, runs anywhere. Compiled extensions get
    #   tags like cp312-cp312-macosx_11_0_arm64.
    #   Installing a wheel = unzip + write metadata. No code runs: fast, safe.
    # - `python -m build` is the standard front-end (PEP 517). It calls the
    #   backend named in [build-system]. Normally it makes a fresh isolated
    #   venv and downloads setuptools; --no-isolation reuses what is
    #   installed (needed here because we have no network).
    print("\n# 07. Build: sdist and wheel")
    wheel = None
    sdist = None
    if importlib.util.find_spec("build") is None or importlib.util.find_spec("setuptools") is None:
        print("SKIP: `build` and/or `setuptools` not installed here (pip install build setuptools).")
    else:
        proc = run([sys.executable, "-m", "build", "--no-isolation", "--outdir", "dist"], project)
        print("$ python -m build --no-isolation   -> exit code", proc.returncode)
        ok_lines = [ln for ln in proc.stdout.splitlines() if ln.startswith("Successfully built")]
        print(" ", ok_lines[-1] if ok_lines else last_line(proc))
        dist = project / "dist"
        wheels = sorted(dist.glob("*.whl")) if dist.exists() else []
        sdists = sorted(dist.glob("*.tar.gz")) if dist.exists() else []
        if proc.returncode != 0 or not wheels:
            print("SKIP: the build failed in this environment; the rest of the demo needs a wheel.")
            print("  reason:", last_line(proc)[:100])
        else:
            wheel, sdist = wheels[0], (sdists[0] if sdists else None)
            print("dist/ contains:", sorted(p.name for p in dist.iterdir()))

    # 08. Inspect the Wheel and the sdist
    # ------------------------------------
    # - A wheel is just a zip. Opening it shows exactly what users receive.
    # - *.dist-info/ is the metadata folder:
    #     METADATA          name, version, requires-python, dependencies, extras
    #     WHEEL             wheel format version, tags, "Root-Is-Purelib"
    #     entry_points.txt  console scripts -> pip creates the launchers
    #     top_level.txt     import names (setuptools)
    #     RECORD            list of every file + its hash + size; pip uses it
    #                       to uninstall cleanly
    # - Tip: if something is "missing after install", look inside the wheel
    #   first - you will usually see it was never packed.
    if wheel:
        print("\n# 08. Inspect the Wheel and the sdist")
        with zipfile.ZipFile(wheel) as zf:
            names = zf.namelist()
            print("wheel file name:", wheel.name)
            print("files inside the wheel:")
            for n in names:
                print("  ", n)
            meta_name = next(n for n in names if n.endswith("/METADATA"))
            print("\nMETADATA (the interesting lines):")
            for line in zf.read(meta_name).decode().splitlines():
                if line.startswith(("Metadata-Version", "Name:", "Version:", "Summary:",
                                    "Requires-Python", "Requires-Dist", "Provides-Extra",
                                    "License:")):
                    print("  ", line)
            ep_name = next(n for n in names if n.endswith("entry_points.txt"))
            print("\nentry_points.txt:")
            print("  ", zf.read(ep_name).decode().strip().replace("\n", "\n   "))
            record_name = next(n for n in names if n.endswith("/RECORD"))
            record = zf.read(record_name).decode().splitlines()
            print("\nRECORD has", len(record), "lines, each 'path,sha256=<hash>,size'. Example:")
            print("  ", re.sub(r"sha256=[A-Za-z0-9_-]+", "sha256=<hash>", record[0]))
        print("\nNote: tests/, CHANGELOG.md and MANIFEST.in are NOT in the wheel (not package code).")
        if sdist:
            with tarfile.open(sdist) as tf:
                members = sorted(n.split("/", 1)[1] for n in tf.getnames() if "/" in n)
            print("\nsdist", sdist.name, "contains:")
            for n in members:
                if not n.endswith(".egg-info") and ".egg-info/" not in n:
                    print("  ", n)
            print("-> the sdist DOES carry tests/, CHANGELOG.md (via MANIFEST.in), pyproject.toml.")
            print("   Rule: package-data decides what goes in the WHEEL; MANIFEST.in decides the SDIST.")

    # 09. Install Offline into a Throwaway venv
    # ------------------------------------
    # - Virtual environment = a private folder with its own python + site-packages.
    #   Installing there never touches your system Python.
    # - Offline install of a wheel we just built:
    #     pip install --no-index --no-deps --no-build-isolation foo.whl
    #     --no-index            never contact PyPI (we have no network)
    #     --no-deps             don't try to fetch requirements (we'd fail offline)
    #     --no-build-isolation  only matters when building from source;
    #                           harmless for wheels, vital for editables below
    # - Always call pip as `python -m pip` so it targets the right interpreter.
    def venv_bin(env_dir, name):
        sub = "Scripts" if os.name == "nt" else "bin"
        suffix = ".exe" if os.name == "nt" and name in ("python", "greet") else ""
        return env_dir / sub / (name + suffix)

    installed = False
    venv_dir = tmp / "venv"
    if wheel:
        print("\n# 09. Install Offline into a Throwaway venv")
        try:
            venv.EnvBuilder(with_pip=True, clear=True).create(venv_dir)
            vpython = venv_bin(venv_dir, "python")
            proc = run([vpython, "-m", "pip", "install", "--no-index", "--no-deps",
                        "--no-build-isolation", wheel], tmp)
            print("$ <venv>/python -m pip install --no-index --no-deps", wheel.name)
            print("  ->", last_line(proc))
            installed = proc.returncode == 0
        except Exception as exc:  # no ensurepip, no permission, ...
            print("SKIP: could not create/use a venv here:", type(exc).__name__, exc)

    # 10. Use the Installed Package
    # ------------------------------------
    if installed:
        print("\n# 10. Use the Installed Package (from inside the venv)")
        proc = run([venv_bin(venv_dir, "greet"), "--name", "Ada", "--lang", "es"], tmp)
        print("$ greet --name Ada --lang es          ->", last_line(proc))
        proc = run([venv_bin(venv_dir, "greet"), "--version"], tmp)
        print("$ greet --version                     ->", last_line(proc))
        proc = run([vpython, "-m", "greeter", "--name", "Grace"], tmp)
        print("$ python -m greeter --name Grace      ->", last_line(proc))
        proc = run([vpython, "-c", "import greeter; print(greeter.greet('Linus', 'fr'))"], tmp)
        print("import from ANY folder (cwd is not the project) ->", last_line(proc))
        print("-> the package data file greetings.csv was found: it travelled inside the wheel.")

        # 11. importlib.metadata - Ask an Installed Package About Itself
        # ------------------------------------
        # - Metadata is the SAME data as in METADATA/entry_points.txt, read at
        #   runtime. This is how tools discover plugins (entry points) and how
        #   code finds its own version WITHOUT hardcoding it twice.
        print("\n# 11. importlib.metadata - Ask an Installed Package About Itself")
        probe = textwrap.dedent('''
            from importlib import metadata
            dist = metadata.distribution("greeter-demo")
            print("version     :", metadata.version("greeter-demo"))
            print("name        :", dist.metadata["Name"])
            print("requires    :", metadata.requires("greeter-demo"))
            eps = metadata.entry_points(group="console_scripts")
            print("entry points:", [(e.name, e.value) for e in eps if e.name == "greet"])
            files = sorted(str(f).replace(chr(92), "/") for f in dist.files)
            print("files       :")
            for f in files:
                if "__pycache__" not in f:   # pip byte-compiles on install; noise here
                    print("   ", f)
            print("same as __version__ in code:", metadata.version("greeter-demo") == __import__("greeter").__version__)
        ''')
        proc = run([vpython, "-c", probe], tmp)
        print(proc.stdout.rstrip() if proc.returncode == 0 else "probe failed: " + last_line(proc))

        # 12. pip show / list / freeze / uninstall
        # ------------------------------------
        print("\n# 12. pip show / list / freeze / uninstall")
        proc = run([vpython, "-m", "pip", "show", "greeter-demo"], tmp)
        for line in proc.stdout.splitlines():
            if line.split(":")[0] in ("Name", "Version", "Summary", "Requires", "Required-by"):
                print("  pip show |", line)
        proc = run([vpython, "-m", "pip", "list", "--format=freeze"], tmp)
        listed = [re.sub(r"==.*", "==<ver>", ln) if not ln.startswith("greeter") else ln
                  for ln in proc.stdout.splitlines()]
        print("  pip list | packages in the venv:", sorted(listed))
        proc = run([vpython, "-m", "pip", "freeze"], tmp)
        print("  pip freeze | (exact pins, format for requirements.txt):",
              [re.sub(r"file://\S+?\.whl#sha256=\w+", "file://<path>.whl#sha256=<hash>", ln)
                       for ln in proc.stdout.splitlines() if ln.startswith("greeter")])
        proc = run([vpython, "-m", "pip", "uninstall", "-y", "greeter-demo"], tmp)
        print("  pip uninstall -y |", last_line(proc))
        proc = run([vpython, "-c", "import greeter"], tmp)
        print("  import after uninstall ->", last_line(proc))

    # 13. Editable Installs (pip install -e .)
    # ------------------------------------
    # - Normal install COPIES the code into site-packages. Edit your source and
    #   nothing changes until you reinstall.
    # - Editable install (`pip install -e .`) links the environment to your
    #   source folder instead. Edit a file, rerun, see the change - the
    #   everyday way to develop a package.
    # - Gotcha: an editable install still needs a BUILD backend available,
    #   so offline we use a venv that can see the system's setuptools
    #   (system_site_packages=True) and pass --no-build-isolation.
    # - Gotcha: new entry points / dependencies / package-data rules are read
    #   at install time - after editing pyproject.toml, reinstall.
    if wheel:
        print("\n# 13. Editable Installs (pip install -e .)")
        edit_venv = tmp / "edit-venv"
        try:
            venv.EnvBuilder(with_pip=True, system_site_packages=True, clear=True).create(edit_venv)
            epython = venv_bin(edit_venv, "python")
            proc = run([epython, "-m", "pip", "install", "--no-index", "--no-deps",
                        "--no-build-isolation", "-e", "."], project)
            print("$ pip install --no-index --no-deps --no-build-isolation -e .")
            print("  ->", last_line(proc))
            if proc.returncode != 0:
                print("SKIP: editable install not possible here:", last_line(proc)[:100])
            else:
                probe = textwrap.dedent('''
                    from importlib import metadata
                    dist = metadata.distribution("greeter-demo")
                    print("editable marker files:", sorted(str(f) for f in dist.files if "editable" in str(f).lower()))
                    import json
                    print("direct_url editable flag:", json.loads(dist.read_text("direct_url.json"))["dir_info"]["editable"])
                ''')
                proc = run([epython, "-c", probe], tmp)
                print(re.sub(r"__editable__[\w.]+", "__editable__<name>", proc.stdout.rstrip()))
                proc = run([venv_bin(edit_venv, "greet"), "--name", "Ada"], tmp)
                print("before edit: greet --name Ada ->", last_line(proc))
                core = project / "src" / "greeter" / "core.py"
                core.write_text(core.read_text().replace('{greetings.get(lang, greetings[\'en\'])}, {name}!',
                                                         '{greetings.get(lang, greetings[\'en\'])}, {name}! (edited)'))
                proc = run([venv_bin(edit_venv, "greet"), "--name", "Ada"], tmp)
                print("after editing core.py, NO reinstall: ->", last_line(proc))
                print("-> editable install picks up source changes immediately.")
        except Exception as exc:
            print("SKIP: editable demo not possible here:", type(exc).__name__, exc)

# (everything above lived in a TemporaryDirectory - it is already deleted)
leftover = [p for p in Path(__file__).resolve().parent.glob("*") if p.name.endswith(".egg-info") or p.name in ("build", "dist")]
print("\nbuild artifacts left in the repo folder:", leftover)

# 14. Versioning
# ------------------------------------
# - SemVer: MAJOR.MINOR.PATCH
#     MAJOR  breaking changes (users must change their code)
#     MINOR  new features, backwards compatible
#     PATCH  bug fixes only
#   Python's real rule is PEP 440, which also allows pre-releases (1.0.0rc1,
#   1.0.0b2, 1.0.0a1), post-releases (1.0.0.post1) and dev builds (1.1.0.dev3).
# - NEVER compare versions as strings: "1.10" < "1.9" is True for strings.
#   Use packaging.version.Version.
# - Single source of truth: write the version ONCE.
#     option 1: static    version = "0.1.0" in pyproject.toml
#     option 2: dynamic   dynamic = ["version"] + attr = "pkg.__version__"
#                         (what the demo package above does)
#     option 3: from git tags (setuptools-scm, hatch-vcs): tag v1.2.3 = version
#   Reading the version at runtime: importlib.metadata.version("dist-name")
#   (it reflects what is INSTALLED - not stale if you forget to bump a file).

print("\n# 14. Versioning (PEP 440 / SemVer)")
if importlib.util.find_spec("packaging") is None:
    print("SKIP: `packaging` is not installed (pip install packaging); examples need it.")
else:
    from packaging.markers import Marker
    from packaging.requirements import Requirement
    from packaging.specifiers import SpecifierSet
    from packaging.version import Version

    print("string compare '1.10' > '1.9':", "1.10" > "1.9", "(wrong)")
    print("Version('1.10') > Version('1.9'):", Version("1.10") > Version("1.9"), "(right)")
    ordering = ["1.0.0", "1.0.0rc1", "1.0.0b2", "1.0.0a1", "1.0.0.post1", "1.0.0.dev1"]
    print("PEP 440 order:", sorted(ordering, key=Version))
    print("Version('2.1.0rc1').is_prerelease:", Version("2.1.0rc1").is_prerelease,
          "| pip skips pre-releases unless asked (--pre)")

    # 15. Dependency Specifiers
    # ------------------------------------
    # - How you describe "which versions of a dependency I accept":
    #     requests==2.31.0        exactly that (a PIN)
    #     requests>=2.28          that or newer (no upper limit)
    #     requests>=2.28,<3       a RANGE: accept 2.x from 2.28, block the 3.0 break
    #     requests~=2.28          "compatible release": >=2.28, ==2.*
    #     requests~=2.28.1        >=2.28.1, ==2.28.*
    #     requests!=2.29.0        skip one known-bad release
    #     requests[security]      with an EXTRA (more deps from [optional-dependencies])
    #     tomli>=2; python_version < "3.11"   only where the MARKER is true
    # - Markers can test python_version, sys_platform, platform_system, os_name,
    #   implementation_name, extra ... (e.g. `pywin32; sys_platform == 'win32'`).
    print("\n# 15. Dependency Specifiers")
    req = Requirement("requests[security,socks]>=2.28,<3; python_version >= '3.8'")
    print("parsed:", req.name, "| extras:", sorted(req.extras), "| specifier:", str(req.specifier),
          "| marker:", req.marker)
    for text, ver in [("~=2.28", "2.31.0"), ("~=2.28", "3.0.0"), ("~=2.28.1", "2.29.0"),
                      (">=2.28,<3", "2.99"), ("==2.31.*", "2.31.4"), ("!=2.29.0", "2.29.0")]:
        print(f"  {text:<10} accepts {ver:<7} -> {SpecifierSet(text).contains(ver)}")
    marker = Marker("python_version < '3.11'")
    print("marker python_version < '3.11' on this Python:", marker.evaluate())
    print("marker sys_platform == 'win32' on this OS:", Marker("sys_platform == 'win32'").evaluate())

# 16. Pinning vs Ranges: Libraries vs Applications
# ------------------------------------
# - LIBRARY (something other projects depend on): declare LOOSE ranges in
#   pyproject.toml  ->  "requests>=2.28,<3".
#   Why: pins would clash with the other libraries in the user's environment
#   (A needs x==1.0, B needs x==1.1 -> unsolvable). Be as permissive as is safe.
# - APPLICATION (a service/CLI you deploy): pin EXACTLY, including indirect
#   dependencies, so every deploy installs the same thing.
#   -> requirements.txt generated by `pip freeze` / pip-compile / a lock file.
#   Why: an unpinned transitive dependency can release a breaking version on
#   Friday night and break your Monday deploy.
# - Typical setup for an application:
#     pyproject.toml         human-written ranges (what you need)
#     requirements.txt/lock  machine-generated pins (what you got) - commit it
# - Lock files: uv.lock (uv), poetry.lock, pdm.lock, pip-tools' compiled
#   requirements.txt (with hashes: --generate-hashes). Re-lock deliberately
#   (a PR that bumps versions) so upgrades are reviewed, not accidental.

print("\n# 16. Pinning vs Ranges: Libraries vs Applications")
print("  library     pyproject.toml  'requests>=2.28,<3'      loose, so it coexists with others")
print("  application requirements.txt 'requests==2.31.0'      exact, reproducible, includes sub-dependencies")
print("  both        pyproject says what you NEED; the lock file records what you GOT")

# 17. pip freeze, pip-tools, uv (Reference)
# ------------------------------------
# - pip freeze > requirements.txt
#     dumps EVERYTHING installed (also tools like pytest you only use for dev)
#     as exact pins. Simple but crude - no distinction between direct and
#     indirect dependencies.
# - pip-tools: write the few packages you want in requirements.in, then
#     pip-compile requirements.in -o requirements.txt   (resolves + pins all)
#     pip-sync requirements.txt                          (make the env match)
# - uv (Astral): a very fast Rust reimplementation of pip/venv/pip-tools and
#   a project manager. Commands below need the network, so they are listed
#   for reference only - this file does not run them.

print("\n# 17. pip freeze, pip-tools, uv (reference only - not run: they need the network)")
uv = shutil.which("uv")
if uv:
    proc = run([uv, "--version"], Path.cwd())
    print("uv is installed here:", re.sub(r"uv (\d+\.\d+\.\d+).*", r"uv \1", last_line(proc)))
else:
    print("uv is not installed here (pip install uv  or  pipx install uv)")
for cmd, meaning in [
    ("uv venv", "create .venv (much faster than python -m venv)"),
    ("uv pip install -r requirements.txt", "pip-compatible installer, 10-100x faster"),
    ("uv pip compile requirements.in -o requirements.txt", "pip-tools replacement"),
    ("uv init / uv add requests", "project workflow: edits pyproject.toml for you"),
    ("uv lock", "write uv.lock: exact, cross-platform pins of every dependency"),
    ("uv sync", "make .venv match uv.lock exactly"),
    ("uv run pytest", "run a command inside the project's env (creates/syncs it first)"),
    ("uv build / uv publish", "build sdist+wheel / upload them"),
    ("uvx ruff check .", "run a tool in a temporary env, like pipx run"),
]:
    print(f"  {cmd:<52}{meaning}")
print("  pip-tools:  pip-compile requirements.in -o requirements.txt  |  pip-sync requirements.txt")

# 18. pipx - Install Applications, not Libraries
# ------------------------------------
# - `pip install black` puts a tool into whichever environment is active, and
#   its dependencies can clash with your project's. pipx installs each
#   command-line app into its OWN isolated venv and exposes just the command:
#       pipx install black      pipx run cowsay hi      pipx upgrade-all
#   Use pip for libraries your code imports; pipx (or uv tool install) for
#   tools you only run (black, ruff, httpie, cookiecutter, twine, ...).

print("\n# 18. pipx - Install Applications, not Libraries (reference only)")
print("  libraries your code imports -> pip inside a project venv")
print("  tools you just run          -> pipx install <tool>  (or: uv tool install <tool>)")

# 19. Publishing to PyPI (Reference Only - Never Executed Here)
# ------------------------------------
# - Flow:  bump version -> build -> check -> upload to TestPyPI -> try
#   installing it -> upload to PyPI.
#       python -m build
#       twine check dist/*                  validates the README renders, metadata ok
#       twine upload --repository testpypi dist/*
#       pip install --index-url https://test.pypi.org/simple/ greeter-demo
#       twine upload dist/*
# - Rules: a PyPI version is IMMUTABLE. You cannot re-upload 0.1.0 with changes
#   (you can only "yank" it). Mistakes cost a new version number - test first.
# - Credentials: use API TOKENS (never your password) or - best - TRUSTED
#   PUBLISHING: in PyPI you declare "this GitHub repo/workflow may publish
#   this project"; the workflow gets a short-lived token via OpenID Connect.
#   No secret stored anywhere. (pypa/gh-action-pypi-publish does the upload.)
# - Name squatting/typos are real attacks: check the name is yours and spelled right.

print("\n# 19. Publishing to PyPI (reference only - NEVER executed by this file)")
for step in [
    "python -m build",
    "twine check dist/*",
    "twine upload --repository testpypi dist/*",
    "pip install --index-url https://test.pypi.org/simple/ greeter-demo",
    "twine upload dist/*   (or: tag a release and let a trusted-publishing workflow do it)",
]:
    print("  $", step)
print("  a published version is immutable - you can yank it, never overwrite it")

# 20. Package Data, MANIFEST.in and Namespace Packages
# ------------------------------------
# - Non-code files (CSV, templates, JSON, py.typed) are NOT included by
#   default. List them: [tool.setuptools.package-data]  pkg = ["*.csv"].
#   Read them at runtime with importlib.resources.files("pkg") / "x.csv"
#   - never with open("x.csv") (the cwd and install location vary; the
#   package could even live inside a zip).
# - MANIFEST.in controls the SDIST only (include/recursive-include/prune lines).
# - Namespace packages (several distributions sharing one import prefix,
#   no __init__.py) are covered in 05-Python Advanced/05-Modules-And-Packages.py.

print("\n# 20. Package Data, MANIFEST.in and Namespace Packages")
print("  wheel contents: package-data | sdist contents: MANIFEST.in")
print("  read data files with importlib.resources, not open() with a relative path")
print("  namespace packages -> 05-Python Advanced/05-Modules-And-Packages.py")

# 21. Public API: __all__ and py.typed
# ------------------------------------
# - __all__ lists the names that make up your PUBLIC API: what
#   `from pkg import *` exports and what docs/linters treat as supported.
#   Everything else (names starting with _, helpers) is private and can change.
# - Re-export the public names in __init__.py (as the demo does) so users write
#   `from greeter import greet` rather than `from greeter.core import greet`;
#   then you can reorganise modules without breaking anyone.
# - py.typed: an EMPTY marker file inside the package (PEP 561). Without it,
#   mypy/pyright treat your inline type hints as unavailable. With it, users
#   get type checking against your annotations. It must be shipped in the
#   wheel -> list it in package-data (the demo does). See
#   06-Standard Library/06-Typing-And-Type-Hints.py for the hints themselves.

print("\n# 21. Public API: __all__ and py.typed")
print("  __all__ = ['greet', '__version__']  -> declares the public API")
print("  py.typed (empty file, shipped via package-data) -> tells type checkers 'my hints are real'")

# 22. Other Build Backends
# ------------------------------------
# - [build-system] is pluggable. The [project] table above stays the same;
#   only requires / build-backend (and the [tool.xxx] tables) change.
#     setuptools   the long-standing default; most flexible, handles C extensions
#     hatchling    modern, fast, sensible defaults, good plugin ecosystem
#                  (requires = ["hatchling"], build-backend = "hatchling.build")
#     flit-core    minimal, pure-Python packages only, almost no config
#     poetry-core  backend of Poetry (poetry also resolves/locks dependencies)
#     pdm-backend  backend of PDM
#     maturin      build Python packages written in RUST (PyO3)
#     scikit-build-core  C/C++ extensions with CMake
# - Pick: pure-Python library -> hatchling or setuptools; Rust -> maturin;
#   already using Poetry -> poetry-core.

print("\n# 22. Other Build Backends")
for backend, blurb in [
    ("setuptools", "classic default, most flexible, C extensions"),
    ("hatchling", "modern, fast, good defaults, plugins"),
    ("flit-core", "tiny, pure-Python only"),
    ("poetry-core", "backend for Poetry (which also locks dependencies)"),
    ("maturin", "Python packages written in Rust"),
]:
    print(f"  {backend:<13}{blurb}")

# 23. Release Checklist
# ------------------------------------
#   [ ] tests green on every supported Python (CI matrix)
#   [ ] version bumped following SemVer (breaking = MAJOR)
#   [ ] CHANGELOG updated (users read it before upgrading)
#   [ ] README renders; license file present; classifiers correct
#   [ ] requires-python and dependency ranges match what you tested
#   [ ] build clean:  rm -rf dist build *.egg-info && python -m build
#   [ ] inspect the wheel (unzip -l) - package data present, no junk
#   [ ] install the wheel in a FRESH venv and run the real command
#   [ ] twine check dist/*
#   [ ] upload to TestPyPI first; install from it; then upload to PyPI
#   [ ] tag the release in git (v1.2.3) and push the tag
#   [ ] never commit secrets/tokens; prefer trusted publishing

print("\n# 23. Release Checklist")
print("  test -> bump version -> changelog -> clean build -> inspect wheel ->")
print("  fresh-venv install -> twine check -> TestPyPI -> PyPI -> git tag")
