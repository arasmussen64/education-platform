import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the three lines."""
    assert run() == '(32, 8) 48 46\n8192 65536\n8000000 16000000 8000000\n'


def test_strides_and_offsets_against_numpy():
    """Strides match NumPy for four shapes and three dtypes, and the offset of an element is its stride-weighted index."""
    c_strides = function("c_strides")
    byte_offset = function("byte_offset")
    for shape in ((7,), (3, 4), (2, 3, 4), (2, 3, 4, 5)):
        for dtype in ("int16", "float32", "float64"):
            a = np.zeros(shape, dtype=dtype)
            assert c_strides(shape, a.itemsize) == a.strides
            last = tuple(size - 1 for size in shape)
            assert byte_offset(shape, a.itemsize, last) == sum(i * s for i, s in zip(last, a.strides))
    assert byte_offset((3, 4), 8, (0, 0)) == 0


def test_cache_eviction():
    """On a 16 by 16 matrix by columns, 15 lines miss every element and 16 lines miss once per line; by rows one line is enough."""
    misses = function("misses")
    assert misses((16, 16), "columns", 15) == 256 and misses((16, 16), "columns", 16) == 32
    assert misses((16, 16), "rows", 1) == 32 and misses((64, 64), "rows", 4) == 512


def test_traffic():
    """A million float32s read once and written once move 8,000,000 bytes; int16 read twice moves 4,000,000; an empty shape is one element."""
    traffic = function("traffic")
    assert traffic((1000, 1000), "float32", 1, 1) == 8_000_000
    assert traffic((1000, 1000), "int16", 2, 0) == 4_000_000
    assert traffic((), "float64", 1, 0) == 8
