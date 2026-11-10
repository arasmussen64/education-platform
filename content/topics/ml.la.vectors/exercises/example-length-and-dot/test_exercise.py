from checks import run


def test_the_walkthrough():
    """Prints the length twice, the unit vector and its length, the dot product, the cosine, the angle, and the axis dots."""
    assert run() == "5.0\n5.0\n[0.6 0.8]\n1.0\n24.0\n0.96\n16.26\n3.0 4.0\n0.0\n"
