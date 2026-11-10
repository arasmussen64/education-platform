import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the four lines."""
    assert run() == '100101 ff 11111111 0\n-128 0 255 127\n3136000 784000 376320000\nuint8 uint16 uint32\n'


def test_to_base_against_python():
    """Agrees with bin, oct and hex for 0 to 999, and writes 0 as a single digit."""
    to_base = function("to_base")
    for n in range(1000):
        assert to_base(n, 2) == format(n, "b") and to_base(n, 8) == format(n, "o") and to_base(n, 16) == format(n, "x")
    assert to_base(0, 16) == "0"


def test_wraps_to_against_numpy():
    """Agrees with what NumPy stores for every value from -300 to 300 in int8, uint8 and int16."""
    wraps_to = function("wraps_to")
    for value in range(-300, 301):
        assert wraps_to(value, 8, True) == int(np.array([value]).astype(np.int8)[0])
        assert wraps_to(value, 8, False) == int(np.array([value]).astype(np.uint8)[0])
        assert wraps_to(value, 16, True) == int(np.array([value]).astype(np.int16)[0])
    assert wraps_to(70000, 16, False) == 4464


def test_array_bytes_against_nbytes():
    """Matches nbytes for small arrays of five dtypes, and an empty shape is one element."""
    array_bytes = function("array_bytes")
    for dtype in ("uint8", "int16", "int32", "float32", "float64"):
        for shape in ((7,), (3, 4), (2, 3, 4)):
            assert array_bytes(shape, dtype) == np.zeros(shape, dtype=dtype).nbytes
    assert array_bytes((), "float64") == 8


def test_smallest_uint_boundaries():
    """255 fits uint8 and 256 needs uint16; 65,535 fits uint16 and 65,536 needs uint32; beyond uint64 raises."""
    smallest_uint = function("smallest_uint")
    assert (smallest_uint(255), smallest_uint(256), smallest_uint(65535), smallest_uint(65536)) == ("uint8", "uint16", "uint16", "uint32")
    assert smallest_uint(2**64 - 1) == "uint64"
    try:
        smallest_uint(2**64)
    except ValueError:
        pass
    else:
        raise AssertionError("2**64 doesn't fit any unsigned dtype")
