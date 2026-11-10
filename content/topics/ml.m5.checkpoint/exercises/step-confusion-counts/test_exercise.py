import numpy as np

from checks import function, run


def test_the_output():
    """Prints both models' counts and 200."""
    printed = run()
    assert printed == '(56, 18, 5, 121)\n(45, 43, 16, 96)\n200\n', f"Your program printed:\n{printed}"


def test_hand_made_labels():
    """Six hand-made labels give (2, 1, 1, 2)."""
    confusion = function("confusion")
    assert confusion(np.array([1, 1, 0, 0, 1, 0]), np.array([1, 0, 1, 0, 1, 0])) == (2, 1, 1, 2)
