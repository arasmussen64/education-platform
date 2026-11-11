"""The working of an estimate is worked out exactly, and nothing but
arithmetic is ever run (ADR-0024)."""

from fractions import Fraction

import pytest
from arithmetic import NotArithmetic, evaluate, exact, round_half_up, show

NAMES = {"a": Fraction(2), "b": Fraction(8), "c": Fraction(12)}


def value(text: str) -> Fraction:
    return evaluate(text, NAMES)


def test_sums_over_the_given_names() -> None:
    assert value("max(8, a) + max(8, b) + max(8, c)") == 28
    assert value("a + b + c") == 22
    assert value("-(a - b) * 2 / 4") == 3
    assert value("+a") == 2


def test_every_operator_and_function() -> None:
    assert value("7 // 2") == 3
    assert value("7 % 4") == 3
    assert value("2 ** 10") == 1024
    assert value("2 ** -1") == Fraction(1, 2)
    assert value("min(a, b, c)") == 2
    assert value("abs(a - c)") == 10
    assert value("ceil(c / 5)") == 3
    assert value("floor(c / 5)") == 2
    assert value("round(c / 7, 2)") == Fraction("1.71")


def test_decimals_are_exact_as_on_paper() -> None:
    # With floats these are 0.30000000000000004 and 8.
    assert value("0.1 + 0.2") == Fraction(3, 10)
    assert value("ceil(0.07 * 100)") == 7
    assert exact(0.0416) == Fraction(416, 10000)
    assert exact(28) == 28


def test_halves_round_away_from_zero_as_taught_at_school() -> None:
    assert value("round(2.5)") == 3
    assert value("round(-2.5)") == -3
    assert value("round(0.125, 2)") == Fraction("0.13")
    assert round_half_up(Fraction(1234), -2) == 1200


def test_a_fractional_power_is_worked_out_as_a_float() -> None:
    assert value("16 ** 0.5") == 4


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("a +", "isn't a sum that can be read"),
        ("d * 2", "uses 'd', which isn't one of the given numbers"),
        ("__import__('os')", "can't use \"__import__('os')\""),
        ("a.real", "can't use 'a.real'"),
        ("'12'", "can't use \"'12'\""),
        ("True + 1", "can't use 'True'"),
        ("a if b else c", "can't use 'a if b else c'"),
        ("(lambda: 1)()", "can't use '(lambda: 1)()'"),
        ("[a, b]", "can't use '[a, b]'"),
        ("max(a)", "max() can't take 1 number"),
        ("ceil(a, b)", "ceil() can't take 2 numbers"),
        ("round(a, ndigits=1)", "can't use 'round(a, ndigits=1)'"),
        ("a / (b - 8)", "divides by zero"),
        ("2 ** 1000", "a power must be a whole number from -100 to 100, not 1000"),
        ("round(a, 0.5)", "round's number of places must be a whole number"),
        ("(-8) ** 0.5", "a negative number to a fractional power isn't real"),
        ("10 ** 400.5", "gives a number too big to work out"),
    ],
)
def test_anything_but_arithmetic_is_refused(text: str, message: str) -> None:
    with pytest.raises(NotArithmetic) as caught:
        value(text)
    assert message in str(caught.value)


def test_values_are_shown_as_a_person_writes_them() -> None:
    assert show(Fraction(28)) == "28"
    assert show(Fraction("27.5")) == "27.5"
    assert show(Fraction(1, 3)) == "0.3333333333"
