from checks import function, run


def test_the_output():
    """Prints 0.75 0.3 0.001."""
    assert run() == '0.75 0.3 0.001\n'


def test_other_coins():
    """Half the flips heads gives 0.5; 9 in 10 gives 0.9."""
    mle_coin = function("mle_coin")
    assert abs(mle_coin(7, 14) - 0.5) < 0.001
    assert abs(mle_coin(9, 10) - 0.9) < 0.001
