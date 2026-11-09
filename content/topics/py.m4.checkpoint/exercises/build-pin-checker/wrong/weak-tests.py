def is_four_digits(pin):
    """Return True when the PIN is exactly 4 digits."""
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
    """Return True unless the digits count up by one."""
    for position in range(1, len(pin)):
        if int(pin[position]) != int(pin[position - 1]) + 1:
            return True
    return False


def check_pin(pin):
    """Return OK or the first problem."""
    if not is_four_digits(pin):
        return "must be 4 digits"
    if not not_all_same(pin):
        return "digits must not all be the same"
    if not not_counting_up(pin):
        return "digits must not count up"
    return "OK"


def test_check_pin():
    assert check_pin("1357") == "OK"
    assert check_pin("4321") == "OK"
    assert check_pin("2468") == "OK"
    assert check_pin("9075") == "OK"
    print("check_pin: all checks passed")


def main():
    """Ask for a PIN and print the verdict."""
    print(check_pin(input("PIN? ")))


if __name__ == "__main__":
    test_check_pin()
    main()
