def to_binary(n, width):
    """A non-negative integer as exactly width bits, most significant first, without bin() or format()."""
    bits = []
    for position in range(width - 1, -1, -1):
        bits.append("1" if (n >> position) & 1 else "0")
    return "".join(bits)


print(to_binary(37, 8), to_binary(5, 4), to_binary(0, 3), to_binary(255, 8))
