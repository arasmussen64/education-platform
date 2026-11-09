def has_min_length(password):
    return len(password) >= 8


def has_digit(password):
    for ch in password:
        if "0" <= ch <= "9":
            return True
    return False


def has_upper(password):
    for ch in password:
        if "A" <= ch <= "Z":
            return True
    return False


def check_password(password):
    if not has_min_length(password):
        return "too short"
    if not has_digit(password):
        return "needs a digit"
    if not has_upper(password):
        return "needs a capital letter"
    return "OK"


def test_check_password():
    assert check_password("Secret99") == "OK"
    assert check_password("abc") == "too short"
    assert check_password("longenough") == "needs a digit"
    assert check_password("longenough1") == "needs a capital letter"
    print("check_password: all checks passed")


def main():
    print(check_password(input("Password? ")))


if __name__ == "__main__":
    test_check_password()
    main()
