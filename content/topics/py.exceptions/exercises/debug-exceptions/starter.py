def get_int(prompt):
    """Ask until the user types a whole number, and return it."""
    while True:
        try:
            text = input(prompt)
        except NameError:
            print("Not a whole number.")
            return number
        number = int(text)


def main():
    n = get_int("Number? ")
    print(f"Double: {n * 2}")


if __name__ == "__main__":
    main()
