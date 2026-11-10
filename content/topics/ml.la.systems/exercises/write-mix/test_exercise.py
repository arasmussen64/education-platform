import numpy as np

from checks import function, run


def test_the_output():
    """Prints [20. 10.]."""
    printed = run()
    assert printed == "[20. 10.]\n", f"Your program printed:\n{printed}"


def test_other_mixes():
    """10 litres at 50% from 20% and 80% is 5 and 5; 100 at 30% from 10% and 50% is 50 and 50."""
    mix = function("mix")
    assert np.allclose(mix(10, 0.5, 0.2, 0.8), [5.0, 5.0])
    assert np.allclose(mix(100, 0.3, 0.1, 0.5), [50.0, 50.0])
