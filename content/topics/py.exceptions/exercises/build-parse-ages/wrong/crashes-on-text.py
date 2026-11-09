def to_age(text):
    """Return the age, or None if negative."""
    age = int(text)
    if age < 0:
        return None
    return age


def valid_ages(texts):
    """Return the valid ages."""
    ages = []
    for text in texts:
        age = to_age(text)
        if age is not None:
            ages.append(age)
    return ages


def require_positive(n):
    """Return n if positive, else raise."""
    if n <= 0:
        raise ValueError("must be positive")
    return n


def main():
    texts = ["34", "x", "-5", "7"]
    ages = valid_ages(texts)
    print(f"Valid ages: {ages}")
    print(f"Skipped: {len(texts) - len(ages)}")


if __name__ == "__main__":
    main()
