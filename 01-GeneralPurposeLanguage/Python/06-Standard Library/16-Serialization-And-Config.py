import argparse
import configparser
import copyreg
import io
import json
import marshal
import os
import pickle
import shelve
import sys
import tempfile
import threading
from collections import ChainMap
from dataclasses import dataclass, field, asdict, astuple
from pathlib import Path

# 01. Serialization and Config - Introduction
# ------------------------------------
# - SERIALIZATION = turning a Python object in memory into bytes/text you can
#   save to a file or send over a network, and loading it back later.
# - CONFIG = settings that live OUTSIDE your code (so you can change them
#   without editing code): files (INI, TOML, JSON) and environment variables.
# - The big question for every format: is it SAFE to load from someone else?
#   (json, ini, toml: yes.  pickle: NO - see section 05.)
# - json basics are in 04-Json-And-Csv.py; layering with ChainMap is a cousin
#   of the examples in 01-Collections-Module.py.

print("# 01. Serialization and Config - Introduction")
print("# ------------------------------------")

# ====================================================================
# PART A - pickle
# ====================================================================

# 02. pickle Basics - Python Objects to Bytes and Back
# ------------------------------------
# - pickle can store almost ANY Python object: nested lists, dicts, sets,
#   tuples, datetimes, your own classes. json cannot (no sets, no tuples,
#   no custom classes).
# - dumps/loads work with bytes; dump/load work with open binary files.
print("\n# 02. pickle basics")
original = {"name": "Asha", "scores": (90, 85), "tags": {"python", "sql"}, "ratio": 0.75}
blob = pickle.dumps(original)
print("type:", type(blob).__name__, "| size:", len(blob), "bytes")
restored = pickle.loads(blob)
print("restored:", restored)
print("equal to original:", restored == original, "| same object:", restored is original)
print("tuple stayed a tuple:", type(restored["scores"]).__name__, "| set stayed a set:", type(restored["tags"]).__name__)

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "data.pkl"
    with open(path, "wb") as f:  # 'wb' - pickle is binary, NOT text
        pickle.dump(original, f)
    with open(path, "rb") as f:
        print("from file:", pickle.load(f)["name"])

# 03. Protocols - Which Pickle Version?
# ------------------------------------
# - Higher protocol = more compact/faster, but older Pythons can't read it.
# - Protocol 0 is the ancient ASCII one; 4 is the default since 3.8;
#   5 (3.8+) adds out-of-band buffers for huge data.
print("\n# 03. Protocols")
print("DEFAULT_PROTOCOL:", pickle.DEFAULT_PROTOCOL, "| HIGHEST_PROTOCOL:", pickle.HIGHEST_PROTOCOL)
sample = list(range(200))
for proto in (0, 2, pickle.HIGHEST_PROTOCOL):
    print(f"protocol {proto}: {len(pickle.dumps(sample, protocol=proto))} bytes")
print("# Sharing files with older Python? Pass protocol=<lowest common>.")

# 04. What CAN'T Be Pickled
# ------------------------------------
# - pickle stores objects BY NAME ("module.function"), not by their code.
#   So anything without an importable name fails: lambdas, nested functions.
# - Live resources (open files, sockets, locks, threads, DB connections)
#   cannot be re-created from bytes at all.
print("\n# 04. Things that cannot be pickled")


def make_local():
    def inner():
        return 1
    return inner


things = {
    "lambda": lambda x: x,
    "local function": make_local(),
    "lock": threading.Lock(),
}
for label, thing in things.items():
    try:
        pickle.dumps(thing)
        print(f"{label}: pickled OK")
    except Exception as e:  # PicklingError / AttributeError / TypeError depending on the object
        print(f"{label}: {type(e).__name__}")  # (message holds a memory address - varies per run)

with tempfile.TemporaryDirectory() as tmp:
    with open(Path(tmp) / "x.txt", "w") as fh:
        try:
            pickle.dumps(fh)
        except TypeError as e:
            print("open file: TypeError:", e)
print("# A module-level function IS fine - pickled as a reference to its name:", len(pickle.dumps(len)), "bytes for 'len'")

# 05. Pickling Custom Classes
# ------------------------------------
# - The instance's __dict__ is saved plus the CLASS NAME (not the class code).
# - __init__ is NOT called when unpickling. Load restores __dict__ directly.
# - GOTCHA: if the class is later renamed/moved, old pickles stop loading.
print("\n# 05. Custom classes")


class Player:
    def __init__(self, name, level):
        print(f"  (__init__ called for {name})")
        self.name = name
        self.level = level

    def __repr__(self):
        return f"Player({self.name!r}, level={self.level})"


p = Player("kai", 7)
loaded_player = pickle.loads(pickle.dumps(p))
print("loaded:", loaded_player, "| __init__ was NOT re-run on load")


# 06. __getstate__ / __setstate__ - Control What Gets Saved
# ------------------------------------
# - Use them to DROP un-picklable or temporary attributes (locks, caches,
#   connections) and rebuild them on load.
print("\n# 06. __getstate__ / __setstate__")


class Counter:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()  # not picklable!
        self.cache = {"big": "data"}  # we don't want to save this

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["lock"]
        del state["cache"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.lock = threading.Lock()  # rebuild fresh
        self.cache = {}


c = Counter()
c.count = 41
c2 = pickle.loads(pickle.dumps(c))
print("count restored:", c2.count, "| fresh lock:", type(c2.lock).__name__, "| cache rebuilt empty:", c2.cache)


# 07. SECURITY: Unpickling Can Run Code
# ------------------------------------
# - pickle is a tiny PROGRAM, not just data. A pickle may say "to rebuild
#   this object, call THIS function with THESE arguments" - via __reduce__.
# - So pickle.loads(untrusted_bytes) = running code someone else wrote.
#   A real attacker would call os.system / open a reverse shell.
# - Below is a HARMLESS demo: the "attack" only calls print().
print("\n# 07. SECURITY - unpickling runs code (harmless demo)")


class Evil:
    def __reduce__(self):
        # (callable, args): loads() will call print("...") for us.
        return (print, ("  >>> this line was printed BY loads(), not by my code!",))


payload = pickle.dumps(Evil())
print("about to call pickle.loads(payload)...")
result = pickle.loads(payload)  # runs print() during loading
print("loads returned:", result, "(print's return value - there is no 'object' at all)")
print("# RULES:")
print("# - Never unpickle data from the network, user uploads, or anywhere untrusted.")
print("# - Signing with hmac (see 15-Hashing-And-Encoding.py) proves WHO made it, not that it's safe.")
print("# - Need data exchange? Use json (safe: only data, never code).")
print("# - pickle is OK for: your own cache files, multiprocessing between your own processes.")

# 08. pickle vs json - Quick Guidance
# ------------------------------------
print("\n# 08. pickle vs json")
print("# json  : text, human-readable, safe, works in every language, limited types.")
print("# pickle: binary, Python-only, any object, UNSAFE on untrusted data, version-fragile.")
print("# Default to json. Reach for pickle only for private, short-lived Python-only data.")

# ====================================================================
# PART B - shelve, marshal, copyreg
# ====================================================================

# 09. shelve - A Dict That Lives on Disk
# ------------------------------------
# - shelve gives dict-like access; values are pickled automatically.
# - KEYS MUST BE str. Values can be anything picklable.
# - Always close it (or use `with`) so data is flushed to disk.
# - Same security warning as pickle applies to the shelf file.
print("\n# 09. shelve")
with tempfile.TemporaryDirectory() as tmp:
    db_path = os.path.join(tmp, "mydb")
    with shelve.open(db_path) as db:
        db["alice"] = {"age": 30, "langs": ["python"]}
        db["bob"] = {"age": 25, "langs": []}
        print("keys:", sorted(db.keys()), "| 'alice' in db:", "alice" in db)

    with shelve.open(db_path) as db:  # a new session - data survived
        print("reopened:", db["alice"])

    try:
        with shelve.open(db_path) as db:
            db[42] = "int key"
    except (TypeError, AttributeError) as e:  # which one depends on the dbm backend
        print("non-str key rejected:", type(e).__name__, "-", e)

    # 10. shelve writeback Gotcha
    # ------------------------------------
    # - db["alice"]["langs"].append("sql") changes a TEMPORARY unpickled copy;
    #   nothing is saved! You must reassign, or open with writeback=True
    #   (which caches everything in memory and writes on close - slower).
    print("\n# 10. shelve writeback gotcha")
    with shelve.open(db_path) as db:
        db["alice"]["langs"].append("sql")  # silently lost
        print("after in-place append (no writeback):", db["alice"]["langs"])
        record = db["alice"]
        record["langs"].append("sql")
        db["alice"] = record  # reassign -> saved
        print("after reassigning the record:        ", db["alice"]["langs"])
    with shelve.open(db_path, writeback=True) as db:
        db["bob"]["langs"].append("go")  # tracked because writeback=True
    with shelve.open(db_path) as db:
        print("bob after writeback=True:", db["bob"]["langs"])
# TemporaryDirectory removes all the dbm files shelve created.

# 11. marshal and copyreg (just so you recognise them)
# ------------------------------------
# - marshal: the format Python uses INTERNALLY for .pyc bytecode files. It
#   handles only core types, is not guaranteed stable across Python versions,
#   and is not secure. You almost never use it - prefer json or pickle.
# - copyreg: lets you register how to pickle a type you cannot edit (e.g. a
#   class from another library). Advanced; reach for it only when needed.
print("\n# 11. marshal / copyreg")
packed = marshal.dumps({"a": 1, "b": [1, 2]})
print("marshal round trip:", marshal.loads(packed), "(internal use; version-specific)")
print("copyreg.pickle exists:", callable(copyreg.pickle), "(register a reducer for foreign types)")

# ====================================================================
# PART C - dataclasses + json
# ====================================================================

# 12. Dataclasses to dict/tuple, and JSON Round-Trip
# ------------------------------------
# - json can't handle dataclass instances directly. asdict() converts them
#   (recursively) to plain dicts; astuple() to tuples.
print("\n# 12. dataclasses + json")


@dataclass
class Address:
    city: str
    zip: str


@dataclass
class User:
    name: str
    age: int
    address: Address
    tags: list = field(default_factory=list)


user = User("Asha", 30, Address("Pune", "411001"), ["admin"])
as_dict = asdict(user)
print("asdict:", as_dict)
print("astuple:", astuple(user))
text = json.dumps(as_dict)
print("json text:", text)
try:
    json.dumps(user)
except TypeError as e:
    print("json.dumps(dataclass) -> TypeError:", e)

# Rebuild from JSON - you must reconstruct nested dataclasses yourself:
raw = json.loads(text)
rebuilt = User(**{**raw, "address": Address(**raw["address"])})
print("rebuilt equals original:", rebuilt == user)

# 13. Custom Encoder / Decoder With object_hook
# ------------------------------------
# - Teach json about your types: encode with a "__type__" tag, decode with
#   object_hook (called for EVERY decoded dict, innermost first).
# - Keeps json's safety: the tag only selects from classes YOU list.
print("\n# 13. Custom JSON encoder / decoder")
REGISTRY = {"Address": Address, "User": User}


def encode_default(obj):  # called only for objects json doesn't understand
    if hasattr(obj, "__dataclass_fields__"):
        return {"__type__": type(obj).__name__, **{k: getattr(obj, k) for k in obj.__dataclass_fields__}}
    raise TypeError(f"Cannot serialize {type(obj).__name__}")


def decode_hook(d):
    cls = REGISTRY.get(d.get("__type__"))
    if cls is None:
        return d  # ordinary dict, leave alone
    return cls(**{k: v for k, v in d.items() if k != "__type__"})


tagged = json.dumps(user, default=encode_default)
print("tagged json:", tagged)
back = json.loads(tagged, object_hook=decode_hook)
print("decoded type:", type(back).__name__, "| nested type:", type(back.address).__name__, "| equal:", back == user)

# ====================================================================
# PART D - configparser (INI)
# ====================================================================

# 14. configparser - Read an INI File
# ------------------------------------
# - INI = sections in [brackets] with key = value lines. Old but very common
#   (pip.conf, setup.cfg, tox.ini, .editorconfig-like tools).
# - EVERYTHING is a string until you convert it with getint/getfloat/getboolean.
print("\n# 14. configparser - read")
INI_TEXT = """
[DEFAULT]
timeout = 30
debug = false

[server]
host = localhost
port = 8080
debug = yes
base_dir = /srv/app
log_dir = %(base_dir)s/logs

[database]
name = shop
pool_size = 5
ratio = 0.75
"""
cfg = configparser.ConfigParser()
cfg.read_string(INI_TEXT)  # cfg.read("file.ini") for a real file
print("sections:", cfg.sections(), "(DEFAULT is special, not listed)")
print("host (str):", cfg["server"]["host"])
print("port as str:", repr(cfg["server"]["port"]), "| getint:", cfg.getint("server", "port"))
print("debug getboolean ('yes' -> True):", cfg.getboolean("server", "debug"))
print("ratio getfloat:", cfg.getfloat("database", "ratio"))

# 15. fallback and DEFAULT Section
# ------------------------------------
# - [DEFAULT] values are inherited by EVERY section (database sees timeout=30).
# - fallback= avoids KeyError/NoOptionError for optional settings.
print("\n# 15. fallback and DEFAULT inheritance")
print("database timeout (inherited from DEFAULT):", cfg["database"]["timeout"])
print("missing key with fallback:", cfg.get("database", "user", fallback="(none)"))
print("missing int with fallback:", cfg.getint("database", "retries", fallback=3))
try:
    cfg["database"]["user"]
except KeyError as e:
    print("KeyError without fallback:", e)
print("has_option:", cfg.has_option("server", "host"), "| has_section('cache'):", cfg.has_section("cache"))

# 16. Interpolation: %(x)s vs ExtendedInterpolation
# ------------------------------------
# - Default BasicInterpolation: %(name)s refers to a key in the SAME section
#   (or DEFAULT). A literal percent sign must be written %%.
# - ExtendedInterpolation: ${section:key} can point at OTHER sections.
print("\n# 16. Interpolation")
print("basic %(base_dir)s ->", cfg["server"]["log_dir"])
try:
    bad = configparser.ConfigParser()
    bad.read_string("[s]\nrate = 50%\n")
    bad["s"]["rate"]
except configparser.InterpolationSyntaxError as e:
    print("a bare '%' breaks BasicInterpolation:", type(e).__name__)
ok = configparser.ConfigParser()
ok.read_string("[s]\nrate = 50%%\n")
print("escaped '%%' ->", ok["s"]["rate"])

ext = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
ext.read_string("[paths]\nroot = /srv\n[logs]\ndir = ${paths:root}/logs\nfile = ${dir}/app.log\n")
print("extended ${paths:root}/logs ->", ext["logs"]["dir"], "|", ext["logs"]["file"])
raw_cfg = configparser.ConfigParser(interpolation=None)  # treat '%' as plain text
raw_cfg.read_string("[s]\nrate = 50%\n")
print("interpolation=None keeps the % literally:", raw_cfg["s"]["rate"])

# 17. Writing INI and the Case-Insensitive Keys Gotcha
# ------------------------------------
# - Keys are lowercased by default (optionxform = str.lower). Section names
#   keep their case. Override optionxform = str to keep key case.
print("\n# 17. Writing + case-insensitivity")
out = configparser.ConfigParser()
out["app"] = {"Name": "Demo", "Version": "1", "Debug": "no"}
out["paths"] = {}
out["paths"]["Data_Dir"] = "/tmp/data"
buffer = io.StringIO()
out.write(buffer)  # write(fileobj) - could be open("x.ini", "w")
print(buffer.getvalue().strip())
print("keys come back lowercase:", list(out["app"].keys()))
print("lookup ignores case:", out["app"]["NAME"], "|", out["app"]["name"])

sensitive = configparser.ConfigParser()
sensitive.optionxform = str  # keep exact key case
sensitive.read_string("[env]\nPATH_Home = /home\nPath_Home = /other\n")
print("case-sensitive keys now:", list(sensitive["env"].keys()))
dupe = configparser.ConfigParser()
try:
    dupe.read_string("[env]\nKey = 1\nkey = 2\n")
except configparser.DuplicateOptionError as e:
    print("without optionxform, Key and key collide:", type(e).__name__)

# ====================================================================
# PART E - tomllib (TOML)
# ====================================================================

# 18. tomllib - Read TOML (Python 3.11+)
# ------------------------------------
# - TOML = modern config format (pyproject.toml, Cargo.toml). Has real types
#   (int, float, bool, strings, arrays, tables, dates) - unlike INI.
# - tomllib is READ-ONLY. To WRITE TOML you need a 3rd-party package such
#   as `tomli-w` (pip install tomli-w -> tomli_w.dumps(dict)).
# - tomllib.loads takes a str; tomllib.load takes a file opened in "rb".
print("\n# 18. tomllib (3.11+)")
TOML_TEXT = """
title = "Demo App"

[server]
host = "localhost"
port = 8080
debug = true
allowed = ["a.com", "b.com"]

[database]
name = "shop"
ratio = 0.75

[[workers]]
name = "w1"
threads = 2

[[workers]]
name = "w2"
threads = 4
"""
if sys.version_info >= (3, 11):
    import tomllib

    conf = tomllib.loads(TOML_TEXT)
    print("title:", conf["title"])
    print("port type:", type(conf["server"]["port"]).__name__, "| debug type:", type(conf["server"]["debug"]).__name__)
    print("allowed list:", conf["server"]["allowed"])
    print("array of tables:", conf["workers"])
    try:
        tomllib.loads("a = ")
    except tomllib.TOMLDecodeError as e:
        print("TOMLDecodeError:", e)
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "app.toml"
        p.write_text(TOML_TEXT)
        with open(p, "rb") as f:  # MUST be binary mode
            print("from file, db name:", tomllib.load(f)["database"]["name"])
    print("# Writing TOML: not in stdlib -> third-party `tomli-w` (tomli_w.dumps(conf)).")
else:
    print("SKIPPED: tomllib needs Python 3.11+ (on older versions: pip install tomli)")
    print("# Writing TOML always needs a 3rd-party package such as `tomli-w`.")

# ====================================================================
# PART F - environment variables and layered config
# ====================================================================

# 19. Environment Variables (12-factor style)
# ------------------------------------
# - The "12-factor app" rule: configuration that differs between deploys
#   (dev/staging/prod) and SECRETS (passwords, API keys) belong in
#   environment variables, not in code or in the git repo.
# - os.environ behaves like a dict of str -> str. Values are ALWAYS strings.
print("\n# 19. Environment variables")
os.environ["DEMO_APP_PORT"] = "9090"  # set for THIS process only
print("os.environ['DEMO_APP_PORT'] =", repr(os.environ["DEMO_APP_PORT"]), "(a str, not an int)")
print("os.environ.get with default:", os.environ.get("DEMO_APP_MISSING", "default-value"))
print("os.getenv same idea      :", os.getenv("DEMO_APP_MISSING", "default-value"))
try:
    os.environ["DEMO_APP_MISSING"]
except KeyError as e:
    print("KeyError for a missing var:", e)
try:
    os.environ["DEMO_APP_X"] = 5  # must be str
except TypeError as e:
    print("TypeError for non-str value:", e)
print("# bool gotcha: bool('false') is True! Parse flags explicitly:")


def env_bool(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes", "on")


print("bool('false'):", bool("false"), "| env_bool('false'):", env_bool("false"), "| env_bool('Yes'):", env_bool("Yes"))
del os.environ["DEMO_APP_PORT"]  # tidy up so the demo leaves no trace

# 20. Layered Config: defaults < file < env < CLI
# ------------------------------------
# - Common pattern: each layer overrides the one before it.
#     1. built-in defaults  (always safe to run)
#     2. config file        (per project/deploy)
#     3. environment vars   (per machine / secrets)
#     4. command-line args  (this single run)
# - ChainMap searches its dicts LEFT to RIGHT, so list the strongest first.
#   It does not copy: it is a live view over the layers.
print("\n# 20. Layered config")
DEFAULTS = {"host": "127.0.0.1", "port": 8000, "debug": False, "workers": 1}


def load_file_layer(ini_text: str) -> dict:
    parser = configparser.ConfigParser()
    parser.read_string(ini_text)
    sec = parser["server"]
    layer = {}
    if "host" in sec:
        layer["host"] = sec["host"]
    if "port" in sec:
        layer["port"] = sec.getint("port")
    if "workers" in sec:
        layer["workers"] = sec.getint("workers")
    return layer


def load_env_layer(prefix="DEMO_APP_") -> dict:
    layer = {}
    for key, value in os.environ.items():
        if key.startswith(prefix):
            name = key[len(prefix):].lower()
            if name in ("port", "workers"):
                layer[name] = int(value)  # env vars are strings -> convert
            elif name == "debug":
                layer[name] = env_bool(value)
            else:
                layer[name] = value
    return layer


def load_cli_layer(argv) -> dict:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host")
    ap.add_argument("--port", type=int)
    ap.add_argument("--workers", type=int)
    ap.add_argument("--debug", action="store_true", default=None)
    ns = vars(ap.parse_args(argv))
    return {k: v for k, v in ns.items() if v is not None}  # only what the user really gave


file_layer = load_file_layer("[server]\nhost = 0.0.0.0\nport = 8080\nworkers = 2\n")

os.environ["DEMO_APP_PORT"] = "9090"
os.environ["DEMO_APP_DEBUG"] = "true"
env_layer = load_env_layer()
cli_layer = load_cli_layer(["--workers", "8"])
for key in ("DEMO_APP_PORT", "DEMO_APP_DEBUG"):
    del os.environ[key]

settings = ChainMap(cli_layer, env_layer, file_layer, DEFAULTS)
print("defaults:", DEFAULTS)
print("file    :", file_layer)
print("env     :", env_layer)
print("cli     :", cli_layer)
print("MERGED  :", dict(settings))
print("where does 'port' come from? env ->", settings["port"], "| 'host'? file ->", settings["host"],
      "| 'workers'? cli ->", settings["workers"])
print("# Gotcha: write only to ONE layer (ChainMap writes go to maps[0]). Never put secrets in the repo file.")

# ====================================================================
# PART G - versioning saved data
# ====================================================================

# 21. Versioning and Migration of Saved Data
# ------------------------------------
# - Your data format WILL change (new field, renamed field). Old files still
#   exist on users' disks. Solution: write a "version" number into the data,
#   and on load, upgrade step by step: v1 -> v2 -> v3 ...
# - Each migration is small and only knows about ONE step. Old files keep working.
print("\n# 21. Versioned data with migrations")
CURRENT_VERSION = 3


def v1_to_v2(d):
    # v1 had "name" as one string; v2 splits it.
    first, _, last = d.pop("name").partition(" ")
    d["first_name"], d["last_name"] = first, last
    return d


def v2_to_v3(d):
    # v3 added a "newsletter" setting with a default.
    d.setdefault("newsletter", False)
    return d


MIGRATIONS = {1: v1_to_v2, 2: v2_to_v3}  # key = version it upgrades FROM


def load_profile(json_text: str) -> dict:
    data = json.loads(json_text)
    version = data.pop("version", 1)  # files from before versioning = v1
    if version > CURRENT_VERSION:
        raise ValueError(f"file is from a NEWER app (v{version}); please upgrade the app")
    while version < CURRENT_VERSION:
        data = MIGRATIONS[version](data)
        version += 1
    data["version"] = CURRENT_VERSION
    return data


def save_profile(data: dict) -> str:
    return json.dumps({**data, "version": CURRENT_VERSION}, sort_keys=True)


old_v1 = '{"name": "Ada Lovelace", "age": 36}'  # no version field at all
old_v2 = '{"version": 2, "first_name": "Alan", "last_name": "Turing", "age": 41}'
print("v1 file ->", load_profile(old_v1))
print("v2 file ->", load_profile(old_v2))
print("save     ->", save_profile({"first_name": "Grace", "last_name": "Hopper", "age": 85, "newsletter": True}))
try:
    load_profile('{"version": 99, "x": 1}')
except ValueError as e:
    print("future file ->", e)
print("# With pickle this is harder (class changes break old pickles) - another reason to prefer json.")

# 22. Format Comparison Table
# ------------------------------------
print("\n# 22. Format comparison")
print("# Format   Human-readable  Safe to load untrusted  Types supported")
print("# ------------------------------------------------------------------------------")
print("# json     yes             yes                     str, int, float, bool, None, list, dict")
print("# pickle   no (binary)     NO - runs code          almost any Python object")
print("# shelve   no (db files)   NO - uses pickle        any picklable value, str keys")
print("# ini      yes             yes                     strings only (convert yourself)")
print("# toml     yes             yes                     str, int, float, bool, datetime, list, table")
print("# csv      yes             yes                     strings only (rows/columns)")
print("#")
print("# Which one?")
print("# - Settings humans edit        -> toml (or ini). json has no comments.")
print("# - Data exchange / web APIs    -> json.")
print("# - Tables for Excel            -> csv.")
print("# - Private Python-only cache   -> pickle / shelve (never from untrusted sources).")
print("# - Secrets                     -> environment variables or a secrets manager, never in git.")

# 23. Gotchas Recap
# ------------------------------------
print("\n# 23. Gotchas recap")
print("# - pickle.loads on untrusted bytes = remote code execution.")
print("# - pickle needs 'wb'/'rb'; unpickling skips __init__; renamed classes break old files.")
print("# - shelve keys must be str; mutate-in-place is lost without writeback=True; always close.")
print("# - configparser: values are strings, keys are lowercased, '%' needs '%%'.")
print("# - tomllib reads only and needs a binary file object; writing needs tomli-w.")
print("# - os.environ values are strings: parse ints and bools yourself.")
print("# - ChainMap order: strongest layer FIRST.")
print("# - Put a version in saved data from day one, then migrate step by step.")
