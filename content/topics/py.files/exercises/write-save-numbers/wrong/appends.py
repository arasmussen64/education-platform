def save_numbers(path, numbers):
    """Write the numbers to the file, one per line."""
    with open(path, "a") as f:
        for number in numbers:
            f.write(f"{number}\n")
