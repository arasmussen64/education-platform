def safe_divide(a, b):
    """Return a divided by b, or None when b is 0."""
    try:
        return a / b
    except ZeroDivisionError:
        return None
