from checks import run


def test_the_four_results():
    """Prints the squares twice, the even squares, the lengths and the first letters."""
    assert run() == (
        "[1, 4, 9, 16, 25]\n[1, 4, 9, 16, 25]\n[4, 16]\n"
        "{'apple': 5, 'fig': 3, 'avocado': 7}\n['a', 'f']\n"
    )
