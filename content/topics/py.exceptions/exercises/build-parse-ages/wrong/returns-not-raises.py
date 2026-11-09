def to_age(text):
    """Return the whole number in the text if it's 0 or more, else None."""
    try:
        age = int(text)
    except ValueError:
        return None
    if age < 0:
        return None
    return age


def valid_ages(texts):
    """Return the valid ages among the texts, in order."""
    ages = []
    for text in texts:
        age = to_age(text)
        if age is not None:
            ages.append(age)
    return ages


def require_positive(n):
    """Return n if it's greater than 0."""
    if n <= 0:
        return "must be positive"
    return n


def main():
    texts = ["34", "x", "-5", "7"]
    ages = valid_ages(texts)
    print(f"Valid ages: {ages}")
    print(f"Skipped: {len(texts) - len(ages)}")


if __name__ == "__main__":
    main()
