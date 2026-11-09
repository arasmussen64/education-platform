def get_int(prompt):
    """Ask until the user types a whole number, and return it."""
    while True:
        try:
            text = input(prompt)
        except ValueError:
            print("Not a whole number.")
        else:
            number = int(text)
            return number


def main():
    n = get_int("Number? ")
    print(f"Double: {n * 2}")


if __name__ == "__main__":
    main()
