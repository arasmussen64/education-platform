def write_lines(path, lines):
    """Write each item to the file, one per line."""
    with open(path, "r") as f:
        for line in lines:
            f.write(line)


def print_lines(path):
    """Print each line of the file, numbered from 1."""
    with open(path) as f:
        number = 1
        for line in f:
            print(number, line)
            number += 1


def main():
    write_lines("todo.txt", ["buy milk", "call Ada"])
    print_lines("todo.txt")


if __name__ == "__main__":
    main()
