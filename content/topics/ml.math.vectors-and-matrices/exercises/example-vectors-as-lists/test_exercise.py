from checks import run


def test_vector_operations():
    """Prints [5, 7, 9], [3, 6, 9], 32 and 5.0."""
    assert run() == "[5, 7, 9]\n[3, 6, 9]\n32\n5.0\n"
