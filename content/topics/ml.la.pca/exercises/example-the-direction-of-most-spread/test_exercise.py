from checks import run


def test_the_walkthrough():
    """Prints the mean, the covariance, the eigenvalues, the first component, the scores, the share kept and the rebuilt points."""
    assert run() == (
        "[4.5 3. ]\n[[3.5 2.8]\n [2.8 2.4]]\nTrue\n[0.096 5.804]\n[0.772 0.635]\n"
        "[-3.201 -1.794 -1.021  1.021  1.794  3.201]\n0.984\n"
        "[[2.03 0.97]\n [3.11 1.86]\n [3.71 2.35]\n [5.29 3.65]\n [5.89 4.14]\n [6.97 5.03]]\n"
    )
