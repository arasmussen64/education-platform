def get_int(prompt):
    """Ask until the user types a whole number, and return it."""
    while True:
        text = input(prompt)
        try:
            return int(text)
        except ValueError:
            print("That's not a whole number. Try again.")


def main():
    age = get_int("Age? ")
    print(f"Next year you'll be {age + 1}.")


if __name__ == "__main__":
    main()
