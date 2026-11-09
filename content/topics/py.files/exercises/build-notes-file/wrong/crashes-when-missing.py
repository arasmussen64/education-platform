def save_lines(path, lines):
    """Write the lines to the file."""
    with open(path, "w") as f:
        for line in lines:
            f.write(f"{line}\n")


def append_line(path, line):
    """Add one line at the end of the file."""
    with open(path, "a") as f:
        f.write(f"{line}\n")


def load_lines(path):
    """Return the lines without line breaks."""
    lines = []
    with open(path) as f:
        for line in f:
            lines.append(line.rstrip("\n"))
    return lines


def count_lines(path):
    """Return how many lines the file has."""
    return len(load_lines(path))


def main():
    save_lines("notes.txt", ["milk", "eggs"])
    append_line("notes.txt", "tea")
    print(count_lines("notes.txt"))
    for line in load_lines("notes.txt"):
        print(line)


if __name__ == "__main__":
    main()
