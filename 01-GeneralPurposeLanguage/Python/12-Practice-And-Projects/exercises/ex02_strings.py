"""Exercise set 2: strings (parsing, checking, formatting, cleaning)."""


def count_vowels(s):
    """Level: easy
    Count the vowels (a, e, i, o, u) in s, ignoring case.
    Example: count_vowels("Hello World") -> 3, count_vowels("rhythm") -> 0
    Hint: s.lower() and a membership test against "aeiou".
    """
    raise NotImplementedError


def is_palindrome(s):
    """Level: easy
    Return True if s reads the same both ways, ignoring case, spaces and punctuation.
    Only letters and digits count. An empty result counts as a palindrome.
    Example: is_palindrome("A man, a plan, a canal: Panama") -> True, is_palindrome("hello") -> False
    Hint: build a cleaned string with str.isalnum(), then compare to its reverse.
    """
    raise NotImplementedError


def is_anagram(a, b):
    """Level: easy
    Return True if a and b use exactly the same letters, ignoring case and spaces.
    Example: is_anagram("Listen", "Silent") -> True, is_anagram("abc", "abd") -> False
    Hint: compare sorted() of the cleaned strings.
    """
    raise NotImplementedError


def capitalize_words(s):
    """Level: easy
    Capitalise the first letter of every word and make the rest lowercase.
    Extra spaces between words collapse to one, and the ends are trimmed.
    Example: capitalize_words("  hELLO   wORLD ") -> "Hello World"
    Hint: split() with no argument already handles any amount of whitespace.
    """
    raise NotImplementedError


def snake_to_camel(name):
    """Level: easy
    Convert snake_case to camelCase. Ignore empty parts from extra underscores.
    Example: snake_to_camel("user_first_name") -> "userFirstName", snake_to_camel("__id__") -> "id"
    Hint: split on "_", drop empty parts, keep the first as is, capitalize the rest.
    """
    raise NotImplementedError


def most_common_char(s):
    """Level: medium
    Return the most frequent character in s, ignoring spaces and case (return it
    lowercase). On a tie, return the one that appears first in s. Empty or all-space
    input returns None.
    Example: most_common_char("Hello World") -> "l", most_common_char("abba") -> "a"
    Hint: collections.Counter keeps first-seen order for ties via most_common().
    """
    raise NotImplementedError


def caesar(text, shift):
    """Level: medium
    Caesar cipher: move each letter `shift` places along the alphabet, wrapping around.
    Keep case. Leave non-letters unchanged. Negative shifts decrypt.
    Example: caesar("Abc xyz!", 3) -> "Def abc!", caesar("Def", -3) -> "Abc"
    Hint: use ord/chr with modulo 26 from the base letter ("a" or "A").
    """
    raise NotImplementedError


def parse_key_values(text):
    """Level: medium
    Parse "key=value" pairs separated by ";" into a dict of strings. Strip spaces
    around keys and values. Skip empty pieces. Split only on the first "=", so a
    value may contain "=". Raise ValueError if a non-empty piece has no "=".
    Example: parse_key_values("a=1; b = 2;") -> {"a": "1", "b": "2"}
    Hint: piece.partition("=") returns (key, sep, value).
    """
    raise NotImplementedError


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
    raise NotImplementedError


def is_valid_email(s):
    """Level: medium
    Simple email check: no spaces, exactly one "@", a non-empty part before it,
    and a domain after it that contains a "." which is not the first or last
    character of the domain.
    Example: is_valid_email("ann@mail.com") -> True, is_valid_email("ann@mail") -> False
    Hint: split on "@" and check the pieces; this is not full RFC validation.
    """
    raise NotImplementedError


def compress_runs(s):
    """Level: medium
    Run-length encode: each run of the same character becomes the character plus
    the run length. A single character still gets a 1. Empty string -> "".
    Example: compress_runs("aaabcc") -> "a3b1c2"
    Hint: itertools.groupby, or loop remembering the previous character.
    """
    raise NotImplementedError


def wrap_text(text, width):
    """Level: hard
    Split text into lines of at most `width` characters, breaking only between
    words (greedy: put as many words on a line as fit, single spaces between).
    A word longer than width goes alone on its own line. Return a list of lines.
    Example: wrap_text("the quick brown fox", 10) -> ["the quick", "brown fox"]
    Hint: keep a current line; if adding " " + word is too long, push it and start over.
    """
    raise NotImplementedError


def longest_unique_substring(s):
    """Level: hard
    Return the longest substring of s with no repeated characters. On a tie return
    the first one. Empty string -> "".
    Example: longest_unique_substring("abcabcbb") -> "abc", longest_unique_substring("pwwkew") -> "wke"
    Hint: sliding window: remember the last index of each char and move the left edge past repeats.
    """
    raise NotImplementedError
