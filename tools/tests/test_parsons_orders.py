"""Which other arrangements of a Parsons item's lines get tried, and how each
is described in the validator's message."""

from math import factorial

from parsons_orders import arrangements, decoy_swaps, other_orders

FOUR = ["a = 1", "b = 2", "c = a + b", "print(c)"]


def described(lines: list[str]) -> dict[tuple[str, ...], str]:
    return {each.lines: each.description for each in other_orders(lines)}


def test_every_other_order_of_a_short_item_is_tried() -> None:
    orders = other_orders(FOUR)
    assert len(orders) == factorial(4) - 1
    assert len({each.lines for each in orders}) == len(orders)
    assert tuple(FOUR) not in {each.lines for each in orders}

    seven = [f"line_{n} = {n}" for n in range(7)]
    assert len(other_orders(seven)) == factorial(7) - 1


def test_a_long_item_gets_swaps_and_moves_only() -> None:
    eight = [f"line_{n} = {n}" for n in range(8)]
    orders = other_orders(eight)
    # Far fewer than the 40,319 other orders of 8 lines.
    assert len(orders) == 105
    assert all(
        "can swap places" in each.description or "can go" in each.description
        for each in orders
    )


def test_a_swap_names_both_lines() -> None:
    assert described(FOUR)[("b = 2", "a = 1", "c = a + b", "print(c)")] == (
        "lines 1 and 2 can swap places ('a = 1' and 'b = 2')"
    )
    assert described(FOUR)[("print(c)", "b = 2", "c = a + b", "a = 1")] == (
        "lines 1 and 4 can swap places ('a = 1' and 'print(c)')"
    )


def test_a_move_says_where_the_line_can_go() -> None:
    orders = described(FOUR)
    assert orders[("b = 2", "c = a + b", "a = 1", "print(c)")] == (
        "line 1 ('a = 1') can go before line 4"
    )
    assert orders[("b = 2", "c = a + b", "print(c)", "a = 1")] == (
        "line 1 ('a = 1') can go last"
    )
    assert orders[("c = a + b", "print(c)", "a = 1", "b = 2")] == (
        "lines 1 to 2 can go last"
    )


def test_an_order_that_is_neither_is_listed_by_number() -> None:
    assert described(FOUR)[("b = 2", "a = 1", "print(c)", "c = a + b")] == (
        "the lines can go in the order 2, 1, 4, 3"
    )


def test_lines_are_shown_without_their_indentation() -> None:
    lines = ["for n in range(2):", "    print(n)", "    print('next')"]
    swapped = ("for n in range(2):", "    print('next')", "    print(n)")
    assert described(lines)[swapped] == (
        "lines 2 and 3 can swap places ('print(n)' and \"print('next')\")"
    )


def test_each_decoy_is_tried_in_place_of_each_line() -> None:
    swaps = decoy_swaps(FOUR, ["print(a)", "c = a - b"])
    assert len(swaps) == 2 * 4
    assert all(each.uses_decoy for each in swaps)
    assert swaps[3].lines == ("a = 1", "b = 2", "c = a + b", "print(a)")
    assert swaps[3].description == (
        "the decoy 'print(a)' can take the place of line 4 ('print(c)')"
    )


def test_a_program_is_its_lines_with_a_newline_after_each() -> None:
    everything = arrangements(FOUR, ["print(a)"])
    assert len(everything) == factorial(4) - 1 + 4
    assert everything[0].program == "b = 2\na = 1\nc = a + b\nprint(c)\n"
