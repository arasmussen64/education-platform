def save_numbers(path, numbers):
    """Write the numbers to the file, one per line."""
    with open(path, "w") as f:
        for number in numbers:
            f.write(str(number))
