from checks import function, run


def test_the_output():
    """Prints the packed colour and the three unpacked tuples."""
    printed = run()
    assert printed == '0xff8007 (255, 128, 7)\n(0, 0, 255) (16, 32, 48)\n', f"Your program printed:\n{printed}"


def test_round_trips():
    """Every byte survives a pack and unpack, including 255 in every position and 0 everywhere."""
    pack = function("pack")
    unpack = function("unpack")
    for r, g, b in ((0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (1, 2, 3), (200, 100, 50)):
        assert unpack(pack(r, g, b)) == (r, g, b)
    assert pack(255, 255, 255) == 0xFFFFFF
