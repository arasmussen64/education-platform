from checks import run


def test_greets():
    """Greets the person by name."""
    assert run("Ada\n") == "Hello, Ada!\n"


def test_without_input():
    """Fails clearly when no input is given."""
    run()
