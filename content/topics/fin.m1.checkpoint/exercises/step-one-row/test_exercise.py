from checks import function, run

EXPECTED = (
    "month 1: interest 90.00, principal 791.64, balance 14,208.36\n"
    "month 2: interest 85.25, principal 796.39, balance 13,411.97\n"
    "month 3: interest 80.47, principal 801.17, balance 12,610.81\n"
    "month 4: interest 75.66, principal 805.97, balance 11,804.83\n"
    "month 5: interest 70.83, principal 810.81, balance 10,994.02\n"
    "month 6: interest 65.96, principal 815.67, balance 10,178.35\n"
    "month 7: interest 61.07, principal 820.57, balance 9,357.78\n"
    "month 8: interest 56.15, principal 825.49, balance 8,532.29\n"
    "month 9: interest 51.19, principal 830.44, balance 7,701.85\n"
    "month 10: interest 46.21, principal 835.43, balance 6,866.42\n"
    "month 11: interest 41.20, principal 840.44, balance 6,025.98\n"
    "month 12: interest 36.16, principal 845.48, balance 5,180.50\n"
    "month 13: interest 31.08, principal 850.56, balance 4,329.94\n"
    "month 14: interest 25.98, principal 855.66, balance 3,474.28\n"
    "month 15: interest 20.85, principal 860.79, balance 2,613.49\n"
    "month 16: interest 15.68, principal 865.96, balance 1,747.53\n"
    "month 17: interest 10.49, principal 871.15, balance 876.38\n"
    "month 18: interest 5.26, principal 876.38, balance 0.00\n"
    "payment 881.64\n"
    "total paid 15,869.49\n"
    "total interest 869.49\n"
    "annualized return 25.4%\n"
    "volatility 24.4%\n"
    "max drawdown 8.5%, from position 3 to position 4\n"
)


def test_the_report():
    """Prints the whole schedule, the totals and the portfolio report."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_another_loan():
    """For 1,000 at 12% a year over 2 months, the schedule's first month has interest 10.00, principal 497.51."""
    print_schedule = function("print_schedule")
    from checks import printed as captured

    out = captured(print_schedule, 1000, 0.12, 2)
    first = out.splitlines()[0] if out else ""
    assert first == "month 1: interest 10.00, principal 497.51, balance 502.49", f"The first line was: {first}"
