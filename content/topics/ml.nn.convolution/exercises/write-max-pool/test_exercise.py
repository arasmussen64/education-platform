import numpy as np

from checks import function, run


def test_the_output():
    """Prints the pooled 2-by-2 and the routed gradient."""
    printed = run()
    assert printed == '[[7.0, 8.0], [6.0, 9.0]]\n[[0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 0.0, 2.0], [0.0, 0.0, 4.0, 0.0], [3.0, 0.0, 0.0, 0.0]]\n', f"Your program printed:\n{printed}"


def test_other_sizes():
    """A batch of two 6-by-6 images pooled by 3: the maxima, one winner per window, and a gradient that lands only on winners."""
    max_pool = function("max_pool")
    max_pool_backward = function("max_pool_backward")
    rng = np.random.default_rng(4)
    X = rng.standard_normal((2, 6, 6))
    pooled, mask = max_pool(X, size=3)
    assert pooled.shape == (2, 2, 2) and mask.shape == (2, 2, 3, 2, 3)
    for n in range(2):
        for y in range(2):
            for x in range(2):
                assert pooled[n, y, x] == X[n, 3 * y : 3 * y + 3, 3 * x : 3 * x + 3].max()
    assert int(mask.sum()) == 8
    grad_out = np.arange(1.0, 9.0).reshape(2, 2, 2)
    back = max_pool_backward(mask, grad_out)
    assert back.shape == (2, 6, 6) and int((back != 0).sum()) == 8 and back.sum() == grad_out.sum()
    assert back[0, :3, :3].max() == 1.0 and back[1, 3:, 3:].max() == 8.0
