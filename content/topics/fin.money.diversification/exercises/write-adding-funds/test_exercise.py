from checks import function, run, run_with

TABLE = (
    "1 of 8: 6.73%\n"
    "2 of 8: 5.19%\n"
    "3 of 8: 4.72%\n"
    "4 of 8: 4.26%\n"
    "5 of 8: 4.06%\n"
    "6 of 8: 3.86%\n"
    "7 of 8: 3.67%\n"
    "8 of 8: 3.38%\n"
)


def test_mix_of_two():
    """mix_of_first([[0.10, 0.20], [0.30, 0.00]], 2) is [0.2, 0.1]: each month's average."""
    mix_of_first = function("mix_of_first")
    got = mix_of_first([[0.10, 0.20], [0.30, 0.00]], 2)
    assert isinstance(got, list) and len(got) == 2, f"Expected a list of two numbers, got {got}"
    assert abs(got[0] - 0.2) < 1e-9 and abs(got[1] - 0.1) < 1e-9, f"Expected [0.2, 0.1], got {got}"


def test_only_the_first_k():
    """With three funds and k = 1, the mix is just the first fund."""
    mix_of_first = function("mix_of_first")
    got = mix_of_first([[0.05, -0.02], [0.30, 0.00], [0.10, 0.10]], 1)
    assert isinstance(got, list) and len(got) == 2, f"Expected a list of two numbers, got {got}"
    assert abs(got[0] - 0.05) < 1e-9 and abs(got[1] + 0.02) < 1e-9, f"Expected [0.05, -0.02], got {got}"


def test_the_table():
    """Prints one line for each number of funds, from 1 of 8 to 8 of 8."""
    printed = run()
    assert printed == TABLE, f"Expected this:\n{TABLE}\nYour program printed:\n{printed}"


def test_other_funds():
    """Works for any list of funds: three funds of four months give a table of three lines."""
    funds = [
        [0.04, -0.02, 0.06, 0.00],
        [-0.01, 0.03, 0.02, 0.04],
        [0.02, 0.02, -0.04, 0.03],
    ]
    expected = "1 of 3: 3.65%\n2 of 3: 1.47%\n3 of 3: 0.57%\n"
    printed = run_with({"funds": funds})
    assert printed == expected, f"With three other funds it should print:\n{expected}\nIt printed:\n{printed}"
