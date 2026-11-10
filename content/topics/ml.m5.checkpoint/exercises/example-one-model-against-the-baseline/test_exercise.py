from checks import run


def test_the_walkthrough():
    """Prints the model's and the baseline's counts, the interval and the paired difference."""
    assert run() == 'model (39, 2, 22, 137) [0.88  0.951 0.639 0.765]\nalways no (0, 0, 61, 139) 0.695\ninterval [0.835 0.925]\nmodel minus baseline 0.185 [0.13  0.245]\n'
