"""Exercise set 2: strings (parsing, checking, formatting, cleaning)."""


def count_vowels(s):
    """Level: easy
    Count the vowels (a, e, i, o, u) in s, ignoring case.
    Example: count_vowels("Hello World") -> 3, count_vowels("rhythm") -> 0
    Hint: s.lower() and a membership test against "aeiou".
    """
    return sum(ch in "aeiou" for ch in s.lower())


def is_palindrome(s):
    """Level: easy
    Return True if s reads the same both ways, ignoring case, spaces and punctuation.
    Only letters and digits count. An empty result counts as a palindrome.
    Example: is_palindrome("A man, a plan, a canal: Panama") -> True, is_palindrome("hello") -> False
    Hint: build a cleaned string with str.isalnum(), then compare to its reverse.
    """
    clean = [c.lower() for c in s if c.isalnum()]
    return clean == clean[::-1]


def is_anagram(a, b):
    """Level: easy
    Return True if a and b use exactly the same letters, ignoring case and spaces.
    Example: is_anagram("Listen", "Silent") -> True, is_anagram("abc", "abd") -> False
    Hint: compare sorted() of the cleaned strings.
    """
    def clean(s):
        return sorted(s.replace(" ", "").lower())
    return clean(a) == clean(b)


def capitalize_words(s):
    """Level: easy
    Capitalise the first letter of every word and make the rest lowercase.
    Extra spaces between words collapse to one, and the ends are trimmed.
    Example: capitalize_words("  hELLO   wORLD ") -> "Hello World"
    Hint: split() with no argument already handles any amount of whitespace.
    """
    return " ".join(w.capitalize() for w in s.split())


def snake_to_camel(name):
    """Level: easy
    Convert snake_case to camelCase. Ignore empty parts from extra underscores.
    Example: snake_to_camel("user_first_name") -> "userFirstName", snake_to_camel("__id__") -> "id"
    Hint: split on "_", drop empty parts, keep the first as is, capitalize the rest.
    """
    parts = [p for p in name.split("_") if p]
    if not parts:
        return ""
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def most_common_char(s):
    """Level: medium
    Return the most frequent character in s, ignoring spaces and case (return it
    lowercase). On a tie, return the one that appears first in s. Empty or all-space
    input returns None.
    Example: most_common_char("Hello World") -> "l", most_common_char("abba") -> "a"
    Hint: collections.Counter keeps first-seen order for ties via most_common().
    """
    from collections import Counter
    counts = Counter(s.replace(" ", "").lower())
    if not counts:
        return None
    return counts.most_common(1)[0][0]  # ties keep insertion order


def caesar(text, shift):
    """Level: medium
    Caesar cipher: move each letter `shift` places along the alphabet, wrapping around.
    Keep case. Leave non-letters unchanged. Negative shifts decrypt.
    Example: caesar("Abc xyz!", 3) -> "Def abc!", caesar("Def", -3) -> "Abc"
    Hint: use ord/chr with modulo 26 from the base letter ("a" or "A").
    """
    out = []
    for ch in text:
        if ch.isascii() and ch.isalpha():
            base = ord("a") if ch.islower() else ord("A")
            out.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            out.append(ch)
    return "".join(out)


def parse_key_values(text):
    """Level: medium
    Parse "key=value" pairs separated by ";" into a dict of strings. Strip spaces
    around keys and values. Skip empty pieces. Split only on the first "=", so a
    value may contain "=". Raise ValueError if a non-empty piece has no "=".
    Example: parse_key_values("a=1; b = 2;") -> {"a": "1", "b": "2"}
    Hint: piece.partition("=") returns (key, sep, value).
    """
    result = {}
    for piece in text.split(";"):
        if not piece.strip():
            continue
        key, sep, value = piece.partition("=")
        if not sep:
            raise ValueError(f"missing '=' in {piece!r}")
        result[key.strip()] = value.strip()
    return result


def format_receipt(items):
    """Level: medium
    Format (name, qty, price) tuples as a text receipt, one line per item, then a
    TOTAL line. Join lines with "\\n". Each item line is exactly
        f"{name:<10} {qty:>2} x {price:>7.2f} = {qty * price:>8.2f}"
    and the last line is f"{'TOTAL':<10}{total:>24.2f}".
    Example: format_receipt([("Tea", 2, 1.5)]) ->
        "Tea         2 x    1.50 =     3.00\\nTOTAL                         3.00"
    Hint: f-string format specs: < left align, > right align, .2f two decimals.
    """
    lines = [f"{name:<10} {qty:>2} x {price:>7.2f} = {qty * price:>8.2f}"
             for name, qty, price in items]
    total = sum(qty * price for _, qty, price in items)
    lines.append(f"{'TOTAL':<10}{total:>24.2f}")
    return "\n".join(lines)


def is_valid_email(s):
    """Level: medium
    Simple email check: no spaces, exactly one "@", a non-empty part before it,
    and a domain after it that contains a "." which is not the first or last
    character of the domain.
    Example: is_valid_email("ann@mail.com") -> True, is_valid_email("ann@mail") -> False
    Hint: split on "@" and check the pieces; this is not full RFC validation.
    """
    if " " in s or s.count("@") != 1:
        return False
    local, domain = s.split("@")
    return bool(local) and "." in domain and not domain.startswith(".") and not domain.endswith(".")


def compress_runs(s):
    """Level: medium
    Run-length encode: each run of the same character becomes the character plus
    the run length. A single character still gets a 1. Empty string -> "".
    Example: compress_runs("aaabcc") -> "a3b1c2"
    Hint: itertools.groupby, or loop remembering the previous character.
    """
    from itertools import groupby
    return "".join(f"{ch}{len(list(group))}" for ch, group in groupby(s))


def wrap_text(text, width):
    """Level: hard
    Split text into lines of at most `width` characters, breaking only between
    words (greedy: put as many words on a line as fit, single spaces between).
    A word longer than width goes alone on its own line. Return a list of lines.
    Example: wrap_text("the quick brown fox", 10) -> ["the quick", "brown fox"]
    Hint: keep a current line; if adding " " + word is too long, push it and start over.
    """
    lines = []
    current = ""
    for word in text.split():
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= width:
            current += " " + word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def longest_unique_substring(s):
    """Level: hard
    Return the longest substring of s with no repeated characters. On a tie return
    the first one. Empty string -> "".
    Example: longest_unique_substring("abcabcbb") -> "abc", longest_unique_substring("pwwkew") -> "wke"
    Hint: sliding window: remember the last index of each char and move the left edge past repeats.
    """
    last = {}
    start = best_start = best_len = 0
    for i, ch in enumerate(s):
        if ch in last and last[ch] >= start:
            start = last[ch] + 1
        last[ch] = i
        if i - start + 1 > best_len:
            best_start, best_len = start, i - start + 1
    return s[best_start:best_start + best_len]
