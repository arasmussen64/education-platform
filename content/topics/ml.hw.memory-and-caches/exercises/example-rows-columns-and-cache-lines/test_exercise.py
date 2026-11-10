from checks import run


def test_the_walkthrough():
    """Prints the strides and offsets, the view and copy, the two miss counts and the bytes moved."""
    assert run() == 'strides: (32, 8) | transposed: (8, 32) | contiguous: True False\na[1, 2] sits 48 bytes from the start; row 1 occupies bytes 32 to 63\nshares memory: slice True | mask False | slice strides (32, 16)\nafter writing 100 through the view, a[0, 0] is 100.0\n256 x 256 floats walked by rows, 64 lines of cache: 8,192 misses\n256 x 256 floats walked by columns, 64 lines of cache: 65,536 misses\na 1000 x 1000 float64 grid is 8,000,000 bytes\ngrid + 1 made a new block: True | grid += 1 wrote in place: 1.0\n'
