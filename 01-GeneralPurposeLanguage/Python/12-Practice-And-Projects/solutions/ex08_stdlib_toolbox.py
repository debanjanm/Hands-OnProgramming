"""Exercise set 08: the standard-library toolbox.

Work from top to bottom. Each problem is marked easy, medium or hard.
"""
import bisect
import enum
import functools
import heapq
import itertools
import json
import re
import textwrap
from collections import Counter, defaultdict, deque
from datetime import timedelta


# ---------------------------------------------------------------- 1 (easy)
def extract_emails(text):
    """Level: easy. (re)

    Return the email addresses found in `text`, lower-cased, without
    duplicates, in the order they first appear. A trailing full stop that ends
    a sentence is not part of the address.

        extract_emails("Mail Bob@Example.com, or bob@example.com. Cc: a.b+c@x.co.uk")
            -> ["bob@example.com", "a.b+c@x.co.uk"]
        extract_emails("no emails here") -> []

    Hint: re.findall with a pattern like [\\w.+-]+@[\\w-]+(?:\\.[\\w-]+)+ ; dedupe with a seen set.
    """
    # Idea: regex finds candidates; a `seen` set keeps first-appearance order.
    seen = set()
    result = []
    for match in re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", text):
        email = match.lower()
        if email not in seen:
            seen.add(email)
            result.append(email)
    return result


# ---------------------------------------------------------------- 2 (easy)
def add_business_days(start, days):
    """Level: easy. (datetime, timedelta)

    `start` is a datetime.date. Return the date that is `days` business days
    later (Monday to Friday count; Saturday and Sunday are skipped).
    `days` of 0 returns `start` unchanged. ValueError if days < 0.

        add_business_days(date(2024, 3, 8), 1)  -> date(2024, 3, 11)   # Fri -> Mon
        add_business_days(date(2024, 3, 6), 5)  -> date(2024, 3, 13)   # Wed -> next Wed
        add_business_days(date(2024, 3, 9), 1)  -> date(2024, 3, 11)   # Sat -> Mon

    Hint: step one day at a time with timedelta(days=1); only count weekdays (date.weekday() < 5).
    """
    # Idea: walk forward day by day and only count the weekdays.
    if days < 0:
        raise ValueError("days must not be negative")
    current = start
    while days > 0:
        current += timedelta(days=1)
        if current.weekday() < 5:
            days -= 1
    return current


# ---------------------------------------------------------------- 3 (easy)
def word_frequencies(text, n):
    """Level: easy. (collections.Counter)

    Return the `n` most common words as (word, count) tuples. Ignore case;
    a word is letters and apostrophes. Ties are sorted alphabetically.

        word_frequencies("the cat and The dog and the bird", 2) -> [("the", 3), ("and", 2)]
        word_frequencies("b a b a c", 3) -> [("a", 2), ("b", 2), ("c", 1)]
        word_frequencies("", 5) -> []

    Hint: Counter(words) gives counts; sort with key=lambda p: (-p[1], p[0]).
    """
    # Idea: Counter counts; an explicit sort makes the tie-break predictable.
    counts = Counter(re.findall(r"[a-z']+", text.lower()))
    return sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))[:n]


# ---------------------------------------------------------------- 4 (easy)
def group_anagrams(words):
    """Level: easy. (collections.defaultdict)

    Group words that are anagrams of each other (ignore case). Return a list of
    groups. Inside a group, keep the words sorted. Sort the groups by their
    first word. Words that have no anagram partner form a group of one.

        group_anagrams(["listen", "silent", "cat", "act", "dog"])
            -> [["act", "cat"], ["dog"], ["listen", "silent"]]
        group_anagrams([]) -> []

    Hint: key = "".join(sorted(word.lower())); groups = defaultdict(list).
    """
    # Idea: anagrams share the same sorted letters, so use that as the dict key.
    groups = defaultdict(list)
    for word in words:
        groups["".join(sorted(word.lower()))].append(word)
    return sorted(sorted(group) for group in groups.values())


# ---------------------------------------------------------------- 5 (easy)
def tail(lines, n):
    """Level: easy. (collections.deque)

    Return the last `n` items of any iterable as a list, reading it only once
    and keeping at most `n` items in memory (like the `tail` command).
    n = 0 gives []. ValueError if n < 0.

        tail(["a", "b", "c", "d"], 2) -> ["c", "d"]
        tail(iter(range(1000)), 3)    -> [997, 998, 999]
        tail([1], 5)                  -> [1]

    Hint: deque(iterable, maxlen=n) drops old items automatically.
    """
    # Idea: a bounded deque forgets the oldest item for free.
    if n < 0:
        raise ValueError("n must not be negative")
    return list(deque(lines, maxlen=n))


# --------------------------------------------------------------- 6 (medium)
def schedule(names, rooms):
    """Level: medium. (itertools)

    Every pair of people must meet once. Return a list of (a, b, room) tuples
    for all pairs, in the order of the names list, giving out the rooms in
    turn (round robin: room 1, room 2, ..., then back to room 1).
    No pairs are possible with fewer than 2 names -> [].

        schedule(["Ann", "Bo", "Cy"], ["R1", "R2"])
            -> [("Ann", "Bo", "R1"), ("Ann", "Cy", "R2"), ("Bo", "Cy", "R1")]

    Hint: itertools.combinations(names, 2) and itertools.cycle(rooms) with zip.
    """
    # Idea: combinations builds the pairs; cycle makes the rooms repeat forever.
    return [(a, b, room) for (a, b), room in zip(itertools.combinations(names, 2), itertools.cycle(rooms))]


# --------------------------------------------------------------- 7 (medium)
def compose(*funcs):
    """Level: medium. (functools.reduce)

    Return a function that applies `funcs` from left to right:
    compose(f, g)(x) == g(f(x)). With no functions it returns its input.

        compose(str.strip, str.upper, lambda s: s + "!")("  hi ") -> "HI!"
        compose()(5) -> 5

    Hint: functools.reduce(lambda value, f: f(value), funcs, x).
    """
    # Idea: reduce feeds the running value through each function in turn.
    return lambda x: functools.reduce(lambda value, f: f(value), funcs, x)


# --------------------------------------------------------------- 8 (medium)
def merge_configs(base_text, override_text):
    """Level: medium. (json)

    Both arguments are JSON texts holding objects. Merge them deeply:
    keys in `override` win; when both values are objects, merge them
    recursively; any other value is simply replaced. Return the result as a
    JSON string with sorted keys and indent=2. Invalid JSON raises ValueError.

        merge_configs('{"a": 1, "db": {"host": "x", "port": 1}}', '{"db": {"port": 2}}')
            -> '{\\n  "a": 1,\\n  "db": {\\n    "host": "x",\\n    "port": 2\\n  }\\n}'

    Hint: json.loads / json.dumps(..., sort_keys=True, indent=2); write a small recursive helper.
    """
    # Idea: recursion only where both sides are dicts; everything else is replaced.
    def merge(base, override):
        result = dict(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = merge(result[key], value)
            else:
                result[key] = value
        return result

    merged = merge(json.loads(base_text), json.loads(override_text))
    return json.dumps(merged, sort_keys=True, indent=2)


# --------------------------------------------------------------- 9 (medium)
def summarize_dir(path):
    """Level: medium. (pathlib)

    `path` is a pathlib.Path to a folder. Count the files in it and in all
    sub-folders by extension (lower-case, with the dot). Files with no
    extension are counted under "(none)". Folders are not counted. Return a
    dict with keys in alphabetical order.

        folder holds a.py, b.PY, notes.txt, README, sub/c.py
            -> {"(none)": 1, ".py": 3, ".txt": 1}

    Hint: path.rglob("*"), p.is_file(), p.suffix.lower(); Counter + sorted.
    """
    # Idea: rglob walks everything; suffix gives the extension.
    counts = Counter(p.suffix.lower() or "(none)" for p in path.rglob("*") if p.is_file())
    return dict(sorted(counts.items()))


# -------------------------------------------------------------- 10 (medium)
def wrap_text(text, width):
    """Level: medium. (textwrap)

    Tidy indented, badly wrapped text: remove the common indent, join each
    paragraph (paragraphs are separated by a blank line) into one line, then
    re-wrap it so that every output line, including a 2-space indent, is at
    most `width` characters. Paragraphs are separated by one blank line.
    Empty text gives "".

        wrap_text("    one two three\\n    four", 12) -> "  one two\\n  three four"

    Hint: textwrap.dedent, re.split(r"\\n\\s*\\n", ...), textwrap.fill, textwrap.indent.
    """
    # Idea: dedent -> split paragraphs -> fill each to width-2 -> indent by 2.
    text = textwrap.dedent(text).strip()
    if not text:
        return ""
    paragraphs = re.split(r"\n\s*\n", text)
    filled = [textwrap.fill(" ".join(p.split()), width=width - 2) for p in paragraphs]
    return textwrap.indent("\n\n".join(filled), "  ")


# -------------------------------------------------------------- 11 (medium)
def grade_report(scores, k):
    """Level: medium. (heapq, bisect, string formatting)

    `scores` is a dict {name: score}. Return report lines for the `k` best
    students, best first (ties: alphabetical by name). Each line is
    name left-aligned in 8 characters, the score right-aligned in 6 with one
    decimal, two spaces, then the letter grade:
    90 and up A, 80 and up B, 70 and up C, 60 and up D, below 60 F.

        grade_report({"ann": 92.5, "bo": 71, "cy": 58.25}, 2)
            -> ["ann       92.5  A", "bo        71.0  C"]

    Hint: heapq.nsmallest(k, items, key=lambda p: (-p[1], p[0])); bisect.bisect([60, 70, 80, 90], score) indexes "FDCBA".
    """
    # Idea: heapq picks the top k without a full sort; bisect turns a score into a grade.
    best = heapq.nsmallest(k, scores.items(), key=lambda pair: (-pair[1], pair[0]))
    return [f"{name:<8}{score:>6.1f}  {'FDCBA'[bisect.bisect([60, 70, 80, 90], score)]}" for name, score in best]


# -------------------------------------------------------------- 12 (hard)
class Status(enum.Enum):
    """Provided for you (enum): the result of checking one order. Used by `process_orders`."""

    OK = "ok"
    INVALID = "invalid"


def process_orders(orders, logger):
    """Level: hard. (logging)

    `orders` is a list of dicts like {"id": 7, "qty": 3}. An order is INVALID
    when "qty" is missing or is not a positive int. For every invalid order
    call `logger.warning("order %s skipped: qty=%r", order_id, qty)` (lazy %
    formatting, not an f-string). When "id" is missing use "?". Return a dict
    {Status.OK: n_ok, Status.INVALID: n_invalid}; both keys are always present.

        process_orders([{"id": 1, "qty": 2}, {"id": 2, "qty": 0}], log)
            -> {Status.OK: 1, Status.INVALID: 1}   and logs "order 2 skipped: qty=0"

    Hint: tests read the log with pytest's caplog. isinstance(True, int) is True, so watch out for bools.
    """
    # Idea: one pass, one counter; the logger formats the message itself.
    counts = {Status.OK: 0, Status.INVALID: 0}
    for order in orders:
        qty = order.get("qty")
        if isinstance(qty, int) and not isinstance(qty, bool) and qty > 0:
            counts[Status.OK] += 1
        else:
            counts[Status.INVALID] += 1
            logger.warning("order %s skipped: qty=%r", order.get("id", "?"), qty)
    return counts
