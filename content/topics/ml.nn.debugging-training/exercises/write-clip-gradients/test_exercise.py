import numpy as np

from checks import function, run


def test_the_output():
    """Prints the norm, the clipped list with its norm, and True."""
    printed = run()
    assert printed == '13.0\n[[[1.5, 0.0], [0.0, 0.0]], [2.0], [6.0]] 6.5\nTrue\n', f"Your program printed:\n{printed}"


def test_other_cases():
    """Random gradients clip to the limit with their direction kept; small ones come back untouched; the originals are never changed."""
    gradient_norm = function("gradient_norm")
    clip_gradients = function("clip_gradients")
    rng = np.random.default_rng(2)
    grads = [rng.standard_normal((3, 4)), rng.standard_normal(5)]
    before = [grad.copy() for grad in grads]
    norm = gradient_norm(grads)
    assert isinstance(norm, float) and abs(norm - np.sqrt(sum((g ** 2).sum() for g in grads))) < 1e-12
    clipped = clip_gradients(grads, 0.5)
    assert abs(gradient_norm(clipped) - 0.5) < 1e-12
    assert np.allclose(clipped[0] / grads[0], clipped[1][0] / grads[1][0])
    assert clip_gradients(grads, norm + 1) is grads
    assert all(np.array_equal(a, b) for a, b in zip(grads, before))
    assert gradient_norm([np.zeros(3)]) == 0.0
