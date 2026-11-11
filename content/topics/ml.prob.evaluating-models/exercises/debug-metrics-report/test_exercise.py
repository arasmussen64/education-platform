from checks import function, run

EXPECTED = 'metrics 0.85 0.75 0.6 0.667\ninterval 0.801 0.899\n'


def test_the_output():
    """Prints the four metrics and the interval."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_f1_and_the_interval():
    """Precision 1 and recall 0.25 give F1 0.4; an accuracy of 0.9 on 100 examples spans 0.841 to 0.959."""
    metrics = function("metrics")
    accuracy_interval = function("accuracy_interval")
    assert abs(metrics(10, 0, 30, 60)[3] - 0.4) < 1e-12
    low, high = accuracy_interval(0.9, 100)
    assert abs(low - 0.8412) < 0.001 and abs(high - 0.9588) < 0.001
