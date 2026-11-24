"""Exercise set 06: errors, context managers and files.

Replace each `raise NotImplementedError` with working code. Run the tests with:
    pytest tests/test_ex06_errors_and_files.py
"""

import contextlib
import copy
import csv
import functools
import json
from pathlib import Path


def parse_ints(items):
    # catch only the errors we expect, keep going
    numbers, bad = [], []
    for item in items:
        try:
            numbers.append(int(item))
        except (ValueError, TypeError):
            bad.append(item)
    return numbers, bad


class BankError(Exception):
    """Base class: callers can catch every bank problem with one except."""


class InsufficientFundsError(BankError):
    def __init__(self, balance, amount):
        super().__init__(f"need {amount}, have {balance}")
        self.balance = balance
        self.amount = amount
        self.shortfall = amount - balance


def withdraw(balance, amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    if amount > balance:
        raise InsufficientFundsError(balance, amount)
    return balance - amount


class ValidationError(Exception):
    def __init__(self, errors):
        super().__init__("; ".join(f"{k}: {v}" for k, v in errors.items()))
        self.errors = errors


def validate_user(user):
    errors = {}
    name = user.get("name")
    if not isinstance(name, str) or not name.strip():
        errors["name"] = "must be a non-empty string"
    email = user.get("email")
    if not isinstance(email, str) or "@" not in email or "." not in email.split("@")[-1]:
        errors["email"] = "must look like a@b.c"
    age = user.get("age")
    if isinstance(age, bool) or not isinstance(age, int) or not 0 <= age <= 150:
        errors["age"] = "must be an integer from 0 to 150"
    if errors:
        raise ValidationError(errors)  # report ALL problems at once
    return user


class ConfigError(Exception):
    pass


def get_setting(config, dotted_key):
    value = config
    try:
        for part in dotted_key.split("."):
            value = value[part]
    except (KeyError, TypeError) as err:
        # `from err` keeps the original error as __cause__ for debugging
        raise ConfigError(f"missing setting: {dotted_key}") from err
    return value


def run_with_cleanup(action, log):
    # finally runs on success and on error
    log.append("start")
    try:
        return action()
    finally:
        log.append("cleanup")


class Transaction:
    def __init__(self, data):
        self.data = data

    def __enter__(self):
        self._snapshot = copy.deepcopy(self.data)
        return self.data

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:  # something failed: roll back
            self.data.clear()
            self.data.update(self._snapshot)
        return False  # False = do not hide the exception


@contextlib.contextmanager
def temp_attr(obj, name, value):
    # generator-based context manager: code before yield = enter, finally = exit
    missing = object()
    old = getattr(obj, name, missing)
    setattr(obj, name, value)
    try:
        yield
    finally:
        if old is missing:
            delattr(obj, name)
        else:
            setattr(obj, name, old)


def write_lines(path, lines):
    # the with-block closes the file for us
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


def read_lines(path, missing_ok=False):
    # bare `raise` re-raises the same error
    try:
        with open(path, encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        if missing_ok:
            return []
        raise


def count_words(path):
    # pathlib read_text is the short way to read a whole file
    counts = {}
    for raw in Path(path).read_text(encoding="utf-8").split():
        word = raw.strip(".,!?;:").lower()
        if word:
            counts[word] = counts.get(word, 0) + 1
    return counts


def write_rows(path, rows, fieldnames):
    # csv module handles quoting for us
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def total_by_category(path):
    # DictReader gives each row as a dict keyed by the header
    totals = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                amount = float(row["amount"])
            except (ValueError, TypeError):
                continue
            key = row["category"].strip()
            totals[key] = totals.get(key, 0.0) + amount
    return totals


def save_json(path, data):
    # json.dump writes straight to the file object
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def load_json(path, default=None):
    # fail soft with a default for a missing or broken file
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def list_by_extension(folder):
    # rglob walks the tree, suffix gives the extension
    root = Path(folder)
    result = {}
    for p in root.rglob("*"):
        if p.is_file():
            result.setdefault(p.suffix.lower(), []).append(p.relative_to(root).as_posix())
    return {ext: sorted(names) for ext, names in result.items()}


def safe_write(path, text):
    # write-then-rename pattern
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=path.name + ".", suffix=".tmp", delete=False) as fh:
        tmp = Path(fh.name)
        try:
            fh.write(text)
        except BaseException:
            fh.close()
            tmp.unlink(missing_ok=True)
            raise
    try:
        tmp.replace(path)  # same directory keeps the replacement on one filesystem
    finally:
        tmp.unlink(missing_ok=True)
    return path


def retry(times, exceptions=(Exception,)):
    # loop with try/except; re-raise on the last attempt
    if times < 1:
        raise ValueError("times must be at least 1")

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
        return wrapper
    return decorator
