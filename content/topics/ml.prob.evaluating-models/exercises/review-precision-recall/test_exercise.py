from checks import function, run


def test_the_output():
    """Prints the two pairs."""
    assert run() == '(0.8, 0.6666666666666666)\n(1.0, 0.3)\n'


def test_other_counts():
    """Flagging everything gives precision below 1 and recall 1; never flagging anything correctly gives precision 0."""
    precision_recall = function("precision_recall")
    assert precision_recall(20, 80, 0) == (0.2, 1.0)
    assert precision_recall(0, 5, 10) == (0.0, 0.0)
