from checks import run


def test_the_walkthrough():
    """Prints surprises, entropies, four beliefs priced against the truth, and the loss in bits and nats."""
    assert run() == '1.0 3.0 0.0 10.0\n1.0 0.469 2.585 0.0\n1.157\nright 1.157 0.0\nhedged 1.28 0.123\nuniform 1.585 0.428\nupside down 2.841 1.684\n[0.152 0.322 0.515 0.737] 0.431 0.299\n'
