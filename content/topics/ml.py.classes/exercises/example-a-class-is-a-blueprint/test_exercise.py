from checks import run


def test_two_accounts():
    """Prints both accounts, then Ada's balance."""
    assert run() == "Account('Ada', 150)\nAccount('Bob', 20)\n150\n"
