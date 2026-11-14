import textwrap
import string
import difflib
import pprint
import reprlib
import unicodedata
import shlex
import fnmatch
import html
import locale
import re
import sys
from collections import Counter

# 01. Text Utilities - Introduction
# ------------------------------------
# - Python's standard library has a whole shelf of small tools for TEXT work
#   that people often re-invent with messy loops and regex:
#     textwrap    -> line wrapping, indenting, trimming blocks of text
#     string      -> character constants, safe Template substitution
#     difflib     -> "how similar?" and "what changed?" between texts
#     pprint      -> readable printing of big nested data
#     reprlib     -> short, bounded repr() for huge containers
#     unicodedata -> the truth about Unicode (accents, widths, normalisation)
#     shlex       -> split / quote shell-style command lines
#     fnmatch     -> shell wildcards (*.py) on strings
#     html        -> escape / unescape HTML special characters
#     locale      -> numbers/dates in the user's regional format
# - The last block (#17) combines several into a small real-world example.

print("# 01. Text Utilities - Introduction")
print("# ------------------------------------")

# 02. textwrap - wrap(), fill(), shorten()
# ------------------------------------
# - wrap(text, width)   -> LIST of lines, each at most `width` characters
# - fill(text, width)   -> ONE string with newlines (same as "\n".join(wrap(...)))
# - shorten(text, w)    -> collapse whitespace and cut to fit, adding "[...]"
# - Words are never split unless a single word is longer than the width.
print("\n# 02. textwrap - wrap(), fill(), shorten()")
paragraph = (
    "Python's standard library is often described as batteries included: "
    "most everyday jobs already have a tested tool waiting for you."
)
print("wrap  ->", textwrap.wrap(paragraph, width=30))
print("fill  ->")
print(textwrap.fill(paragraph, width=40))
print("shorten(40)  ->", textwrap.shorten(paragraph, width=40))
print("shorten(40, placeholder='...') ->", textwrap.shorten(paragraph, width=40, placeholder="..."))
# shorten() collapses runs of whitespace first (handy for previews of messy text)
print("whitespace collapsed ->", repr(textwrap.shorten("a   lot \n of    space", width=50)))

# 03. textwrap - dedent() and indent()
# ------------------------------------
# - Triple-quoted strings keep the indentation you typed inside your code.
#   dedent() removes the COMMON leading whitespace so the text starts at column 0.
# - indent(text, prefix) adds a prefix to every (non-blank) line - perfect for
#   quoting ("> ") or nesting a block in generated code.
print("\n# 03. textwrap - dedent() and indent()")


def usage_text():
    raw = """
        usage: tool [options]

            --help     show this help
            --verbose  more output
        """
    return raw


print("raw (with code indentation):")
print(usage_text())
print("after dedent().strip():")
print(textwrap.dedent(usage_text()).strip())
print("indent with '> ':")
print(textwrap.indent("line one\nline two\n\nline four", "> "))
print("indent only some lines (predicate):")
print(textwrap.indent("keep\n# comment\nkeep too", "    ", predicate=lambda line: not line.startswith("#")))

# 04. textwrap.TextWrapper - reusable options
# ------------------------------------
# - TextWrapper holds settings so you can reuse them: initial_indent,
#   subsequent_indent (hanging indents, bullet lists), max_lines, placeholder,
#   break_long_words, break_on_hyphens, replace_whitespace, drop_whitespace.
print("\n# 04. textwrap.TextWrapper options")
bullet = textwrap.TextWrapper(width=36, initial_indent="* ", subsequent_indent="  ")
print(bullet.fill("A bullet point that is long enough to need wrapping onto a second or third line."))
limited = textwrap.TextWrapper(width=24, max_lines=2, placeholder=" ...")
print("max_lines=2 ->", limited.wrap(paragraph))
url = "https://example.com/a/very/long/path/that/has/no/spaces/at/all"
print("long word, break_long_words=True (default):", textwrap.wrap(url, 25))
print("long word, break_long_words=False         :", textwrap.wrap(url, 25, break_long_words=False))
print("# Gotcha: wrap()/fill() treat newlines as plain whitespace, so paragraphs get merged.")
text = "First paragraph here.\n\nSecond paragraph is here too."
print("whole text   :", repr(textwrap.fill(text, 40)))
print("per paragraph:", repr("\n\n".join(textwrap.fill(p, 40) for p in text.split("\n\n"))))

# 05. string module - constants and capwords
# ------------------------------------
# - Ready-made character sets: no more typing "abcdefghijklmnopqrstuvwxyz".
# - Handy for validation, generating tokens, building translation tables.
print("\n# 05. string module - constants and capwords")
print("ascii_lowercase:", string.ascii_lowercase)
print("ascii_uppercase:", string.ascii_uppercase)
print("digits         :", string.digits)
print("hexdigits      :", string.hexdigits)
print("punctuation    :", string.punctuation)
print("whitespace     :", repr(string.whitespace))
print("printable has", len(string.printable), "chars")
# strip punctuation with a translation table
cleaned = "Hello, world! (it's 100% fine...)".translate(str.maketrans("", "", string.punctuation))
print("punctuation removed:", cleaned)
print("is every char a hex digit?", all(c in string.hexdigits for c in "deadBEEF"))
print("capwords       :", string.capwords("the  quick   brown fox"), "(also collapses extra spaces)")
print("str.title()    :", "they're bill's friends".title(), "<- gotcha: capital after apostrophes")
print("capwords       :", string.capwords("they're bill's friends"))

# 06. string.Template - safe substitution
# ------------------------------------
# - Template uses $name or ${name}. It does ONLY name lookup: no attribute
#   access, no indexing, no format specs, no code. That makes it the safe choice
#   when the TEMPLATE TEXT itself comes from users (emails, config, plugins).
# - substitute()      -> raises KeyError if a name is missing (strict)
# - safe_substitute() -> leaves unknown $names untouched (forgiving)
# - "$$" is a literal dollar sign.
print("\n# 06. string.Template")
tpl = string.Template("Hi $name, your order ${item}s ships on $day. Cost: $$5")
print(tpl.substitute(name="Asha", item="book", day="Monday"))
try:
    tpl.substitute(name="Asha")
except KeyError as e:
    print("substitute() missing key -> KeyError:", e)
print("safe_substitute:", tpl.safe_substitute(name="Asha"))


class Account:
    def __init__(self):
        self.owner = "Asha"
        self._api_key = "SECRET-123"

    def __str__(self):
        return "<Account>"


acct = Account()
evil = "Owner: {a.owner} | key: {a._api_key}"  # imagine a user typed this template
print("str.format with user template LEAKS :", evil.format(a=acct))
print("Template with '$a.owner'             :", string.Template("Owner: $a.owner").substitute(a=acct),
      "<- only the name 'a' is substituted; '.owner' is just text")
print("Template '${a._api_key}' cannot peek  :", string.Template("key: ${a._api_key}").safe_substitute(a=acct))
print("# Rule: trusted template + your data -> f-string / format.  Untrusted template -> Template.")

# 07. string.Formatter - the engine behind str.format (brief)
# ------------------------------------
# - str.format() is implemented by string.Formatter. Subclass it to customise
#   how fields are looked up or converted. parse() shows how a format string
#   is split into pieces.
print("\n# 07. string.Formatter (brief)")
fmt = string.Formatter()
print("parse ->", list(fmt.parse("Hello {name!r:>8}, you owe {amt:.2f}")))


class DefaultFormatter(string.Formatter):
    """Missing keys become <missing> instead of raising KeyError."""

    def get_value(self, key, args, kwargs):
        if isinstance(key, str):
            return kwargs.get(key, "<missing>")
        return super().get_value(key, args, kwargs)


print(DefaultFormatter().format("{greeting}, {who}!", greeting="Hi"))

# 08. difflib - similarity ratio and "did you mean?"
# ------------------------------------
# - SequenceMatcher(None, a, b).ratio() -> 0.0 .. 1.0 (1.0 = identical)
# - get_close_matches(word, options, n=3, cutoff=0.6) -> best fuzzy matches
#   (the engine behind "Did you mean ...?" messages)
print("\n# 08. difflib - ratio and get_close_matches")
for a, b in [("apple", "apple"), ("apple", "appel"), ("apple", "orange"), ("kitten", "sitting")]:
    r = difflib.SequenceMatcher(None, a, b).ratio()
    print(f"ratio({a!r:9}, {b!r:9}) = {r:.2f}")
commands = ["commit", "checkout", "branch", "merge", "rebase", "status"]
for typo in ["comit", "chekout", "stauts", "xyz"]:
    print(f"did you mean for {typo!r:10} ->", difflib.get_close_matches(typo, commands, n=2, cutoff=0.6))
print("# Gotcha: ratio is character-based (not meaning-based) and can depend on argument ORDER.")
print("   ratio('bcda','abab'):", difflib.SequenceMatcher(None, "bcda", "abab").ratio(),
      "| ratio('abab','bcda'):", difflib.SequenceMatcher(None, "abab", "bcda").ratio())
print("# Gotcha: ratio() is case-sensitive - normalise first (lower/casefold).")
print("   'Python' vs 'python':", round(difflib.SequenceMatcher(None, "Python", "python").ratio(), 3),
      "| after lower():", difflib.SequenceMatcher(None, "python", "python").ratio())

# 09. difflib - unified_diff, ndiff, opcodes, HtmlDiff
# ------------------------------------
# - unified_diff : the familiar `git diff` / patch format (+ and - lines)
# - ndiff        : line AND character-level hints (lines starting with "?")
# - get_opcodes  : machine-readable list of edits (equal/replace/delete/insert)
# - HtmlDiff     : side-by-side HTML table (write it to a file to open in a browser)
print("\n# 09. difflib - unified_diff, ndiff, opcodes, HtmlDiff")
old = ["name = 'app'", "debug = True", "port = 8000", "workers = 2"]
new = ["name = 'app'", "debug = False", "port = 8000", "workers = 4", "log = 'info'"]
print("unified_diff:")
for line in difflib.unified_diff(old, new, fromfile="config_old.py", tofile="config_new.py", lineterm=""):
    print("  " + line)
print("ndiff (note the ? hint lines pointing at changed characters):")
for line in difflib.ndiff(["workers = 12"], ["workers = 14"]):
    print("  " + line)
print("opcodes:")
sm = difflib.SequenceMatcher(None, "qabxcd", "abycdf")
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    print(f"  {tag:8} a[{i1}:{i2}]={'qabxcd'[i1:i2]!r:6} b[{j1}:{j2}]={'abycdf'[j1:j2]!r}")
page = difflib.HtmlDiff().make_file(old, new, "old", "new")
print("HtmlDiff produced an HTML page, starts with:", page[:15].strip(), "| size > 1000 chars:", len(page) > 1000)

# 10. pprint - readable printing of nested data
# ------------------------------------
# - print() of a big nested dict is one unreadable line. pprint wraps it nicely.
# - pprint.pprint(obj) prints, pprint.pformat(obj) RETURNS the string (for logs).
# - Options: width, depth (collapse deeper levels to ...), sort_dicts (default True),
#   compact (pack short items), indent. pprint.pp() = pprint with sort_dicts=False.
print("\n# 10. pprint")
config = {
    "service": "billing",
    "version": (1, 4, 2),
    "database": {"host": "db.internal", "port": 5432, "options": {"ssl": True, "timeout": 30}},
    "features": ["invoices", "refunds", "reports", "webhooks", "exports", "audit-log"],
    "owners": {"zed": 1, "amy": 2},
}
print("plain print():")
print(config)
print("pprint(width=60):")
pprint.pprint(config, width=60)
print("depth=1 (deeper levels become ...):")
pprint.pprint(config, depth=1, width=60)
print("sort_dicts=False (keep insertion order):")
pprint.pprint(config["owners"], sort_dicts=False)
print("sorted (default)                       :", end=" ")
pprint.pprint(config["owners"])
print("compact=True packs many short items per line:")
pprint.pprint(list(range(1, 31)), width=40, compact=True)
text_form = pprint.pformat(config["features"], width=30)
print("pformat returns a string:", type(text_form).__name__, "with", text_form.count("\n") + 1, "lines")
printer = pprint.PrettyPrinter(indent=4, width=50)
print("PrettyPrinter(indent=4):")
printer.pprint({"a": [1, 2, 3], "b": {"c": "x" * 30, "d": "y" * 10}})
print("isreadable / isrecursive:", pprint.isreadable([1, 2]), pprint.isrecursive([1, 2]))

# 11. reprlib - bounded repr() for huge containers
# ------------------------------------
# - repr() of a list with a million items would flood your terminal or log file.
#   reprlib.repr() shortens it with "...". Great for debug messages and __repr__.
print("\n# 11. reprlib")
big = list(range(100000))
print("reprlib.repr(list) :", reprlib.repr(big))
print("reprlib.repr(str)  :", reprlib.repr("x" * 200))
print("reprlib.repr(dict) :", reprlib.repr({i: i * i for i in range(50)}))
r = reprlib.Repr()
r.maxlist = 3
r.maxstring = 12
print("custom limits      :", r.repr(list(range(10))), "|", r.repr("a very long string indeed"))


class Basket:
    def __init__(self, items):
        self.items = items

    @reprlib.recursive_repr()  # guards against infinite recursion on self-referencing objects
    def __repr__(self):
        return f"Basket({reprlib.repr(self.items)})"


print("safe __repr__      :", Basket(list(range(1000))))
loop = Basket([])
loop.items.append(loop)  # basket contains itself
print("self-referencing   :", repr(loop))

# 12. unicodedata - the truth about Unicode text
# ------------------------------------
# - The SAME visible character can be stored in more than one way.
#   "é" can be ONE code point (U+00E9) or TWO: "e" + combining accent (U+0301).
#   They look identical but are NOT equal, differ in len(), and break dict/set
#   lookups, searching, sorting and deduplication.
# - Fix: normalise both sides first. unicodedata.normalize(form, text):
#     NFC  : compose into single code points where possible   (use for storage/compare)
#     NFD  : decompose into base letter + combining marks      (use for accent stripping)
#     NFKC / NFKD : also fold "compatibility" forms (ligature fi -> fi, superscript 2 -> 2)
print("\n# 12. unicodedata - normalisation")
one = "café"  # é as a single code point
two = "café"  # e + combining acute accent
print("shown          :", one, two)
print("one == two     :", one == two, "  <- looks equal, is NOT")
print("len(one), len(two):", len(one), len(two))
print("code points    :", [hex(ord(c)) for c in one], [hex(ord(c)) for c in two])
print("NFC(one) == NFC(two):", unicodedata.normalize("NFC", one) == unicodedata.normalize("NFC", two))
print("NFD(one) == NFD(two):", unicodedata.normalize("NFD", one) == unicodedata.normalize("NFD", two))
print("dict lookup problem :", {one: "found"}.get(two, "KeyError-ish: not found"))
print("is_normalized NFC   :", unicodedata.is_normalized("NFC", one), unicodedata.is_normalized("NFC", two))
print("NFKC folds compatibility chars:", unicodedata.normalize("NFKC", "ﬁnal ² ＡＢ"), "(from 'ﬁnal ² ＡＢ')")

# 13. unicodedata - category(), name(), digits, widths, accents, casefold
# ------------------------------------
print("\n# 13. unicodedata - category, name, east_asian_width")
for ch in ["A", "a", "7", " ", "!", "$", "é", "́", "日", "€"]:
    print(f"  {ch!r:10} category={unicodedata.category(ch):3} name={unicodedata.name(ch, '?')}")
print("# category letters: L=letter N=number P=punctuation S=symbol Z=separator M=mark(accent) C=control")
print("lookup by name   :", unicodedata.lookup("GREEK SMALL LETTER ALPHA"), unicodedata.lookup("SNOWMAN"))

# Other scripts have their own digits - isdigit()/int() accept them!
arabic_three = "٣"
print("Arabic-Indic digit:", arabic_three, "isdigit:", arabic_three.isdigit(), "int():", int(arabic_three),
      "unicodedata.decimal():", unicodedata.decimal(arabic_three), "| in string.digits:", arabic_three in string.digits)
print("# Gotcha: validate '0-9 only' with string.digits or re.ASCII, not str.isdigit().")

# East Asian width: how many terminal columns does text really occupy?
# W/F (wide/fullwidth) = 2 columns, H/Na/N/A = 1 column (A = ambiguous)
print("east_asian_width :", {c: unicodedata.east_asian_width(c) for c in ["a", "日", "Ａ", "ｱ"]})


def display_width(text):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text if not unicodedata.combining(c))


for sample in ["Python", "日本語", "café"]:
    print(f"  {sample!r:14} len={len(sample)} display_width={display_width(sample)}")
print("# len() counts code points, not columns - alignment code needs display_width().")


def strip_accents(text):
    decomposed = unicodedata.normalize("NFD", text)  # split e + accent
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")  # drop Mark,nonspacing


print("strip_accents    :", strip_accents("Crème brûlée, Ångström, naïve, jalapeño"))
print("# Note: 'ø', 'ß', 'æ' have no decomposition, so stripping leaves them unchanged:", strip_accents("straße ø"))

# casefold() vs lower() - for CASE-INSENSITIVE comparison use casefold()
german = "Straße"  # Straße
print("lower()          :", german.lower(), "==", "STRASSE".lower(), "->", german.lower() == "STRASSE".lower())
print("casefold()       :", german.casefold(), "==", "STRASSE".casefold(), "->", german.casefold() == "STRASSE".casefold())


def same_text(a, b):
    """Compare strings the way a human would: ignore composition form AND case."""
    norm = lambda s: unicodedata.normalize("NFC", s).casefold()
    return norm(a) == norm(b)


print("same_text(one, two)           :", same_text(one, two))
print("same_text('Stra\\u00dfe','STRASSE'):", same_text(german, "STRASSE"))
print("# Even tighter: casefold(NFC(casefold(NFD(x)))) handles a few rare edge cases.")

# 14. shlex - parse and build shell-style command lines
# ------------------------------------
# - str.split() breaks on every space, even inside quotes. shlex.split() follows
#   shell quoting rules, so quoted phrases stay together.
# - shlex.quote(s) makes ANY string safe to paste into a shell command.
# - shlex.join(list) = the reverse of split.
# - Best practice with subprocess: pass a LIST of args (no shell). If you must
#   build a shell string, quote every piece. (See the subprocess topic in this folder.)
print("\n# 14. shlex")
cmdline = 'cp "my file.txt" /backup/ --note="two words" --flag \'single quoted\''
print("str.split :", cmdline.split())
print("shlex.split:", shlex.split(cmdline))
print("comments=True:", shlex.split("echo hi # this is a comment", comments=True))
filename = "report; rm -rf /"  # hostile or just unlucky file name
print("shlex.quote :", shlex.quote(filename))
print("safe string :", "cat " + shlex.quote(filename))
print("quote leaves safe words alone:", shlex.quote("plain-name_1.txt"), "|", repr(shlex.quote("")))
args = ["grep", "-n", "hello world", "my file.txt"]
print("shlex.join :", shlex.join(args))
print("round trip :", shlex.split(shlex.join(args)) == args)
try:
    shlex.split('echo "unterminated')
except ValueError as e:
    print("bad quoting -> ValueError:", e)

# 15. fnmatch - shell wildcards on strings (no file access)
# ------------------------------------
# - fnmatch only compares STRINGS to a pattern; it never touches the disk.
#   (glob = patterns against real files, see 19-File-Utils-And-Archives.py)
# - Pattern syntax:  *  any chars | ?  one char | [abc] one of | [!abc] none of
# - fnmatch()      : case rules follow the OS (insensitive on Windows!)
# - fnmatchcase()  : ALWAYS case-sensitive - use it for portable behaviour
# - filter(names, pat) : keep matching names | translate(pat) : the regex behind it
print("\n# 15. fnmatch")
files = ["main.py", "test_main.py", "README.md", "data01.csv", "data2.csv", "Notes.TXT", ".hidden.py"]
print("*.py            :", fnmatch.filter(files, "*.py"))
print("test_*.py       :", fnmatch.filter(files, "test_*.py"))
print("data?? .csv     :", fnmatch.filter(files, "data??.csv"))
print("data[0-9].csv   :", fnmatch.filter(files, "data[0-9].csv"))
print("[!t]*.py        :", fnmatch.filter(files, "[!t]*.py"))
print("case-sensitive  :", fnmatch.fnmatchcase("Notes.TXT", "*.txt"), "| fnmatchcase(*.TXT):", fnmatch.fnmatchcase("Notes.TXT", "*.TXT"))
print("fnmatch (os rule): Notes.TXT vs *.txt ->", fnmatch.fnmatch("Notes.TXT", "*.txt"), "(True on Windows, False on Linux/macOS)")
print("'*' matches '/' too:", fnmatch.fnmatch("src/deep/mod.py", "*.py"), "<- unlike real glob")
print("'*' matches leading dot:", fnmatch.fnmatch(".hidden.py", "*.py"), "<- unlike real glob")
print("translate        :", fnmatch.translate("*.py"), "(a regex; exact text varies by Python version)")
ignore = ["*.pyc", "__pycache__", ".git*", "*.log"]
paths = ["a.py", "a.pyc", "__pycache__", ".gitignore", "run.log", "b.py"]
print("ignore-list style:", [p for p in paths if not any(fnmatch.fnmatchcase(p, pat) for pat in ignore)])

# 16. html.escape / html.unescape
# ------------------------------------
# - Put user text into HTML? Escape the 5 special characters first or you invite
#   XSS (cross-site scripting): < > & " '
# - Escape at OUTPUT time, and only once (double-escaping shows "&amp;lt;").
print("\n# 16. html.escape / html.unescape")
user_input = '<script>alert("hi & bye")</script>'
safe = html.escape(user_input)
print("escaped   :", safe)
print("unescaped :", html.unescape(safe) == user_input)
print("quote=False leaves quotes:", html.escape('say "hi" & <go>', quote=False))
print("double escape gotcha     :", html.escape(html.escape("<b>")))
print("unescape handles entities:", html.unescape("&lt;p&gt; caf&eacute; &#169; &#x263A; &amp;"))
print("# Escaping is for HTML text/attributes only - not for SQL (use ?) or shells (use shlex.quote).")

# 17. re - where the regex lessons live
# ------------------------------------
# - Pattern matching, groups, substitution and flags are covered in depth in
#   05-Python Advanced/07-Regular-Expressions.py. Here we only USE a small regex
#   to tokenise words in the worked example below.
print("\n# 17. re - pointer")
print("quick word tokeniser:", re.findall(r"[a-z']+", "it's a dog-eat-dog world".lower()))

# 18. locale - regional number formatting (brief, guarded)
# ------------------------------------
# - locale formats numbers/currency/dates the way a REGION expects
#   (1,234,567.89 in the US, 1.234.567,89 in Germany, 12,34,567.89 in India).
# - setlocale() is PROCESS-WIDE and the locale must be installed on the OS, so:
#     * always wrap it in try/except locale.Error
#     * restore the old setting afterwards
#     * for simple thousands separators use format(n, ",") - no locale needed.
print("\n# 18. locale (brief)")
amount = 1234567.891
print("format(n, ',')    :", format(amount, ",.2f"), " <- locale independent, usually what you want")
print("underscore style  :", format(1234567, "_"))
saved = locale.setlocale(locale.LC_ALL)  # read the current setting
for name in ["en_US.UTF-8", "de_DE.UTF-8", "fr_FR.UTF-8"]:
    try:
        locale.setlocale(locale.LC_ALL, name)
    except locale.Error:
        print(f"{name:12} -> skipped: locale not installed on this machine")
        continue
    print(f"{name:12} ->", locale.format_string("%.2f", amount, grouping=True))
locale.setlocale(locale.LC_ALL, saved)  # restore
print("restored locale   :", locale.setlocale(locale.LC_ALL) == saved)

# 19. Worked example - word frequency, slugify, text report
# ------------------------------------
# - Combines: unicodedata (accent-safe, case-safe words), re (tokenise),
#   Counter (count), textwrap (wrap summary), format specs (aligned table).
print("\n# 19. Worked example - word frequency + slugify + report")
article = """
    Café culture: the café is a place to read, to write, and to wait.
    A good CAFÉ serves coffee; a great café serves conversation too.
    Read the menu, read the room, then write your own story.
"""

STOP_WORDS = {"a", "the", "is", "to", "and", "too", "your", "own", "then"}


def normalise(text):
    """Unicode-safe lowercase: compose, then casefold."""
    return unicodedata.normalize("NFC", text).casefold()


def tokenize(text):
    return re.findall(r"\w+(?:'\w+)?", normalise(text))  # \w is Unicode-aware, so café stays one word


def word_frequency(text, top=6):
    counts = Counter(w for w in tokenize(text) if w not in STOP_WORDS)
    # sort by count DESC, then alphabetically so the output is deterministic
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:top]


def slugify(title):
    """'Café Culture: A Guide!' -> 'cafe-culture-a-guide'"""
    ascii_only = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_only.lower())
    return slug.strip("-")


def text_report(text, width=44):
    words = tokenize(text)
    freq = word_frequency(text)
    lines = []
    lines.append("TEXT REPORT".center(width, "="))
    lines.append(f"{'words':<14}{len(words):>6}")
    lines.append(f"{'unique words':<14}{len(set(words)):>6}")
    lines.append(f"{'avg length':<14}{sum(map(len, words)) / len(words):>6.1f}")
    lines.append("-" * width)
    peak = freq[0][1]
    for word, n in freq:
        lines.append(f"{word:<12}{n:>3}  {'#' * n:<{peak}}")
    lines.append("-" * width)
    summary = " ".join(" ".join(text.split()).split()[:18]) + " ..."
    lines.append(textwrap.fill(summary, width, initial_indent="Preview: ", subsequent_indent="         "))
    return "\n".join(lines)


print(text_report(article))
for title in ["Café Culture: A Guide!", "  Hello,   World  ", "Straße 42 — 日本語", "Already-a-slug"]:
    print(f"slugify({title!r}) -> {slugify(title)!r}")
print("# Gotcha: slugify drops anything with no ASCII form ('ß', '日本語' vanish); real sites keep a fallback id.")

# 20. Which tool for which text job
# ------------------------------------
# - Job                                         -> Tool
# - Wrap text to a terminal width               -> textwrap.fill / wrap
# - Strip code indentation from """ blocks      -> textwrap.dedent
# - Quote / indent a block                      -> textwrap.indent
# - Preview long text with "..."                -> textwrap.shorten
# - Character sets (letters, digits, punct.)    -> string.ascii_letters, digits, punctuation
# - Fill a template from UNTRUSTED text         -> string.Template (safe_substitute)
# - Fill a template you wrote                   -> f-string / str.format
# - "Did you mean ...?" / fuzzy match           -> difflib.get_close_matches
# - Show what changed between two texts         -> difflib.unified_diff (or ndiff)
# - Print big nested data readably              -> pprint.pprint / pformat
# - Short repr of a huge container              -> reprlib.repr
# - Strings look equal but are not              -> unicodedata.normalize("NFC")
# - Case-insensitive compare                    -> str.casefold() (not lower)
# - Remove accents                              -> NFD + drop category "Mn"
# - Column width of CJK text                    -> unicodedata.east_asian_width
# - Parse "a command line with 'quotes'"        -> shlex.split
# - Insert text safely into a shell command     -> shlex.quote (better: subprocess list args)
# - Match names against *.py style patterns     -> fnmatch.fnmatchcase / filter
# - Match real files on disk                    -> glob (see 19-File-Utils-And-Archives.py)
# - Put text inside HTML                        -> html.escape
# - Search / extract / replace with patterns    -> re (05-Python Advanced/07-Regular-Expressions.py)
# - Numbers in the user's regional format       -> locale (or Babel for serious i18n)
# - Count words / items                         -> collections.Counter
print("\n# 20. Which tool for which text job - see the table in the comments above")
print("python", ".".join(map(str, sys.version_info[:3])), "- all modules used here are standard library")
