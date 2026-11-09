from checks import function


def test_adds_bonus():
    """with_bonus([70, 80], 5) returns [75, 85], and with_bonus([], 5) returns []."""
    with_bonus = function("with_bonus")
    assert with_bonus([70, 80], 5) == [75, 85], (
        f"with_bonus([70, 80], 5) returned {with_bonus([70, 80], 5)!r}"
    )
    assert with_bonus([], 5) == [], f"with_bonus([], 5) returned {with_bonus([], 5)!r}"


def test_original_untouched():
    """The list passed in is unchanged, and the result is a different list."""
    with_bonus = function("with_bonus")
    scores = [70, 80]
    result = with_bonus(scores, 5)
    assert scores == [70, 80], f"the original list became {scores!r}"
    assert result is not scores, "with_bonus should return a new list, not the one passed in"
