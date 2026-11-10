from checks import run


def test_three_tests_pass():
    """Prints each test's name as it passes, then 3 passed."""
    assert run() == (
        "test_centuries_are_not_leap passed\n"
        "test_every_fourth_century_is_leap passed\n"
        "test_every_fourth_year_is_leap passed\n3 passed\n"
    )
