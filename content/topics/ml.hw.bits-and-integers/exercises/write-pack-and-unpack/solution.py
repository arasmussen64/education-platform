def pack(r, g, b):
    """Three bytes (0 to 255) packed into one integer: red in the top byte, green in the middle, blue at the bottom."""
    return (r << 16) | (g << 8) | b


def unpack(packed):
    """The three bytes back out, as a tuple (r, g, b)."""
    return ((packed >> 16) & 0xFF, (packed >> 8) & 0xFF, packed & 0xFF)


print(hex(pack(255, 128, 7)), unpack(0xFF8007))
print(unpack(pack(0, 0, 255)), unpack(pack(16, 32, 48)))
