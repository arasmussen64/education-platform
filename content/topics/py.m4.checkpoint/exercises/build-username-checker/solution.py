# One function per rule, each answering a yes/no question
def is_right_length(name):
    """Return True when the name has 3 to 12 characters."""
    return 3 <= len(name) <= 12


def is_letter(ch):
    """Return True when the character is a letter, a to z or A to Z."""
    return "a" <= ch <= "z" or "A" <= ch <= "Z"


def starts_with_letter(name):
    """Return True when the first character is a letter."""
    return is_letter(name[0])


def is_simple(name):
    """Return True when every character is a letter, a digit or an underscore."""
    for ch in name:
        if not (is_letter(ch) or "0" <= ch <= "9" or ch == "_"):
            return False
    return True


# The verdict: the first rule that fails decides the message
def check_username(name):
    """Return OK, or the first problem with the username."""
    if not is_right_length(name):
        return "must be 3 to 12 characters"
    if not starts_with_letter(name):
        return "must start with a letter"
    if not is_simple(name):
        return "only letters, digits and underscores"
    return "OK"


# The tests: a good name, each rule failing, and the length boundaries
def test_check_username():
    assert check_username("ada_42") == "OK"
    assert check_username("Ada") == "OK"
    assert check_username("abcdefghijkl") == "OK"
    assert check_username("ab") == "must be 3 to 12 characters"
    assert check_username("abcdefghijklm") == "must be 3 to 12 characters"
    assert check_username("9lives") == "must start with a letter"
    assert check_username("ada-42") == "only letters, digits and underscores"
    print("check_username: all checks passed")


# The program
def main():
    """Ask for a username and print the verdict."""
    name = input("Username? ")
    print(check_username(name))


if __name__ == "__main__":
    test_check_username()
    main()
