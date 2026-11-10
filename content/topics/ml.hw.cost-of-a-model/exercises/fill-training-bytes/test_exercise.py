from checks import function, run


def test_the_output():
    """Prints the two totals."""
    printed = run()
    assert printed == '4063904\n16.064\n', f"Your program printed:\n{printed}"


def test_more_values():
    """A batch of 0 is 16 bytes per parameter in float32 and 8 in float16, and activations add batch times values times bytes."""
    training_bytes = function("training_bytes")
    assert training_bytes(1000, 0, 500, 4) == 16000 and training_bytes(1000, 0, 500, 2) == 8000
    assert training_bytes(1000, 10, 500, 4) == 16000 + 20000
