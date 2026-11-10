from checks import run


def test_scales_the_recipe():
    """Prints the raw amount, then 1.67, then 1.67 cups of sugar."""
    assert run() == "1.6666666666666665\n1.67\n1.67 cups of sugar\n"
