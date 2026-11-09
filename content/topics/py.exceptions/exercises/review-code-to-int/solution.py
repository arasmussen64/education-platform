def to_int(text):
    """Return the whole number in the text, or None if there isn't one."""
    try:
        return int(text)
    except ValueError:
        return None
