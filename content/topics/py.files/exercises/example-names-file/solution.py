def save_names(path, names):
    """Write the names to the file, one per line."""
    with open(path, "w") as f:
        for name in names:
            f.write(name + "\n")


def load_names(path):
    """Return the names in the file, without their line breaks."""
    names = []
    with open(path) as f:
        for line in f:
            names.append(line.rstrip())
    return names


def main():
    save_names("names.txt", ["Ron", "Hermione", "Harry"])
    for name in sorted(load_names("names.txt")):
        print(name)


if __name__ == "__main__":
    main()
