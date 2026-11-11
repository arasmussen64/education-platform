"""Works out a short sum written in content, like "max(8, a) + 3 * b",
without running it as Python (ADR-0024).

An estimate question's working is text in a content file. Python's eval()
would run whatever that text says, so instead the text is parsed into a tree
(Python's own `ast` module reads it), and only the few shapes of plain
arithmetic are worked out. Anything else is refused, with a message that
says what is allowed.

Numbers are exact fractions, so the sums come out as they would on paper:
0.1 + 0.2 is 0.3, and ceil(0.07 * 100) is 7. With ordinary floating-point
numbers they would be 0.30000000000000004 and 8.
"""

from __future__ import annotations

import ast
import keyword
import math
from collections.abc import Callable, Mapping
from fractions import Fraction


class NotArithmetic(ValueError):
    """The text isn't a sum this module can work out."""


# Anything bigger than this as a power or a rounding place is a typo, and
# 10 ** 100000000 would take a very long time to work out exactly.
LARGEST_EXPONENT = 100

# The most binary digits a number in a sum may have, on top or underneath:
# about 300 decimal digits, far more than any estimate needs. Every part of a
# sum is held to it, because a power of a power, ((10 ** 100) ** 100) ** 100
# and so on, would otherwise grow too big to work out or even to print, and
# the validator would hang.
LARGEST_BITS = 1000

ALLOWED = (
    "numbers, the given names, + - * / // % **, brackets, "
    "and min, max, round, ceil, floor, abs"
)


def exact(number: int | float) -> Fraction:
    """A number from a YAML file as an exact fraction: 0.1 is one tenth, not
    the binary number closest to it. repr() gives the shortest decimal that
    reads back as the same float, which is the decimal the author wrote."""
    if isinstance(number, bool):
        raise NotArithmetic(f"{number!r} isn't a number")
    if isinstance(number, int):
        return Fraction(number)
    return Fraction(repr(number))


def round_half_up(value: Fraction, places: int = 0) -> Fraction:
    """Rounds the way it's taught at school: a half goes away from zero, so
    2.5 becomes 3 and -2.5 becomes -3. (Python's own round() sends a half to
    the even number, so it gives 2, which a learner wouldn't expect.)"""
    scale = Fraction(10) ** places
    rounded = Fraction(math.floor(abs(value) * scale + Fraction(1, 2))) / scale
    return -rounded if value < 0 else rounded


def whole(value: Fraction, what: str) -> int:
    """The value as an int, for a power or a rounding place."""
    if value.denominator != 1 or abs(value) > LARGEST_EXPONENT:
        raise NotArithmetic(
            f"{what} must be a whole number from -{LARGEST_EXPONENT} to "
            f"{LARGEST_EXPONENT}, not {show(value)}"
        )
    return int(value)


def power(base: Fraction, exponent: Fraction) -> Fraction:
    """base ** exponent, exactly when the exponent is a whole number. A square
    root (** 0.5) can't be an exact fraction, so it's worked out as a float."""
    if exponent.denominator == 1:
        return base ** whole(exponent, "a power")
    if base < 0:
        raise NotArithmetic("a negative number to a fractional power isn't real")
    return Fraction(float(base) ** float(exponent))


def round_to_places(value: Fraction, places: Fraction = Fraction(0)) -> Fraction:
    return round_half_up(value, whole(places, "round's number of places"))


def ceiling(value: Fraction) -> Fraction:
    return Fraction(math.ceil(value))


def flooring(value: Fraction) -> Fraction:
    return Fraction(math.floor(value))


def smallest(*values: Fraction) -> Fraction:
    return min(values)


def largest(*values: Fraction) -> Fraction:
    return max(values)


def absolute(value: Fraction) -> Fraction:
    return abs(value)


# Each function the working may call, with how many numbers it takes.
FUNCTIONS: dict[str, tuple[Callable[..., Fraction], range]] = {
    "min": (smallest, range(2, 100)),
    "max": (largest, range(2, 100)),
    "round": (round_to_places, range(1, 3)),
    "ceil": (ceiling, range(1, 2)),
    "floor": (flooring, range(1, 2)),
    "abs": (absolute, range(1, 2)),
}

# Words Python keeps for itself (in, if, and, for...). A given named one of
# them can't be read in a sum: "vcpus * in" isn't arithmetic to the parser.
RESERVED_WORDS = frozenset(keyword.kwlist)

BINARY: dict[type[ast.operator], Callable[[Fraction, Fraction], Fraction]] = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.FloorDiv: lambda a, b: Fraction(a // b),
    ast.Mod: lambda a, b: a % b,
    ast.Pow: power,
}


def evaluate(text: str, names: Mapping[str, Fraction]) -> Fraction:
    """Works out `text`, a sum over `names`. Raises NotArithmetic, with a
    message for the author, if it isn't one."""
    try:
        tree = ast.parse(text.strip(), mode="eval")
        return value_of(tree.body, names)
    except SyntaxError as exc:
        raise NotArithmetic(f"isn't a sum that can be read ({exc.msg})") from exc
    except RecursionError as exc:
        # Thousands of terms, or brackets inside brackets: never a real sum.
        raise NotArithmetic("is nested too deeply to work out") from exc
    except ZeroDivisionError as exc:
        raise NotArithmetic("divides by zero") from exc
    except OverflowError as exc:
        raise NotArithmetic("gives a number too big to work out") from exc


def value_of(node: ast.expr, names: Mapping[str, Fraction]) -> Fraction:
    """The value of one part of the parsed sum, held to LARGEST_BITS, so the
    next step never starts on a number too big to work out."""
    value = part_value(node, names)
    if bits_in(value) > LARGEST_BITS:
        raise NotArithmetic("gives a number too big to work out")
    return value


def bits_in(value: Fraction) -> int:
    """How many binary digits a number takes, on top or underneath."""
    return max(abs(value.numerator).bit_length(), value.denominator.bit_length())


def part_value(node: ast.expr, names: Mapping[str, Fraction]) -> Fraction:
    """The value of one part of the parsed sum, working down the tree."""
    match node:
        case ast.Constant(value=bool()):
            pass  # True and False are numbers to Python, but not in a sum.
        case ast.Constant(value=int() | float() as number):
            return exact(number)
        case ast.Name(id=name):
            if name in names:
                return names[name]
            raise NotArithmetic(f"uses {name!r}, which isn't one of the given numbers")
        case ast.UnaryOp(op=ast.USub(), operand=operand):
            return -value_of(operand, names)
        case ast.UnaryOp(op=ast.UAdd(), operand=operand):
            return value_of(operand, names)
        case ast.BinOp(left=left, op=op, right=right) if type(op) in BINARY:
            return BINARY[type(op)](value_of(left, names), value_of(right, names))
        case ast.Call(func=ast.Name(id=name), args=args, keywords=[]) if (
            name in FUNCTIONS
        ):
            function, counts = FUNCTIONS[name]
            if len(args) not in counts:
                raise NotArithmetic(
                    f"{name}() can't take {len(args)} "
                    f"number{'' if len(args) == 1 else 's'}"
                )
            return function(*(value_of(arg, names) for arg in args))
    raise NotArithmetic(f"can't use {ast.unparse(node)!r}: only {ALLOWED}")


def show(value: Fraction) -> str:
    """A value as a person would write it: 28, 27.5, 0.3333333333."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{float(value):.10g}"
