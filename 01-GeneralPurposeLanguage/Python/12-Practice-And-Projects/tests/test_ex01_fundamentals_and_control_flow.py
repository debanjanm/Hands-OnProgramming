import pytest


@pytest.fixture(scope="module")
def ex(load):
    return load("ex01_fundamentals_and_control_flow")


def test_fizzbuzz_small(ex):
    assert ex.fizzbuzz(5) == ["1", "2", "Fizz", "4", "Buzz"]


def test_fizzbuzz_fifteen_and_zero(ex):
    assert ex.fizzbuzz(15)[-1] == "FizzBuzz"
    assert ex.fizzbuzz(0) == []
    assert ex.fizzbuzz(1) == ["1"]


def test_sum_of_digits(ex):
    assert ex.sum_of_digits(1234) == 10
    assert ex.sum_of_digits(0) == 0
    assert ex.sum_of_digits(-45) == 9
    assert ex.sum_of_digits(1000) == 1


def test_leap_year(ex):
    assert ex.is_leap_year(2024) is True
    assert ex.is_leap_year(2023) is False
    assert ex.is_leap_year(1900) is False
    assert ex.is_leap_year(2000) is True


def test_grade_boundaries(ex):
    assert ex.grade(100) == "A"
    assert ex.grade(90) == "A"
    assert ex.grade(89.9) == "B"
    assert ex.grade(70) == "C"
    assert ex.grade(60) == "D"
    assert ex.grade(59.9) == "F"
    assert ex.grade(0) == "F"


@pytest.mark.parametrize("bad", [-1, 100.5, 101])
def test_grade_rejects_out_of_range(ex, bad):
    with pytest.raises(ValueError):
        ex.grade(bad)


def test_is_prime(ex):
    assert [n for n in range(15) if ex.is_prime(n)] == [2, 3, 5, 7, 11, 13]
    assert ex.is_prime(97) is True
    assert ex.is_prime(91) is False  # 7 * 13
    assert ex.is_prime(-7) is False


def test_primes_up_to(ex):
    assert ex.primes_up_to(20) == [2, 3, 5, 7, 11, 13, 17, 19]
    assert ex.primes_up_to(2) == [2]
    assert ex.primes_up_to(1) == []
    assert len(ex.primes_up_to(100)) == 25


def test_reverse_number(ex):
    assert ex.reverse_number(123) == 321
    assert ex.reverse_number(-120) == -21
    assert ex.reverse_number(0) == 0
    assert ex.reverse_number(1000) == 1


def test_gcd_lcm(ex):
    assert ex.gcd_lcm(12, 18) == (6, 36)
    assert ex.gcd_lcm(7, 13) == (1, 91)
    assert ex.gcd_lcm(5, 5) == (5, 5)
    assert ex.gcd_lcm(1, 9) == (1, 9)


def test_collatz_steps(ex):
    assert ex.collatz_steps(1) == 0
    assert ex.collatz_steps(6) == 8
    assert ex.collatz_steps(27) == 111


@pytest.mark.parametrize("bad", [0, -5])
def test_collatz_rejects_non_positive(ex, bad):
    with pytest.raises(ValueError):
        ex.collatz_steps(bad)


def test_armstrong(ex):
    assert [n for n in range(1, 1000) if ex.is_armstrong(n)] == [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 153, 370, 371, 407]
    assert ex.is_armstrong(0) is True
    assert ex.is_armstrong(154) is False
    assert ex.is_armstrong(-153) is False


def test_pyramid(ex):
    assert ex.pyramid(1) == "*"
    assert ex.pyramid(3) == "  *\n ***\n*****"
    assert ex.pyramid(0) == ""
    assert ex.pyramid(4).split("\n")[-1] == "*" * 7


def test_to_base(ex):
    assert ex.to_base(255, 16) == "ff"
    assert ex.to_base(5, 2) == "101"
    assert ex.to_base(0, 8) == "0"
    assert ex.to_base(1000, 10) == "1000"
    assert ex.to_base(35, 16) == "23"


@pytest.mark.parametrize("n,base", [(5, 1), (5, 17), (-1, 2)])
def test_to_base_rejects_bad_input(ex, n, base):
    with pytest.raises(ValueError):
        ex.to_base(n, base)
