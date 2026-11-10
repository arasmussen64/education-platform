from checks import run


def test_the_walkthrough():
    """Prints the bases, the wraps, the negative bits, the three sizes and the flag arithmetic."""
    assert run() == '0b100101 0xff 37 255\n00100101 = 32 + 4 + 1 = 37\nint8 + 5: [ 125 -126 -124]\nuint8 + 1: [251   0]\nPython int: 1267650600228229401496703205376\nthe bits of -1 and -128 in int8: 11111111 10000000\nthe same bytes read as unsigned: [255 128 127]\n  uint8: 784,000 bytes for 1,000 images of 784 pixels\nfloat32: 3,136,000 bytes for 1,000 images of 784 pixels\nfloat64: 6,272,000 bytes for 1,000 images of 784 pixels\nperms: 5 101 can write: False can run: True\nafter granting write and revoking run: 011\nrgb packed: 0xff8007 green: 128 | 1 << 10 = 1024 | 1024 >> 3 = 128\n'
