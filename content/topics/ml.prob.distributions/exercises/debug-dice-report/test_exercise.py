import numpy as np

from checks import function, run

EXPECTED = 'faces [0.168 0.166 0.165 0.165 0.167 0.168]\n0 0.48 0.482\n1 0.385 0.386\n2 0.119 0.116\n3 0.015 0.015\n4 0.001 0.001\n'


def test_the_output():
    """Prints the six faces' fractions and the table of sixes in four rolls."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_the_die_has_six_faces():
    """roll produces every face from 1 to 6 and nothing else."""
    roll = function("roll")
    faces = set(np.unique(roll(np.random.default_rng(0), 10000)).tolist())
    assert faces == {1, 2, 3, 4, 5, 6}


def test_the_table_sums_to_one():
    """sixes_pmf's five entries sum to 1, and one six in four rolls has chance 0.386."""
    sixes_pmf = function("sixes_pmf")
    assert abs(sum(sixes_pmf(k) for k in range(5)) - 1) < 1e-12
    assert abs(sixes_pmf(1) - 0.3858) < 0.001
