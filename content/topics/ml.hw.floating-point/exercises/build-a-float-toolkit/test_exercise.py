import math
import struct

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the four lines."""
    assert run() == '(0, 0, 0) (1, 1, 2097152) (0, -4, 5033165)\nTrue False True\n10000.0\n1001.313262 [0.268941, 0.731059]\n'


def test_decode_against_struct():
    """For 2.0, 0.5, 3.75, -1.0 and 1e10, the parts rebuild the float32 value exactly."""
    decode_float32 = function("decode_float32")
    for x in (2.0, 0.5, 3.75, -1.0, 1e10):
        sign, exponent, mantissa = decode_float32(x)
        stored = struct.unpack(">f", struct.pack(">f", x))[0]
        assert (-1) ** sign * (1 + mantissa / 2**23) * 2**exponent == stored


def test_close_both_ways():
    """close is symmetric, accepts a relative gap of 1e-12, rejects one of 1e-6, and needs the absolute tolerance near zero."""
    close = function("close")
    assert close(1e6, 1e6 + 1e-6) and close(1e6 + 1e-6, 1e6)
    assert not close(1.0, 1.000001)
    assert not close(0.0, 1e-12) and close(0.0, 1e-12, abs_=1e-9)


def test_kahan_sum():
    """A hundred thousand tenths come to 10,000 within a thousandth."""
    kahan_sum = function("kahan_sum")
    assert abs(kahan_sum([0.1] * 100_000) - 10000) < 0.001


def test_log_sum_exp_and_softmax():
    """log_sum_exp of large and of very negative logits is finite and right; softmax sums to 1 and keeps the ratios."""
    log_sum_exp = function("log_sum_exp")
    softmax = function("softmax")
    assert math.isclose(log_sum_exp([1000.0, 1001.0]), 1001 + math.log(1 + math.exp(-1)))
    assert math.isclose(log_sum_exp([-1000.0, -1001.0]), -1000 + math.log(1 + math.exp(-1)))
    probabilities = softmax([1000.0, 1001.0, 1002.0])
    assert math.isclose(sum(probabilities), 1.0) and math.isclose(probabilities[2] / probabilities[1], math.e)
    assert math.isclose(sum(softmax([-1000.0, -999.0])), 1.0)
