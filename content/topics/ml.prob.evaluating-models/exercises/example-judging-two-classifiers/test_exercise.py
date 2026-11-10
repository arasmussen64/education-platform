from checks import run


def test_the_walkthrough():
    """Prints two models' reports, the baseline, an interval, two thresholds and the paired comparison."""
    assert run() == 'A (61, 21, 13, 105) [0.83  0.744 0.824 0.782]\nB (53, 31, 21, 95) [0.74  0.631 0.716 0.671]\nalways no 0.63\n0.83 0.027 [0.778 0.882]\n1.3 0.85\n1.2 0.86\n0.09 [0.015 0.165]\n'
