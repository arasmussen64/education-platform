from checks import function, run


def test_the_output():
    """Prints both models' metrics."""
    printed = run()
    assert printed == '[0.885 0.757 0.918 0.83 ]\n[0.705 0.511 0.738 0.604]\n', f"Your program printed:\n{printed}"


def test_known_counts():
    """8, 2, 4, 86 give accuracy 0.94, precision 0.8, recall 2/3 and F1 8/11."""
    metrics = function("metrics")
    accuracy, precision, recall, f1 = metrics(8, 2, 4, 86)
    assert abs(accuracy - 0.94) < 1e-12 and abs(precision - 0.8) < 1e-12
    assert abs(recall - 2 / 3) < 1e-12 and abs(f1 - 8 / 11) < 1e-12
