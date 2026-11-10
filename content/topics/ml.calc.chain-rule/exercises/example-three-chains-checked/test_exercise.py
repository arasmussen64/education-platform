from checks import run


def test_the_walkthrough():
    """Prints three checked chain-rule derivatives and a backward pass."""
    assert run() == '42.0 42.0\n0.013296 0.013296\n4.01815\n2 54.59815 1 0.017986\n1.964028 1.964028\n1.964028\n'
