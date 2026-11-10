from checks import function, run

EXPECTED = 'fair coin 1.0 bits\nfair die 2.585 bits\nkl 0.123\n'


def test_the_output():
    """Prints the two entropies and the KL divergence."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_units_and_sign():
    """Four equal outcomes are 2 bits, and KL from [0.9, 0.1] to [0.5, 0.5] is positive."""
    entropy = function("entropy")
    kl = function("kl")
    assert entropy([0.25, 0.25, 0.25, 0.25]) == 2.0
    assert kl([0.9, 0.1], [0.5, 0.5]) > 0
