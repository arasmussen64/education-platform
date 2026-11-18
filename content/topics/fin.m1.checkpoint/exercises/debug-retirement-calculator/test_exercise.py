from checks import function, run, run_with

EXPECTED = (
    "growth per year: 5.61%\n"
    "after inflation: 2.53%\n"
    "months of saving: 360\n"
    "saved in all: 144,000.00\n"
    "at 65, in today's money: 215,252.79\n"
)


def line(printed, number):
    lines = printed.splitlines()
    return lines[number] if len(lines) > number else "(no such line)"


def test_growth_per_year():
    """growth_per_year gives the steady yearly rate that compounds to the same total: +50% then -50% is about -13.4% a year."""
    growth_per_year = function("growth_per_year")
    got = growth_per_year([0.5, -0.5])
    assert abs(got - (0.75**0.5 - 1)) < 1e-9, f"growth_per_year([0.5, -0.5]) returned {got}"
    got = growth_per_year([0.1, 0.1])
    assert abs(got - 0.1) < 1e-9, f"growth_per_year([0.1, 0.1]) returned {got}"


def test_after_inflation():
    """The second line is the growth per year after inflation: after inflation: 2.53%."""
    got = line(run(), 1)
    assert got == "after inflation: 2.53%", f"The second line should be after inflation: 2.53%. It was: {got}"


def test_monthly_rate():
    """monthly_rate turns a yearly rate into a monthly one: 6% a year is 0.5% a month."""
    monthly_rate = function("monthly_rate")
    got = monthly_rate(0.06)
    assert abs(got - 0.005) < 1e-12, f"monthly_rate(0.06) returned {got}"


def test_months_of_saving():
    """Saving from a 25th birthday to a 65th is 40 years, 480 months."""
    months_of_saving = function("months_of_saving")
    got = months_of_saving(25, 65)
    assert got == 480, f"months_of_saving(25, 65) returned {got}"


def test_the_report():
    """Prints the five lines, ending at 65, in today's money: 215,252.79."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_another_saver():
    """Works for another fund and saver: 250 a month from 40 to 60 ends at 78,043.32."""
    printed = run_with(
        {
            "past_returns": [0.30, -0.20, 0.10],
            "inflation": 0.02,
            "monthly_saving": 250,
            "start_age": 40,
            "retire_age": 60,
        }
    )
    expected = (
        "growth per year: 4.59%\n"
        "after inflation: 2.54%\n"
        "months of saving: 240\n"
        "saved in all: 60,000.00\n"
        "at 60, in today's money: 78,043.32\n"
    )
    assert printed == expected, f"With that fund and saver it should print:\n{expected}\nIt printed:\n{printed}"
