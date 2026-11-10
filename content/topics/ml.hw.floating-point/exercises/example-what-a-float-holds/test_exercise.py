from checks import run


def test_the_walkthrough():
    """Prints the tenth's bits, the precision lines, the sums and the two softmaxes."""
    assert run() == 'False 0.30000000000000004 0.10000000000000000555\n0.1 as float32: 0 01111011 10011001100110011001101\nexponent 123 - 127 = -4 | mantissa 1 + 5033165 / 2**23\nwhich is 0.10000000149011612\nepsilon: float32 1.1920928955078125e-07 float64 2.220446049250313e-16\n16777216 + 1 in float32: 16777216.0 | in float64: 16777217.0\nisclose: True | allclose: True\nten tenths, one at a time: 0.9999999999999999 | sum(): 1.0 | fsum: 1.0 | 0.1 * 10: 1.0\n100,000 tenths in float32, one at a time: 9998.556640625\nthe same with np.sum (pairwise): 10000.0009765625\noverflow: inf | inf - inf: nan | nan == nan: False\nnaive softmax of [1000, 1001]: [nan nan]\nstable softmax: [0.26894142 0.73105858] | log-sum-exp: 1001.3132616875182\n'
