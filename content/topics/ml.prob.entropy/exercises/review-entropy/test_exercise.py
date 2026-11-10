from checks import function, run


def test_the_output():
    """Prints the four entropies."""
    assert run() == '1.0 0.469 2.0 0.0\n'


def test_other_distributions():
    """[0.5, 0.25, 0.25] is 1.5 bits and a fair die is 2.585."""
    entropy = function("entropy")
    assert entropy([0.5, 0.25, 0.25]) == 1.5
    assert abs(entropy([1 / 6] * 6) - 2.585) < 0.001
