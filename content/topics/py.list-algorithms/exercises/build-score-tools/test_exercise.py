from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

SCORES = [72, 45, 88, 91, 60]


def test_passing():
    """passing keeps the scores at or above the cutoff, in order; the cutoff itself passes."""
    passing = function("passing")
    assert passing(SCORES, 60) == [72, 88, 91, 60]
    assert passing(SCORES, 100) == []
    assert passing([], 50) == []


def test_position_of():
    """position_of finds the first match, and gives -1 when there is none."""
    position_of = function("position_of")
    assert position_of(SCORES, 88) == 2
    assert position_of(["a", "b", "a"], "a") == 0
    assert position_of(SCORES, 7) == -1


def test_top_three():
    """top_three gives the three highest, highest first, or fewer for a short list."""
    top_three = function("top_three")
    assert top_three(SCORES) == [91, 88, 72]
    assert top_three([5, 9]) == [9, 5]
    assert top_three([]) == []


def test_lists_unchanged():
    """None of the functions changes the list it's given."""
    scores = [72, 45, 88, 91, 60]
    function("passing")(scores, 60)
    function("position_of")(scores, 88)
    function("top_three")(scores)
    assert scores == [72, 45, 88, 91, 60]


def test_program():
    """Running the program prints the three lines for the example scores."""
    assert run() == "Passing: [72, 88, 91, 60]\nPosition of 88: 2\nTop three: [91, 88, 72]\n"
