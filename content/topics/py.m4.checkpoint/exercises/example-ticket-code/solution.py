def is_right_length(code):
    """Return True when the code has exactly 6 characters."""
    return len(code) == 6


def starts_with_letter(code):
    """Return True when the first character is a letter, A to Z or a to z."""
    first = code[0]
    return "A" <= first <= "Z" or "a" <= first <= "z"


def ends_with_digit(code):
    """Return True when the last character is a digit, 0 to 9."""
    return "0" <= code[-1] <= "9"


def check_code(code):
    """Return OK, or the first problem: wrong length, then the first and last characters."""
    if not is_right_length(code):
        return "wrong length"
    if not starts_with_letter(code):
        return "must start with a letter"
    if not ends_with_digit(code):
        return "must end with a digit"
    return "OK"


def test_check_code():
    assert check_code("AB1234") == "OK"
    assert check_code("AB12") == "wrong length"
    assert check_code("AB12345") == "wrong length"
    assert check_code("12345A") == "must start with a letter"
    assert check_code("ABCDEF") == "must end with a digit"
    print("check_code: all checks passed")


def main():
    """Ask for a ticket code and print the verdict."""
    code = input("Ticket code? ")
    print(check_code(code))


if __name__ == "__main__":
    test_check_code()
    main()
