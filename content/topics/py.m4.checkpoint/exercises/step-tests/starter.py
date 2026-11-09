# One function per rule, each answering a yes/no question
def has_min_length(password):
    """Return True when the password has at least 8 characters."""
    return len(password) >= 8


def has_digit(password):
    """Return True when the password has at least one digit, 0 to 9."""
    for ch in password:
        if "0" <= ch <= "9":
            return True
    return False


def has_upper(password):
    """Return True when the password has at least one capital letter, A to Z."""
    for ch in password:
        if "A" <= ch <= "Z":
            return True
    return False


# The verdict: the first rule that fails decides the message
def check_password(password):
    """Return OK, or the first problem: too short, needs a digit, needs a capital letter."""
    if not has_min_length(password):
        return "too short"
    if not has_digit(password):
        return "needs a digit"
    if not has_upper(password):
        return "needs a capital letter"
    return "OK"


# The tests: a good password, each rule failing, and the length boundary
def test_check_password():
    assert check_password("Secret99") == ...
    assert check_password("Abcdefg1") == ...
    assert check_password("Abcdef1") == ...
    assert check_password("abc") == ...
    assert check_password("longenough") == ...
    assert check_password("longenough1") == ...
    print("check_password: all checks passed")


# The program
def main():
    """Ask for a password and print the verdict."""
    password = input("Password? ")
    print(check_password(password))


if __name__ == "__main__":
    test_check_password()
    main()
