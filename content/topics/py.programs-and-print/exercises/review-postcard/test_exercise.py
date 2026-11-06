from checks import run

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.

MESSAGE = ["The weather is lovely.", "Wish you were here,", "Sam"]


def test_greeting_then_blank_line():
    """Starts with the greeting, then a blank line."""
    lines = run().splitlines()
    assert lines[:2] == ["Greetings from Python!", ""]


def test_message():
    """Then the three lines of the message, in order."""
    assert run().splitlines()[2:5] == MESSAGE


def test_exactly():
    """Prints exactly the postcard, with nothing extra."""
    assert run() == "Greetings from Python!\n\n" + "\n".join(MESSAGE) + "\n"
