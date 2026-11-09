from checks import run, run_with


def test_three_scores():
    """The shared list shows 100 through both names; the copy shows 0; is tells them apart."""
    assert run() == "[70, 80, 90, 100]\n[70, 80, 90, 100]\n[70, 80, 90, 0]\nTrue\nFalse\n"


def test_one_score():
    """The same holds for a one-item list."""
    assert run_with({"scores": [1]}) == "[1, 100]\n[1, 100]\n[1, 0]\nTrue\nFalse\n"
