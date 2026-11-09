def check_percent(n):
    """Return n if it's between 0 and 100; otherwise raise ValueError."""
    if n <= 0 or n >= 100:
        raise ValueError("out of range")
    return n
