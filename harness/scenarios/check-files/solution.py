def total_in(path):
    """Return the sum of the numbers, one per line, in the file."""
    total = 0
    with open(path) as f:
        for line in f:
            total += int(line)
    return total


def main():
    with open("numbers.txt", "w") as f:
        f.write("1\n2\n3\n")
    print(total_in("numbers.txt"))


if __name__ == "__main__":
    main()
