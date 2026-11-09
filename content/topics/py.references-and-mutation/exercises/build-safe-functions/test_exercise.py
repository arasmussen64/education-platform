from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_add_bonus():
    """add_bonus([70, 55, 90], 5) is [75, 60, 95]; the list given is unchanged and the result is new."""
    add_bonus = function("add_bonus")
    scores = [70, 55, 90]
    result = add_bonus(scores, 5)
    assert result == [75, 60, 95]
    assert scores == [70, 55, 90]
    assert result is not scores


def test_without_lowest():
    """without_lowest drops the first occurrence of the smallest, keeps the order, and changes nothing."""
    without_lowest = function("without_lowest")
    scores = [70, 55, 90]
    assert without_lowest(scores) == [70, 90]
    assert scores == [70, 55, 90]
    assert without_lowest([5, 9, 5]) == [9, 5]
    assert without_lowest([3]) == []


def test_program():
    """Running the program prints the three lines, the last showing the original intact."""
    assert run() == "With bonus: [75, 60, 95]\nWithout lowest: [70, 90]\nOriginal: [70, 55, 90]\n"
