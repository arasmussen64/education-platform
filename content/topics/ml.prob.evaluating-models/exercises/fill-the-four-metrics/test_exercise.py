from checks import function, run


def test_the_output():
    """Prints the three classifiers' metrics."""
    printed = run()
    assert printed == '(0.94, 0.8, 0.667, 0.727)\n(0.65, 1.0, 0.3, 0.462)\n(0.5, 0.5, 1.0, 0.667)\n', f"Your program printed:\n{printed}"


def test_a_perfect_and_a_balanced_classifier():
    """A perfect classifier scores 1 on everything; 10 true positives, 10 false positives and 30 misses give precision 0.5 and recall 0.25."""
    metrics = function("metrics")
    assert metrics(20, 0, 0, 80) == (1.0, 1.0, 1.0, 1.0)
    assert metrics(10, 10, 30, 50)[1:3] == (0.5, 0.25)
