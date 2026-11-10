from checks import run


def test_the_walkthrough():
    """Prints the table, the rule, a second test, a simulation and a belief updated flip by flip."""
    assert run() == '950 9900\n0.088\n0.088\n0.477\n0.085\n[0.    0.    0.001 0.009 0.037 0.099 0.188 0.267 0.265 0.134 0.   ]\n0.7\n'
