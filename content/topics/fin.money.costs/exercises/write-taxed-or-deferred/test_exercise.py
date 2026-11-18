from checks import function, run, run_with

EXPECTED = "Taxed every year: $66,132.84\nTaxed at the end: $81,984.06\nDifference: $15,851.21\n"


def test_taxed_every_year():
    """taxed_every_year(1000, 0.1, 0.5, 2) is 1102.5: each year's gain is halved by the tax."""
    taxed_every_year = function("taxed_every_year")
    got = taxed_every_year(1000, 0.1, 0.5, 2)
    assert abs(got - 1102.5) < 0.005, f"taxed_every_year(1000, 0.1, 0.5, 2) returned {got}"


def test_taxed_at_the_end():
    """taxed_at_the_end(1000, 0.1, 0.5, 2) is 1105.0: $1,210 less half of the $210 gain."""
    taxed_at_the_end = function("taxed_at_the_end")
    got = taxed_at_the_end(1000, 0.1, 0.5, 2)
    assert abs(got - 1105.0) < 0.005, f"taxed_at_the_end(1000, 0.1, 0.5, 2) returned {got}"


def test_the_report():
    """Prints both final amounts and the difference."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_numbers():
    """Works for other numbers: $5,000 at 5% for 40 years with a 20% tax."""
    expected = "Taxed every year: $24,005.10\nTaxed at the end: $29,159.95\nDifference: $5,154.85\n"
    printed = run_with({"start": 5000, "growth": 0.05, "tax": 0.2, "years": 40})
    assert printed == expected, f"With those numbers it should print:\n{expected}\nIt printed:\n{printed}"
