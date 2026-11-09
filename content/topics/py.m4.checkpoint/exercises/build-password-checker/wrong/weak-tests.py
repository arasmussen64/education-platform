def has_min_length(password):
    """Return True when the password has at least 8 characters."""
    return len(password) >= 8


def has_digit(password):
    """Return True when the password has at least one digit."""
    for ch in password:
        if "0" <= ch <= "9":
            return True
    return False


def has_upper(password):
    """Return True when the password has at least one capital letter."""
    for ch in password:
        if "A" <= ch <= "Z":
            return True
    return False


def check_password(password):
    """Return OK or the first problem."""
    if not has_min_length(password):
        return "too short"
    if not has_digit(password):
        return "needs a digit"
    if not has_upper(password):
        return "needs a capital letter"
    return "OK"


def test_check_password():
    assert check_password("Secret99") == "OK"
    assert check_password("Abcdefg1") == "OK"
    assert check_password("Longenough1") == "OK"
    assert check_password("GoodOne99") == "OK"
    print("check_password: all checks passed")


def main():
    """Ask for a password and print the verdict."""
    print(check_password(input("Password? ")))


if __name__ == "__main__":
    test_check_password()
    main()
