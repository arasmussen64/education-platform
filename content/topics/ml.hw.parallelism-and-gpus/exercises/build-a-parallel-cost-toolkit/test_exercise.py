from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the five lines."""
    assert run() == '4.71 10.0 39.3\n(2147483648, 12582912) 170.7\n0.5 128.0\n214.7 24.0\n0.04 10.04\n'


def test_amdahl_limits():
    """Fully parallel work speeds up by the worker count, fully serial not at all, and a fifth serial never passes 5."""
    amdahl = function("amdahl")
    assert abs(amdahl(1.0, 32) - 32) < 1e-9 and abs(amdahl(0.0, 32) - 1) < 1e-9
    assert amdahl(0.8, 64) < 5 and abs(amdahl(0.8, 10**12) - 5) < 1e-6


def test_matmul_counts():
    """(2, 3) @ (3, 4) in float64 is 48 FLOPs and 208 bytes; (5, 7) @ (7, 2) in float16 is 140 FLOPs and 118 bytes."""
    matmul_cost = function("matmul_cost")
    assert tuple(matmul_cost(2, 3, 4, 8)) == (48, 208)
    assert tuple(matmul_cost(5, 7, 2, 2)) == (140, 118)


def test_roofline_both_sides():
    """Above the ridge the arithmetic time wins, below it the memory time, and intensity is FLOPs over bytes."""
    intensity = function("intensity")
    roofline_seconds = function("roofline_seconds")
    assert abs(intensity(48, 208) - 48 / 208) < 1e-12
    assert abs(roofline_seconds(1e9, 1e6, 1e12, 1e9) - 1e-3) < 1e-12
    assert abs(roofline_seconds(1e6, 1e9, 1e12, 1e9) - 1.0) < 1e-12


def test_transfer():
    """A gigabyte in one piece at 25 GB/s is 40 ms plus one latency; in a thousand pieces it costs a thousand latencies."""
    transfer_seconds = function("transfer_seconds")
    assert abs(transfer_seconds(10**9, 1, 25e9, 1e-5) - 0.04001) < 1e-9
    assert abs(transfer_seconds(10**9, 1000, 25e9, 1e-5) - 0.05) < 1e-9
