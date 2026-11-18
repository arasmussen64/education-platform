from checks import run, run_with

EXPECTED = (
    "Prices rose 7.19% from 2022 to 2024.\n"
    "Your $10,000 grew to $11,200.00.\n"
    "To keep up with prices it needed $10,718.73.\n"
    "Real return: 4.49%\n"
)


def lines_of(printed):
    return printed.splitlines()


def test_needed_to_keep_up():
    """Says $10,718.73 was needed to keep up with prices from 2022 to 2024."""
    got = lines_of(run())
    want = EXPECTED.splitlines()[2]
    assert want in got, f"Expected the line:\n{want}\nYour program printed:\n" + "\n".join(got)


def test_real_return():
    """Prints a real return of 4.49%."""
    got = lines_of(run())
    want = EXPECTED.splitlines()[3]
    assert want in got, f"Expected the line:\n{want}\nYour program printed:\n" + "\n".join(got)


def test_whole_report():
    """Prints the whole report as shown."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_years():
    """Works for other years and returns: 10% from 2019 to 2021 needed $10,598.97 and is a real 3.78%."""
    printed = run_with({"start_year": 2019, "end_year": 2021, "nominal": 0.10})
    expected = (
        "Prices rose 5.99% from 2019 to 2021.\n"
        "Your $10,000 grew to $11,000.00.\n"
        "To keep up with prices it needed $10,598.97.\n"
        "Real return: 3.78%\n"
    )
    assert printed == expected, (
        f"With start_year = 2019, end_year = 2021 and nominal = 0.10 it should print:\n{expected}\n"
        f"It printed:\n{printed}"
    )
