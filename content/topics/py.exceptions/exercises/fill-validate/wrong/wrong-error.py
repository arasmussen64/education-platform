def get_positive(prompt):
    """Ask until the user types a whole number greater than 0, and return it."""
    while True:
        text = input(prompt)
        try:
            number = int(text)
        except NameError:
            print("Not a whole number.")
        else:
            if number > 0:
                return number
            print("Must be more than 0.")


def main():
    n = get_positive("How many? ")
    print(f"Twice that is {n * 2}")


if __name__ == "__main__":
    main()
