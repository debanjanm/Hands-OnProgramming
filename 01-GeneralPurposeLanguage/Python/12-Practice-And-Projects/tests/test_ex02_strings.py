import pytest


@pytest.fixture(scope="module")
def ex(load):
    return load("ex02_strings")


def test_count_vowels(ex):
    assert ex.count_vowels("Hello World") == 3
    assert ex.count_vowels("rhythm") == 0
    assert ex.count_vowels("") == 0
    assert ex.count_vowels("AEIOU") == 5


def test_is_palindrome(ex):
    assert ex.is_palindrome("A man, a plan, a canal: Panama") is True
    assert ex.is_palindrome("hello") is False
    assert ex.is_palindrome("") is True
    assert ex.is_palindrome("12321") is True


def test_is_anagram(ex):
    assert ex.is_anagram("Listen", "Silent") is True
    assert ex.is_anagram("abc", "abd") is False
    assert ex.is_anagram("dormitory", "dirty room") is True
    assert ex.is_anagram("aab", "ab") is False


def test_capitalize_words(ex):
    assert ex.capitalize_words("  hELLO   wORLD ") == "Hello World"
    assert ex.capitalize_words("") == ""
    assert ex.capitalize_words("python") == "Python"


def test_snake_to_camel(ex):
    assert ex.snake_to_camel("user_first_name") == "userFirstName"
    assert ex.snake_to_camel("__id__") == "id"
    assert ex.snake_to_camel("name") == "name"
    assert ex.snake_to_camel("") == ""


def test_most_common_char(ex):
    assert ex.most_common_char("Hello World") == "l"
    assert ex.most_common_char("abba") == "a"  # tie: first seen wins
    assert ex.most_common_char("   ") is None
    assert ex.most_common_char("") is None
    assert ex.most_common_char("AaB") == "a"


def test_caesar_encrypt(ex):
    assert ex.caesar("Abc xyz!", 3) == "Def abc!"
    assert ex.caesar("Hello, World", 0) == "Hello, World"
    assert ex.caesar("abc", 26) == "abc"


def test_caesar_round_trip_and_negative(ex):
    assert ex.caesar("Def", -3) == "Abc"
    msg = "Attack at Dawn, 5 o'clock!"
    assert ex.caesar(ex.caesar(msg, 7), -7) == msg
    assert ex.caesar("abc", -1) == "zab"


def test_parse_key_values(ex):
    assert ex.parse_key_values("a=1; b = 2;") == {"a": "1", "b": "2"}
    assert ex.parse_key_values("") == {}
    assert ex.parse_key_values("url=x=y") == {"url": "x=y"}
    assert ex.parse_key_values("k=;") == {"k": ""}


def test_parse_key_values_missing_equals(ex):
    with pytest.raises(ValueError):
        ex.parse_key_values("a=1; oops")


def test_format_receipt(ex):
    out = ex.format_receipt([("Tea", 2, 1.5)])
    assert out == "Tea         2 x    1.50 =     3.00\n" + "TOTAL" + "3.00".rjust(29)


def test_format_receipt_many_and_empty(ex):
    out = ex.format_receipt([("Apple", 3, 0.5), ("Bread", 1, 2.25)]).split("\n")
    assert len(out) == 3
    assert out[0] == "Apple       3 x    0.50 =     1.50"
    assert out[-1].startswith("TOTAL") and out[-1].endswith("3.75")
    assert ex.format_receipt([]) == "TOTAL" + "0.00".rjust(29)


@pytest.mark.parametrize("email", ["ann@mail.com", "a.b@x.co.uk"])
def test_valid_emails(ex, email):
    assert ex.is_valid_email(email) is True


@pytest.mark.parametrize("email", [
    "ann@mail", "@mail.com", "ann@@mail.com", "ann mail@x.com",
    "ann@.com", "ann@mail.", "annmail.com", ""])
def test_invalid_emails(ex, email):
    assert ex.is_valid_email(email) is False


def test_compress_runs(ex):
    assert ex.compress_runs("aaabcc") == "a3b1c2"
    assert ex.compress_runs("") == ""
    assert ex.compress_runs("z") == "z1"
    assert ex.compress_runs("aabbaa") == "a2b2a2"


def test_wrap_text(ex):
    assert ex.wrap_text("the quick brown fox", 10) == ["the quick", "brown fox"]
    assert ex.wrap_text("", 10) == []
    assert ex.wrap_text("extraordinary day", 5) == ["extraordinary", "day"]
    assert ex.wrap_text("a b c d", 3) == ["a b", "c d"]
    assert all(len(line) <= 12 for line in ex.wrap_text("one two three four five six seven", 12))


def test_longest_unique_substring(ex):
    assert ex.longest_unique_substring("abcabcbb") == "abc"
    assert ex.longest_unique_substring("pwwkew") == "wke"
    assert ex.longest_unique_substring("") == ""
    assert ex.longest_unique_substring("bbbb") == "b"
    assert ex.longest_unique_substring("abba") == "ab"
