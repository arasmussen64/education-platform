from checks import run, run_with


def test_this_test():
    """Prints Positive and sick: 9, then Positive and healthy: 99."""
    printed = run()
    assert printed == "Positive and sick: 9\nPositive and healthy: 99\n", (
        f"Your program printed:\n{printed}"
    )


def test_another_test():
    """Works for other numbers: 2% with a perfect catch rate and 5% false positives gives 20 and 49."""
    printed = run_with({"rate": 0.02, "sensitivity": 1.0, "false_positive": 0.05})
    assert printed == "Positive and sick: 20\nPositive and healthy: 49\n", (
        f"With rate 0.02, sensitivity 1.0 and false_positive 0.05 it should print 20, then 49. It printed:\n{printed}"
    )
