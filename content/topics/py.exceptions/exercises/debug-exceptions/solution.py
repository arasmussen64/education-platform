def get_int(prompt):
    """Ask until the user types a whole number, and return it."""
    while True:
        text = input(prompt)
        try:
            number = int(text)
        except ValueError:
            print("Not a whole number.")
        else:
            return number


def main():
    n = get_int("Number? ")
    print(f"Double: {n * 2}")


if __name__ == "__main__":
    main()
