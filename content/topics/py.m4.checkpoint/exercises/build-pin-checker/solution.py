# One function per rule, each answering a yes/no question
def is_four_digits(pin):
    """Return True when the PIN is exactly 4 characters, all digits."""
    if len(pin) != 4:
        return False
    for ch in pin:
        if not ("0" <= ch <= "9"):
            return False
    return True


def not_all_same(pin):
    """Return True when the characters are not all the same."""
    for ch in pin:
        if ch != pin[0]:
            return True
    return False


def not_counting_up(pin):
    """Return True unless each digit is one more than the one before it."""
    for position in range(1, len(pin)):
        if int(pin[position]) != int(pin[position - 1]) + 1:
            return True
    return False


# The verdict: the first rule that fails decides the message
def check_pin(pin):
    """Return OK, or the first problem with the PIN."""
    if not is_four_digits(pin):
        return "must be 4 digits"
    if not not_all_same(pin):
        return "digits must not all be the same"
    if not not_counting_up(pin):
        return "digits must not count up"
    return "OK"


# The tests: a good PIN, each rule failing, and a PIN that counts down
def test_check_pin():
    assert check_pin("1357") == "OK"
    assert check_pin("4321") == "OK"
    assert check_pin("12345") == "must be 4 digits"
    assert check_pin("12a4") == "must be 4 digits"
    assert check_pin("1111") == "digits must not all be the same"
    assert check_pin("1234") == "digits must not count up"
    print("check_pin: all checks passed")


# The program
def main():
    """Ask for a PIN and print the verdict."""
    pin = input("PIN? ")
    print(check_pin(pin))


if __name__ == "__main__":
    test_check_pin()
    main()
