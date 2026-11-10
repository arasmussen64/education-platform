import numpy as np

from checks import function, run


def test_the_output():
    """Prints the accuracy and the evaluation tuple."""
    printed = run()
    assert printed == '0.5\n(0.5, 0.5)\n', f"Your program printed:\n{printed}"


def test_other_logits():
    """Accuracy is a fraction of rows, not a count; a perfect and an all-wrong set give 1 and 0; evaluate returns the loss first."""
    accuracy = function("accuracy")
    evaluate = function("evaluate")
    logits = np.array([[0.1, 0.9], [0.8, 0.2], [0.3, 0.7], [0.6, 0.4], [0.5, 0.5001]])
    assert accuracy(logits, np.array([1, 0, 1, 0, 1])) == 1.0 and accuracy(logits, np.array([0, 1, 0, 1, 0])) == 0.0
    assert accuracy(logits, np.array([1, 0, 0, 0, 0])) == 0.6

    class Net:
        def forward(self, X):
            return logits

    class Loss:
        def forward(self, logits, labels):
            return 0.25

    assert evaluate(Net(), Loss(), np.zeros((5, 1)), np.array([1, 0, 1, 0, 1])) == (0.25, 1.0)
