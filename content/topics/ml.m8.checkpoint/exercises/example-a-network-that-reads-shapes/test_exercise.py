from checks import run


def test_the_walkthrough():
    """Prints the data, the check, the accuracy, the double evaluation and the reading."""
    assert run() == '(240, 10, 10) (80, 10, 10) [20, 20, 20, 20]\ngradient check: passes\nloss 1.24 -> 0.02 | held-out accuracy 0.99 | at least 0.9: True | 448 parameters\nevaluating twice gives the same answer: True\nthe first held-out image of each shape reads: bar post cross box\n'
