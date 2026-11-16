"""Exercise set 1: fundamentals and control flow (numbers, conditionals, loops)."""


def fizzbuzz(n):
    """Level: easy
    Return a list of strings for 1..n. Multiples of 3 -> "Fizz", of 5 -> "Buzz",
    of both -> "FizzBuzz", otherwise the number as a string.
    Example: fizzbuzz(5) -> ["1", "2", "Fizz", "4", "Buzz"]
    Hint: check the "both" case (15) first.
    """
    raise NotImplementedError


def sum_of_digits(n):
    """Level: easy
    Return the sum of the digits of an integer. Ignore the sign.
    Example: sum_of_digits(1234) -> 10, sum_of_digits(-45) -> 9
    Hint: use abs() and divmod(n, 10), or loop over str(abs(n)).
    """
    raise NotImplementedError


def is_leap_year(year):
    """Level: easy
    Return True if year is a leap year: divisible by 4, except century years,
    which must be divisible by 400.
    Example: is_leap_year(2024) -> True, is_leap_year(1900) -> False, is_leap_year(2000) -> True
    Hint: one boolean expression with and / or is enough.
    """
    raise NotImplementedError


def grade(score):
    """Level: easy
    Turn a score (0..100) into a letter: 90+ "A", 80+ "B", 70+ "C", 60+ "D", else "F".
    Raise ValueError if the score is below 0 or above 100.
    Example: grade(85) -> "B", grade(59.9) -> "F"
    Hint: validate first, then an if / elif chain from the highest limit down.
    """
    raise NotImplementedError


def is_prime(n):
    """Level: medium
    Return True if n is a prime number. Numbers below 2 are not prime.
    Example: is_prime(13) -> True, is_prime(15) -> False, is_prime(1) -> False
    Hint: you only need to test divisors up to the square root of n.
    """
    raise NotImplementedError


def primes_up_to(n):
    """Level: medium
    Return a list of all primes <= n, in increasing order.
    Example: primes_up_to(20) -> [2, 3, 5, 7, 11, 13, 17, 19]
    Hint: the Sieve of Eratosthenes (cross out multiples), or reuse is_prime logic.
    """
    raise NotImplementedError


def reverse_number(n):
    """Level: medium
    Reverse the digits of an integer and keep the sign. Do it with math or str, your choice.
    Example: reverse_number(123) -> 321, reverse_number(-120) -> -21, reverse_number(0) -> 0
    Hint: remember int("021") is 21, so trailing zeros vanish naturally.
    """
    raise NotImplementedError


def gcd_lcm(a, b):
    """Level: medium
    Return (gcd, lcm) of two positive integers without using math.gcd.
    Example: gcd_lcm(12, 18) -> (6, 36)
    Hint: Euclid: while b: a, b = b, a % b. Then lcm = a * b // gcd.
    """
    raise NotImplementedError


def collatz_steps(n):
    """Level: medium
    Count the steps for n to reach 1: if even do n // 2, if odd do 3n + 1.
    Raise ValueError if n < 1.
    Example: collatz_steps(6) -> 8 (6,3,10,5,16,8,4,2,1), collatz_steps(1) -> 0
    Hint: a while loop with a counter.
    """
    raise NotImplementedError


def is_armstrong(n):
    """Level: medium
    Return True if n equals the sum of its digits, each raised to the power of
    the number of digits. Negative numbers are not Armstrong numbers.
    Example: is_armstrong(153) -> True (1 + 125 + 27), is_armstrong(154) -> False
    Hint: digits = str(n); power = len(digits).
    """
    raise NotImplementedError


def pyramid(n):
    """Level: hard
    Return a centered star pyramid with n rows as a single string, rows joined by
    "\\n" (no trailing newline). Row i (1-based) has 2*i - 1 stars, padded with
    spaces on the left only. n <= 0 gives "".
    Example: pyramid(3) -> "  *\\n ***\\n*****"
    Hint: row = " " * (n - i) + "*" * (2 * i - 1).
    """
    raise NotImplementedError


def to_base(n, base):
    """Level: hard
    Convert a non-negative integer n to a string in the given base (2..16),
    using digits 0-9 then lowercase a-f. Do not use bin/hex/format.
    Raise ValueError for a base outside 2..16 or a negative n.
    Example: to_base(255, 16) -> "ff", to_base(5, 2) -> "101", to_base(0, 8) -> "0"
    Hint: repeatedly divmod(n, base) and collect remainders, then reverse.
    """
    raise NotImplementedError
