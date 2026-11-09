def is_right_length(name):
    """Return True when the name has 3 to 12 characters."""
    return 3 <= len(name) <= 12


def starts_with_letter(name):
    """Return True when the first character is a letter."""
    return "a" <= name[0] <= "z" or "A" <= name[0] <= "Z"


def is_simple(name):
    """Return True when every character is a letter, a digit or an underscore."""
    for ch in name:
        if not ("a" <= ch <= "z" or "A" <= ch <= "Z" or "0" <= ch <= "9" or ch == "_"):
            return False
    return True


def check_username(name):
    """Return OK or the first problem."""
    if not is_right_length(name):
        return "must be 3 to 12 characters"
    if not starts_with_letter(name):
        return "must start with a letter"
    if not is_simple(name):
        return "only letters, digits and underscores"
    return "OK"


def test_check_username():
    assert check_username("ada_42") == "OK"
    assert check_username("ab") == "must be 3 to 12 characters"
    assert check_username("9lives") == "must start with a letter"
    assert check_username("ada-42") == "only letters, digits and underscores"
    print("check_username: all checks passed")


def main():
    """Ask for a username and print the verdict."""
    print(check_username(input("Username? ")))


test_check_username()
main()
