from checks import run


def test_grid_and_records():
    """Prints the cell, each row, the grid as text, then one line per student."""
    assert run() == "6\n[1, 2, 3]\n[4, 5, 6]\n1 2 3 \n4 5 6 \nAda: 91\nBob: 78\n"
